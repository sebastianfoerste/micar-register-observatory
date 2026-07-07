from observatory.diff import diff_snapshots
from observatory.models import RegisterEntry, RegisterSnapshot, Snapshot


def entry(name: str, row_hash: str = "h1") -> RegisterEntry:
    return RegisterEntry(
        entry_id=RegisterEntry.make_entry_id("other-wp", "", name, "https://x.example"),
        register_slug="other-wp",
        authority="NCA",
        member_state="DE",
        entity_name=name,
        lei="",
        wp_url="https://x.example",
        last_update="01/01/2026",
        format_class="unspecified",
        row_hash=row_hash,
    )


def snapshot(date: str, entries: list[RegisterEntry], fetched: bool = True) -> Snapshot:
    return Snapshot(
        snapshot_date=date,
        registers=[
            RegisterSnapshot(
                slug="other-wp",
                title="t",
                kind="whitepaper",
                source_url="https://esma.example/OTHER.csv",
                fetched=fetched,
                entries=entries,
            )
        ],
    )


def test_first_run_records_baseline_not_added_rows():
    changes = diff_snapshots(None, snapshot("2026-07-07", [entry("A"), entry("B")]))
    assert len(changes) == 1
    assert changes[0].change == "baseline"
    assert "2 entries" in changes[0].detail


def test_added_changed_removed():
    old = snapshot("2026-07-07", [entry("A"), entry("B")])
    new = snapshot(
        "2026-07-14", [entry("A", row_hash="h2"), entry("C")]
    )
    changes = diff_snapshots(old, new)
    kinds = {(c.change, c.entity_name) for c in changes}
    assert ("changed", "A") in kinds
    assert ("added", "C") in kinds
    assert ("removed", "B") in kinds
    assert len(changes) == 3


def test_failed_fetch_produces_no_changes():
    old = snapshot("2026-07-07", [entry("A")])
    new = snapshot("2026-07-14", [], fetched=False)
    assert diff_snapshots(old, new) == []
