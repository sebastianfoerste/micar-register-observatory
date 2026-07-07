"""CLI: refresh the register snapshot and re-render the dashboard.

Usage:
    python -m observatory refresh [--date YYYY-MM-DD] [--data-dir data] [--fixtures DIR]
    python -m observatory render  [--data-dir data]

`--fixtures DIR` reads `<slug>.csv` files from DIR instead of fetching ESMA —
used by tests and offline runs.
"""

from __future__ import annotations

import argparse
import datetime
import sys
from pathlib import Path

from observatory.config import SOURCES
from observatory.diff import diff_snapshots
from observatory.fetch import fetch_source
from observatory.models import RegisterSnapshot, Snapshot
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
    update_readme(Path(args.readme), render_dashboard(snapshot, changelog))
    write_feed(Path(args.feed), snapshot, changelog)
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

    render = subparsers.add_parser("render")
    render.set_defaults(func=cmd_render)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
