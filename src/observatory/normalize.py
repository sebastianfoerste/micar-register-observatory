"""Parse raw ESMA register CSVs into normalized entries."""

from __future__ import annotations

import csv
import hashlib
import io

from observatory.config import REQUIRED_COLUMNS, WHITEPAPER_COLUMNS, RegisterSource
from observatory.coverage import classify_format
from observatory.models import RegisterEntry


def _row_hash(row: dict[str, str]) -> str:
    canonical = "|".join(f"{k}={v.strip()}" for k, v in sorted(row.items()) if k)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


class SchemaError(ValueError):
    """The downloaded file is not a register CSV of the expected shape."""


def normalize_csv(
    source: RegisterSource, raw: bytes, *, enforce_min_rows: bool = False
) -> list[RegisterEntry]:
    # ESMA files are UTF-8 with BOM; utf-8-sig handles both cases.
    text = raw.decode("utf-8-sig", errors="replace")
    reader = csv.DictReader(io.StringIO(text))
    header = {(name or "").strip() for name in reader.fieldnames or []}
    required = REQUIRED_COLUMNS + (WHITEPAPER_COLUMNS if source.kind == "whitepaper" else ())
    missing = [column for column in required if column not in header]
    if missing:
        raise SchemaError(f"{source.slug}: missing columns {missing}")
    entries: list[RegisterEntry] = []
    for row in reader:
        row = {(k or "").strip(): (v or "").strip() for k, v in row.items()}
        entity_name = row.get("ae_lei_name", "")
        lei = row.get("ae_lei", "")
        wp_url = row.get("wp_url", "")
        if not entity_name and not lei and not wp_url:
            continue
        entries.append(
            RegisterEntry(
                entry_id=RegisterEntry.make_entry_id(
                    source.slug, lei, entity_name, wp_url
                ),
                register_slug=source.slug,
                authority=row.get("ae_competentAuthority", ""),
                member_state=row.get("ae_homeMemberState", ""),
                entity_name=entity_name,
                lei=lei,
                wp_url=wp_url,
                last_update=row.get("wp_lastupdate", ""),
                format_class=(
                    classify_format(wp_url) if source.kind == "whitepaper" else "n/a"
                ),
                row_hash=_row_hash(row),
            )
        )
    if enforce_min_rows and len(entries) < source.min_rows:
        raise SchemaError(
            f"{source.slug}: {len(entries)} rows, below the minimum of {source.min_rows}"
        )
    return entries
