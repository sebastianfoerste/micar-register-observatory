"""Every committed edition's data section is what the generator writes for the
snapshot that edition records, and docs/index.html is the newest edition's page.

A failure here means a generated block was hand-edited, rebuilt from another
snapshot, or that the generator changed without rebuilding the editions.
"""

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
EDITIONS = sorted((REPO / "editions").glob("*.md"))
# Editions whose data section has been generated; a new quarter's file is
# skipped until `make report` fills it.
BUILT = [
    edition
    for edition in EDITIONS
    if recorded_snapshot_date(edition.read_text(encoding="utf-8")) is not None
]


def _metrics(edition: Path) -> dict:
    recorded = recorded_snapshot_date(edition.read_text(encoding="utf-8"))
    assert recorded is not None
    return analyze(load_latest(dated_snapshot(recorded, REPO / "data")))


def test_at_least_one_edition_records_its_snapshot() -> None:
    assert BUILT, "no edition records the snapshot its data section was built from"


@pytest.mark.parametrize("edition", BUILT, ids=lambda path: path.stem)
def test_edition_data_section_matches_its_snapshot(edition: Path) -> None:
    text = edition.read_text(encoding="utf-8")
    assert edition_data_block(text) == "\n" + render_data_section(_metrics(edition)) + "\n"


def test_index_html_is_the_newest_editions_page() -> None:
    newest = EDITIONS[-1]
    if newest not in BUILT:
        pytest.skip(f"{newest.name} has no generated data section yet")
    html = (REPO / "docs" / "index.html").read_text(encoding="utf-8")
    assert html == render_html(_metrics(newest), edition_title(newest))
