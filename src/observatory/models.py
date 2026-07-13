"""Normalized register entries and snapshot containers."""

from __future__ import annotations

import hashlib

from pydantic import BaseModel


CONTENT_VERIFICATION_FIELDS = (
    "content_verification_status",
    "verified_at",
    "requested_url",
    "final_url",
    "http_status",
    "content_type",
    "declared_content_type",
    "declared_content_length",
    "bytes_read",
    "content_truncated",
    "content_sha256",
    "verified_format",
    "inline_xbrl",
    "detection_basis",
    "verification_error",
)


class RegisterEntry(BaseModel):
    entry_id: str
    register_slug: str
    authority: str
    member_state: str
    entity_name: str
    lei: str
    wp_url: str
    last_update: str  # raw register value, DD/MM/YYYY where populated
    format_class: str  # URL-shape class; see coverage.classify_format
    row_hash: str

    # Optional content-level evidence. Defaults preserve compatibility with snapshots
    # created before content verification was introduced.
    content_verification_status: str = "not_checked"
    verified_at: str = ""
    requested_url: str = ""
    final_url: str = ""
    http_status: int | None = None
    content_type: str = ""
    declared_content_type: str = ""
    declared_content_length: int | None = None
    bytes_read: int = 0
    content_truncated: bool = False
    content_sha256: str | None = None
    verified_format: str = ""
    inline_xbrl: bool = False
    detection_basis: str = ""
    verification_error: str = ""

    @staticmethod
    def make_entry_id(register: str, lei: str, entity_name: str, wp_url: str) -> str:
        # LEI is the stable identifier; name+URL is the fallback for rows without one.
        key = f"{register}|{lei or entity_name}|{wp_url}".lower()
        return hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]


class RegisterSnapshot(BaseModel):
    slug: str
    title: str
    kind: str
    source_url: str
    fetched: bool
    fetch_error: str = ""
    entries: list[RegisterEntry] = []


class Snapshot(BaseModel):
    snapshot_date: str  # YYYY-MM-DD
    registers: list[RegisterSnapshot] = []

    def register(self, slug: str) -> RegisterSnapshot | None:
        for reg in self.registers:
            if reg.slug == slug:
                return reg
        return None


class ChangeRecord(BaseModel):
    snapshot_date: str
    register_slug: str
    change: str  # "added" | "removed" | "changed" | "baseline"
    entry_id: str
    entity_name: str
    member_state: str
    wp_url: str = ""
    detail: str = ""
