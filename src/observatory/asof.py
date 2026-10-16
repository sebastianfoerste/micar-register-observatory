"""Answer "what did the register list for this firm on this date?" from the
recorded snapshots and the changelog.

The answer comes from the last snapshot recorded on or before the date: the
weekly export as the observatory fetched it, not ESMA's register on that exact
day. Rows are matched by LEI, or by a case-insensitive part of the name.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from observatory.config import SERVICE_NAMES, SOURCES
from observatory.models import ChangeRecord, RegisterEntry, Snapshot
from observatory.store import load_snapshot, read_changelog, snapshot_dates


@dataclass
class AsOfAnswer:
    as_of: str
    lei: str = ""
    name: str = ""
    register: str = ""
    snapshot_date: str = ""  # "" when no snapshot was recorded on or before as_of
    rows: list[RegisterEntry] = field(default_factory=list)
    not_listed_in: list[str] = field(default_factory=list)
    history: list[ChangeRecord] = field(default_factory=list)
    quarantined: list[str] = field(default_factory=list)  # exports set aside since

    def to_json(self) -> dict[str, Any]:
        return {
            "as_of": self.as_of,
            "query": {"lei": self.lei, "name": self.name, "register": self.register},
            "snapshot_date": self.snapshot_date or None,
            "rows": [row.model_dump() for row in self.rows],
            "not_listed_in": self.not_listed_in,
            "history": [record.model_dump() for record in self.history],
            "quarantined_exports_since_snapshot": self.quarantined,
        }


def matches(entry: RegisterEntry, lei: str, name: str) -> bool:
    if lei:
        return entry.lei.strip().upper() == lei.strip().upper()
    needle = name.strip().lower()
    return bool(needle) and (
        needle in entry.entity_name.lower() or needle in entry.commercial_name.lower()
    )


def find_rows(snapshot: Snapshot, lei: str, name: str, register: str = "") -> list[RegisterEntry]:
    return [
        entry
        for reg in snapshot.registers
        if reg.fetched and (not register or reg.slug == register)
        for entry in reg.rows()
        if matches(entry, lei, name)
    ]


def as_of(
    data_dir: Path, date: str, *, lei: str = "", name: str = "", register: str = ""
) -> AsOfAnswer:
    answer = AsOfAnswer(as_of=date, lei=lei, name=name, register=register)
    dates = [day for day in snapshot_dates(data_dir) if day <= date]
    if not dates:
        return answer
    snapshot = load_snapshot(data_dir, dates[-1])
    answer.snapshot_date = snapshot.snapshot_date
    answer.rows = find_rows(snapshot, lei, name, register)
    listed = {row.register_slug for row in answer.rows}
    answer.not_listed_in = [
        reg.slug
        for reg in snapshot.registers
        if reg.fetched and reg.slug not in listed and (not register or reg.slug == register)
    ]
    # Changelog records before version 2 carry no LEI: collect the entry ids the
    # firm's rows had in every snapshot up to the date.
    entry_ids = {
        row.entry_id
        for day in dates
        for row in find_rows(load_snapshot(data_dir, day), lei, name, register)
    }
    answer.history = [
        record
        for record in read_changelog(data_dir)
        if record.snapshot_date <= snapshot.snapshot_date
        and (not register or record.register_slug == register)
        and (
            record.entry_id in entry_ids
            or (lei and record.lei.strip().upper() == lei.strip().upper())
        )
    ]
    answer.quarantined = sorted(
        path.stem
        for path in (data_dir / "quarantine").glob("*.json")
        if snapshot.snapshot_date < path.stem <= date
    )
    return answer


def _describe(entry: RegisterEntry) -> list[str]:
    head = entry.entity_name + (f" (LEI {entry.lei})" if entry.lei else " (no LEI)")
    lines = [f"  {head}; {entry.member_state}; {entry.authority}"]
    facts = []
    if entry.wp_url:
        facts.append(f"white paper {entry.wp_url}")
    if entry.authorisation_date:
        facts.append(f"authorised {entry.authorisation_date}")
    if entry.withdrawal_date:
        facts.append(f"withdrawal date {entry.withdrawal_date}")
    if entry.services:
        facts.append("services " + ", ".join(entry.services))
    if entry.service_countries:
        facts.append("service countries " + ", ".join(entry.service_countries))
    if entry.offer_countries:
        facts.append("offer countries " + ", ".join(entry.offer_countries))
    if entry.decision_date:
        facts.append(f"decision {entry.decision_date}")
    if entry.last_update:
        facts.append(f"last update {entry.last_update}")
    if facts:
        lines.append("    " + "; ".join(facts))
    return lines


def render_text(answer: AsOfAnswer) -> str:
    query = f"LEI {answer.lei}" if answer.lei else f"name containing {answer.name!r}"
    if not answer.snapshot_date:
        return f"No snapshot was recorded on or before {answer.as_of}.\n"
    lines = [
        f"{query}, as of {answer.as_of}: the snapshot of {answer.snapshot_date}, the last "
        "recorded on or before that date (ESMA's export as fetched that week).",
        "",
    ]
    titles = {source.slug: source.title for source in SOURCES}
    for slug in [source.slug for source in SOURCES]:
        rows = [row for row in answer.rows if row.register_slug == slug]
        if not rows:
            continue
        lines.append(f"{titles[slug]}: {len(rows)} row{'s' if len(rows) != 1 else ''}")
        for row in rows:
            lines.extend(_describe(row))
        lines.append("")
    if answer.not_listed_in:
        lines.append("Not listed in: " + ", ".join(answer.not_listed_in) + ".")
        lines.append("")
    if any(row.services for row in answer.rows):
        used = sorted({letter for row in answer.rows for letter in row.services})
        lines.append("Services: " + "; ".join(f"{s} = {SERVICE_NAMES[s]}" for s in used) + ".")
        lines.append("")
    if answer.history:
        lines.append(f"Recorded changes up to {answer.snapshot_date}:")
        for record in answer.history:
            lines.append(
                f"  {record.snapshot_date}  {record.register_slug:<8}  {record.change:<8}  "
                f"{record.entity_name}" + (f" ({record.detail})" if record.detail else "")
            )
        lines.append("")
    if answer.quarantined:
        lines.append(
            "Exports set aside after a sharp drop in rows and not recorded: "
            + ", ".join(answer.quarantined) + "."
        )
        lines.append("")
    if answer.rows and not any(row.fields for row in answer.rows):
        lines.append(
            "Snapshots up to 2026-10-12 keep only the core columns: no dates, services "
            "or countries."
        )
    return "\n".join(lines) + "\n"
