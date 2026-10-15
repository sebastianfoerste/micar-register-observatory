import json
from pathlib import Path

from report.analyze import analyze

FIXTURE = json.loads(
    (Path(__file__).parent / "fixtures" / "snapshot.json").read_text(encoding="utf-8")
)


def test_totals_match_frozen_snapshot():
    m = analyze(FIXTURE)
    # Frozen 2026-07-07 observatory snapshot.
    assert m["snapshot_date"] == "2026-07-07"
    assert m["total_whitepapers"] == 953  # 912 + 41 + 0
    assert m["register_totals"]["casps"] == 283
    assert m["register_totals"]["ncasp"] == 162


def test_machine_readable_and_landing_counts():
    m = analyze(FIXTURE)
    assert m["machine_readable"] == 114
    assert m["landing_page"] == 584
    assert m["pdf"] == 254
    # 114 of 953 is ~12%.
    assert 11.5 <= m["machine_readable_pct"] <= 12.5
    assert 60.5 <= m["landing_page_pct"] <= 62.0


def test_member_states_sorted_ireland_first():
    m = analyze(FIXTURE)
    assert m["member_states"][0][0] == "IE"
    assert m["member_states"][0][1] == 340


def test_percentages_are_internally_consistent():
    m = analyze(FIXTURE)
    total = m["total_whitepapers"]
    assert sum(m["format_counts"].values()) == total


def test_entity_totals_count_firms_as_well_as_rows():
    totals = analyze(FIXTURE)["entity_totals"]
    assert totals["casps"] == {"rows": 283, "entities": 279, "with_withdrawal_date": None}
    assert totals["other-wp"] == {"rows": 912, "entities": 561}
    assert totals["art-wp"] == {"rows": 0, "entities": 0}
