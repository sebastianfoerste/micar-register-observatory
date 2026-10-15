import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from observatory.__main__ import cmd_refresh
from observatory.asof import as_of, render_text
from test_pipeline import FIXTURES, args_for, seed_readme

CASP_ONE = "529900CASPONE0000001"
CUSTODY = "529900EXAMPLECUST001"


@pytest.fixture
def data(tmp_path: Path) -> Path:
    """Two weekly refreshes: CASP One adds a country, Example Custody leaves the export."""
    seed_readme(tmp_path)
    (tmp_path / "data").mkdir()
    edited = tmp_path / "edited"
    shutil.copytree(FIXTURES, edited)
    casps = edited / "casps.csv"
    lines = casps.read_text(encoding="utf-8").splitlines(keepends=True)
    casps.write_text(
        "".join(line for line in lines if CUSTODY not in line).replace("FR|BE|DE", "FR|BE|DE|IT"),
        encoding="utf-8",
    )
    assert cmd_refresh(args_for(tmp_path, "2026-10-19", FIXTURES)) == 0
    assert cmd_refresh(args_for(tmp_path, "2026-10-26", edited)) == 0
    return tmp_path / "data"


def test_the_answer_comes_from_the_last_snapshot_on_or_before_the_date(data: Path) -> None:
    answer = as_of(data, "2026-10-25", lei=CASP_ONE)
    assert answer.snapshot_date == "2026-10-19"
    assert [row.authorisation_date for row in answer.rows] == ["2026-01-15", "2026-06-01"]
    assert answer.rows[0].service_countries == ["BE", "DE", "FR"]
    assert answer.not_listed_in == ["other-wp", "emt-wp", "art-wp", "ncasp"]
    assert answer.history == []

    later = as_of(data, "2026-10-26", lei=CASP_ONE.lower())
    assert later.snapshot_date == "2026-10-26"
    assert later.rows[0].service_countries == ["BE", "DE", "FR", "IT"]
    [record] = later.history
    assert (record.change, record.subtypes) == ("changed", ["service_countries_added"])


def test_history_follows_a_firm_that_left_the_export(data: Path) -> None:
    before = as_of(data, "2026-10-19", name="example CUSTODY")
    assert [row.withdrawal_date for row in before.rows] == ["2026-04-30"]
    after = as_of(data, "2026-11-30", lei=CUSTODY)
    assert after.snapshot_date == "2026-10-26"
    assert after.rows == [] and "casps" in after.not_listed_in
    assert [(r.snapshot_date, r.change) for r in after.history] == [("2026-10-26", "missing")]


def test_a_register_filter_and_dates_before_the_first_snapshot(data: Path) -> None:
    answer = as_of(data, "2026-10-26", name="unregistered", register="ncasp")
    assert len(answer.rows) == 2 and answer.not_listed_in == []
    assert as_of(data, "2026-10-26", name="unregistered", register="casps").rows == []
    early = as_of(data, "2026-07-01", lei=CASP_ONE)
    assert early.snapshot_date == "" and early.rows == []
    assert render_text(early) == "No snapshot was recorded on or before 2026-07-01.\n"


def test_quarantined_exports_after_the_snapshot_are_named(data: Path) -> None:
    (data / "quarantine").mkdir()
    (data / "quarantine" / "2026-11-02.json").write_text("{}", encoding="utf-8")
    assert as_of(data, "2026-11-01", lei=CASP_ONE).quarantined == []
    answer = as_of(data, "2026-11-05", lei=CASP_ONE)
    assert answer.quarantined == ["2026-11-02"]
    assert "Exports set aside after a sharp drop in rows and not recorded: 2026-11-02." in (
        render_text(answer)
    )


def test_render_text_lists_rows_services_and_changes(data: Path) -> None:
    text = render_text(as_of(data, "2026-10-26", lei=CASP_ONE))
    assert text.startswith(f"LEI {CASP_ONE}, as of 2026-10-26: the snapshot of 2026-10-26")
    assert "Authorised crypto-asset service providers (CASPs): 2 rows" in text
    assert "authorised 2026-01-15; services a, c; service countries BE, DE, FR, IT" in text
    assert "a = providing custody and administration of crypto-assets on behalf of clients" in text
    assert "Not listed in: other-wp, emt-wp, art-wp, ncasp." in text
    assert "2026-10-26  casps     changed   CASP One SAS" in text


def run_cli(data: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "observatory", "--data-dir", str(data), "asof", *args],
        capture_output=True,
        text=True,
    )


def test_the_cli_prints_text_or_json(data: Path) -> None:
    result = run_cli(data, "--lei", CUSTODY, "--date", "2026-10-26", "--json")
    assert result.returncode == 0, result.stderr
    answer = json.loads(result.stdout)
    assert answer["snapshot_date"] == "2026-10-26"
    assert answer["query"] == {"lei": CUSTODY, "name": "", "register": ""}
    assert [record["change"] for record in answer["history"]] == ["missing"]

    text = run_cli(data, "--name", "casp one", "--date", "2026-10-19")
    assert text.returncode == 0 and "CASP One SAS (LEI 529900CASPONE0000001)" in text.stdout
    assert run_cli(data, "--lei", CUSTODY, "--date", "2026-01-01").returncode == 1
    assert run_cli(data, "--lei", CUSTODY, "--date", "19/10/2026").returncode == 2
