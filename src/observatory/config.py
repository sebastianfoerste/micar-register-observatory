"""Register sources for the ESMA interim MiCAR register.

ESMA publishes the interim register as CSV files at stable URLs and updates
them in place (Art. 109 MiCAR). The `2024-12` path segment is part of the
stable URL, not a data date — check the HTTP Last-Modified header for freshness.
"""

from __future__ import annotations

from pydantic import BaseModel

BASE_URL = "https://www.esma.europa.eu/sites/default/files/2024-12"

USER_AGENT = (
    "micar-register-observatory/0.1 "
    "(+https://github.com/sebastianfoerste/micar-register-observatory)"
)


class RegisterSource(BaseModel):
    slug: str
    filename: str
    title: str
    kind: str  # "whitepaper" | "entity"
    # Sanity floor for a live fetch: a register that shrinks below this is treated
    # as a bad download, not as data. art-wp is legitimately empty (floor 0).
    min_rows: int = 0

    @property
    def url(self) -> str:
        return f"{BASE_URL}/{self.filename}"


SOURCES: list[RegisterSource] = [
    RegisterSource(
        slug="other-wp",
        min_rows=500,
        filename="OTHER.csv",
        title="White papers — other crypto-assets (Title II)",
        kind="whitepaper",
    ),
    RegisterSource(
        slug="emt-wp",
        min_rows=20,
        filename="EMTWP.csv",
        title="White papers — e-money tokens (Title IV)",
        kind="whitepaper",
    ),
    RegisterSource(
        slug="art-wp",
        filename="ARTZZ.csv",
        title="White papers — asset-referenced tokens (Title III)",
        kind="whitepaper",
    ),
    RegisterSource(
        slug="casps",
        min_rows=150,
        filename="CASPS.csv",
        title="Authorised crypto-asset service providers (CASPs)",
        kind="entity",
    ),
    RegisterSource(
        slug="ncasp",
        min_rows=80,
        filename="NCASP.csv",
        title="Non-compliant entities flagged by NCAs",
        kind="entity",
    ),
]

# Columns every register export must carry for normalize_csv to be meaningful.
REQUIRED_COLUMNS = ("ae_competentAuthority", "ae_homeMemberState", "ae_lei_name", "ae_lei")
WHITEPAPER_COLUMNS = ("wp_url", "wp_lastupdate")
