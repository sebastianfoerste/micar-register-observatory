from pathlib import Path

from observatory.config import SOURCES
from observatory.models import RegisterEntry, RegisterSnapshot, Snapshot
from observatory.normalize import normalize_csv
from observatory.render import render_dashboard

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
