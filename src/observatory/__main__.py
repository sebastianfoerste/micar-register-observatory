"""CLI: refresh the register snapshot, re-render the dashboard, query history.

Usage:
    python -m observatory refresh [--date YYYY-MM-DD] [--data-dir data] [--fixtures DIR]
                                  [--accept-shrink] [--force] [--no-archive]
    python -m observatory render  [--data-dir data]
    python -m observatory asof    (--lei LEI | --name TEXT) [--date YYYY-MM-DD]
                                  [--register SLUG] [--json]

`refresh` and `render` rewrite the README dashboard, docs/feed.json,
docs/changes.atom, data/exports/ and the latest digest under digests/.
`--fixtures DIR` reads `<slug>.csv` files from DIR instead of fetching ESMA —
used by tests and offline runs. `--accept-shrink` records an export that would
otherwise be quarantined for a sharp drop in rows (see diff.export_shrinks).
A refresh is skipped, and records nothing, when an export was already fetched
(recorded or quarantined) within the last REFRESH_WINDOW_DAYS days: the weekly
workflow has a fallback slot that must not add a second snapshot to a week.
`--force` and `--accept-shrink` fetch anyway.
An export that ESMA's CDN refuses (a 403 from the CloudFront edge, as every
GitHub-hosted runner got from 2026-10-26) is taken from the newest copy in the
Wayback Machine when that copy is at most MAX_ARCHIVE_AGE_DAYS old; the snapshot
and the feed say so (`fetched_from`, `archived_at`), as do the raw manifest
(`url`, `archived_at`) and the dashboard. `--no-archive` fails instead of using
an archived copy.
`asof` prints what the last snapshot recorded on or before a date lists for a
firm, and the firm's recorded changes up to then.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import sys
from pathlib import Path

from observatory.asof import as_of, render_text
from observatory.config import SOURCES, RegisterSource
from observatory.diff import Shrink, diff_snapshots, export_shrinks
from observatory.digest import write_atom, write_digests
from observatory.export import write_exports
from observatory.fetch import Download, fetch_export, utc_now
from observatory.models import ChangeRecord, RegisterSnapshot, Snapshot
from observatory.normalize import column_drift, parse_register
from observatory.render import Quarantine, render_dashboard, update_readme, write_feed
from observatory.store import (
    append_changelog,
    latest_quarantine,
    load_latest,
    quarantine_dates,
    read_changelog,
    save_quarantine,
    save_raw,
    save_snapshot,
    snapshot_dates,
)

# An export fetched this many days or fewer before the snapshot date counts as
# this week's: a second scheduled run then records nothing. Six would skip the
# Monday after a Tuesday-dated fallback snapshot; five does not.
REFRESH_WINDOW_DAYS = 5


def read_fixture(fixtures: Path, source: RegisterSource) -> Download:
    path = fixtures / f"{source.slug}.csv"
    return Download(body=path.read_bytes(), url=f"fixture:{path.name}", retrieved_at=utc_now())


def build_snapshot(
    snapshot_date: str, fixtures: Path | None, archive: bool = True
) -> tuple[Snapshot, dict[str, Download]]:
    """Fetch and parse every source; also return the downloads, by slug.

    `archive` allows the Wayback Machine to stand in for an export ESMA refuses.
    """
    registers = []
    downloads: dict[str, Download] = {}
    for source in SOURCES:
        try:
            if fixtures is not None:
                download = read_fixture(fixtures, source)
            else:
                download = fetch_export(source, archive=archive)
            if download.archived_at:
                print(
                    f"::warning title=Archived copy used::{source.slug}: ESMA refused the "
                    f"download; using the Wayback Machine's copy captured "
                    f"{download.archived_at} ({download.url})"
                )
            parsed = parse_register(source, download.body, enforce_min_rows=fixtures is None)
            downloads[source.slug] = download
            registers.append(
                RegisterSnapshot(
                    slug=source.slug,
                    title=source.title,
                    kind=source.kind,
                    source_url=source.url,
                    fetched=True,
                    entries=parsed.entries,
                    columns=parsed.columns,
                    source_last_modified=download.last_modified,
                    source_sha256=hashlib.sha256(download.body).hexdigest(),
                    fetched_from=download.url,
                    archived_at=download.archived_at,
                )
            )
        except Exception as error:  # noqa: BLE001 — one failed source must not kill the run
            registers.append(
                RegisterSnapshot(
                    slug=source.slug,
                    title=source.title,
                    kind=source.kind,
                    source_url=source.url,
                    fetched=False,
                    # Room for ESMA's described refusal and the archive's reason
                    # (fetch.SourceUnavailable); a failed source is never recorded.
                    fetch_error=str(error)[:2000],
                )
            )
    return Snapshot(snapshot_date=snapshot_date, registers=registers), downloads


def report_column_drift(snapshot: Snapshot) -> list[str]:
    """Warn (as a GitHub Actions annotation) when ESMA changed a file's columns."""
    warnings = []
    for source in SOURCES:
        register = snapshot.register(source.slug)
        if register is None or not register.fetched:
            continue
        added, dropped = column_drift(source, register.columns)
        if added or dropped:
            warnings.append(
                f"::warning title=ESMA source change::{source.slug}: "
                f"columns added {added}, dropped {dropped}"
            )
    for warning in warnings:
        print(warning)
    return warnings


def unconfirmed_shrinks(
    data_dir: Path, previous: Snapshot | None, current: Snapshot
) -> list[Shrink]:
    """Sharp drops in rows that the previous, quarantined export did not show too.

    One export with a sharp drop is set aside; when the next export shows the
    same register just as far below the last recorded snapshot, the drop is real.
    """
    shrinks = export_shrinks(previous, current)
    if previous is None or not shrinks:
        return []
    earlier = latest_quarantine(data_dir, previous.snapshot_date)
    confirmed = {shrink.slug for shrink in export_shrinks(previous, earlier)} if earlier else set()
    for shrink in shrinks:
        if shrink.slug in confirmed:
            print(
                f"::notice title=Register drop confirmed::{shrink.describe()} in two "
                "consecutive exports; recording it"
            )
    return [shrink for shrink in shrinks if shrink.slug not in confirmed]


def pending_quarantine(data_dir: Path, snapshot: Snapshot) -> Quarantine | None:
    """The export set aside after `snapshot`, when the last refresh quarantined one."""
    earlier = latest_quarantine(data_dir, snapshot.snapshot_date)
    shrinks = export_shrinks(snapshot, earlier) if earlier else []
    if earlier is None or not shrinks:
        return None
    return Quarantine(snapshot_date=earlier.snapshot_date, shrinks=shrinks)


def publish(
    args: argparse.Namespace,
    snapshot: Snapshot,
    changelog: list[ChangeRecord],
    note: Quarantine | None = None,
) -> None:
    """Rewrite every file derived from the recorded data: the README dashboard,
    docs/feed.json, data/exports/, the digests and docs/changes.atom."""
    data_dir = Path(args.data_dir)
    update_readme(Path(args.readme), render_dashboard(snapshot, changelog, note))
    write_feed(Path(args.feed), snapshot, changelog, note)
    write_exports(data_dir / "exports", snapshot, changelog)
    write_digests(Path(args.digests), data_dir, changelog)
    write_atom(Path(args.atom), data_dir, changelog)


def quarantine(
    args: argparse.Namespace,
    previous: Snapshot,
    current: Snapshot,
    shrinks: list[Shrink],
    downloads: dict[str, Download],
) -> int:
    """Set the export aside, leave the recorded history alone and say so."""
    data_dir = Path(args.data_dir)
    path = save_quarantine(data_dir, current)
    save_raw(data_dir, current.snapshot_date, downloads, recorded_as="quarantine")
    for shrink in shrinks:
        print(
            f"::warning title=Register export quarantined::{shrink.describe()} since "
            f"{previous.snapshot_date}; the export is kept in {path} and not recorded"
        )
    note = Quarantine(snapshot_date=current.snapshot_date, shrinks=shrinks)
    publish(args, previous, read_changelog(data_dir), note)
    print(
        f"snapshot {current.snapshot_date} quarantined; "
        f"the recorded snapshot stays {previous.snapshot_date}"
    )
    return 0


def fetched_this_week(data_dir: Path, snapshot_date: str) -> str:
    """The date of an export recorded or quarantined within REFRESH_WINDOW_DAYS
    days before `snapshot_date` (or on it); "" when there is none."""
    dates = [day for day in snapshot_dates(data_dir) + quarantine_dates(data_dir) if day]
    if not dates:
        return ""
    newest = max(dates)
    age = (datetime.date.fromisoformat(snapshot_date) - datetime.date.fromisoformat(newest)).days
    return newest if 0 <= age <= REFRESH_WINDOW_DAYS else ""


def cmd_refresh(args: argparse.Namespace) -> int:
    data_dir = Path(args.data_dir)
    snapshot_date = args.date or datetime.date.today().isoformat()
    fixtures = Path(args.fixtures) if args.fixtures else None

    force = bool(getattr(args, "force", False) or args.accept_shrink)
    recent = "" if force else fetched_this_week(data_dir, snapshot_date)
    if recent:
        print(
            f"::notice title=Export already fetched this week::an export dated {recent} is "
            f"recorded or quarantined; {snapshot_date} fetches nothing (use --force to fetch)"
        )
        return 0

    archive = not getattr(args, "no_archive", False)
    current, downloads = build_snapshot(snapshot_date, fixtures, archive=archive)
    failed = [r for r in current.registers if not r.fetched]
    if failed:
        # Fail closed: a partial snapshot would be committed and then trip the
        # freshness gate; better to keep the last good data and fail loudly.
        for register in failed:
            print(f"refresh failed: {register.slug}: {register.fetch_error}", file=sys.stderr)
        return 1

    report_column_drift(current)
    previous = load_latest(data_dir)
    unconfirmed = [] if args.accept_shrink else unconfirmed_shrinks(data_dir, previous, current)
    if previous is not None and unconfirmed:
        return quarantine(args, previous, current, unconfirmed, downloads)
    changes = diff_snapshots(previous, current, read_changelog(data_dir))
    save_snapshot(data_dir, current)
    save_raw(data_dir, snapshot_date, downloads, recorded_as="snapshot")
    append_changelog(data_dir, changes)

    publish(args, current, read_changelog(data_dir))

    fetched = sum(1 for register in current.registers if register.fetched)
    print(
        f"snapshot {snapshot_date}: {fetched}/{len(current.registers)} sources, "
        f"{sum(len(r.entries) for r in current.registers)} entries, "
        f"{len(changes)} change records"
    )
    return 0


def cmd_render(args: argparse.Namespace) -> int:
    data_dir = Path(args.data_dir)
    snapshot = load_latest(data_dir)
    if snapshot is None:
        print("no snapshot found; run refresh first", file=sys.stderr)
        return 1
    publish(args, snapshot, read_changelog(data_dir), pending_quarantine(data_dir, snapshot))
    print(f"rendered dashboard for snapshot {snapshot.snapshot_date}")
    return 0


def cmd_asof(args: argparse.Namespace) -> int:
    date = args.date or datetime.date.today().isoformat()
    answer = as_of(
        Path(args.data_dir),
        date,
        lei=args.lei or "",
        name=args.name or "",
        register=args.register or "",
    )
    if args.json:
        print(json.dumps(answer.to_json(), ensure_ascii=False, indent=1))
    else:
        print(render_text(answer), end="")
    return 0 if answer.snapshot_date else 1


def iso_day(value: str) -> str:
    return datetime.date.fromisoformat(value).isoformat()


def main() -> int:
    parser = argparse.ArgumentParser(prog="observatory")
    parser.add_argument("--data-dir", default="data")
    parser.add_argument("--readme", default="README.md")
    parser.add_argument("--feed", default="docs/feed.json")
    parser.add_argument("--atom", default="docs/changes.atom")
    parser.add_argument("--digests", default="digests")
    subparsers = parser.add_subparsers(dest="command", required=True)

    refresh = subparsers.add_parser("refresh")
    refresh.add_argument("--date", default=None)
    refresh.add_argument("--fixtures", default=None)
    refresh.add_argument("--accept-shrink", action="store_true")
    refresh.add_argument(
        "--force", action="store_true", help="fetch even if an export was fetched this week"
    )
    refresh.add_argument(
        "--no-archive",
        action="store_true",
        help="fail when ESMA refuses an export instead of using the Wayback Machine's copy",
    )
    refresh.set_defaults(func=cmd_refresh)

    render = subparsers.add_parser("render")
    render.set_defaults(func=cmd_render)

    asof = subparsers.add_parser(
        "asof", help="what the register listed for a firm on a date, from the recorded history"
    )
    who = asof.add_mutually_exclusive_group(required=True)
    who.add_argument("--lei", default=None)
    who.add_argument("--name", default=None, help="case-insensitive part of the name")
    asof.add_argument("--date", type=iso_day, default=None, help="YYYY-MM-DD; default today")
    asof.add_argument("--register", choices=[source.slug for source in SOURCES], default=None)
    asof.add_argument("--json", action="store_true")
    asof.set_defaults(func=cmd_asof)

    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
