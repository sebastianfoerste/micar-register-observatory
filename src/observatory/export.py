"""Flat CSV exports of the latest snapshot and of the changelog, under data/exports/.

One file per kind of register plus one for the change records, for people who
want a spreadsheet or a dataframe rather than the nested snapshot JSON. Every
column is a typed field of the snapshot (see docs/data-dictionary.md); the
verbatim ESMA columns stay in the snapshot's `fields`. Lists are joined with
"|", as ESMA's own exports do, and dates are ISO. The files are rewritten from
the recorded data by every refresh and by `render`.
"""

from __future__ import annotations

import csv
import io
from collections.abc import Iterable
from pathlib import Path

from observatory.models import ChangeRecord, RegisterEntry, Snapshot
from observatory.normalize import iso_date

ENTRY_COLUMNS = (
    "snapshot_date",
    "register",
    "entry_id",
    "row_key",
    "lei",
    "entity_name",
    "commercial_name",
    "authority",
    "member_state",
)

# The column order of each export; contracts/exports.v1.schema.json lists the same.
EXPORT_COLUMNS: dict[str, tuple[str, ...]] = {
    "casps": (
        *ENTRY_COLUMNS,
        "authorisation_date",
        "withdrawal_date",
        "services",
        "service_countries",
        "website",
        "comments",
        "last_update",
    ),
    "ncasp": (
        *ENTRY_COLUMNS,
        "decision_date",
        "reason",
        "website",
        "comments",
        "last_update",
    ),
    "whitepapers": (
        *ENTRY_COLUMNS,
        "wp_url",
        "format_class",
        "dti_ffg",
        "dti",
        "offer_countries",
        "offer_start_date",
        "authorisation_date",
        "withdrawal_date",
        "casp_name",
        "casp_lei",
        "modification_noted",
        "comments",
        "last_update",
    ),
    "changes": (
        "snapshot_date",
        "register",
        "change",
        "entry_id",
        "lei",
        "entity_name",
        "member_state",
        "wp_url",
        "subtypes",
        "changed_fields",
        "detail",
        "record_version",
        "row_key",
        "row_hash",
    ),
}

# Which registers go into which export.
EXPORT_REGISTERS: dict[str, tuple[str, ...]] = {
    "casps": ("casps",),
    "ncasp": ("ncasp",),
    "whitepapers": ("other-wp", "emt-wp", "art-wp"),
}


def _cell(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, list):
        return "|".join(str(item) for item in value)
    return str(value)


def entry_row(snapshot_date: str, entry: RegisterEntry) -> dict[str, str]:
    """An entry as export cells, for every column any entry export has."""
    values = entry.model_dump(exclude={"fields"})
    values.update(
        snapshot_date=snapshot_date,
        register=entry.register_slug,
        last_update=iso_date(entry.last_update),
    )
    row = {key: _cell(value) for key, value in values.items()}
    if not entry.fields:  # written before the v2 fields: the flag was never computed
        row["modification_noted"] = ""
    return row


def change_row(record: ChangeRecord) -> dict[str, str]:
    values = record.model_dump()
    values.update(
        register=record.register_slug,
        changed_fields=[change.field for change in record.changed_fields],
    )
    return {key: _cell(value) for key, value in values.items()}


def to_csv(columns: tuple[str, ...], rows: Iterable[dict[str, str]]) -> str:
    buffer = io.StringIO()
    writer = csv.DictWriter(
        buffer, fieldnames=columns, extrasaction="ignore", lineterminator="\n"
    )
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def export_tables(snapshot: Snapshot, changes: list[ChangeRecord]) -> dict[str, str]:
    """The CSV text of every export, by name."""
    tables: dict[str, str] = {}
    for name, slugs in EXPORT_REGISTERS.items():
        rows = [
            entry_row(snapshot.snapshot_date, entry)
            for slug in slugs
            if (register := snapshot.register(slug)) is not None and register.fetched
            for entry in register.rows()
        ]
        tables[name] = to_csv(EXPORT_COLUMNS[name], rows)
    tables["changes"] = to_csv(EXPORT_COLUMNS["changes"], map(change_row, changes))
    return tables


def write_exports(folder: Path, snapshot: Snapshot, changes: list[ChangeRecord]) -> list[Path]:
    folder.mkdir(parents=True, exist_ok=True)
    paths = []
    for name, text in export_tables(snapshot, changes).items():
        path = folder / f"{name}.csv"
        path.write_text(text, encoding="utf-8")
        paths.append(path)
    return paths
