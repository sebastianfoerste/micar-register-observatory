"""Compare two snapshots register by register."""

from __future__ import annotations

from pydantic import BaseModel

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


class RemovalChurn(BaseModel):
    """Removed records of one register, split by whether the entry came back."""

    register_slug: str
    removed: int = 0
    relisted: int = 0

    @property
    def net(self) -> int:
        return self.removed - self.relisted


def removal_churn(
    changes: list[ChangeRecord], current: Snapshot | None = None
) -> list[RemovalChurn]:
    """Split every `removed` record into a temporary drop or a net removal.

    A removal is a temporary drop when the same entry (same register, same entry
    identity) is listed again in a later snapshot: a later `added` record exists
    for it, or it is listed in `current`. The second test covers entries that
    came back after a register was re-baselined. Every other removal is a net
    removal: the entry has not been listed again as of the latest snapshot. A net
    removal is not evidence of a withdrawal; it can also be an upstream
    correction or a changed white-paper URL.
    """
    last_added: dict[tuple[str, str], str] = {}
    for change in changes:
        if change.change == "added":
            key = (change.register_slug, change.entry_id)
            if change.snapshot_date > last_added.get(key, ""):
                last_added[key] = change.snapshot_date

    listed_now: set[tuple[str, str]] = set()
    if current is not None:
        listed_now = {
            (register.slug, entry.entry_id)
            for register in current.registers
            if register.fetched
            for entry in register.entries
        }

    churn: dict[str, RemovalChurn] = {}
    for change in changes:
        if change.change != "removed":
            continue
        key = (change.register_slug, change.entry_id)
        summary = churn.setdefault(
            change.register_slug, RemovalChurn(register_slug=change.register_slug)
        )
        summary.removed += 1
        if last_added.get(key, "") > change.snapshot_date or (
            key in listed_now
            and current is not None
            and current.snapshot_date > change.snapshot_date
        ):
            summary.relisted += 1

    order = [register.slug for register in current.registers] if current else []
    return sorted(
        churn.values(),
        key=lambda item: (
            order.index(item.register_slug)
            if item.register_slug in order
            else len(order),
            item.register_slug,
        ),
    )
