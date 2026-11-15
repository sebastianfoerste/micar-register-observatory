"""Source snapshots stay byte-exact, and the texts that cite them say what they say."""

import csv
import hashlib
import html
import io
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "sources"

# A register row links the file and gives its SHA-256 in backticks.
_ROW = re.compile(r"^\| \[`(?P<path>[^`]+)`\]\([^)]+\) \|.*?\| `(?P<sha>[0-9a-f]{64})` \|")
LATEST_ESMA = "esma/2026-11-14"


def _registered() -> dict[str, str]:
    rows: dict[str, str] = {}
    for line in (SOURCES / "README.md").read_text(encoding="utf-8").splitlines():
        match = _ROW.match(line)
        if match:
            rows[match["path"]] = match["sha"]
    return rows


def _text(relative: str) -> str:
    raw = (SOURCES / relative).read_text(encoding="utf-8")
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", raw)))


def test_every_snapshot_is_registered_with_its_hash():
    registered = _registered()
    on_disk = {
        path.relative_to(SOURCES).as_posix()
        for path in SOURCES.rglob("*")
        if path.is_file() and path.name != "README.md"
    }
    assert on_disk == set(registered)
    for relative, sha in registered.items():
        digest = hashlib.sha256((SOURCES / relative).read_bytes()).hexdigest()
        assert digest == sha, f"{relative} differs from its registered SHA-256"


def test_snapshots_contain_the_cited_wording():
    micar = _text("eu/32023R1114.xhtml")
    assert "ESMA’s register shall be publicly available on its website" in micar
    assert "practical arrangements to ensure that such data is machine-readable" in micar
    assert micar.count("(c) the crypto-asset white papers and any modified crypto-asset") == 2
    assert (
        "The register shall be publicly available on ESMA’s website in a machine-readable" in micar
    )
    rts = _text("eu/32025R0421.xhtml")
    assert "and in particular Article 109(8), third subparagraph, thereof" in rts
    assert "This Regulation shall apply from 23 December 2025." in rts
    inserting = _text("eu/32023R2869.xhtml")
    assert "From 10 January 2030, the information referred to in Articles 109 and 110" in inserting
    # The cross-reference the claim ledger records: point (3) defines another term.
    assert "(a) be submitted in a machine-readable format as defined in Article 2, point (3)" in (
        inserting
    )
    esap = _text("eu/32023R2859.xhtml")
    assert "(3) ‘data extractable format’ means" in esap
    assert "(4) ‘machine-readable format’ means" in esap
    consolidated = _text("eu/02023R1114-20240109.xhtml")
    assert "Article 110a Accessibility of information on the European single access point" in (
        consolidated
    )


def test_readme_states_article_109_as_the_snapshots_do():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "machine-readable register" not in readme
    for pinpoint in (
        "Art. 109(1)",
        "Art. 109(8)",
        "Delegated Regulation (EU) 2025/421",
        "Art. 110a(4)",
        "Regulation (EU) 2023/2869",
        "10 January 2030",
        "Art. 6(10), 19(9) and 51(9)",
        "Implementing Regulation (EU) 2024/2984",
    ):
        assert pinpoint in readme
    # The Art. 110a(4)(a) cross-reference defect is recorded in the ledger only.
    assert "point (3)" not in readme
    ledger = (ROOT / "docs" / "regulatory-claim-ledger.md").read_text(encoding="utf-8")
    assert "Article 2, point (3)" in ledger


def test_the_ledger_keeps_both_kinds_of_evidence():
    ledger = (ROOT / "docs" / "regulatory-claim-ledger.md").read_text(encoding="utf-8")
    assert "EUR-Lex 10 November 2026" in ledger
    assert "OJ snapshot 14 October 2026" in ledger
    for answer in ("(O1)", "(O2)", "(O3)", "(O4)", "(O5)"):
        assert answer in ledger
    assert "pending the owner's review" not in ledger


def test_the_ledger_dates_snapshots_as_they_were_committed():
    # The snapshot row once called 2026-08-24 and 2026-08-31 "the committed
    # snapshots of that month"; August 2026 has five. Dates the row names must be
    # committed snapshots, and the two it puts around 26 August the nearest ones.
    ledger = (ROOT / "docs" / "regulatory-claim-ledger.md").read_text(encoding="utf-8")
    row = next(line for line in ledger.splitlines() if "never committed" in line)
    committed = sorted(path.stem for path in (ROOT / "data" / "snapshots").glob("*.json"))
    assert "2026-08-26" not in committed
    named = re.findall(r"\b20\d\d-\d\d-\d\d\b", row)
    assert named and set(named) <= set(committed)
    before = max(date for date in committed if date < "2026-08-26")
    after = min(date for date in committed if date > "2026-08-26")
    assert f"nearest committed snapshots are dated {before} and {after}" in row
    assert "snapshots of that month" not in row


def test_the_english_corrigendum_leaves_the_cited_articles_alone():
    corrigendum = _text("eu/32023R1114R03.xhtml")
    corrected = re.findall(r"On page \d+, (Article \d+\(\d+\))", corrigendum)
    assert corrected == ["Article 45(4)", "Article 81(15)", "Article 92(2)", "Article 111(1)"]


def test_edition_opening_cites_what_the_snapshots_say():
    edition = (ROOT / "editions" / "2026-Q3.md").read_text(encoding="utf-8")
    assert "machine-readable register" not in edition
    for pinpoint in (
        "Article 6(10)",
        "Article 19(9)",
        "Article 51(9)",
        "(EU) 2024/2984",
        "23 December 2025",
        "Recital 5",
        "Articles 109 and 110",
    ):
        assert pinpoint in edition
    micar = _text("eu/32023R1114.xhtml")
    duty = "The crypto-asset white paper shall be made available in a machine-readable format."
    assert micar.count(duty) == 3
    its = _text("eu/32024R2984.xhtml")
    assert "It shall apply from 23 December 2025." in its
    assert (
        "To further facilitate the analysis and comparability of the crypto-asset white papers"
        in its
    )


def _described_fields(relative: str) -> dict[str, list[str]]:
    text = (SOURCES / relative).read_bytes().decode("utf-8-sig")
    fields: dict[str, list[str]] = {}
    for row in list(csv.reader(io.StringIO(text)))[1:]:
        if len(row) > 1 and row[0]:
            fields.setdefault(row[0], []).append(row[1])
    return fields


def test_the_field_description_documents_the_placeholders_and_the_new_casp_field():
    raw = SOURCES / LATEST_ESMA / "Description_of_the_fields_in_the_interim_MiCA_register.csv"
    text = raw.read_bytes().decode("utf-8-sig")
    assert "EMT_NO_WP (Authorised EMT that has not issued any white paper)" in text
    assert "EMT_CRIN (for Credit institutions that do not need to report white papers)" in text
    latest = _described_fields(
        f"{LATEST_ESMA}/Description_of_the_fields_in_the_interim_MiCA_register.csv"
    )
    earlier = _described_fields(
        "esma/2026-10-14/Description_of_the_fields_in_the_interim_MiCA_register.csv"
    )
    assert latest["CASPS"][-1] == "ac_legal_basis"
    assert "ac_legal_basis" not in earlier["CASPS"]


def test_the_mica_page_links_every_configured_export():
    from observatory.config import SOURCES as CONFIGURED

    page = (SOURCES / LATEST_ESMA / "markets-crypto-assets-regulation-mica.html").read_text(
        encoding="utf-8"
    )
    links = set(re.findall(r'href="(/sites/default/files/[^"]+\.csv)"', page))
    for source in CONFIGURED:
        assert f"/sites/default/files/2024-12/{source.filename}" in links
    assert "Last update: 11 November 2026" in page
