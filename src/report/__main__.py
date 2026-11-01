"""CLI: regenerate an edition's data section and the shareable HTML page.

    python -m report build [--edition 2026-Q3] [--fixture PATH | --use-latest]

Without --edition the newest file in editions/ is used. The snapshot it is built
from is chosen so that a rebuild never moves an edition's published numbers by
accident:

- an edition whose data section records a snapshot date is rebuilt from
  data/snapshots/<that date>.json;
- an edition without one (a new quarter's file whose data section is still
  empty) is filled from data/latest.json;
- --use-latest reads data/latest.json in either case, and --fixture PATH reads
  that JSON file instead.

docs/index.html is the newest edition's page, so it is only written when the
edition built is the newest one.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from report.analyze import analyze
from report.render import (
    edition_title,
    recorded_snapshot_date,
    render_data_section,
    render_html,
    update_edition,
)
from report.sources import dated_snapshot, load_latest


def _latest_edition(editions_dir: Path) -> Path | None:
    editions = sorted(editions_dir.glob("*.md"))
    return editions[-1] if editions else None


def _snapshot_source(args: argparse.Namespace, edition_path: Path) -> tuple[Path, str]:
    """The snapshot file to build from, and why that one."""
    data_dir = Path(args.data_dir)
    if args.fixture:
        return Path(args.fixture), "--fixture"
    if args.use_latest:
        return data_dir / "latest.json", "--use-latest"
    recorded = recorded_snapshot_date(edition_path.read_text(encoding="utf-8"))
    if recorded is None:
        return data_dir / "latest.json", "the edition records no snapshot yet"
    return dated_snapshot(recorded, data_dir), f"the snapshot {edition_path.name} records"


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

    snapshot_path, reason = _snapshot_source(args, edition_path)
    if not snapshot_path.exists():
        print(
            f"{snapshot_path} not found ({reason}); nothing was written. "
            "Pass --fixture PATH to build from another snapshot, or --use-latest "
            "to build from data/latest.json.",
            file=sys.stderr,
        )
        return 1
    snapshot = load_latest(snapshot_path)

    metrics = analyze(snapshot)
    update_edition(edition_path, render_data_section(metrics))
    html_path = Path(args.html)
    newest = _latest_edition(editions_dir)
    if newest is not None and edition_path.resolve() == newest.resolve():
        html_path.parent.mkdir(parents=True, exist_ok=True)
        html_path.write_text(render_html(metrics, edition_title(edition_path)), encoding="utf-8")
        page = f"; wrote {html_path}"
    else:
        page = f"; {html_path} left alone, it is the page of the newest edition"
    print(
        f"built {edition_path.name} from {snapshot_path} ({reason}): "
        f"{metrics['total_whitepapers']} white papers, "
        f"{metrics['deep_lint_candidate_pct']}% XHTML/HTML, JSON or DOCX links "
        f"(snapshot {metrics['snapshot_date']}){page}"
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="report")
    parser.add_argument("--editions-dir", default="editions")
    parser.add_argument("--html", default="docs/index.html")
    parser.add_argument("--data-dir", default="data")
    subparsers = parser.add_subparsers(dest="command", required=True)

    build = subparsers.add_parser("build")
    build.add_argument("--edition", default=None)
    source = build.add_mutually_exclusive_group()
    source.add_argument("--fixture", default=None, help="build from this snapshot JSON file")
    source.add_argument(
        "--use-latest",
        action="store_true",
        help="build from data/latest.json even if the edition records another snapshot",
    )
    build.set_defaults(func=cmd_build)

    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
