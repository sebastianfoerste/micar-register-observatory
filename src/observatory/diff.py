"""Compare two snapshots register by register."""

from __future__ import annotations

from collections import defaultdict

from observatory.models import ChangeRecord, RegisterSnapshot, Snapshot


def diff_registers(
    previous: RegisterSnapshot | None,
    current: RegisterSnapshot,
    snapshot_date: str,
) -> list[ChangeRecord]:
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

    old: dict[str, list] = defaultdict(list)
    new: dict[str, list] = defaultdict(list)
    for entry in previous.entries:
        old[entry.entry_id].append(entry)
    for entry in current.entries:
        new[entry.entry_id].append(entry)
    changes: list[ChangeRecord] = []

    for entry_id in sorted(set(old) | set(new)):
        unmatched_old = sorted(
            old.get(entry_id, []),
            key=lambda entry: entry.row_hash,
        )
        unmatched_new = sorted(
            new.get(entry_id, []),
            key=lambda entry: entry.row_hash,
        )

        for entry in list(unmatched_new):
            exact_index = next(
                (
                    index
                    for index, old_entry in enumerate(unmatched_old)
                    if old_entry.row_hash == entry.row_hash
                ),
                None,
            )
            if exact_index is not None:
                unmatched_old.pop(exact_index)
                unmatched_new.remove(entry)

        paired = min(len(unmatched_old), len(unmatched_new))
        for index in range(paired):
            entry = unmatched_new[index]
            changes.append(
                ChangeRecord(
                    snapshot_date=snapshot_date,
                    register_slug=current.slug,
                    change="changed",
                    entry_id=entry_id,
                    entity_name=entry.entity_name,
                    member_state=entry.member_state,
                    wp_url=entry.wp_url,
                    detail="register row content changed",
                )
            )
        for entry in unmatched_new[paired:]:
            changes.append(
                ChangeRecord(
                    snapshot_date=snapshot_date,
                    register_slug=current.slug,
                    change="added",
                    entry_id=entry_id,
                    entity_name=entry.entity_name,
                    member_state=entry.member_state,
                    wp_url=entry.wp_url,
                )
            )
        for entry in unmatched_old[paired:]:
            changes.append(
                ChangeRecord(
                    snapshot_date=snapshot_date,
                    register_slug=current.slug,
                    change="removed",
                    entry_id=entry_id,
                    entity_name=entry.entity_name,
                    member_state=entry.member_state,
                    wp_url=entry.wp_url,
                    detail="entry no longer present in the register export",
                )
            )

    return changes


def diff_snapshots(
    previous: Snapshot | None, current: Snapshot
) -> list[ChangeRecord]:
    changes: list[ChangeRecord] = []
    for register in current.registers:
        old_register = previous.register(register.slug) if previous else None
        changes.extend(
            diff_registers(old_register, register, current.snapshot_date)
        )
    return changes
