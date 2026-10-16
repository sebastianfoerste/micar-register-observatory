import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from observatory.__main__ import cmd_refresh
from observatory.digest import (
    ATOM_ENTRIES,
    ATOM_NS,
    code,
    link,
    render_atom,
    render_digest,
    text,
    write_digests,
)
from observatory.models import ChangeRecord
from observatory.store import load_snapshot, read_changelog
from test_pipeline import FIXTURES, args_for, seed_readme

A = f"{{{ATOM_NS}}}"


@pytest.fixture
def site(tmp_path: Path) -> Path:
    """Two weekly refreshes: CASP One adds a country, SKYGATE leaves the Title II export."""
    seed_readme(tmp_path)
    (tmp_path / "data").mkdir()
    edited = tmp_path / "edited"
    shutil.copytree(FIXTURES, edited)
    casps = edited / "casps.csv"
    casps.write_text(
        casps.read_text(encoding="utf-8").replace("FR|BE|DE", "FR|BE|DE|IT"), encoding="utf-8"
    )
    other = edited / "other-wp.csv"
    lines = other.read_text(encoding="utf-8").splitlines(keepends=True)
    other.write_text("".join(line for line in lines if "SKYGATE" not in line), encoding="utf-8")
    assert cmd_refresh(args_for(tmp_path, "2026-10-19", FIXTURES)) == 0
    assert cmd_refresh(args_for(tmp_path, "2026-10-26", edited)) == 0
    return tmp_path


def test_each_refresh_writes_a_digest(site: Path) -> None:
    first = (site / "digests" / "2026-10-19.md").read_text(encoding="utf-8")
    assert first.startswith("# MiCAR register changes recorded on 2026-10-19\n")
    assert "recorded on 2026-10-19, the first snapshot." in first
    assert "- `casps`: baseline established with 4 entries." in first

    digest = (site / "digests" / "2026-10-26.md").read_text(encoding="utf-8")
    assert "compared with the snapshot of 2026-10-19" in digest
    assert "makes no assessment of any issuer" in digest
    assert (
        "| Authorised crypto-asset service providers (CASPs), `casps` | 4 | 3 "
        "| 0 | 1 | 0 | 0 | 0 |" in digest
    )
    assert "## Changed (1)" in digest
    assert "- **casps** · CASP One SAS · FR · LEI 529900CASPONE0000001" in digest
    assert "  - `ac_serviceCode_cou`: `FR|BE|DE` → `FR|BE|DE|IT`" in digest
    assert "  - `service_countries_added`" in digest
    assert "## Missing (1)" in digest
    assert "- **other-wp** · SKYGATE Network GmbH · AT · LEI 984500BBFE52FE449926" in digest
    assert "`missing`: not in this export for the first time." in digest
    assert "record version 1" not in digest


def test_digests_already_written_are_kept_and_the_latest_is_rewritten(site: Path) -> None:
    folder = site / "digests"
    (folder / "2026-10-19.md").write_text("as published\n", encoding="utf-8")
    (folder / "2026-10-26.md").write_text("stale\n", encoding="utf-8")
    written = write_digests(folder, site / "data", read_changelog(site / "data"))
    assert written == [folder / "2026-10-26.md"]
    assert (folder / "2026-10-19.md").read_text(encoding="utf-8") == "as published\n"
    assert (folder / "2026-10-26.md").read_text(encoding="utf-8").startswith("# MiCAR")


def test_version_1_absences_are_explained_with_their_own_meaning(site: Path) -> None:
    snapshot = load_snapshot(site / "data", "2026-10-26")
    removed = ChangeRecord(
        snapshot_date="2026-10-26", register_slug="other-wp", change="removed",
        entry_id="0123456789abcdef", entity_name="Old Record Ltd", member_state="DE",
        detail="entry no longer present in the register export",
    )
    digest = render_digest(snapshot, "2026-10-19", [removed])
    assert "## Removed (1)" in digest
    assert "record version 1): `removed` means not in this export, for the first time" in digest
    assert "`removed`: not in two consecutive exports" not in digest


def test_register_text_cannot_break_the_markdown() -> None:
    assert text("A | B *bold* [x](y)\nnext") == r"A \| B \*bold\* \[x\](y) next"
    assert link("https://example.com/a_b*c.pdf") == "<https://example.com/a_b*c.pdf>"
    assert link("WWW.EXAMPLE.AT") == "WWW.EXAMPLE.AT"
    assert link("https://a.example\nhttps://b.example") == r"https://a.example https://b.example"
    assert code("") == "(blank)"
    assert code("x" * 100) == "`" + "x" * 79 + "…`"
    assert code("a`b") == "`` a`b ``"


def test_the_atom_feed_has_one_entry_per_snapshot_newest_first(site: Path) -> None:
    feed = ET.fromstring((site / "docs" / "changes.atom").read_text(encoding="utf-8"))
    assert feed.tag == f"{A}feed"
    assert feed.findtext(f"{A}updated") == "2026-10-26T00:00:00Z"
    assert feed.find(f"{A}author/{A}name") is not None
    self_link = feed.find(f"{A}link[@rel='self']")
    assert self_link is not None and self_link.get("href", "").endswith("/docs/changes.atom")
    entries = feed.findall(f"{A}entry")
    assert [entry.findtext(f"{A}title") for entry in entries] == [
        "2026-10-26: 1 changed, 1 missing",
        "2026-10-19: first snapshot",
    ]
    newest = entries[0]
    assert newest.findtext(f"{A}id", "").endswith("/changes/2026-10-26")
    assert newest.findtext(f"{A}summary") == "casps: 1 changed; other-wp: 1 missing"
    digest_link = newest.find(f"{A}link")
    assert digest_link is not None
    assert digest_link.get("href", "").endswith("/blob/main/digests/2026-10-26.md")
    first = entries[1].findtext(f"{A}summary", "")
    assert first.startswith("art-wp: baseline established with 0 entries; casps: baseline")


def test_the_atom_feed_keeps_a_year_of_snapshots() -> None:
    dates = [f"2026-{month:02d}-{day:02d}" for month in range(1, 13) for day in (1, 15)]
    dates += [f"2027-01-{day:02d}" for day in range(1, 31)]
    feed = ET.fromstring(render_atom(dates, []))
    entries = feed.findall(f"{A}entry")
    assert len(entries) == ATOM_ENTRIES
    assert entries[0].findtext(f"{A}title") == "2027-01-30: no changes"
    assert ET.fromstring(render_atom([], [])).findtext(f"{A}updated") == "1970-01-01T00:00:00Z"
