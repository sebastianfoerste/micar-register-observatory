from pathlib import Path

import pytest

from observatory.config import SOURCES
from observatory.models import RegisterEntry
from observatory.normalize import (
    SchemaError,
    column_drift,
    iso_date,
    normalize_csv,
    notes_modification,
    parse_countries,
    parse_register,
    parse_services,
)

FIXTURES = Path(__file__).parent / "fixtures"


def source(slug: str):
    return next(s for s in SOURCES if s.slug == slug)


def test_normalize_other_wp_handles_bom_and_fields():
    entries = normalize_csv(source("other-wp"), (FIXTURES / "other-wp.csv").read_bytes())
    assert len(entries) == 2
    first = entries[0]
    assert first.authority.startswith("Austrian")
    assert first.member_state == "AT"
    assert first.entity_name == "SKYGATE Network GmbH"
    assert first.lei == "984500BBFE52FE449926"
    assert first.format_class == "unspecified"
    assert entries[1].format_class == "xhtml/html"


def test_entry_id_is_stable_across_runs():
    raw = (FIXTURES / "other-wp.csv").read_bytes()
    first = normalize_csv(source("other-wp"), raw)
    second = normalize_csv(source("other-wp"), raw)
    assert [e.entry_id for e in first] == [e.entry_id for e in second]


def test_empty_register_yields_no_entries():
    entries = normalize_csv(source("art-wp"), (FIXTURES / "art-wp.csv").read_bytes())
    assert entries == []


def test_entity_register_has_na_format():
    entries = normalize_csv(source("casps"), (FIXTURES / "casps.csv").read_bytes())
    assert len(entries) == 4
    assert {e.format_class for e in entries} == {"n/a"}


def test_missing_required_columns_raise() -> None:
    import pytest

    from observatory.config import SOURCES
    from observatory.normalize import SchemaError, normalize_csv

    with pytest.raises(SchemaError, match="missing columns"):
        normalize_csv(SOURCES[0], b"foo,bar\n1,2\n")


def test_min_rows_floor_enforced_only_when_requested() -> None:
    import pytest

    from observatory.config import SOURCES
    from observatory.normalize import SchemaError, normalize_csv

    source = next(s for s in SOURCES if s.slug == "ncasp")
    raw = b"ae_competentAuthority,ae_homeMemberState,ae_lei_name,ae_lei\nA,DE,X Ltd,L1\n"
    assert len(normalize_csv(source, raw)) == 1
    with pytest.raises(SchemaError, match="below the minimum"):
        normalize_csv(source, raw, enforce_min_rows=True)


# --- v2: every column kept, typed fields, row keys -----------------------------


def test_v1_identity_is_unchanged_by_the_v2_fields() -> None:
    entries = normalize_csv(source("other-wp"), (FIXTURES / "other-wp.csv").read_bytes())
    # Same register, LEI and URL as in the frozen 2026-07-07 snapshot.
    assert entries[0].entry_id == "dbecc8085986d0c9"


def test_repeated_header_lines_are_not_entries() -> None:
    raw = (FIXTURES / "other-wp.csv").read_bytes()
    assert raw.count(b"ae_competentAuthority") == 2
    entries = normalize_csv(source("other-wp"), raw)
    assert [e.entity_name for e in entries] == ["SKYGATE Network GmbH", "Example Issuer GmbH"]
    assert not any(e.is_header_echo() for e in entries)


def test_casp_rows_keep_every_column_and_get_typed_fields() -> None:
    parsed = parse_register(source("casps"), (FIXTURES / "casps.csv").read_bytes())
    assert parsed.columns == list(source("casps").columns)
    first, second, withdrawn, no_lei = parsed.entries
    assert set(first.fields) == set(source("casps").columns)
    assert first.fields["ac_serviceCode_cou"] == "FR|BE|DE"
    assert first.services == ["a", "c"]
    assert first.service_countries == ["BE", "DE", "FR"]
    assert first.authorisation_date == "2026-01-15"
    assert first.last_update == "15/01/2026"  # the CASP register's own ac_lastupdate
    assert first.commercial_name == "CASP One" and first.website == "https://caspone.example"
    assert second.services == ["e"] and second.comments == "Second authorisation"
    assert withdrawn.withdrawal_date == "2026-04-30"
    assert no_lei.services == ["d", "j"]
    assert no_lei.service_countries == ["IE", "MT", "NL"]


def test_casp_firms_are_counted_once_and_rows_told_apart() -> None:
    entries = normalize_csv(source("casps"), (FIXTURES / "casps.csv").read_bytes())
    assert len(entries) == 4
    assert len({e.entity_key() for e in entries}) == 3
    first, second = entries[0], entries[1]
    assert first.entry_id == second.entry_id  # same LEI, no white paper URL
    assert first.row_key != second.row_key  # different authorisation dates


def test_ncasp_typed_fields_and_row_keys() -> None:
    first, second = normalize_csv(source("ncasp"), (FIXTURES / "ncasp.csv").read_bytes())
    assert first.decision_date == "2026-02-12"
    assert first.reason == "Synthetic reason text for a fixture"
    assert first.last_update == "18/02/2026"  # the register's own ae_lastupdate
    assert first.entry_id == second.entry_id and first.row_key != second.row_key


def test_whitepaper_typed_fields() -> None:
    raw = (
        "﻿ae_competentAuthority,ae_homeMemberState,ae_lei_name,ae_lei,ae_lei_cou_code,"
        "ae_lei_name_casp,ae_lei_casp,ae_offerCode_cou,ae_DTI_FFG,ae_DTI,wp_url,wp_comments,"
        "wp_lastupdate\n"
        "NCA,DE,Token Issuer GmbH,529900TOKENISSUER001,DE,Not applicable,Not applicable,"
        '"LU, AT, BE",abc123xyz,"Q1 | q2",https://t.example/wp.pdf,Modification,01/02/2026\n'
    ).encode()
    [entry] = normalize_csv(source("other-wp"), raw)
    assert entry.offer_countries == ["AT", "BE", "LU"]
    assert entry.dti_ffg == "ABC123XYZ" and entry.dti == ["Q1", "Q2"]
    assert entry.casp_name == "" and entry.casp_lei == ""
    assert entry.comments == "Modification"
    assert entry.modification_noted
    assert entry.fields["ae_lei_casp"] == "Not applicable"  # verbatim stays available


def test_modification_markers_are_read_from_the_start_of_the_comment() -> None:
    for comment in (
        "wp update", "Modification", "Modified", "Art.12 Mod", "Art. 12 mod, notified 8/12/25",
        "Modified content on 04-09-2025", "modification v.2 as of 9 July 2026",
        "Updated WP July 2026", "  MODIFICATIONS ",
    ):
        assert notes_modification(comment), comment
    for comment in (
        "", "URL UPDATE", "UPDATE", "Note that the publication date for the modified white "
        "paper is 24.02.2026 at which point this record will be updated with the link",
        "Unmodified", "modifiedly",
    ):
        assert not notes_modification(comment), comment


def test_only_white_paper_rows_carry_the_modification_flag() -> None:
    edited = (FIXTURES / "casps.csv").read_text(encoding="utf-8").replace(
        "Second authorisation", "Modification"
    )
    entries = normalize_csv(source("casps"), edited.encode("utf-8"))
    assert entries[1].comments == "Modification"
    assert not any(entry.modification_noted for entry in entries)


def test_services_are_read_from_the_text_not_the_letter() -> None:
    assert parse_services("c. exchange of crypto-assets for other crypto-assets") == ["d"]
    assert parse_services(
        "a. providing custody and administration of crypto-assets on behalf of clients "
        "e. execution of orders for crypto-assets on behalf of clients"
    ) == ["a", "e"]
    assert parse_services(
        "exchange between crypto assets and fiat currency/ exchange between crypto assets/"
    ) == ["c", "d"]
    assert parse_services("") == []


def test_countries_dates_and_placeholders() -> None:
    assert parse_countries("AT | BE |\n CY") == ["AT", "BE", "CY"]
    assert parse_countries("9845003D98SCC2851458 | de") == ["DE"]
    assert iso_date("01/04/2025") == "2025-04-01"
    assert iso_date("1.4.2025") == "2025-04-01"
    assert iso_date("n/a") == "" and iso_date("31/02/2026") == ""


def test_row_with_more_values_than_the_header_is_rejected() -> None:
    raw = b"ae_competentAuthority,ae_homeMemberState,ae_lei_name,ae_lei\nA,DE,X Ltd,L1,surplus\n"
    with pytest.raises(SchemaError, match="more values than the header"):
        normalize_csv(source("ncasp"), raw)


def test_column_drift_names_added_and_dropped_columns() -> None:
    columns = [c for c in source("ncasp").columns if c != "ae_reason"] + ["ae_new"]
    assert column_drift(source("ncasp"), columns) == (["ae_new"], ["ae_reason"])


def test_old_snapshot_entries_still_load() -> None:
    entry = RegisterEntry.model_validate(
        {
            "entry_id": "x", "register_slug": "casps", "authority": "", "member_state": "",
            "entity_name": "A", "lei": "", "wp_url": "", "last_update": "",
            "format_class": "n/a", "row_hash": "h",
        }
    )
    assert entry.fields == {} and entry.services == [] and entry.row_key == ""
