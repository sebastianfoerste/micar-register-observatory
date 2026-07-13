"""CLI for register refreshes, content verification, and dashboard rendering.

Usage:
    python -m observatory refresh [--date YYYY-MM-DD] [--fixtures DIR]
    python -m observatory verify-content [--limit 25] [--timeout 30]
    python -m observatory render

`--fixtures DIR` reads `<slug>.csv` files from DIR instead of fetching ESMA.
"""

from __future__ import annotations

import argparse
import datetime
import sys
import time
from collections import Counter
from pathlib import Path

from observatory.config import SOURCES
from observatory.content_verify import DEFAULT_MAX_BYTES, normalise_url, verify_url
from observatory.diff import diff_snapshots
from observatory.fetch import fetch_source
from observatory.models import (
    CONTENT_VERIFICATION_FIELDS,
    RegisterSnapshot,
    Snapshot,
)
from observatory.normalize import normalize_csv
from observatory.render import render_dashboard, update_readme, write_feed
from observatory.store import (
    append_changelog,
    load_latest,
    read_changelog,
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
            entries = normalize_csv(source, raw)
            registers.append(
                RegisterSnapshot(
                    slug=source.slug,
                    title=source.title,
                    kind=source.kind,
                    source_url=source.url,
                    fetched=True,
                    entries=entries,
                )
            )
        except Exception as error:  # noqa: BLE001 - one failed source must not kill the run
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


def carry_content_verification(previous: Snapshot | None, current: Snapshot) -> None:
    """Keep evidence only when an entry's source row is unchanged."""
    if previous is None:
        return
    previous_entries = {
        (entry.entry_id, entry.row_hash): entry
        for register in previous.registers
        for entry in register.entries
        if entry.content_verification_status != "not_checked"
    }
    for register in current.registers:
        for entry in register.entries:
            old = previous_entries.get((entry.entry_id, entry.row_hash))
            if old is None:
                continue
            for field in CONTENT_VERIFICATION_FIELDS:
                setattr(entry, field, getattr(old, field))


def _render_outputs(args: argparse.Namespace, snapshot: Snapshot) -> None:
    changelog = read_changelog(Path(args.data_dir))
    update_readme(Path(args.readme), render_dashboard(snapshot, changelog))
    write_feed(Path(args.feed), snapshot, changelog)


def cmd_refresh(args: argparse.Namespace) -> int:
    data_dir = Path(args.data_dir)
    snapshot_date = args.date or datetime.date.today().isoformat()
    fixtures = Path(args.fixtures) if args.fixtures else None

    current = build_snapshot(snapshot_date, fixtures)
    if not any(register.fetched for register in current.registers):
        print("refresh aborted: no register source could be fetched", file=sys.stderr)
        return 1

    previous = load_latest(data_dir)
    changes = diff_snapshots(previous, current)
    carry_content_verification(previous, current)
    save_snapshot(data_dir, current)
    append_changelog(data_dir, changes)
    _render_outputs(args, current)

    fetched = sum(1 for register in current.registers if register.fetched)
    print(
        f"snapshot {snapshot_date}: {fetched}/{len(current.registers)} sources, "
        f"{sum(len(r.entries) for r in current.registers)} entries, "
        f"{len(changes)} change records"
    )
    return 0


def cmd_verify_content(args: argparse.Namespace) -> int:
    data_dir = Path(args.data_dir)
    snapshot = load_latest(data_dir)
    if snapshot is None:
        print("no snapshot found; run refresh first", file=sys.stderr)
        return 1
    if args.limit < 0 or args.timeout <= 0 or args.max_bytes <= 0 or args.delay < 0:
        print("limit and delay must be non-negative; timeout and max-bytes must be positive", file=sys.stderr)
        return 2

    linked_entries = [
        entry
        for register in snapshot.registers
        if register.kind == "whitepaper" and register.fetched
        for entry in register.entries
        if entry.wp_url
    ]
    groups = {}
    for entry in linked_entries:
        groups.setdefault(normalise_url(entry.wp_url), []).append(entry)
    unchecked = [
        group
        for group in groups.values()
        if any(entry.content_verification_status == "not_checked" for entry in group)
    ]
    failed = [
        group
        for group in groups.values()
        if all(entry.content_verification_status != "not_checked" for entry in group)
        and any(
            entry.content_verification_status not in {"verified", "too_large"}
            for entry in group
        )
    ]
    if args.force:
        candidates = list(groups.values())
    elif args.retry_failures:
        candidates = unchecked + failed
    else:
        candidates = unchecked
    selected = candidates if args.limit == 0 else candidates[: args.limit]
    if not selected:
        print("no unchecked or retryable white-paper targets remain")
        _render_outputs(args, snapshot)
        return 0

    results = []
    updated_rows = 0
    for index, group in enumerate(selected):
        result = verify_url(
            group[0].wp_url,
            timeout=args.timeout,
            max_bytes=args.max_bytes,
        )
        for entry in group:
            for field in CONTENT_VERIFICATION_FIELDS:
                setattr(entry, field, result[field])
            updated_rows += 1
        results.append(result)
        if args.delay and index + 1 < len(selected):
            time.sleep(args.delay)

    save_snapshot(data_dir, snapshot)
    _render_outputs(args, snapshot)
    statuses = Counter(result["content_verification_status"] for result in results)
    rendered = ", ".join(f"{status}={count}" for status, count in sorted(statuses.items()))
    remaining = len(candidates) - len(selected)
    print(
        f"checked {len(selected)} unique targets across {updated_rows} register rows "
        f"({rendered}); {remaining} unchecked or retryable targets remain"
    )
    return 0


def cmd_render(args: argparse.Namespace) -> int:
    snapshot = load_latest(Path(args.data_dir))
    if snapshot is None:
        print("no snapshot found; run refresh first", file=sys.stderr)
        return 1
    _render_outputs(args, snapshot)
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
    refresh.set_defaults(func=cmd_refresh)

    verify = subparsers.add_parser("verify-content")
    verify.add_argument("--limit", type=int, default=25, help="0 checks every remaining URL")
    verify.add_argument("--timeout", type=float, default=30)
    verify.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_BYTES)
    verify.add_argument("--delay", type=float, default=0.25)
    verify.add_argument("--force", action="store_true")
    verify.add_argument("--retry-failures", action="store_true")
    verify.set_defaults(func=cmd_verify_content)

    render = subparsers.add_parser("render")
    render.set_defaults(func=cmd_render)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
