"""ESMA's reuse wording, quoted once and reused wherever register data is published.

ESMA's legal notice authorises reproduction "provided the source is
acknowledged" and, where the material is transformed and republished, requires
a disclaimer in prescribed words. The two sentences below are copied from the
snapshot in sources/esma/2026-11-14/legal-notice-and-data-protection.html
(retrieved 14 November 2026; same text as the copy of 14 October 2026);
tests/test_notice.py checks them against both. Do not reword.
"""

from __future__ import annotations

from observatory.config import MICA_PAGE_URL, REPO_URL

ESMA_LEGAL_NOTICE_URL = "https://www.esma.europa.eu/legal-notice"

ESMA_SOURCE_SENTENCE = (
    "This document has been drafted using material downloaded from ESMA’s website"
)

ESMA_ENDORSEMENT_SENTENCE = (
    "ESMA does not endorse this publication and in no way is liable for copyright "
    "or other intellectual property rights infringements nor for any damages "
    "caused to third parties through this publication"
)

DATA_NOTICE_URL = f"{REPO_URL}/blob/main/DATA_NOTICE.md"

ESMA_PUBLISHER = "European Securities and Markets Authority (ESMA)"

ESMA_DISCLAIMER = f"{ESMA_SOURCE_SENTENCE}. {ESMA_ENDORSEMENT_SENTENCE}."

# What each licence covers (owner answer O6 of 10 November 2026): MIT for the
# code, CC BY 4.0 for the observatory's own prose, nothing for ESMA's data.
LICENCE_SUMMARY = (
    "No licence is granted for the register data; ESMA's terms apply. Code: MIT. "
    f"The observatory's own prose in editions and docs: CC BY 4.0. See {DATA_NOTICE_URL}"
)


def feed_notice() -> dict[str, object]:
    """Source, disclaimer and licence fields for docs/feed.json."""
    return {
        "source": {
            "publisher": ESMA_PUBLISHER,
            "dataset": "Interim MiCA register",
            "url": MICA_PAGE_URL,
        },
        "notice": ESMA_DISCLAIMER,
        "data_licence": LICENCE_SUMMARY,
    }
