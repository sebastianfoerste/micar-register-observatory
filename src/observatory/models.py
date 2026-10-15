"""Normalized register entries and snapshot containers.

Fields are only ever added, never renamed or removed: eu-reg-mcp and other
consumers read data/latest.json and data/changelog.jsonl from main. Fields added
after the v1 contract default to empty so that older snapshots and changelog
records still load.
"""

from __future__ import annotations

import hashlib

from pydantic import BaseModel

# The changelog record format written by this code; records without the field
# are version 1. Version 2 records mean `removed` = absent from two consecutive
# exports (version 1: absent from one) and add the `missing` and `restored` kinds.
CHANGE_RECORD_VERSION = 2


def _short_hash(key: str) -> str:
    return hashlib.sha256(key.lower().encode("utf-8")).hexdigest()[:16]


class RegisterEntry(BaseModel):
    # --- v1 contract -----------------------------------------------------------
    entry_id: str
    register_slug: str
    authority: str
    member_state: str
    entity_name: str
    lei: str
    wp_url: str
    last_update: str  # raw register value, DD/MM/YYYY where populated
    format_class: str  # see coverage.classify_format
    row_hash: str
    # --- v2 contract: empty in snapshots written before 2026-10 ------------------
    row_key: str = ""  # finer row identity, see make_row_key
    fields: dict[str, str] = {}  # every ESMA column of the row, verbatim
    commercial_name: str = ""
    website: str = ""
    authorisation_date: str = ""  # ISO dates from here on; "" when blank or unparseable
    withdrawal_date: str = ""
    offer_start_date: str = ""
    decision_date: str = ""
    services: list[str] = []  # letters a-j of Art. 3(1)(16) MiCAR
    service_countries: list[str] = []  # CASP: Member States where it intends to provide them
    offer_countries: list[str] = []  # white papers: Member States of the offer or admission
    dti_ffg: str = ""
    dti: list[str] = []
    casp_name: str = ""  # Title II: the CASP named on the white paper record
    casp_lei: str = ""
    reason: str = ""  # non-compliant entities: the NCA's stated reason
    comments: str = ""

    @staticmethod
    def make_entry_id(register: str, lei: str, entity_name: str, wp_url: str) -> str:
        # LEI is the stable identifier; name+URL is the fallback for rows without one.
        return _short_hash(f"{register}|{lei or entity_name}|{wp_url}")

    @staticmethod
    def make_row_key(register: str, lei: str, entity_name: str, *parts: str) -> str:
        """Row identity within an entry_id: entry_id alone is not unique.

        White papers add the DTI FFG, the DTIs and the CASP's LEI; CASP rows the
        authorisation date; non-compliant entities the decision date. Rows that
        still share a key are told apart by content (see diff.match_rows).
        """
        return _short_hash("|".join((register, lei or entity_name, *parts)))

    def entity_key(self) -> str:
        """The firm behind the row: its LEI, or its name when there is none."""
        return self.lei.upper() if self.lei else f"name:{self.entity_name.strip().lower()}"

    def is_header_echo(self) -> bool:
        """A repeated CSV header line that an older snapshot stored as an entry."""
        return (
            self.authority == "ae_competentAuthority"
            and self.entity_name == "ae_lei_name"
            and self.lei == "ae_lei"
        )


class RegisterSnapshot(BaseModel):
    slug: str
    title: str
    kind: str
    source_url: str
    fetched: bool
    fetch_error: str = ""
    entries: list[RegisterEntry] = []
    # v2: the export's header, in ESMA's order.
    columns: list[str] = []

    def rows(self) -> list[RegisterEntry]:
        """The register's rows, without header lines that older snapshots stored."""
        return [entry for entry in self.entries if not entry.is_header_echo()]

    def entity_count(self) -> int:
        """Distinct firms or issuers: LEIs, or names for rows without one."""
        return len({entry.entity_key() for entry in self.rows()})

    def entities_with_withdrawal_date(self) -> int | None:
        """Entities with a withdrawal date on one of their rows; None for snapshots
        written before v2, which did not keep the column."""
        rows = self.rows()
        if not any(entry.fields for entry in rows):
            return None
        return len({entry.entity_key() for entry in rows if entry.withdrawal_date})


class Snapshot(BaseModel):
    snapshot_date: str  # YYYY-MM-DD
    registers: list[RegisterSnapshot] = []

    def register(self, slug: str) -> RegisterSnapshot | None:
        for reg in self.registers:
            if reg.slug == slug:
                return reg
        return None


class FieldChange(BaseModel):
    field: str  # ESMA column name
    old: str
    new: str


class ChangeRecord(BaseModel):
    snapshot_date: str
    register_slug: str
    # "added" | "changed" | "missing" | "removed" | "restored" | "baseline"
    change: str
    entry_id: str
    entity_name: str
    member_state: str
    wp_url: str = ""
    detail: str = ""
    # Added with changelog record version 2; defaults keep version 1 records loadable.
    record_version: int = 1
    lei: str = ""
    row_key: str = ""
    row_hash: str = ""
    subtypes: list[str] = []
    changed_fields: list[FieldChange] = []
