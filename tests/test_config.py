"""The register titles follow ESMA's MiCA page and Art. 109(1) MiCAR.

Written from the snapshot of ESMA's MiCA page of 14 November 2026 and the OJ
text of MiCAR in sources/, before the titles in config.py were changed.
"""

import csv
import html
import io
import json
import re
from pathlib import Path

from observatory.config import SOURCES
from report.analyze import analyze
from report.render import register_label, render_data_section

ROOT = Path(__file__).resolve().parents[1]
MICA_PAGE = ROOT / "sources" / "esma" / "2026-11-14" / "markets-crypto-assets-regulation-mica.html"

# Art. 109(1)(b) and (c) MiCAR make these two partitions registers of issuers,
# and ESMA's MiCA page lists the files under these names.
ISSUER_REGISTERS = {
    "art-wp": "Issuers of asset-referenced tokens (Title III)",
    "emt-wp": "Issuers of e-money tokens (Title IV)",
}


def _page_text() -> str:
    raw = MICA_PAGE.read_text(encoding="utf-8")
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", raw)))


def test_issuer_register_titles_follow_esma():
    page = _page_text()
    titles = {source.slug: source.title for source in SOURCES}
    for slug, title in ISSUER_REGISTERS.items():
        assert title in page
        assert titles[slug] == title


def test_micar_names_both_issuer_registers():
    micar = (ROOT / "sources" / "eu" / "32023R1114.xhtml").read_text(encoding="utf-8")
    text = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", micar)))
    assert "(b) issuers of asset-referenced tokens; (c) issuers of e-money tokens;" in text


def test_a_new_snapshot_is_labelled_with_the_issuer_titles():
    metrics = {"register_titles": {slug: title for slug, title in ISSUER_REGISTERS.items()}}
    for slug, title in ISSUER_REGISTERS.items():
        assert register_label(slug, metrics) == title
    # Without recorded titles the configured ones apply.
    assert register_label("emt-wp", {}) == ISSUER_REGISTERS["emt-wp"]
    assert register_label("casps", {}) == "Authorised CASPs"


SOURCES_README = ROOT / "sources" / "README.md"
FIELD_DESCRIPTION = MICA_PAGE.parent / "Description_of_the_fields_in_the_interim_MiCA_register.csv"


def _observed_headers() -> dict[str, tuple[str, ...]]:
    """The header rows recorded in sources/README.md, nameless columns left out."""
    headers: dict[str, tuple[str, ...]] = {}
    for line in SOURCES_README.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^\| `(\w+\.csv)` \|.*\| `([^`]*)` \|$", line)
        if match:
            headers[match[1]] = tuple(name for name in match[2].split(",") if name)
    return headers


def _described_fields() -> dict[str, list[str]]:
    fields: dict[str, list[str]] = {}
    text = FIELD_DESCRIPTION.read_bytes().decode("utf-8-sig")
    for row in list(csv.reader(io.StringIO(text)))[1:]:
        if len(row) > 1 and row[0]:
            fields.setdefault(row[0], []).append(row[1])
    return fields


def test_expected_columns_are_the_headers_esma_served():
    observed = _observed_headers()
    assert set(observed) == {source.filename for source in SOURCES}
    for source in SOURCES:
        assert source.columns == observed[source.filename], source.slug


def test_expected_columns_differ_from_the_field_description_only_as_recorded():
    described = _described_fields()
    for source in SOURCES:
        template = source.filename.removesuffix(".csv")
        expected = list(described[template])
        if template == "ARTZZ":  # the served file lacks the two DTI columns
            expected = [name for name in expected if name not in {"ae_DTI_FFG", "ae_DTI"}]
        assert list(source.columns) == expected, source.slug


def test_an_edition_keeps_the_titles_its_snapshot_recorded():
    snapshot = json.loads((ROOT / "data" / "snapshots" / "2026-09-21.json").read_text("utf-8"))
    section = render_data_section(analyze(snapshot))
    assert "| White papers — e-money tokens (Title IV) | 49 |" in section
    assert "| White papers — asset-referenced tokens (Title III) | 0 |" in section
    assert "| Authorised CASPs | 352 |" in section
    assert "Issuers of" not in section
