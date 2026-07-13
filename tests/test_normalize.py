from pathlib import Path

from observatory.config import SOURCES
from observatory.normalize import normalize_csv

FIXTURES = Path(__file__).parent / "fixtures"


def source(slug: str):
    return next(s for s in SOURCES if s.slug == slug)


def test_normalize_other_wp_handles_bom_and_fields():
    entries = normalize_csv(source("other-wp"), (FIXTURES / "other-wp.csv").read_bytes())
    assert len(entries) == 2
    first = entries[0]
    assert first.authority.startswith("Austrian")
    assert first.member_state == "AT"
    assert first.entity_name == "SKYGATE Network GmbH"
    assert first.lei == "984500BBFE52FE449926"
    assert first.format_class == "unspecified"
    assert first.content_verification_status == "not_checked"
    assert first.content_sha256 is None
    assert entries[1].format_class == "xhtml/html"


def test_entry_id_is_stable_across_runs():
    raw = (FIXTURES / "other-wp.csv").read_bytes()
    first = normalize_csv(source("other-wp"), raw)
    second = normalize_csv(source("other-wp"), raw)
    assert [e.entry_id for e in first] == [e.entry_id for e in second]


def test_empty_register_yields_no_entries():
    entries = normalize_csv(source("art-wp"), (FIXTURES / "art-wp.csv").read_bytes())
    assert entries == []


def test_entity_register_has_na_format():
    entries = normalize_csv(source("casps"), (FIXTURES / "casps.csv").read_bytes())
    assert len(entries) == 1
    assert entries[0].format_class == "n/a"
