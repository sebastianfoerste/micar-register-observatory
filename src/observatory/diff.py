"""Compare two snapshots register by register.

Rows are matched within each entry_id as a multiset: several rows can share an
entry_id (a firm with two authorisations, an issuer with several tokens behind
one URL), and every one of them is compared. Within an entry_id, identical rows
pair first, then rows with the same v2 row key, then the most similar rows.

Absences are confirmed before they are reported: a row's first absence from an
export is `missing`, a second absence in a row makes it `removed`, and a row that
is listed again is `restored`. The export has dropped and re-listed hundreds of
rows within a week, so a single absence is not evidence that an entry left.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Sequence
from dataclasses import dataclass, field

from pydantic import BaseModel

from observatory.config import MAX_WEEKLY_SHRINK, MIN_SHRINK_ROWS
from observatory.models import (
    CHANGE_RECORD_VERSION,
    ChangeRecord,
    FieldChange,
    RegisterEntry,
    RegisterSnapshot,
    Snapshot,
)
from observatory.normalize import iso_date, parse_countries, parse_services


@dataclass
class RowMatching:
    """How the rows of one register pair up; every input row appears exactly once."""

    unchanged: list[tuple[int, int]] = field(default_factory=list)  # (old index, new index)
    changed: list[tuple[int, int]] = field(default_factory=list)
    unmatched_old: list[int] = field(default_factory=list)
    unmatched_new: list[int] = field(default_factory=list)
    # Rows that went missing in the previous export and are listed again:
    # (index into `missing`, new index). `still_missing` are the others.
    returned: list[tuple[int, int]] = field(default_factory=list)
    still_missing: list[int] = field(default_factory=list)


def _similarity(old: RegisterEntry, new: RegisterEntry) -> int:
    if old.fields and new.fields:
        keys = set(old.fields) | set(new.fields)
        return sum(1 for key in keys if old.fields.get(key) == new.fields.get(key))
    core = ("authority", "member_state", "entity_name", "lei", "wp_url", "last_update")
    return sum(1 for name in core if getattr(old, name) == getattr(new, name))


def match_rows(
    old: list[RegisterEntry],
    new: list[RegisterEntry],
    missing: Sequence[tuple[str, str]] = (),
) -> RowMatching:
    """Pair old and new rows; `missing` are the (entry_id, row_hash) of rows that
    were absent from the previous export after being listed before it."""
    matching = RowMatching()
    old_groups: dict[str, list[int]] = defaultdict(list)
    new_groups: dict[str, list[int]] = defaultdict(list)
    missing_groups: dict[str, list[int]] = defaultdict(list)
    for index, entry in enumerate(old):
        old_groups[entry.entry_id].append(index)
    for index, entry in enumerate(new):
        new_groups[entry.entry_id].append(index)
    for index, (entry_id, _) in enumerate(missing):
        missing_groups[entry_id].append(index)

    for entry_id in sorted(set(old_groups) | set(new_groups)):
        olds = old_groups.get(entry_id, [])
        news = new_groups.get(entry_id, [])
        gone = missing_groups.get(entry_id, [])
        for j in list(news):  # identical rows
            i = next((i for i in olds if old[i].row_hash == new[j].row_hash), None)
            if i is not None:
                olds.remove(i)
                news.remove(j)
                matching.unchanged.append((i, j))
        for j in list(news):  # missing rows listed again exactly as they were
            k = next((k for k in gone if missing[k][1] == new[j].row_hash), None)
            if k is not None:
                gone.remove(k)
                news.remove(j)
                matching.returned.append((k, j))
        for j in list(news):  # the same row, with new content
            i = next(
                (i for i in olds if new[j].row_key and old[i].row_key == new[j].row_key), None
            )
            if i is not None:
                olds.remove(i)
                news.remove(j)
                matching.changed.append((i, j))
        candidates = sorted((-_similarity(old[i], new[j]), i, j) for i in olds for j in news)
        for _, i, j in candidates:  # the rest, most similar first
            if i in olds and j in news:
                olds.remove(i)
                news.remove(j)
                matching.changed.append((i, j))
        for j in list(news):  # missing rows listed again with other content
            if gone:
                matching.returned.append((gone.pop(0), j))
                news.remove(j)
        matching.unmatched_old.extend(olds)
        matching.unmatched_new.extend(news)
    matching.still_missing = sorted(k for ks in missing_groups.values() for k in ks)
    return matching


def field_changes(old: RegisterEntry, new: RegisterEntry) -> list[FieldChange]:
    """ESMA columns whose value differs; empty when either row predates `fields`."""
    if not old.fields or not new.fields:
        return []
    keys = list(new.fields) + [key for key in old.fields if key not in new.fields]
    return [
        FieldChange(field=key, old=old.fields.get(key, ""), new=new.fields.get(key, ""))
        for key in keys
        if old.fields.get(key, "") != new.fields.get(key, "")
    ]


def _offer_countries(fields: dict[str, str]) -> list[str]:
    return parse_countries(fields.get("ae_offerCode_cou") or fields.get("wp_url_cou", ""))


def change_subtypes(old: RegisterEntry, new: RegisterEntry) -> list[str]:
    """Mechanical labels for what changed, re-read from the verbatim columns."""
    if not old.fields or not new.fields:
        return []
    subtypes: list[str] = []
    before = iso_date(old.fields.get("ac_authorisationEndDate", ""))
    after = iso_date(new.fields.get("ac_authorisationEndDate", ""))
    if after and not before:
        subtypes.append("withdrawal_date_recorded")
    elif before and not after:
        subtypes.append("withdrawal_date_cleared")
    elif before != after:
        subtypes.append("withdrawal_date_changed")
    sets = (
        ("services", parse_services(old.fields.get("ac_serviceCode", "")),
         parse_services(new.fields.get("ac_serviceCode", ""))),
        ("service_countries", parse_countries(old.fields.get("ac_serviceCode_cou", "")),
         parse_countries(new.fields.get("ac_serviceCode_cou", ""))),
        ("offer_countries", _offer_countries(old.fields), _offer_countries(new.fields)),
    )
    for name, old_values, new_values in sets:
        if set(new_values) - set(old_values):
            subtypes.append(f"{name}_added")
        if set(old_values) - set(new_values):
            subtypes.append(f"{name}_removed")
    if old.last_update != new.last_update:
        subtypes.append("last_update_changed")
    if old.comments != new.comments:
        subtypes.append("comments_changed")
    return subtypes


def _record(
    snapshot_date: str, slug: str, change: str, entry: RegisterEntry, detail: str = ""
) -> ChangeRecord:
    return ChangeRecord(
        snapshot_date=snapshot_date,
        register_slug=slug,
        change=change,
        entry_id=entry.entry_id,
        entity_name=entry.entity_name,
        member_state=entry.member_state,
        wp_url=entry.wp_url,
        detail=detail,
        record_version=CHANGE_RECORD_VERSION,
        lei=entry.lei,
        row_key=entry.row_key,
        row_hash=entry.row_hash,
    )


def absent_rows(history: Sequence[ChangeRecord]) -> Counter[str]:
    """Rows per entry_id that left the export and have not been listed again.

    Changelog records before version 2 called a first absence `removed` and a
    relisting `added`. From version 2 a first absence is `missing`, `removed`
    confirms an absence already counted, and a relisting is `restored`.
    """
    absent: Counter[str] = Counter()
    for record in history:
        if record.change == "baseline":
            absent.clear()
        elif record.change == "missing" or (
            record.change == "removed" and record.record_version < CHANGE_RECORD_VERSION
        ):
            absent[record.entry_id] += 1
        elif record.change in ("restored", "added") and absent[record.entry_id] > 0:
            absent[record.entry_id] -= 1
    return absent


def _missing_record(
    record: ChangeRecord, snapshot_date: str, change: str, detail: str
) -> ChangeRecord:
    return record.model_copy(
        update={
            "snapshot_date": snapshot_date,
            "change": change,
            "detail": detail,
            "record_version": CHANGE_RECORD_VERSION,
            "subtypes": [],
            "changed_fields": [],
        }
    )


def diff_registers(
    previous: RegisterSnapshot | None,
    current: RegisterSnapshot,
    snapshot_date: str,
    *,
    previous_date: str = "",
    history: Sequence[ChangeRecord] = (),
) -> list[ChangeRecord]:
    """Change records for one register; `history` is the changelog so far."""
    if not current.fetched:
        return []
    if previous is None or not previous.fetched:
        # First observation of this register: record a baseline, not N "added" rows.
        return [
            ChangeRecord(
                snapshot_date=snapshot_date,
                register_slug=current.slug,
                change="baseline",
                entry_id="-",
                entity_name="-",
                member_state="-",
                detail=f"baseline established with {len(current.entries)} entries",
            )
        ]

    # Older snapshots stored repeated CSV header lines as entries; they are not rows.
    old = [entry for entry in previous.entries if not entry.is_header_echo()]
    new = [entry for entry in current.entries if not entry.is_header_echo()]
    own_history = [record for record in history if record.register_slug == current.slug]
    pending = [
        record
        for record in own_history
        if record.change == "missing" and previous_date and record.snapshot_date == previous_date
    ]
    # Rows that left before the previous export: a new row of the same entry_id
    # is one of them coming back, as long as fewer have come back than left.
    absent_earlier = absent_rows(own_history)
    absent_earlier.subtract(record.entry_id for record in pending)
    last_absence = {r.entry_id: r for r in own_history if r.change in ("missing", "removed")}

    matching = match_rows(old, new, [(r.entry_id, r.row_hash) for r in pending])
    changed = {j: i for i, j in matching.changed}
    returned = {j: k for k, j in matching.returned}
    unmatched_new = set(matching.unmatched_new)
    changes: list[ChangeRecord] = []

    for j, entry in enumerate(new):
        if j in returned:
            detail = f"listed again after one export without it (missing on {previous_date})"
            changes.append(_record(snapshot_date, current.slug, "restored", entry, detail))
        elif j in unmatched_new and absent_earlier[entry.entry_id] > 0:
            absent_earlier[entry.entry_id] -= 1
            last = last_absence[entry.entry_id]
            detail = f"listed again (last recorded as {last.change} on {last.snapshot_date})"
            changes.append(_record(snapshot_date, current.slug, "restored", entry, detail))
        elif j in unmatched_new:
            changes.append(_record(snapshot_date, current.slug, "added", entry))
        elif j in changed:
            before = old[changed[j]]
            fields = field_changes(before, entry)
            detail = "register row content changed"
            if fields:
                detail += f" ({', '.join(change.field for change in fields)})"
            record = _record(snapshot_date, current.slug, "changed", entry, detail)
            record.changed_fields = fields
            record.subtypes = change_subtypes(before, entry)
            changes.append(record)

    for i in sorted(matching.unmatched_old):
        detail = "not in this export; recorded as removed if the next export also lacks it"
        changes.append(_record(snapshot_date, current.slug, "missing", old[i], detail))
    for k in matching.still_missing:
        detail = f"not in two consecutive exports (missing since {previous_date})"
        changes.append(_missing_record(pending[k], snapshot_date, "removed", detail))
    return changes


def diff_snapshots(
    previous: Snapshot | None,
    current: Snapshot,
    history: Sequence[ChangeRecord] = (),
) -> list[ChangeRecord]:
    changes: list[ChangeRecord] = []
    for register in current.registers:
        old_register = previous.register(register.slug) if previous else None
        changes.extend(
            diff_registers(
                old_register,
                register,
                current.snapshot_date,
                previous_date=previous.snapshot_date if previous else "",
                history=history,
            )
        )
    return changes


class Shrink(BaseModel):
    """A register whose export lost a large share of its rows in one step."""

    slug: str
    before: int
    after: int

    def describe(self) -> str:
        share = (self.before - self.after) / self.before if self.before else 0.0
        return f"{self.slug} fell from {self.before} to {self.after} rows (-{share:.1%})"


def _row_count(register: RegisterSnapshot) -> int:
    return sum(1 for entry in register.entries if not entry.is_header_echo())


def export_shrinks(
    previous: Snapshot | None,
    current: Snapshot,
    max_share: float = MAX_WEEKLY_SHRINK,
    min_rows: int = MIN_SHRINK_ROWS,
) -> list[Shrink]:
    """Registers that lost more than `max_share` of their rows, and at least
    `min_rows` rows, between `previous` and `current`."""
    if previous is None:
        return []
    shrinks: list[Shrink] = []
    for register in current.registers:
        before_register = previous.register(register.slug)
        if before_register is None or not before_register.fetched or not register.fetched:
            continue
        before, after = _row_count(before_register), _row_count(register)
        if before - after >= min_rows and before - after > max_share * before:
            shrinks.append(Shrink(slug=register.slug, before=before, after=after))
    return shrinks
