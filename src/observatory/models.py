"""Normalized register entries and snapshot containers."""

from __future__ import annotations

import hashlib

from pydantic import BaseModel


class RegisterEntry(BaseModel):
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
