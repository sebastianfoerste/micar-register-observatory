import csv
import io
import shutil
from pathlib import Path

import pytest

from observatory.__main__ import cmd_refresh
from observatory.export import EXPORT_COLUMNS, export_tables, to_csv
from observatory.store import load_latest, read_changelog
from test_pipeline import FIXTURES, args_for, seed_readme


def read_csv(text: str) -> tuple[list[str], list[dict[str, str]]]:
    reader = csv.DictReader(io.StringIO(text))
    return list(reader.fieldnames or []), list(reader)


@pytest.fixture
def data(tmp_path: Path) -> Path:
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
    return tmp_path / "data"


def test_the_refresh_writes_one_csv_per_export(data: Path) -> None:
    for name, columns in EXPORT_COLUMNS.items():
        header, _ = read_csv((data / "exports" / f"{name}.csv").read_text(encoding="utf-8"))
        assert tuple(header) == columns


def test_entity_exports_carry_the_typed_fields_of_the_latest_snapshot(data: Path) -> None:
    snapshot = load_latest(data)
    assert snapshot is not None
    tables = export_tables(snapshot, read_changelog(data))
    _, casps = read_csv(tables["casps"])
    assert len(casps) == 4
    first = casps[0]
    assert first["snapshot_date"] == "2026-10-26" and first["register"] == "casps"
    assert first["entity_name"] == "CASP One SAS" and first["lei"] == "529900CASPONE0000001"
    assert first["authorisation_date"] == "2026-01-15"
    assert first["services"] == "a|c"
    assert first["service_countries"] == "BE|DE|FR|IT"
    assert first["last_update"] == "2026-01-15"  # ISO, from ESMA's 15/01/2026
    custody = next(row for row in casps if row["entity_name"] == "Example Custody GmbH")
    assert custody["withdrawal_date"] == "2026-04-30"

    _, ncasp = read_csv(tables["ncasp"])
    assert [row["decision_date"] for row in ncasp] == ["2026-02-12", "2026-10-09"]
    assert ncasp[0]["reason"] == "Synthetic reason text for a fixture"


def test_the_white_paper_export_joins_the_three_registers(data: Path) -> None:
    snapshot = load_latest(data)
    assert snapshot is not None
    _, rows = read_csv(export_tables(snapshot, [])["whitepapers"])
    assert [(row["register"], row["entity_name"]) for row in rows] == [
        ("other-wp", "Example Issuer GmbH"),
        ("emt-wp", "EMT Issuer Ltd"),
    ]
    assert rows[0]["offer_countries"] == "DE|FR" and rows[0]["format_class"] == "xhtml/html"
    assert rows[0]["modification_noted"] == "false"
    assert rows[1]["offer_start_date"] == "2026-01-01"


def test_a_snapshot_without_v2_fields_leaves_the_modification_flag_empty(data: Path) -> None:
    snapshot = load_latest(data)
    assert snapshot is not None
    other = snapshot.register("other-wp")
    assert other is not None
    other.entries = [entry.model_copy(update={"fields": {}}) for entry in other.entries]
    _, rows = read_csv(export_tables(snapshot, [])["whitepapers"])
    assert rows[0]["modification_noted"] == ""


def test_the_change_export_has_one_row_per_changelog_record(data: Path) -> None:
    changes = read_changelog(data)
    _, rows = read_csv((data / "exports" / "changes.csv").read_text(encoding="utf-8"))
    assert len(rows) == len(changes)
    changed = next(row for row in rows if row["change"] == "changed")
    assert changed["entity_name"] == "CASP One SAS"
    assert changed["changed_fields"] == "ac_serviceCode_cou"
    assert changed["subtypes"] == "service_countries_added"
    assert changed["record_version"] == "2"
    missing = next(row for row in rows if row["change"] == "missing")
    assert missing["entity_name"] == "SKYGATE Network GmbH"


def test_cells_with_separators_survive_a_round_trip() -> None:
    value = 'Name, "quoted"\nsecond line'
    text = to_csv(("a", "b"), [{"a": value, "b": "x"}])
    assert read_csv(text)[1] == [{"a": value, "b": "x"}]
