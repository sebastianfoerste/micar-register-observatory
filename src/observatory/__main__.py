"""CLI: refresh the register snapshot and re-render the dashboard.

Usage:
    python -m observatory refresh [--date YYYY-MM-DD] [--data-dir data] [--fixtures DIR]
                                  [--accept-shrink]
    python -m observatory render  [--data-dir data]

`--fixtures DIR` reads `<slug>.csv` files from DIR instead of fetching ESMA —
used by tests and offline runs. `--accept-shrink` records an export that would
otherwise be quarantined for a sharp drop in rows (see diff.export_shrinks).
"""

from __future__ import annotations

import argparse
import datetime
import sys
from pathlib import Path

from observatory.config import SOURCES
from observatory.diff import Shrink, diff_snapshots, export_shrinks
from observatory.fetch import fetch_source
from observatory.models import RegisterSnapshot, Snapshot
from observatory.normalize import column_drift, parse_register
from observatory.render import Quarantine, render_dashboard, update_readme, write_feed
from observatory.store import (
    append_changelog,
    latest_quarantine,
    load_latest,
    read_changelog,
    save_quarantine,
    save_snapshot,
)


def build_snapshot(snapshot_date: str, fixtures: Path | None) -> Snapshot:
    registers = []
    for source in SOURCES:
        try:
            if fixtures is not None:
                raw = (fixtures / f"{source.slug}.csv").read_bytes()
            else:
                raw = fetch_source(source)
            parsed = parse_register(source, raw, enforce_min_rows=fixtures is None)
            registers.append(
                RegisterSnapshot(
                    slug=source.slug,
                    title=source.title,
                    kind=source.kind,
                    source_url=source.url,
                    fetched=True,
                    entries=parsed.entries,
                    columns=parsed.columns,
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
                    fetch_error=str(error)[:200],
                )
            )
    return Snapshot(snapshot_date=snapshot_date, registers=registers)


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


def quarantine(
    args: argparse.Namespace, previous: Snapshot, current: Snapshot, shrinks: list[Shrink]
) -> int:
    """Set the export aside, leave the recorded history alone and say so."""
    data_dir = Path(args.data_dir)
    path = save_quarantine(data_dir, current)
    for shrink in shrinks:
        print(
            f"::warning title=Register export quarantined::{shrink.describe()} since "
            f"{previous.snapshot_date}; the export is kept in {path} and not recorded"
        )
    note = Quarantine(snapshot_date=current.snapshot_date, shrinks=shrinks)
    changelog = read_changelog(data_dir)
    update_readme(Path(args.readme), render_dashboard(previous, changelog, note))
    write_feed(Path(args.feed), previous, changelog, note)
    print(
        f"snapshot {current.snapshot_date} quarantined; "
        f"the recorded snapshot stays {previous.snapshot_date}"
    )
    return 0


def cmd_refresh(args: argparse.Namespace) -> int:
    data_dir = Path(args.data_dir)
    snapshot_date = args.date or datetime.date.today().isoformat()
    fixtures = Path(args.fixtures) if args.fixtures else None

    current = build_snapshot(snapshot_date, fixtures)
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
        return quarantine(args, previous, current, unconfirmed)
    changes = diff_snapshots(previous, current, read_changelog(data_dir))
    save_snapshot(data_dir, current)
    append_changelog(data_dir, changes)

    update_readme(Path(args.readme), render_dashboard(current, read_changelog(data_dir)))
    write_feed(Path(args.feed), current, read_changelog(data_dir))

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
    changelog = read_changelog(data_dir)
    note = pending_quarantine(data_dir, snapshot)
    update_readme(Path(args.readme), render_dashboard(snapshot, changelog, note))
    write_feed(Path(args.feed), snapshot, changelog, note)
    print(f"rendered dashboard for snapshot {snapshot.snapshot_date}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="observatory")
    parser.add_argument("--data-dir", default="data")
    parser.add_argument("--readme", default="README.md")
    parser.add_argument("--feed", default="docs/feed.json")
    subparsers = parser.add_subparsers(dest="command", required=True)

    refresh = subparsers.add_parser("refresh")
    refresh.add_argument("--date", default=None)
    refresh.add_argument("--fixtures", default=None)
    refresh.add_argument("--accept-shrink", action="store_true")
    refresh.set_defaults(func=cmd_refresh)

    render = subparsers.add_parser("render")
    render.set_defaults(func=cmd_render)

    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
