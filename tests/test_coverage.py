import csv
import io
import re
from pathlib import Path

from observatory.coverage import classify_format


def test_classify_xhtml_and_html():
    assert classify_format("https://a.example/wp.xhtml") == "xhtml/html"
    assert classify_format("https://a.example/wp.HTML") == "xhtml/html"


def test_classify_pdf():
    assert classify_format("https://a.example/whitepaper.pdf") == "pdf"


def test_bare_domain_is_unspecified():
    assert classify_format("WWW.SKYGATETOKEN.AT") == "unspecified"


def test_query_string_does_not_confuse_extension():
    assert classify_format("https://a.example/wp.pdf?v=2") == "pdf"


def test_empty_is_none():
    assert classify_format("") == "none"


# Written from ESMA's field description file (sources/esma/2026-11-14/, retrieved
# 14 November 2026): the EMTWP wp_url field takes either an address or one of the
# placeholder values listed under "Applies to".
FIELD_DESCRIPTION = (
    Path(__file__).resolve().parents[1]
    / "sources"
    / "esma"
    / "2026-11-14"
    / "Description_of_the_fields_in_the_interim_MiCA_register.csv"
)


def _emt_wp_url_placeholders() -> set[str]:
    rows = csv.reader(io.StringIO(FIELD_DESCRIPTION.read_bytes().decode("utf-8-sig")))
    for row in rows:
        if row[:2] == ["EMTWP", "wp_url"]:
            return set(re.findall(r"\bEMT_[A-Z_]+\b", row[5]))
    raise AssertionError("EMTWP wp_url row missing from the field description")


def test_field_description_lists_two_placeholders():
    assert _emt_wp_url_placeholders() == {"EMT_NO_WP", "EMT_CRIN"}


def test_esma_placeholder_values_are_not_links():
    for value in _emt_wp_url_placeholders():
        assert classify_format(value) == "none"
        assert classify_format(f" {value.lower()} ") == "none"


def test_a_value_that_only_contains_a_placeholder_is_still_a_link():
    assert classify_format("https://a.example/EMT_NO_WP.pdf") == "pdf"
    assert classify_format("EMT_NO_WP_2") == "unspecified"
