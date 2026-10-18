"""`report build` picks the snapshot an edition records, so a rebuild cannot move
its published numbers; only an edition without one is filled from latest.json."""

import json
from pathlib import Path

import pytest

from observatory.coverage import classify_format
from observatory.models import RegisterEntry, RegisterSnapshot, Snapshot
from report.__main__ import main
from report.analyze import analyze
from report.render import (
    DATA_END,
    DATA_START,
    recorded_snapshot_date,
    render_data_section,
)

RECORDED = "2026-07-07"
LATEST = "2026-07-14"
# Synthetic white-paper links, one for each format class the report counts.
_LINKS = (
    "https://issuer{n}.example/whitepaper.xhtml",
    "https://issuer{n}.example/whitepaper.pdf",
    "https://issuer{n}.example/mica",
    "",
)


def _snapshot(snapshot_date: str, papers: int) -> dict:
    """A snapshot of `papers` Title II white papers from synthetic issuers."""
    entries = []
    for n in range(papers):
        url = _LINKS[n % len(_LINKS)].format(n=n)
        name, lei = f"Issuer {n} GmbH", f"LEI{n:017d}"
        entries.append(
            RegisterEntry(
                entry_id=RegisterEntry.make_entry_id("other-wp", lei, name, url),
                register_slug="other-wp",
                authority="NCA",
                member_state=("DE", "IE", "MT")[n % 3],
                entity_name=name,
                lei=lei,
                wp_url=url,
                last_update="01/01/2026",
                format_class=classify_format(url),
                row_hash=f"h{n}",
            )
        )
    register = RegisterSnapshot(
        slug="other-wp",
        title="White papers, synthetic",
        kind="whitepaper",
        source_url="https://esma.example/OTHER.csv",
        fetched=True,
        entries=entries,
    )
    return Snapshot(snapshot_date=snapshot_date, registers=[register]).model_dump(mode="json")


RECORDED_SNAPSHOT = _snapshot(RECORDED, 40)
# Stands in for data/latest.json: a later snapshot with different numbers.
LATEST_SNAPSHOT = _snapshot(LATEST, 30)


def _edition(data_section: str | None) -> str:
    block = f"\n{data_section}\n" if data_section is not None else "\n"
    return f"# Test edition\n\nNarrative.\n\n{DATA_START}{block}{DATA_END}\n\nMore narrative.\n"


def _setup(tmp_path: Path, data_section: str | None) -> Path:
    snapshots = tmp_path / "data" / "snapshots"
    snapshots.mkdir(parents=True)
    (snapshots / f"{RECORDED}.json").write_text(json.dumps(RECORDED_SNAPSHOT), encoding="utf-8")
    (tmp_path / "data" / "latest.json").write_text(json.dumps(LATEST_SNAPSHOT), encoding="utf-8")
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
    edition = _setup(tmp_path, render_data_section(analyze(RECORDED_SNAPSHOT)))
    before = edition.read_text(encoding="utf-8")

    assert _build(tmp_path) == 0

    assert edition.read_text(encoding="utf-8") == before
    assert f"Snapshot: {RECORDED}." in _html(tmp_path)


def test_an_edition_without_a_recorded_snapshot_is_filled_from_latest(tmp_path: Path) -> None:
    edition = _setup(tmp_path, None)

    assert _build(tmp_path) == 0

    text = edition.read_text(encoding="utf-8")
    assert recorded_snapshot_date(text) == LATEST
    assert render_data_section(analyze(LATEST_SNAPSHOT)) in text
    assert f"Snapshot: {LATEST}." in _html(tmp_path)


def test_use_latest_overrides_the_recorded_snapshot(tmp_path: Path) -> None:
    edition = _setup(tmp_path, render_data_section(analyze(RECORDED_SNAPSHOT)))

    assert _build(tmp_path, "--use-latest") == 0

    assert recorded_snapshot_date(edition.read_text(encoding="utf-8")) == LATEST


def test_fixture_overrides_the_recorded_snapshot(tmp_path: Path) -> None:
    edition = _setup(tmp_path, render_data_section(analyze(RECORDED_SNAPSHOT)))

    assert _build(tmp_path, "--fixture", str(tmp_path / "data" / "latest.json")) == 0

    assert recorded_snapshot_date(edition.read_text(encoding="utf-8")) == LATEST


def test_a_missing_recorded_snapshot_fails_without_writing(tmp_path: Path) -> None:
    edition = _setup(tmp_path, render_data_section(analyze(RECORDED_SNAPSHOT)))
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
    assert (
        recorded_snapshot_date(_edition(render_data_section(analyze(RECORDED_SNAPSHOT))))
        == RECORDED
    )
    assert recorded_snapshot_date(_edition(None)) is None
    assert recorded_snapshot_date("# An edition without data markers\n") is None
