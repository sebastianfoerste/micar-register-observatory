"""Parse raw ESMA register CSVs into normalized entries.

Every column of a row is kept verbatim in `RegisterEntry.fields`. The typed
fields next to it (dates, services, country lists, DTIs) are mechanical
normalizations of those columns; the verbatim value always stays available.
"""

from __future__ import annotations

import csv
import datetime
import hashlib
import io
import re

from pydantic import BaseModel

from observatory.config import REQUIRED_COLUMNS, WHITEPAPER_COLUMNS, RegisterSource
from observatory.coverage import classify_format
from observatory.models import RegisterEntry


def _row_hash(row: dict[str, str]) -> str:
    canonical = "|".join(f"{k}={v.strip()}" for k, v in sorted(row.items()) if k)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


class SchemaError(ValueError):
    """The downloaded file is not a register CSV of the expected shape."""


class ParsedRegister(BaseModel):
    columns: list[str]
    entries: list[RegisterEntry]


# Values the export uses for "nothing here"; typed fields store them as "".
_PLACEHOLDERS = {"", "-", "n/a", "na", "none", "not applicable", "not available"}

_DATE = re.compile(r"^(\d{1,2})[./-](\d{1,2})[./-](\d{4})$")

_COUNTRY = re.compile(r"^[A-Z]{2}$")

# Matched against the whole lower-cased services cell: one cell can hold several
# services separated by pipes, commas, slashes or nothing at all.
_SERVICE_PATTERNS: dict[str, re.Pattern[str]] = {
    "a": re.compile(r"custody"),
    "b": re.compile(r"trading platform"),
    "c": re.compile(r"for funds|for fiat|and fiat"),
    "d": re.compile(r"for other|between crypto[- ]?assets?(?! and fiat)"),
    "e": re.compile(r"execution of (?:client )?orders"),
    "f": re.compile(r"placing"),
    "g": re.compile(r"reception and transmission"),
    "h": re.compile(r"advice"),
    "i": re.compile(r"portfolio management"),
    "j": re.compile(r"transfer services?"),
}


_COMMENTS_COLUMN = {"casps": "ac_comments", "ncasp": "ae_comments"}


def clean(value: str) -> str:
    value = value.strip()
    return "" if value.lower() in _PLACEHOLDERS else value


def iso_date(value: str) -> str:
    """DD/MM/YYYY (also with . or -) to YYYY-MM-DD; "" when blank or not a date."""
    match = _DATE.match(value.strip())
    if not match:
        return ""
    day, month, year = (int(group) for group in match.groups())
    try:
        return datetime.date(year, month, day).isoformat()
    except ValueError:
        return ""


def parse_countries(value: str) -> list[str]:
    """Two-letter country codes, sorted and unique; other tokens are dropped."""
    tokens = re.split(r"[|,;\s]+", value.upper())
    return sorted({token for token in tokens if _COUNTRY.match(token)})


def parse_services(value: str) -> list[str]:
    text = " ".join(value.replace("\t", " ").split()).lower()
    return [code for code, pattern in _SERVICE_PATTERNS.items() if pattern.search(text)]


def parse_dti(value: str) -> list[str]:
    return sorted({clean(token).upper() for token in re.split(r"[|,;]", value) if clean(token)})


def _is_header_echo(row: dict[str, str]) -> bool:
    # ESMA's exports have contained the header line again in the middle of the file.
    return all(row.get(column) == column for column in REQUIRED_COLUMNS)


def _entry(source: RegisterSource, row: dict[str, str]) -> RegisterEntry:
    entity_name = row.get("ae_lei_name", "")
    lei = row.get("ae_lei", "")
    wp_url = row.get("wp_url", "")
    dti_ffg = clean(row.get("ae_DTI_FFG", "")).upper()
    dti = parse_dti(row.get("ae_DTI", ""))
    casp_lei = clean(row.get("ae_lei_casp", ""))
    authorisation_date = iso_date(row.get("ac_authorisationNotificationDate", ""))
    decision_date = iso_date(row.get("ae_decision_date", ""))
    if source.kind == "whitepaper":
        key_parts: tuple[str, ...] = (wp_url, dti_ffg, ",".join(dti), casp_lei)
    elif source.slug == "ncasp":
        key_parts = (decision_date,)
    else:
        key_parts = (authorisation_date,)
    return RegisterEntry(
        entry_id=RegisterEntry.make_entry_id(source.slug, lei, entity_name, wp_url),
        register_slug=source.slug,
        authority=row.get("ae_competentAuthority", ""),
        member_state=row.get("ae_homeMemberState", ""),
        entity_name=entity_name,
        lei=lei,
        wp_url=wp_url,
        last_update=row.get(source.last_update_column, ""),
        format_class=classify_format(wp_url) if source.kind == "whitepaper" else "n/a",
        row_hash=_row_hash(row),
        row_key=RegisterEntry.make_row_key(source.slug, lei, entity_name, *key_parts),
        fields={key: value for key, value in row.items() if key},
        commercial_name=clean(row.get("ae_commercial_name", "")),
        website=clean(row.get("ae_website", "")),
        authorisation_date=authorisation_date,
        withdrawal_date=iso_date(row.get("ac_authorisationEndDate", "")),
        offer_start_date=iso_date(row.get("wp_authorisationNotificationDate", "")),
        decision_date=decision_date,
        services=parse_services(row.get("ac_serviceCode", "")),
        service_countries=parse_countries(row.get("ac_serviceCode_cou", "")),
        offer_countries=parse_countries(row.get("ae_offerCode_cou") or row.get("wp_url_cou", "")),
        dti_ffg=dti_ffg,
        dti=dti,
        casp_name=clean(row.get("ae_lei_name_casp", "")),
        casp_lei=casp_lei,
        reason=clean(row.get("ae_reason", "")),
        comments=row.get(_COMMENTS_COLUMN.get(source.slug, "wp_comments"), ""),
    )


def parse_register(
    source: RegisterSource, raw: bytes, *, enforce_min_rows: bool = False
) -> ParsedRegister:
    # ESMA files are UTF-8 with BOM; utf-8-sig handles both cases.
    text = raw.decode("utf-8-sig", errors="replace")
    reader = csv.DictReader(io.StringIO(text))
    columns = [(name or "").strip() for name in reader.fieldnames or []]
    required = REQUIRED_COLUMNS + (WHITEPAPER_COLUMNS if source.kind == "whitepaper" else ())
    missing = [column for column in required if column not in columns]
    if missing:
        raise SchemaError(f"{source.slug}: missing columns {missing}")
    entries: list[RegisterEntry] = []
    for raw_row in reader:
        if None in raw_row:  # DictReader files surplus values under the key None
            raise SchemaError(
                f"{source.slug}: line {reader.line_num} has more values than the header"
            )
        row = {(k or "").strip(): (v or "").strip() for k, v in raw_row.items()}
        if not row.get("ae_lei_name") and not row.get("ae_lei") and not row.get("wp_url"):
            continue
        if _is_header_echo(row):
            continue
        entries.append(_entry(source, row))
    if enforce_min_rows and len(entries) < source.min_rows:
        raise SchemaError(
            f"{source.slug}: {len(entries)} rows, below the minimum of {source.min_rows}"
        )
    return ParsedRegister(columns=[column for column in columns if column], entries=entries)


def normalize_csv(
    source: RegisterSource, raw: bytes, *, enforce_min_rows: bool = False
) -> list[RegisterEntry]:
    return parse_register(source, raw, enforce_min_rows=enforce_min_rows).entries


def column_drift(source: RegisterSource, columns: list[str]) -> tuple[list[str], list[str]]:
    """Columns ESMA added and dropped relative to the reviewed header in config."""
    if not source.columns:
        return [], []
    added = [column for column in columns if column not in source.columns]
    dropped = [column for column in source.columns if column not in columns]
    return added, dropped
