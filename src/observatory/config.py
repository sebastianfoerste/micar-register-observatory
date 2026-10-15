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
    # The register's own "last update of the record" column.
    last_update_column: str = "wp_lastupdate"
    # The header ESMA published when this source was last reviewed; a different
    # header is reported as a source change but does not stop the refresh.
    columns: tuple[str, ...] = ()

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
        columns=(
            "ae_competentAuthority", "ae_homeMemberState", "ae_lei_name", "ae_lei",
            "ae_lei_cou_code", "ae_lei_name_casp", "ae_lei_casp", "ae_offerCode_cou",
            "ae_DTI_FFG", "ae_DTI", "wp_url", "wp_comments", "wp_lastupdate",
        ),
    ),
    RegisterSource(
        slug="emt-wp",
        min_rows=20,
        filename="EMTWP.csv",
        title="White papers — e-money tokens (Title IV)",
        kind="whitepaper",
        columns=(
            "ae_competentAuthority", "ae_homeMemberState", "ae_lei_name", "ae_lei",
            "ae_lei_cou_code", "ae_commercial_name", "ae_address", "ae_website",
            "ac_authorisationNotificationDate", "ac_authorisationEndDate",
            "ae_exemption48_4", "ae_exemption48_5", "ae_authorisation_other_emt",
            "ae_DTI_FFG", "ae_DTI", "wp_url", "wp_authorisationNotificationDate",
            "wp_comments", "wp_lastupdate",
        ),
    ),
    RegisterSource(
        slug="art-wp",
        filename="ARTZZ.csv",
        title="White papers — asset-referenced tokens (Title III)",
        kind="whitepaper",
        columns=(
            "ae_competentAuthority", "ae_homeMemberState", "ae_lei_name", "ae_lei",
            "ae_lei_cou_code", "ae_commercial_name", "ae_address", "ae_website",
            "ac_authorisationNotificationDate", "ac_authorisationEndDate",
            "ae_credit_institution", "wp_url", "wp_authorisationNotificationDate",
            "wp_url_cou", "wp_comments", "wp_lastupdate",
        ),
    ),
    RegisterSource(
        slug="casps",
        min_rows=150,
        filename="CASPS.csv",
        title="Authorised crypto-asset service providers (CASPs)",
        kind="entity",
        last_update_column="ac_lastupdate",
        columns=(
            "ae_competentAuthority", "ae_homeMemberState", "ae_lei_name", "ae_lei",
            "ae_lei_cou_code", "ae_commercial_name", "ae_address", "ae_website",
            "ae_website_platform", "ac_authorisationNotificationDate",
            "ac_authorisationEndDate", "ac_serviceCode", "ac_serviceCode_cou",
            "ac_comments", "ac_lastupdate",
        ),
    ),
    RegisterSource(
        slug="ncasp",
        min_rows=80,
        filename="NCASP.csv",
        title="Non-compliant entities flagged by NCAs",
        kind="entity",
        last_update_column="ae_lastupdate",
        columns=(
            "ae_competentAuthority", "ae_homeMemberState", "ae_lei_name", "ae_lei",
            "ae_lei_cou_code", "ae_commercial_name", "ae_website", "ae_infrigment",
            "ae_reason", "ae_decision_date", "ae_comments", "ae_lastupdate",
        ),
    ),
]

# Columns every register export must carry for normalize_csv to be meaningful.
REQUIRED_COLUMNS = ("ae_competentAuthority", "ae_homeMemberState", "ae_lei_name", "ae_lei")
WHITEPAPER_COLUMNS = ("wp_url", "wp_lastupdate")

# The crypto-asset services of Art. 3(1)(16) MiCAR, by the letter ESMA's CASP
# export uses. The export gives free text, sometimes with a wrong letter, so
# normalize.parse_services maps the text, not the letter.
SERVICE_NAMES: dict[str, str] = {
    "a": "providing custody and administration of crypto-assets on behalf of clients",
    "b": "operation of a trading platform for crypto-assets",
    "c": "exchange of crypto-assets for funds",
    "d": "exchange of crypto-assets for other crypto-assets",
    "e": "execution of orders for crypto-assets on behalf of clients",
    "f": "placing of crypto-assets",
    "g": "reception and transmission of orders for crypto-assets on behalf of clients",
    "h": "providing advice on crypto-assets",
    "i": "providing portfolio management on crypto-assets",
    "j": "providing transfer services for crypto-assets on behalf of clients",
}
