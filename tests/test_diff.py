from observatory.diff import diff_snapshots, removal_churn
from observatory.models import ChangeRecord, RegisterEntry, RegisterSnapshot, Snapshot
from observatory.render import render_dashboard


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


def record(date: str, change: str, name: str) -> ChangeRecord:
    return ChangeRecord(
        snapshot_date=date,
        register_slug="other-wp",
        change=change,
        entry_id=entry(name).entry_id,
        entity_name=name,
        member_state="DE",
    )


def test_removal_churn_separates_temporary_drops_from_net_removals():
    changes = [
        record("2026-07-07", "baseline", "-"),
        record("2026-07-14", "added", "E"),
        # A drops out and comes back: a temporary drop.
        record("2026-07-21", "removed", "A"),
        record("2026-07-28", "added", "A"),
        # B drops out for good: a net removal.
        record("2026-07-21", "removed", "B"),
        # C comes back once, then drops out again: one drop, one net removal.
        record("2026-07-21", "removed", "C"),
        record("2026-07-28", "added", "C"),
        record("2026-08-04", "removed", "C"),
        # E was added before it was removed; that addition is not a relisting.
        record("2026-07-21", "removed", "E"),
    ]
    [churn] = removal_churn(changes)
    assert churn.register_slug == "other-wp"
    assert churn.removed == 5
    assert churn.relisted == 2
    assert churn.net == 3


def test_removal_churn_counts_entries_listed_in_the_current_snapshot():
    # D came back after a re-baseline, so no "added" record exists for it.
    changes = [record("2026-07-21", "removed", "D")]
    assert removal_churn(changes)[0].net == 1
    current = snapshot("2026-08-04", [entry("D")])
    [churn] = removal_churn(changes, current)
    assert churn.relisted == 1 and churn.net == 0


def test_dashboard_reports_net_removals_not_withdrawals():
    changes = [
        record("2026-07-07", "baseline", "-"),
        record("2026-07-21", "removed", "A"),
        record("2026-07-28", "added", "A"),
        record("2026-07-21", "removed", "B"),
    ]
    dashboard = render_dashboard(snapshot("2026-07-28", [entry("A")]), changes)
    assert "### Entries no longer listed" in dashboard
    assert "| Register | Removals | Listed again later | Net removals |" in dashboard
    assert "| other-wp | 2 | 1 | 1 |" in dashboard
    assert "withdrawals" not in dashboard


def test_dashboard_without_removals_says_so():
    changes = [record("2026-07-07", "baseline", "-")]
    dashboard = render_dashboard(snapshot("2026-07-07", [entry("A")]), changes)
    expected = "No register entry has dropped out of the export since 2026-07-07."
    assert expected in dashboard
