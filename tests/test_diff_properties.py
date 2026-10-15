"""Property tests: the diff never loses or double-counts a register row."""

from collections import Counter

from hypothesis import given, settings
from hypothesis import strategies as st

from observatory.diff import diff_registers, match_rows
from observatory.models import RegisterEntry, RegisterSnapshot

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
    assert len(new) - len(old) == counts["added"] - counts["removed"]
    assert counts["changed"] + counts["removed"] <= len(old)
    assert counts["changed"] + counts["added"] <= len(new)


@settings(max_examples=100, deadline=None)
@given(ROWS)
def test_an_unchanged_register_produces_no_records(rows) -> None:
    assert diff_registers(register(entries(rows)), register(entries(rows)), "2026-10-19") == []
