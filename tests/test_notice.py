"""The data notice quotes ESMA's legal notice word for word.

Written from the snapshots of ESMA's legal notice in sources/esma/, retrieved on
14 October and 14 November 2026, before the notice text was added here.
"""

import html
import json
import re
from pathlib import Path

import pytest

from observatory.models import RegisterSnapshot, Snapshot
from observatory.notice import (
    DATA_NOTICE_URL,
    ESMA_ENDORSEMENT_SENTENCE,
    ESMA_LEGAL_NOTICE_URL,
    ESMA_SOURCE_SENTENCE,
    feed_notice,
)
from observatory.render import write_feed

ROOT = Path(__file__).resolve().parents[1]
LEGAL_NOTICES = sorted((ROOT / "sources" / "esma").glob("*/legal-notice-and-data-protection.html"))
CC_BY = "https://creativecommons.org/licenses/by/4.0/"


def _text(path: Path) -> str:
    raw = path.read_text(encoding="utf-8")
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", raw)))


def test_both_snapshots_of_the_legal_notice_are_there():
    assert [path.parent.name for path in LEGAL_NOTICES] == ["2026-10-14", "2026-11-14"]


@pytest.mark.parametrize("snapshot", LEGAL_NOTICES, ids=lambda path: path.parent.name)
def test_prescribed_sentences_are_esmas_exact_wording(snapshot: Path):
    text = _text(snapshot)
    assert f"‘{ESMA_SOURCE_SENTENCE}’" in text
    assert f"{ESMA_ENDORSEMENT_SENTENCE}’" in text


def test_data_notice_quotes_esma_with_url_and_retrieval_date():
    notice = (ROOT / "DATA_NOTICE.md").read_text(encoding="utf-8")
    assert ESMA_SOURCE_SENTENCE in notice
    assert ESMA_ENDORSEMENT_SENTENCE in notice
    assert ESMA_LEGAL_NOTICE_URL in notice
    assert "retrieved on 14 November 2026 at 13:22 UTC" in notice
    assert "sources/esma/2026-11-14/legal-notice-and-data-protection.html" in notice
    assert "European Securities and Markets Authority (ESMA)" in notice
    assert "covers the code in this repository and reaches its documentation files" in notice
    assert "only" not in notice.split("**Code.**", 1)[1].split("\n", 1)[0]
    assert "Neither licence extends to the register data" in notice
    assert CC_BY in notice
    assert "No licence is granted for the register data." in notice


def test_readme_carries_the_short_notice_and_the_licence_scope():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "## Data notice" in readme
    assert ESMA_SOURCE_SENTENCE in readme
    assert ESMA_ENDORSEMENT_SENTENCE in readme
    assert "(DATA_NOTICE.md)" in readme
    assert "The MIT licence covers the code and its documentation files." in readme
    assert "The MIT licence covers the code only." not in readme
    assert CC_BY in readme
    assert "No licence is granted for the register data." in readme


def test_feed_names_esma_and_carries_the_notice(tmp_path):
    snapshot = Snapshot(
        snapshot_date="2026-10-12",
        registers=[
            RegisterSnapshot(
                slug="other-wp",
                title="t",
                kind="whitepaper",
                source_url="https://esma.example/OTHER.csv",
                fetched=True,
            )
        ],
    )
    feed = tmp_path / "feed.json"
    write_feed(feed, snapshot, [])
    payload = json.loads(feed.read_text(encoding="utf-8"))
    assert payload["source"] == feed_notice()["source"]
    assert payload["source"]["publisher"] == "European Securities and Markets Authority (ESMA)"
    assert ESMA_SOURCE_SENTENCE in payload["notice"]
    assert ESMA_ENDORSEMENT_SENTENCE in payload["notice"]
    assert payload["data_licence"].startswith("No licence is granted for the register data")
    assert "CC BY 4.0" in payload["data_licence"]


# The quarterly edition and its shareable HTML page republish the same data, so
# they carry the same acknowledgement and disclaimer as the README and the feed.

_EDITION_FIXTURE = json.loads(
    (ROOT / "tests" / "fixtures" / "snapshot.json").read_text(encoding="utf-8")
)


def test_edition_data_section_names_esma_and_carries_the_notice():
    from report.analyze import analyze
    from report.render import render_data_section

    section = render_data_section(analyze(_EDITION_FIXTURE))
    assert "European Securities and Markets Authority (ESMA)" in section
    assert ESMA_SOURCE_SENTENCE in section
    assert ESMA_ENDORSEMENT_SENTENCE in section
    assert DATA_NOTICE_URL in section


def test_edition_page_names_esma_and_carries_the_notice():
    from report.analyze import analyze
    from report.render import render_html

    page = render_html(analyze(_EDITION_FIXTURE), "Edition")
    footer = page[page.index("<footer>") :]
    assert "European Securities and Markets Authority (ESMA)" in footer
    assert html.escape(ESMA_SOURCE_SENTENCE) in footer
    assert html.escape(ESMA_ENDORSEMENT_SENTENCE) in footer
    assert DATA_NOTICE_URL in footer


def test_committed_editions_and_page_carry_the_notice():
    published = sorted((ROOT / "editions").glob("*.md")) + [ROOT / "docs" / "index.html"]
    for path in published:
        text = html.unescape(path.read_text(encoding="utf-8"))
        assert ESMA_SOURCE_SENTENCE in text, path.name
        assert ESMA_ENDORSEMENT_SENTENCE in text, path.name
