"""Property tests: the diff never loses or double-counts a register row."""

from collections import Counter

from hypothesis import given, settings
from hypothesis import strategies as st

from observatory.diff import absent_rows, diff_registers, diff_snapshots, match_rows
from observatory.models import ChangeRecord, RegisterEntry, RegisterSnapshot, Snapshot

# A tiny alphabet forces many rows to share an entry_id, row hash or row key.
ROWS = st.lists(
    st.tuples(
        st.sampled_from(["e1", "e2", "e3"]),
        st.sampled_from(["h1", "h2", "h3", "h4"]),
        st.sampled_from(["", "k1", "k2"]),
    ),
    max_size=10,
)


def entries(rows: list[tuple[str, str, str]]) -> list[RegisterEntry]:
    return [
        RegisterEntry(
            entry_id=entry_id,
            register_slug="other-wp",
            authority="NCA",
            member_state="DE",
            entity_name=entry_id,
            lei="",
            wp_url="",
            last_update=row_hash,
            format_class="none",
            row_hash=row_hash,
            row_key=row_key,
        )
        for entry_id, row_hash, row_key in rows
    ]


def register(rows: list[RegisterEntry]) -> RegisterSnapshot:
    return RegisterSnapshot(
        slug="other-wp", title="t", kind="whitepaper", source_url="u", fetched=True, entries=rows
    )


@settings(max_examples=300, deadline=None)
@given(ROWS, ROWS)
def test_every_row_is_matched_exactly_once(old_rows, new_rows) -> None:
    old, new = entries(old_rows), entries(new_rows)
    matching = match_rows(old, new)
    pairs = matching.unchanged + matching.changed
    assert sorted([i for i, _ in pairs] + matching.unmatched_old) == list(range(len(old)))
    assert sorted([j for _, j in pairs] + matching.unmatched_new) == list(range(len(new)))
    assert matching.returned == [] and matching.still_missing == []
    assert all(old[i].entry_id == new[j].entry_id for i, j in pairs)
    assert all(old[i].row_hash == new[j].row_hash for i, j in matching.unchanged)


@settings(max_examples=300, deadline=None)
@given(ROWS, ROWS)
def test_identical_rows_are_paired_as_far_as_possible(old_rows, new_rows) -> None:
    old, new = entries(old_rows), entries(new_rows)
    identical = Counter((e.entry_id, e.row_hash) for e in old) & Counter(
        (e.entry_id, e.row_hash) for e in new
    )
    assert len(match_rows(old, new).unchanged) == sum(identical.values())


@settings(max_examples=300, deadline=None)
@given(ROWS, ROWS)
def test_the_diff_conserves_rows(old_rows, new_rows) -> None:
    old, new = entries(old_rows), entries(new_rows)
    counts = Counter(c.change for c in diff_registers(register(old), register(new), "2026-10-19"))
    assert len(new) - len(old) == counts["added"] - counts["missing"]
    assert counts["changed"] + counts["missing"] <= len(old)
    assert counts["changed"] + counts["added"] <= len(new)
    assert counts["removed"] == counts["restored"] == 0  # nothing was missing before


@settings(max_examples=300, deadline=None)
@given(ROWS, ROWS, ROWS)
def test_rows_missing_before_are_either_restored_or_removed(old_rows, new_rows, gone_rows) -> None:
    old, new = entries(old_rows), entries(new_rows)
    pending = [
        ChangeRecord(
            snapshot_date="2026-10-12", register_slug="other-wp", change="missing",
            entry_id=e.entry_id, entity_name=e.entity_name, member_state="DE", row_hash=e.row_hash,
        )
        for e in entries(gone_rows)
    ]
    records = diff_registers(
        register(old), register(new), "2026-10-19", previous_date="2026-10-12", history=pending
    )
    counts = Counter(c.change for c in records)
    returned = sum(1 for c in records if c.detail.startswith("listed again after one export"))
    assert returned == counts["restored"]  # nothing left before the previous export
    assert returned + counts["removed"] == len(pending)
    assert len(new) - len(old) == counts["added"] + counts["restored"] - counts["missing"]


@settings(max_examples=300, deadline=None)
@given(st.lists(ROWS, min_size=2, max_size=6))
def test_week_after_week_every_row_is_accounted_for(weeks) -> None:
    history: list[ChangeRecord] = []
    previous: Snapshot | None = None
    for week, rows in enumerate(weeks):
        current = Snapshot(
            snapshot_date=f"2026-10-{10 + week}", registers=[register(entries(rows))]
        )
        records = diff_snapshots(previous, current, history)
        if previous is not None:
            before = Counter(e.entry_id for e in previous.registers[0].entries)
            after = Counter(e.entry_id for e in current.registers[0].entries)
            absent_before = absent_rows(history)
            absent_after = absent_rows(history + records)
            just_missing = Counter(
                c.entry_id
                for c in history
                if c.change == "missing" and c.snapshot_date == previous.snapshot_date
            )
            assert Counter(c.entry_id for c in records if c.change == "removed") <= just_missing
            for entry_id in set(before) | set(after) | set(absent_before):
                mine = Counter(c.change for c in records if c.entry_id == entry_id)
                assert after[entry_id] - before[entry_id] == (
                    mine["added"] + mine["restored"] - mine["missing"]
                )
                assert absent_after[entry_id] == (
                    absent_before[entry_id] + mine["missing"] - mine["restored"]
                )
                if mine["added"]:  # rows come back before any row counts as new
                    assert mine["restored"] == absent_before[entry_id]
                    assert mine["removed"] == 0
        history.extend(records)
        previous = current


@settings(max_examples=100, deadline=None)
@given(ROWS)
def test_an_unchanged_register_produces_no_records(rows) -> None:
    assert diff_registers(register(entries(rows)), register(entries(rows)), "2026-10-19") == []
