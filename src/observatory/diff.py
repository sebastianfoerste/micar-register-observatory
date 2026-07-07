"""Compare two snapshots register by register."""

from __future__ import annotations

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

    old = {entry.entry_id: entry for entry in previous.entries}
    new = {entry.entry_id: entry for entry in current.entries}
    changes: list[ChangeRecord] = []

    for entry_id, entry in new.items():
        if entry_id not in old:
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
        elif old[entry_id].row_hash != entry.row_hash:
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

    for entry_id, entry in old.items():
        if entry_id not in new:
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
