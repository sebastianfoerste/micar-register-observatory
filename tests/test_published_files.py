"""The committed generated files are what the code writes from the committed
data: README summary block, DASHBOARD.md, docs/feed.json, docs/changes.atom,
data/exports/ and the latest digest. A failure here means a generated file was
edited by hand, or the renderer changed without `uv run python -m observatory
render` being run and committed."""

import argparse
import shutil
from pathlib import Path

from observatory.__main__ import pending_quarantine, publish
from observatory.store import load_latest, read_changelog

REPO = Path(__file__).resolve().parents[1]
GENERATED = (
    "README.md",
    "DASHBOARD.md",
    "docs/feed.json",
    "docs/changes.atom",
    "data/exports/casps.csv",
    "data/exports/changes.csv",
    "data/exports/ncasp.csv",
    "data/exports/whitepapers.csv",
)


def test_committed_generated_files_match_the_renderer(tmp_path: Path) -> None:
    data = tmp_path / "data"
    shutil.copytree(REPO / "data", data, ignore=shutil.ignore_patterns("raw"))
    (tmp_path / "docs").mkdir()
    for rel in ("README.md", "DASHBOARD.md", "docs/feed.json", "docs/changes.atom"):
        shutil.copy(REPO / rel, tmp_path / rel)
    shutil.copytree(REPO / "digests", tmp_path / "digests")
    args = argparse.Namespace(
        data_dir=str(data),
        readme=str(tmp_path / "README.md"),
        dashboard=str(tmp_path / "DASHBOARD.md"),
        feed=str(tmp_path / "docs" / "feed.json"),
        atom=str(tmp_path / "docs" / "changes.atom"),
        digests=str(tmp_path / "digests"),
    )
    snapshot = load_latest(data)
    assert snapshot is not None
    publish(args, snapshot, read_changelog(data), pending_quarantine(data, snapshot))

    for rel in GENERATED:
        assert (tmp_path / rel).read_bytes() == (REPO / rel).read_bytes(), rel
    committed = sorted(path.name for path in (REPO / "digests").glob("*.md"))
    assert sorted(path.name for path in (tmp_path / "digests").glob("*.md")) == committed
    for name in committed:
        assert (tmp_path / "digests" / name).read_bytes() == (REPO / "digests" / name).read_bytes()
