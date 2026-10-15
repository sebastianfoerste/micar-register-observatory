import csv
import io
from pathlib import Path

from observatory.config import SOURCES
from observatory.diff import diff_snapshots
from observatory.models import ChangeRecord, RegisterEntry, RegisterSnapshot, Snapshot
from observatory.normalize import normalize_csv


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


def test_added_changed_missing():
    old = snapshot("2026-07-07", [entry("A"), entry("B")])
    new = snapshot(
        "2026-07-14", [entry("A", row_hash="h2"), entry("C")]
    )
    changes = diff_snapshots(old, new)
    kinds = {(c.change, c.entity_name) for c in changes}
    assert ("changed", "A") in kinds
    assert ("added", "C") in kinds
    assert ("missing", "B") in kinds  # a first absence is not yet a removal
    assert len(changes) == 3


def test_failed_fetch_produces_no_changes():
    old = snapshot("2026-07-07", [entry("A")])
    new = snapshot("2026-07-14", [], fetched=False)
    assert diff_snapshots(old, new) == []


# --- multiset matching (several rows can share an entry_id) ---------------------


def test_non_unique_entry_ids_are_compared_as_a_multiset():
    old = snapshot("2026-07-07", [entry("A", row_hash="same"), entry("A", row_hash="old-variant")])
    new = snapshot("2026-07-14", [entry("A", row_hash="same"), entry("A", row_hash="new-variant")])
    changes = diff_snapshots(old, new)
    assert [(c.change, c.entity_name) for c in changes] == [("changed", "A")]
    assert changes[0].row_hash == "new-variant"


def test_a_vanished_duplicate_row_is_reported_not_lost():
    old = snapshot("2026-07-07", [entry("A"), entry("A")])
    new = snapshot("2026-07-14", [entry("A")])
    assert [c.change for c in diff_snapshots(old, new)] == ["missing"]


def test_an_extra_duplicate_row_is_added():
    old = snapshot("2026-07-07", [entry("A")])
    new = snapshot("2026-07-14", [entry("A"), entry("A", row_hash="h2")])
    changes = diff_snapshots(old, new)
    assert [(c.change, c.row_hash) for c in changes] == [("added", "h2")]


def test_row_key_pairs_rows_that_share_an_entry_id():
    x_old = entry("A", row_hash="x1").model_copy(update={"row_key": "kx", "last_update": "x"})
    y_old = entry("A", row_hash="y1").model_copy(update={"row_key": "ky", "last_update": "y"})
    # y changed; by content alone it now looks more like x, the row key says otherwise.
    y_new = entry("A", row_hash="y2").model_copy(update={"row_key": "ky", "last_update": "x"})
    x_new = entry("A", row_hash="x2").model_copy(update={"row_key": "kx", "last_update": "y"})
    changes = diff_snapshots(
        snapshot("2026-07-07", [x_old, y_old]), snapshot("2026-07-14", [y_new, x_new])
    )
    assert sorted((c.row_key, c.row_hash) for c in changes) == [("kx", "x2"), ("ky", "y2")]


def test_header_echo_entries_of_older_snapshots_are_ignored():
    echo = entry("ae_lei_name").model_copy(
        update={"authority": "ae_competentAuthority", "lei": "ae_lei"}
    )
    old = snapshot("2026-07-07", [entry("A"), echo])
    new = snapshot("2026-07-14", [entry("A")])
    assert diff_snapshots(old, new) == []


# --- field-level changes ---------------------------------------------------------

CASPS_SOURCE = next(s for s in SOURCES if s.slug == "casps")
CASPS_CSV = (Path(__file__).parent / "fixtures" / "casps.csv").read_text(encoding="utf-8")


def casp_snapshot(date: str, csv_text: str) -> Snapshot:
    return Snapshot(
        snapshot_date=date,
        registers=[
            RegisterSnapshot(
                slug="casps",
                title="t",
                kind="entity",
                source_url="https://esma.example/CASPS.csv",
                fetched=True,
                entries=normalize_csv(CASPS_SOURCE, csv_text.encode("utf-8")),
            )
        ],
    )


def edit_csv(text: str, edits: dict[tuple[int, str], str]) -> str:
    """Set cells of a fixture CSV by (row index, column name)."""
    reader = csv.reader(io.StringIO(text.lstrip("\ufeff")))
    header, *rows = list(reader)
    for (row, column), value in edits.items():
        rows[row][header.index(column)] = value
    out = io.StringIO()
    csv.writer(out, lineterminator="\n").writerows([header, *rows])
    return out.getvalue()


def test_changed_rows_carry_field_changes_and_subtypes():
    services = (
        "a. providing custody and administration of crypto-assets on behalf of clients | "
        "c. exchange of crypto-assets for funds | h. providing advice on crypto-assets"
    )
    edited = edit_csv(
        CASPS_CSV,
        {
            (0, "ac_serviceCode"): services,
            (0, "ac_serviceCode_cou"): "FR|BE|DE|IT",
            (0, "ac_lastupdate"): "20/10/2026",
            (3, "ac_authorisationEndDate"): "15/10/2026",
        },
    )
    changes = diff_snapshots(
        casp_snapshot("2026-10-12", CASPS_CSV), casp_snapshot("2026-10-19", edited)
    )
    by_name = {c.entity_name: c for c in changes}
    assert len(changes) == 2 and {c.change for c in changes} == {"changed"}

    extended = by_name["CASP One SAS"]
    assert extended.subtypes == ["services_added", "service_countries_added", "last_update_changed"]
    assert [f.field for f in extended.changed_fields] == [
        "ac_serviceCode", "ac_serviceCode_cou", "ac_lastupdate",
    ]
    assert extended.changed_fields[1].old == "FR|BE|DE"
    assert extended.changed_fields[1].new == "FR|BE|DE|IT"
    assert extended.detail == (
        "register row content changed (ac_serviceCode, ac_serviceCode_cou, ac_lastupdate)"
    )
    assert extended.lei == "529900CASPONE0000001" and extended.record_version == 2

    withdrawn = by_name["No LEI Trading Ltd"]
    assert withdrawn.subtypes == ["withdrawal_date_recorded"]
    assert [(f.field, f.old, f.new) for f in withdrawn.changed_fields] == [
        ("ac_authorisationEndDate", "", "15/10/2026"),
    ]


OTHER_SOURCE = next(s for s in SOURCES if s.slug == "other-wp")
OTHER_CSV = (Path(__file__).parent / "fixtures" / "other-wp.csv").read_text(encoding="utf-8")


def other_wp_snapshot(date: str, csv_text: str) -> Snapshot:
    return Snapshot(
        snapshot_date=date,
        registers=[
            RegisterSnapshot(
                slug="other-wp", title="t", kind="whitepaper",
                source_url="https://esma.example/OTHER.csv", fetched=True,
                entries=normalize_csv(OTHER_SOURCE, csv_text.encode("utf-8")),
            )
        ],
    )


def test_a_modification_noted_by_esma_is_labelled():
    noted = edit_csv(
        OTHER_CSV, {(2, "wp_comments"): "Art.12 Mod", (2, "wp_lastupdate"): "01/10/2026"}
    )
    new_row = (
        "NCA,DE,Example Issuer GmbH,529900EXAMPLELEI0001,DE,,,DE,,,"
        "https://example.com/wp-v2.xhtml,wp update,01/10/2026\n"
    )
    changes = diff_snapshots(
        other_wp_snapshot("2026-10-12", OTHER_CSV), other_wp_snapshot("2026-10-19", noted + new_row)
    )
    assert [(c.change, c.wp_url, c.subtypes) for c in changes] == [
        ("changed", "https://example.com/wp.xhtml",
         ["last_update_changed", "comments_changed", "modification_noted"]),
        ("added", "https://example.com/wp-v2.xhtml", ["modification_noted"]),
    ]


def test_an_unrelated_comment_change_is_not_a_modification():
    edited = edit_csv(OTHER_CSV, {(2, "wp_comments"): "URL UPDATE"})
    [record] = diff_snapshots(
        other_wp_snapshot("2026-10-12", OTHER_CSV), other_wp_snapshot("2026-10-19", edited)
    )
    assert record.subtypes == ["comments_changed"]


def test_a_v1_previous_snapshot_gives_changes_without_field_detail():
    current = casp_snapshot("2026-10-19", CASPS_CSV)
    v1_entries = [
        e.model_copy(update={"fields": {}, "row_key": "", "row_hash": e.row_hash + "x"})
        for e in current.registers[0].entries
    ]
    previous = current.model_copy(
        update={
            "snapshot_date": "2026-10-12",
            "registers": [current.registers[0].model_copy(update={"entries": v1_entries})],
        }
    )
    changes = diff_snapshots(previous, current)
    assert [c.change for c in changes] == ["changed"] * 4
    assert all(c.changed_fields == [] and c.subtypes == [] for c in changes)
    assert {c.detail for c in changes} == {"register row content changed"}


def test_unchanged_rows_produce_no_records_across_the_v1_to_v2_switch():
    current = casp_snapshot("2026-10-19", CASPS_CSV)
    v1_entries = [
        e.model_copy(update={"fields": {}, "row_key": "", "services": []})
        for e in current.registers[0].entries
    ]
    previous = Snapshot(
        snapshot_date="2026-10-12",
        registers=[current.registers[0].model_copy(update={"entries": v1_entries})],
    )
    assert diff_snapshots(previous, current) == []


# --- missing, removed, restored ------------------------------------------------


def run_weeks(*weeks: tuple[str, list[RegisterEntry]]) -> list:
    """Diff consecutive snapshots like the weekly refresh, threading the changelog."""
    history: list = []
    previous = None
    for date, rows in weeks:
        current = snapshot(date, rows)
        history.extend(diff_snapshots(previous, current, history))
        previous = current
    return history


def test_a_second_absence_in_a_row_confirms_the_removal():
    history = run_weeks(
        ("2026-07-07", [entry("A"), entry("B")]),
        ("2026-07-14", [entry("A")]),
        ("2026-07-21", [entry("A")]),
        ("2026-07-28", [entry("A")]),
    )
    rows = [(c.snapshot_date, c.change, c.entity_name) for c in history[1:]]
    assert rows == [("2026-07-14", "missing", "B"), ("2026-07-21", "removed", "B")]
    assert history[-1].detail == "not in two consecutive exports (missing since 2026-07-14)"
    assert history[-1].row_hash == "h1" and history[-1].record_version == 2


def test_a_row_back_after_one_missing_export_is_restored():
    history = run_weeks(
        ("2026-07-07", [entry("A"), entry("B")]),
        ("2026-07-14", [entry("A")]),
        ("2026-07-21", [entry("A"), entry("B")]),
    )
    rows = [(c.snapshot_date, c.change, c.entity_name) for c in history[1:]]
    assert rows == [("2026-07-14", "missing", "B"), ("2026-07-21", "restored", "B")]
    assert "missing on 2026-07-14" in history[-1].detail


def test_a_row_back_with_new_content_is_restored_too():
    history = run_weeks(
        ("2026-07-07", [entry("A"), entry("B")]),
        ("2026-07-14", [entry("A")]),
        ("2026-07-21", [entry("A"), entry("B", row_hash="h9")]),
    )
    assert [(c.change, c.row_hash) for c in history[2:]] == [("restored", "h9")]


def test_a_row_back_after_a_confirmed_removal_is_restored():
    history = run_weeks(
        ("2026-07-07", [entry("A"), entry("B")]),
        ("2026-07-14", [entry("A")]),
        ("2026-07-21", [entry("A")]),
        ("2026-08-04", [entry("A"), entry("B")]),
    )
    assert [c.change for c in history[1:]] == ["missing", "removed", "restored"]
    assert history[-1].detail == "listed again (last recorded as removed on 2026-07-21)"


def test_an_old_style_removal_followed_by_a_relisting_is_restored():
    # Changelog records written before version 2 used `removed` for a first absence.
    v1_removal = ChangeRecord(
        snapshot_date="2026-08-03", register_slug="other-wp", change="removed",
        entry_id=entry("B").entry_id, entity_name="B", member_state="DE",
    )
    previous = snapshot("2026-08-03", [entry("A")])
    current = snapshot("2026-08-10", [entry("A"), entry("B")])
    [record] = diff_snapshots(previous, current, [v1_removal])
    assert record.change == "restored"


def test_a_returning_row_is_not_mistaken_for_a_change_of_another_row():
    x = entry("A", row_hash="x").model_copy(update={"last_update": "x"})
    y = entry("A", row_hash="y").model_copy(update={"last_update": "y"})
    history = run_weeks(
        ("2026-07-07", [x, y]),
        ("2026-07-14", [x]),  # y goes missing
        ("2026-07-21", [y]),  # y is back exactly as it was, x is gone
    )
    assert [(c.snapshot_date, c.change, c.row_hash) for c in history[1:]] == [
        ("2026-07-14", "missing", "y"),
        ("2026-07-21", "restored", "y"),
        ("2026-07-21", "missing", "x"),
    ]


def test_only_the_previous_exports_missing_rows_are_confirmed():
    stale = ChangeRecord(
        snapshot_date="2026-07-07", register_slug="other-wp", change="missing",
        entry_id=entry("B").entry_id, entity_name="B", member_state="DE",
    )
    previous = snapshot("2026-07-21", [entry("A")])
    current = snapshot("2026-07-28", [entry("A")])
    assert diff_snapshots(previous, current, [stale]) == []


def test_only_as_many_rows_are_restored_as_went_missing():
    history = run_weeks(
        ("2026-07-07", [entry("A"), entry("B")]),
        ("2026-07-14", [entry("A")]),
        ("2026-07-21", [entry("A"), entry("B"), entry("B")]),
    )
    assert [c.change for c in history[2:]] == ["restored", "added"]


def test_a_removed_row_is_restored_while_other_rows_of_its_entry_stay_listed():
    x = entry("A", row_hash="x").model_copy(update={"last_update": "x"})
    y = entry("A", row_hash="y").model_copy(update={"last_update": "y"})
    history = run_weeks(
        ("2026-07-07", [x, y]),
        ("2026-07-14", [x]),
        ("2026-07-21", [x]),
        ("2026-07-28", [x]),
        ("2026-08-04", [x, y]),
    )
    assert [(c.snapshot_date, c.change) for c in history[1:]] == [
        ("2026-07-14", "missing"),
        ("2026-07-21", "removed"),
        ("2026-08-04", "restored"),
    ]


def test_an_old_style_relisting_is_not_restored_twice():
    # Version 1 recorded a relisting as `added`; that row is back already.
    v1 = [
        ChangeRecord(
            snapshot_date=date, register_slug="other-wp", change=change,
            entry_id=entry("B").entry_id, entity_name="B", member_state="DE",
        )
        for date, change in (("2026-08-03", "removed"), ("2026-08-10", "added"))
    ]
    previous = snapshot("2026-08-10", [entry("A"), entry("B")])
    current = snapshot("2026-08-17", [entry("A"), entry("B"), entry("B", row_hash="h2")])
    [record] = diff_snapshots(previous, current, v1)
    assert record.change == "added"
