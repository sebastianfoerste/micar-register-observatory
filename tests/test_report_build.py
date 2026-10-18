"""`report build` picks the snapshot an edition records, so a rebuild cannot move
its published numbers; only an edition without one is filled from latest.json."""

import copy
import json
from pathlib import Path

import pytest

from report.__main__ import main
from report.analyze import analyze
from report.render import (
    DATA_END,
    DATA_START,
    recorded_snapshot_date,
    render_data_section,
)

FIXTURE = json.loads(
    (Path(__file__).parent / "fixtures" / "snapshot.json").read_text(encoding="utf-8")
)
RECORDED = "2026-07-07"  # the fixture's snapshot date
LATEST = "2026-07-14"


def _latest_snapshot() -> dict:
    """A later snapshot with different numbers, standing in for data/latest.json."""
    later = copy.deepcopy(FIXTURE)
    later["snapshot_date"] = LATEST
    for register in later["registers"]:
        if register["slug"] == "other-wp":
            register["entries"] = register["entries"][:-100]
    return later


def _edition(data_section: str | None) -> str:
    block = f"\n{data_section}\n" if data_section is not None else "\n"
    return f"# Test edition\n\nNarrative.\n\n{DATA_START}{block}{DATA_END}\n\nMore narrative.\n"


def _setup(tmp_path: Path, data_section: str | None) -> Path:
    snapshots = tmp_path / "data" / "snapshots"
    snapshots.mkdir(parents=True)
    (snapshots / f"{RECORDED}.json").write_text(json.dumps(FIXTURE), encoding="utf-8")
    (tmp_path / "data" / "latest.json").write_text(json.dumps(_latest_snapshot()), encoding="utf-8")
    (tmp_path / "editions").mkdir()
    edition = tmp_path / "editions" / "2026-Q3.md"
    edition.write_text(_edition(data_section), encoding="utf-8")
    return edition


def _build(tmp_path: Path, *build_args: str) -> int:
    return main(
        [
            "--editions-dir",
            str(tmp_path / "editions"),
            "--html",
            str(tmp_path / "docs" / "index.html"),
            "--data-dir",
            str(tmp_path / "data"),
            "build",
            *build_args,
        ]
    )


def _html(tmp_path: Path) -> str:
    return (tmp_path / "docs" / "index.html").read_text(encoding="utf-8")


def test_an_edition_with_a_recorded_snapshot_is_rebuilt_from_it(tmp_path: Path) -> None:
    edition = _setup(tmp_path, render_data_section(analyze(FIXTURE)))
    before = edition.read_text(encoding="utf-8")

    assert _build(tmp_path) == 0

    assert edition.read_text(encoding="utf-8") == before
    assert f"Snapshot: {RECORDED}." in _html(tmp_path)


def test_an_edition_without_a_recorded_snapshot_is_filled_from_latest(tmp_path: Path) -> None:
    edition = _setup(tmp_path, None)

    assert _build(tmp_path) == 0

    text = edition.read_text(encoding="utf-8")
    assert recorded_snapshot_date(text) == LATEST
    assert render_data_section(analyze(_latest_snapshot())) in text
    assert f"Snapshot: {LATEST}." in _html(tmp_path)


def test_use_latest_overrides_the_recorded_snapshot(tmp_path: Path) -> None:
    edition = _setup(tmp_path, render_data_section(analyze(FIXTURE)))

    assert _build(tmp_path, "--use-latest") == 0

    assert recorded_snapshot_date(edition.read_text(encoding="utf-8")) == LATEST


def test_fixture_overrides_the_recorded_snapshot(tmp_path: Path) -> None:
    edition = _setup(tmp_path, render_data_section(analyze(FIXTURE)))

    assert _build(tmp_path, "--fixture", str(tmp_path / "data" / "latest.json")) == 0

    assert recorded_snapshot_date(edition.read_text(encoding="utf-8")) == LATEST


def test_a_missing_recorded_snapshot_fails_without_writing(tmp_path: Path) -> None:
    edition = _setup(tmp_path, render_data_section(analyze(FIXTURE)))
    before = edition.read_text(encoding="utf-8")
    (tmp_path / "data" / "snapshots" / f"{RECORDED}.json").unlink()

    assert _build(tmp_path) == 1

    assert edition.read_text(encoding="utf-8") == before
    assert not (tmp_path / "docs" / "index.html").exists()


def test_fixture_and_use_latest_cannot_be_combined(tmp_path: Path) -> None:
    _setup(tmp_path, None)
    with pytest.raises(SystemExit):
        _build(tmp_path, "--use-latest", "--fixture", str(tmp_path / "data" / "latest.json"))


def test_the_recorded_date_is_read_back_from_the_generated_section() -> None:
    assert recorded_snapshot_date(_edition(render_data_section(analyze(FIXTURE)))) == RECORDED
    assert recorded_snapshot_date(_edition(None)) is None
    assert recorded_snapshot_date("# An edition without data markers\n") is None
