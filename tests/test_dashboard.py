from pathlib import Path

from observatory.config import SOURCES
from observatory.models import ChangeRecord, RegisterEntry, RegisterSnapshot, Snapshot
from observatory.normalize import normalize_csv
from observatory.render import http_date, render_dashboard

FIXTURES = Path(__file__).parent / "fixtures"


def register(slug: str, entries: list[RegisterEntry]) -> RegisterSnapshot:
    source = next(s for s in SOURCES if s.slug == slug)
    return RegisterSnapshot(
        slug=slug, title=source.title, kind=source.kind, source_url=source.url,
        fetched=True, entries=entries,
    )


def fixture_register(slug: str) -> RegisterSnapshot:
    source = next(s for s in SOURCES if s.slug == slug)
    return register(slug, normalize_csv(source, (FIXTURES / f"{slug}.csv").read_bytes()))


def test_totals_count_rows_and_entities_and_casp_withdrawal_dates():
    snapshot = Snapshot(
        snapshot_date="2026-10-19",
        registers=[fixture_register("other-wp"), fixture_register("casps")],
    )
    dashboard = render_dashboard(snapshot, [])
    assert "| Register | Rows | Entities | Source status |" in dashboard
    assert "Authorised crypto-asset service providers (CASPs)](" in dashboard
    assert "| 4 | 3 | ok |" in dashboard  # CASP One SAS has two authorisation rows
    assert (
        "CASP register: 3 firms in 4 rows, 1 of them with a withdrawal date "
        "(`ac_authorisationEndDate`)." in dashboard
    )


def test_header_lines_of_older_snapshots_are_not_counted():
    casps = fixture_register("casps")
    v1_rows = [entry.model_copy(update={"fields": {}}) for entry in casps.entries]
    echo = v1_rows[0].model_copy(
        update={
            "authority": "ae_competentAuthority", "entity_name": "ae_lei_name", "lei": "ae_lei",
            "member_state": "ae_homeMemberState",
        }
    )
    snapshot = Snapshot(
        snapshot_date="2026-10-12", registers=[register("casps", [*v1_rows, echo])]
    )
    dashboard = render_dashboard(snapshot, [])
    assert "| 4 | 3 | ok |" in dashboard
    # A v1 snapshot has no withdrawal dates to count, so none are claimed.
    assert "CASP register: 3 firms in 4 rows." in dashboard


def test_the_source_status_gives_the_date_esma_last_modified_the_file():
    casps = fixture_register("casps")
    casps.source_last_modified = "Tue, 07 Oct 2026 09:12:44 GMT"
    dashboard = render_dashboard(Snapshot(snapshot_date="2026-10-19", registers=[casps]), [])
    assert "| 4 | 3 | ok (file modified 2026-10-07) |" in dashboard
    assert http_date("") == "" and http_date("not a date") == ""


def _changes_table(changes: list[ChangeRecord]) -> list[str]:
    snapshot = Snapshot(snapshot_date="2026-10-19", registers=[fixture_register("other-wp")])
    dashboard = render_dashboard(snapshot, changes)
    start = dashboard.index("| Change | Register | Entity | MS | Link |")
    rows = dashboard[start:].splitlines()[2:]
    return [row for row in rows if row.startswith("| ")]


def _change(entity_name: str, member_state: str = "DE", wp_url: str = "") -> ChangeRecord:
    return ChangeRecord(
        snapshot_date="2026-10-19", register_slug="other-wp", change="added",
        entry_id="e1", entity_name=entity_name, member_state=member_state, wp_url=wp_url,
    )


def test_register_values_are_escaped_in_the_changes_table():
    rows = _changes_table(
        [
            _change("Issuer A|B Ltd", "C*", "https://example.invalid/wp]"),
            _change("Issuer Two\nLines", "DE", "https://a.invalid/one\nhttps://b.invalid/two"),
            _change("Issuer Three", "FR", "www.example.invalid/whitepaper"),
            _change("Issuer Four", "IT", "EMT_NO_WP"),
            _change("Issuer Five", "NL", "https://example.invalid/wp (final).pdf"),
        ]
    )
    assert len(rows) == 5
    for row in rows:
        assert row.count(" | ") == 4 and row.endswith(" |"), row
    pipe, two_urls, bare, code, parens = rows
    assert "| Issuer A\\|B Ltd | C\\* |" in pipe
    assert "[https://example.invalid/wp\\]](https://example.invalid/wp%5D)" in pipe
    assert "| Issuer Two Lines |" in two_urls  # a newline cannot split a table row
    assert "](" not in two_urls and "https://a.invalid/one https://b.invalid/two" in two_urls
    assert "[www.example.invalid/whitepaper](https://www.example.invalid/whitepaper)" in bare
    assert "EMT\\_NO\\_WP" in code and "](" not in code
    assert "](" not in parens and "wp (final).pdf" in parens


def test_long_labels_are_cut_before_they_are_escaped():
    url = "https://example.invalid/" + "a_" * 40
    (row,) = _changes_table([_change("Issuer Six", "LU", url)])
    label = row.split("[", 1)[1].split("](", 1)[0]
    assert label.endswith("...") and not label.endswith("\\...")
    assert "\\_" in label  # escaped, after the cut


def test_a_fetch_error_is_escaped_in_the_source_status():
    failed = RegisterSnapshot(
        slug="casps", title="CASPs", kind="entity", source_url="u", fetched=False,
        fetch_error="HTTP Error 403: Forbidden (server=x|y)",
    )
    dashboard = render_dashboard(Snapshot(snapshot_date="2026-10-19", registers=[failed]), [])
    assert "| fetch failed: HTTP Error 403: Forbidden (server=x\\|y) |" in dashboard


def test_member_states_are_escaped_in_the_member_state_table():
    entry = fixture_register("other-wp").entries[0].model_copy(update={"member_state": "D|E"})
    snapshot = Snapshot(
        snapshot_date="2026-10-19",
        registers=[register("other-wp", [entry])],
    )
    assert "| D\\|E | 1 |" in render_dashboard(snapshot, [])
