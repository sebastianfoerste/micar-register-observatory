"""Every committed edition's data section is what the generator writes for the
snapshot that edition records, and docs/index.html is the newest edition's page.

The generator rewrites the recorded date on every build, so that date is pinned
to text the generator never writes: the edition's row in the README editions
table, and every `--edition NAME --fixture data/snapshots/DATE.json` command in
the README or an edition. A failure here means a generated block was
hand-edited, an edition was rebuilt from a snapshot other than the one its README
row names, or the generator changed without rebuilding the editions.
"""

import re
from pathlib import Path

import pytest

from report.analyze import analyze
from report.render import (
    edition_data_block,
    edition_title,
    recorded_snapshot_date,
    render_data_section,
    render_html,
)
from report.sources import dated_snapshot, load_latest

REPO = Path(__file__).resolve().parents[1]
README = (REPO / "README.md").read_text(encoding="utf-8")
EDITIONS = sorted((REPO / "editions").glob("*.md"))
# Editions whose data section has been generated; a new quarter's file is
# skipped until `make report` fills it.
BUILT = [
    edition
    for edition in EDITIONS
    if recorded_snapshot_date(edition.read_text(encoding="utf-8")) is not None
]

# A row of the README editions table: | [2026-Q3](editions/2026-Q3.md) | 2026-09-21 | ...
_README_ROW = re.compile(
    r"^\| \[(?P<edition>[^\]]+)\]\(editions/(?P=edition)\.md\) \| (?P<snapshot>[^|]*?) \|",
    re.MULTILINE,
)
_REBUILD_COMMAND = re.compile(
    r"--edition (?P<edition>\S+) --fixture data/snapshots/(?P<snapshot>\d{4}-\d{2}-\d{2})\.json"
)


def _recorded(edition: Path) -> str:
    recorded = recorded_snapshot_date(edition.read_text(encoding="utf-8"))
    assert recorded is not None
    return recorded


def _metrics(edition: Path) -> dict:
    return analyze(load_latest(dated_snapshot(_recorded(edition), REPO / "data")))


def test_at_least_one_edition_records_its_snapshot() -> None:
    assert BUILT, "no edition records the snapshot its data section was built from"


@pytest.mark.parametrize("edition", BUILT, ids=lambda path: path.stem)
def test_edition_data_section_matches_its_snapshot(edition: Path) -> None:
    text = edition.read_text(encoding="utf-8")
    assert edition_data_block(text) == "\n" + render_data_section(_metrics(edition)) + "\n"


@pytest.mark.parametrize("edition", BUILT, ids=lambda path: path.stem)
def test_edition_records_the_snapshot_its_readme_row_names(edition: Path) -> None:
    rows = {match["edition"]: match["snapshot"] for match in _README_ROW.finditer(README)}
    assert edition.stem in rows, f"README editions table has no row for {edition.stem}"
    assert rows[edition.stem] == _recorded(edition)


@pytest.mark.parametrize("document", [REPO / "README.md", *EDITIONS], ids=lambda path: path.name)
def test_rebuild_commands_name_the_recorded_snapshot(document: Path) -> None:
    built = {edition.stem: _recorded(edition) for edition in BUILT}
    for match in _REBUILD_COMMAND.finditer(document.read_text(encoding="utf-8")):
        assert match["edition"] in built, f"{match[0]} names an edition with no data section"
        assert match["snapshot"] == built[match["edition"]], match[0]


def test_index_html_is_the_newest_editions_page() -> None:
    newest = EDITIONS[-1]
    if newest not in BUILT:
        pytest.skip(f"{newest.name} has no generated data section yet")
    html = (REPO / "docs" / "index.html").read_text(encoding="utf-8")
    assert html == render_html(_metrics(newest), edition_title(newest))
