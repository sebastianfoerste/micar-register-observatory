from observatory.models import ChangeRecord, RegisterEntry, RegisterSnapshot, Snapshot
from observatory.signals import build_signal_room


def entry(name: str, state: str = "DE", format_class: str = "pdf") -> RegisterEntry:
    return RegisterEntry(
        entry_id=RegisterEntry.make_entry_id("other-wp", "", name, f"https://{name}.example/wp"),
        register_slug="other-wp",
        authority="NCA",
        member_state=state,
        entity_name=name,
        lei="",
        wp_url=f"https://{name}.example/wp",
        last_update="01/07/2026",
        format_class=format_class,
        row_hash=name,
    )


def snapshot(entries, *, fetched=True):
    return Snapshot(
        snapshot_date="2026-07-28",
        registers=[
            RegisterSnapshot(
                slug="other-wp",
                title="Other white papers",
                kind="whitepaper",
                source_url="https://esma.example/OTHER.csv",
                fetched=fetched,
                entries=entries,
            )
        ],
    )


def test_signal_room_flags_source_failure_as_critical():
    room = build_signal_room(snapshot([], fetched=False), [])

    assert room["status"] == "REVIEW_REQUIRED"
    assert room["summary"]["source_failures"] == 1
    assert room["register_signals"][0]["severity"] == "critical"
    assert room["external_actions_allowed"] is False


def test_signal_room_flags_material_removal_rate_for_review():
    entries = [entry(f"issuer-{index}") for index in range(18)]
    changes = [
        ChangeRecord(
            snapshot_date="2026-07-28",
            register_slug="other-wp",
            change="removed",
            entry_id=f"removed-{index}",
            entity_name=f"Removed {index}",
            member_state="DE",
        )
        for index in range(2)
    ]

    room = build_signal_room(snapshot(entries), changes)

    assert room["status"] == "REVIEW_REQUIRED"
    assert room["register_signals"][0]["severity"] == "review"
    assert room["register_signals"][0]["removal_rate"] == 0.1


def test_signal_room_reports_concentration_and_format_candidates():
    entries = [
        entry("one", state="IE", format_class="xhtml/html"),
        entry("two", state="IE", format_class="pdf"),
        entry("three", state="DE", format_class="json"),
    ]

    room = build_signal_room(snapshot(entries), [])
    concentration, format_signal = room["market_structure_signals"]

    assert concentration["top_member_state"] == "IE"
    assert concentration["top_member_state_share"] == 0.6667
    assert format_signal["deep_lint_candidates"] == 2
    assert format_signal["deep_lint_candidate_share"] == 0.6667
    assert len(room["signal_room_sha256"]) == 64


def test_non_unique_entry_ids_are_review_signals():
    duplicated = entry("one")
    room = build_signal_room(snapshot([duplicated, duplicated.model_copy()]), [])

    assert room["register_signals"][0]["severity"] == "review"
    assert room["register_signals"][0]["duplicate_entry_ids"] == 1
    assert "multiset diff" in room["register_signals"][0]["reasons"][0]


def test_signal_room_is_deterministic():
    current = snapshot([entry("one")])

    assert build_signal_room(current, []) == build_signal_room(current, [])


def test_signal_room_adds_recent_movement_context():
    current = snapshot([entry("one")])
    changes = [
        ChangeRecord(
            snapshot_date="2026-07-21",
            register_slug="other-wp",
            change="added",
            entry_id="prior-added",
            entity_name="Prior",
            member_state="DE",
        )
    ]
    changes.extend(
        ChangeRecord(
            snapshot_date="2026-07-28",
            register_slug="other-wp",
            change="added",
            entry_id=f"current-{index}",
            entity_name=f"Current {index}",
            member_state="DE",
        )
        for index in range(3)
    )

    room = build_signal_room(
        current,
        changes,
        ["2026-07-14", "2026-07-21", "2026-07-28"],
    )
    movement = room["movement_context"]

    assert movement["periods_available"] == 3
    assert movement["history"][0]["movement_records"] == 0
    assert movement["current_movement_records"] == 3
    assert movement["previous_movement_records"] == 1
    assert movement["current_vs_previous_delta"] == 2
    assert movement["direction"] == "increased"
    assert "supervisory intensity" in movement["interpretation"]
