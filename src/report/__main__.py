"""CLI: regenerate an edition's data section and the shareable HTML page.

    python -m report build [--edition 2026-Q3] [--fixture PATH]

Without --edition the newest file in editions/ is used. With --fixture the
snapshot is read from that JSON file instead of data/latest.json, for example
a dated file under data/snapshots/.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from report.analyze import analyze
from report.render import render_data_section, render_html, update_edition
from report.sources import load_latest


def _latest_edition(editions_dir: Path) -> Path | None:
    editions = sorted(editions_dir.glob("*.md"))
    return editions[-1] if editions else None


def _edition_title(edition_path: Path) -> str:
    for line in edition_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return edition_path.stem


def cmd_build(args: argparse.Namespace) -> int:
    editions_dir = Path(args.editions_dir)
    edition_path: Path | None
    if args.edition:
        edition_path = editions_dir / f"{args.edition}.md"
    else:
        edition_path = _latest_edition(editions_dir)
    if edition_path is None or not edition_path.exists():
        print(f"edition not found under {editions_dir}", file=sys.stderr)
        return 1

    snapshot = load_latest(Path(args.fixture)) if args.fixture else load_latest()

    metrics = analyze(snapshot)
    update_edition(edition_path, render_data_section(metrics))
    Path(args.html).parent.mkdir(parents=True, exist_ok=True)
    Path(args.html).write_text(
        render_html(metrics, _edition_title(edition_path)), encoding="utf-8"
    )
    print(
        f"built {edition_path.name}: {metrics['total_whitepapers']} white papers, "
        f"{metrics['machine_readable_pct']}% machine-readable "
        f"(snapshot {metrics['snapshot_date']})"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="report")
    parser.add_argument("--editions-dir", default="editions")
    parser.add_argument("--html", default="docs/index.html")
    subparsers = parser.add_subparsers(dest="command", required=True)

    build = subparsers.add_parser("build")
    build.add_argument("--edition", default=None)
    build.add_argument("--fixture", default=None)
    build.set_defaults(func=cmd_build)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
