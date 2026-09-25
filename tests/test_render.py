import json
from pathlib import Path

from report.analyze import analyze
from report.render import (
    DATA_END,
    DATA_START,
    render_data_section,
    render_html,
    update_edition,
)

FIXTURE = json.loads(
    (Path(__file__).parent / "fixtures" / "snapshot.json").read_text(encoding="utf-8")
)


def test_data_section_contains_headline_numbers():
    section = render_data_section(analyze(FIXTURE))
    assert "953" in section
    assert "114" in section
    assert "machine-readable" in section
    assert "| Member State | White papers | Share |" in section


def test_update_edition_replaces_only_the_data_block(tmp_path):
    edition = tmp_path / "2026-Q3.md"
    edition.write_text(
        f"# Title\n\nAuthored intro.\n\n{DATA_START}\nOLD\n{DATA_END}\n\nAuthored outro.\n",
        encoding="utf-8",
    )
    update_edition(edition, render_data_section(analyze(FIXTURE)))
    out = edition.read_text(encoding="utf-8")
    assert "Authored intro." in out
    assert "Authored outro." in out
    assert "OLD" not in out
    assert "953" in out
    assert out.count(DATA_START) == 1 and out.count(DATA_END) == 1


def test_html_is_self_contained_and_has_stat():
    page = render_html(analyze(FIXTURE), "The State of the MiCAR Register — 2026 Q3")
    assert page.startswith("<!doctype html>")
    assert "<svg" in page
    assert "http-equiv" not in page  # no external redirects
    assert "src=" not in page  # no external assets
    assert "%" in page
