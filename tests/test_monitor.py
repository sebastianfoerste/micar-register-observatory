"""The source monitor checks the bytes a refresh used and never stops it.

The classification rules were fixed on 10 November 2026 under the owner's
delegation (plans/github-profile-continuation-2026-11-10.md, § 3 item 3) and
these tests were written from them before classify_source_change:

- ISSUE: a moved final URL; a configured export no longer linked on ESMA's MiCA
  page; a header change; a charset other than UTF-8; a row drop greater than
  max(5, 10 % of the previous count); a fall to 0.
- LOG: last_modified, last_update_line, content_length, any growth, and a
  refusal by ESMA (the bytes came from the archive).
"""

import json
import shutil
import urllib.error
from pathlib import Path

import pytest

import observatory.__main__ as cli
from observatory.__main__ import cmd_refresh
from observatory.config import MICA_PAGE_URL, SOURCES
from observatory.fetch import Download, SourceUnavailable
from observatory.monitor import (
    FINGERPRINT_MARKER,
    PAGE_SOURCE_ID,
    STATE_FILE,
    Action,
    ClassifiedDifference,
    Outcome,
    SourceObservation,
    canonical_url,
    classify_source_change,
    csv_shape,
    effective_charset,
    load_state,
    next_state,
    observe_csv,
    observe_page,
    original_url,
    run_monitor,
)
from test_pipeline import FIXTURES, args_for, seed_readme

ROOT = Path(__file__).resolve().parents[1]
ESMA_PAGES = ROOT / "sources" / "esma"
CASPS = next(source for source in SOURCES if source.slug == "casps")
ARCHIVE_URL = f"https://web.archive.org/web/20261114082357id_/{CASPS.url}"
REFUSAL = (
    "HTTP Error 403: Forbidden (server=CloudFront; "
    'body="Request blocked. We can\'t connect to the server for this app or website at this time.")'
)


def esma(body: bytes, **fields: str) -> Download:
    values = {"final_url": CASPS.url, "content_type": "text/csv", **fields}
    return Download(
        body=body, url=CASPS.url, last_modified="Wed, 11 Nov 2026 13:55:41 GMT", **values
    )


def archived(body: bytes) -> Download:
    return Download(
        body=body,
        url=ARCHIVE_URL,
        last_modified="Wed, 11 Nov 2026 13:55:41 GMT",
        archived_at="Sat, 14 Nov 2026 08:23:57 GMT",
        final_url=ARCHIVE_URL,
        content_type="text/csv",
        esma_refusal=REFUSAL,
    )


CASPS_BODY = (FIXTURES / "casps.csv").read_bytes()


def observation(**fields: object) -> SourceObservation:
    base: dict[str, object] = {
        "source_id": "casps",
        "kind": "csv",
        "url": CASPS.url,
        "observed": True,
        "via": "esma",
        "final_url": CASPS.url,
        "content_type": "text/csv",
        "charset": "utf-8",
        "last_modified": "Wed, 11 Nov 2026 13:55:41 GMT",
        "content_length": 1000,
        "csv_header": CASPS.columns,
        "row_count": 100,
    }
    base.update(fields)
    return SourceObservation.model_validate(base)


def decide(**changes: object) -> list[tuple[str, Action]]:
    return [
        (item.difference.attribute, item.action)
        for item in classify_source_change(observation(), observation(**changes))
    ]


# --- What a download shows ----------------------------------------------------


def test_an_esma_download_is_observed_as_esma_served_it():
    seen = observe_csv(CASPS, esma(CASPS_BODY))
    assert seen.observed and seen.via == "esma" and seen.esma_refusal == ""
    assert seen.final_url == CASPS.url
    assert seen.csv_header == CASPS.columns  # the trailing nameless column is left out
    assert seen.row_count == 4
    assert seen.charset == "utf-8"


def test_an_archived_copy_is_observed_with_its_provenance():
    seen = observe_csv(CASPS, archived(CASPS_BODY))
    assert seen.via == "archive"
    assert seen.fetched_from == ARCHIVE_URL
    assert seen.archived_at == "Sat, 14 Nov 2026 08:23:57 GMT"
    assert seen.esma_refusal == REFUSAL
    # The ESMA URL the copy belongs to, not the archive URL: no false "moved".
    assert seen.final_url == CASPS.url
    assert seen.row_count == 4 and seen.csv_header == CASPS.columns


def test_urls_compare_by_resource_not_by_spelling():
    assert original_url(ARCHIVE_URL) == CASPS.url
    assert original_url(
        "https://web.archive.org/web/20261114082357id_/https:/www.esma.europa.eu/a.csv"
    ) == ("https://www.esma.europa.eu/a.csv")
    assert (
        canonical_url("http://WWW.ESMA.EUROPA.EU:443/sites/a.csv")
        == "https://www.esma.europa.eu/sites/a.csv"
    )
    assert original_url(CASPS.url) == CASPS.url


def test_repeated_header_lines_and_blank_rows_are_not_rows():
    body = b"a,b,\nx,1,\n\n,,\na,b,\ny,2,\n"
    assert csv_shape(body) == (("a", "b"), 2)
    assert csv_shape(b"") == (None, None)


def test_the_charset_is_utf8_only_when_declared_so_or_undeclared_and_decodable():
    assert effective_charset("text/csv", "é".encode()) == "utf-8"
    assert effective_charset("text/csv; charset=UTF-8", b"\xef\xbb\xbfa") == "utf-8"
    assert effective_charset('text/csv; charset="windows-1252"', b"a") == "windows-1252"
    assert effective_charset("text/csv", "é".encode("latin-1")) == "not utf-8"
    assert effective_charset("text/csv; charset=utf-8", "é".encode("latin-1")) == "not utf-8"


# --- Hard checks on the bytes used --------------------------------------------


def run(fetched: dict, previous=(), page="not fetched in a unit test", **kwargs):
    return run_monitor([CASPS], fetched, page, list(previous), checked_on="2026-11-16", **kwargs)


def failed_checks(report) -> set[str]:
    return {check.check for check in report.checks if not check.passed}


def test_a_good_esma_download_passes_every_check():
    report = run({"casps": esma(CASPS_BODY)}, enforce_floors=False)
    assert failed_checks(report) == set()


def test_the_hard_checks_run_on_the_archived_bytes_and_a_refusal_is_no_finding():
    report = run({"casps": archived(CASPS_BODY)}, enforce_floors=False)
    assert failed_checks(report) == set()
    assert report.issue_items() == []
    assert report.outcome is Outcome.UNKNOWN  # only because the page was not fetched here


def test_a_changed_header_fails_its_check_on_the_bytes_used():
    body = CASPS_BODY.replace(b"ac_lastupdate,ac_legal_basis,", b"ac_lastupdate,")
    report = run({"casps": archived(body)}, enforce_floors=False)
    assert failed_checks(report) == {"csv_header"}
    detail = next(c.detail for c in report.checks if c.check == "csv_header")
    assert detail == "missing ['ac_legal_basis']"
    assert report.outcome is Outcome.ISSUE


def test_content_type_charset_and_floor_are_hard_checks():
    report = run({"casps": esma(CASPS_BODY, content_type="text/html; charset=windows-1252")})
    assert failed_checks(report) == {"content_type", "charset", "row_count"}
    floor = next(c.detail for c in report.checks if c.check == "row_count")
    assert floor == f"4 rows (floor {CASPS.min_rows})"


def test_a_body_without_a_header_has_no_row_count():
    report = run({"casps": esma(b"\n\n")}, enforce_floors=False)
    assert {"csv_header", "row_count"} <= failed_checks(report)


def test_a_source_neither_esma_nor_the_archive_gave_is_unknown_not_a_pass():
    refused = SourceUnavailable(f"{REFUSAL}; Wayback Machine: no archived copy")
    before = observation()
    report = run({"casps": refused}, previous=[before], enforce_floors=False)
    assert report.checks == [] or all(c.source_id == PAGE_SOURCE_ID for c in report.checks)
    assert report.outcome is Outcome.UNKNOWN
    assert report.carried_over == [before]
    assert next_state(report).observations == [before]  # the baseline survives the week


def test_a_permanent_answer_from_esma_is_a_finding():
    gone = urllib.error.HTTPError(CASPS.url, 404, "Not Found", {}, None)  # type: ignore[arg-type]
    report = run({"casps": gone})
    assert failed_checks(report) == {"available"}
    assert report.outcome is Outcome.ISSUE


# --- The MiCA page, from the snapshots of 14 October and 14 November 2026 ------


def page_download(day: str, archived_copy: bool = False) -> Download:
    body = (ESMA_PAGES / day / "markets-crypto-assets-regulation-mica.html").read_bytes()
    if archived_copy:
        url = f"https://web.archive.org/web/20261113092535id_/{MICA_PAGE_URL}"
        return Download(
            body=body,
            url=url,
            final_url=url,
            content_type="text/html; charset=utf-8",
            archived_at="Fri, 13 Nov 2026 09:25:35 GMT",
            esma_refusal=REFUSAL,
        )
    return Download(
        body=body,
        url=MICA_PAGE_URL,
        final_url=MICA_PAGE_URL,
        content_type="text/html; charset=utf-8",
    )


def test_the_page_snapshot_links_every_export_and_names_its_update():
    seen = observe_page(MICA_PAGE_URL, page_download("2026-11-14", archived_copy=True))
    assert seen.last_update_line == "Last update: 11 November 2026"
    assert {canonical_url(source.url) for source in SOURCES} <= set(seen.linked_csv_urls or ())
    assert seen.final_url == MICA_PAGE_URL
    report = run_monitor(SOURCES, {}, page_download("2026-11-14"), [], checked_on="2026-11-16")
    page_checks = {c.check: c.passed for c in report.checks if c.source_id == PAGE_SOURCE_ID}
    assert page_checks == {
        "content_type": True,
        "charset": True,
        "last_update_line": True,
        "links_every_export": True,
    }


def test_the_page_change_between_the_snapshots_is_only_logged():
    before = observe_page(MICA_PAGE_URL, page_download("2026-10-14"))
    after = observe_page(MICA_PAGE_URL, page_download("2026-11-14"))
    decided = {item.difference.attribute: item for item in classify_source_change(before, after)}
    assert set(decided) == {"last_update_line", "linked_csv_urls", "content_length"}
    assert all(item.action is Action.LOG for item in decided.values())
    added = set(decided["linked_csv_urls"].difference.current or ()) - set(
        decided["linked_csv_urls"].difference.previous or ()
    )
    assert added == {
        "https://www.esma.europa.eu/sites/default/files/2026-10/"
        "ESMA65-955014868-17734_MIDAS_Feedback_File_Sample.csv"
    }


def test_a_page_that_stops_linking_an_export_is_an_issue():
    page = page_download("2026-11-14")
    unlinked = Download(
        body=page.body.replace(b'href="/sites/default/files/2024-12/CASPS.csv"', b'href="/moved"'),
        url=page.url,
        final_url=page.final_url,
        content_type=page.content_type,
    )
    before = observe_page(MICA_PAGE_URL, page)
    after = observe_page(MICA_PAGE_URL, unlinked)
    decided = {item.difference.attribute: item for item in classify_source_change(before, after)}
    assert decided["linked_csv_urls"].action is Action.ISSUE
    assert "CASPS.csv" in decided["linked_csv_urls"].reason
    report = run_monitor(SOURCES, {}, unlinked, [before], checked_on="2026-11-16")
    assert "links_every_export" in failed_checks(report)


# --- classify_source_change ----------------------------------------------------


def test_a_moved_final_url_is_an_issue():
    assert decide(final_url="https://www.esma.europa.eu/sites/default/files/2026-12/CASPS.csv") == [
        ("final_url", Action.ISSUE)
    ]


def test_a_final_url_seen_for_the_first_time_is_logged():
    first = classify_source_change(observation(final_url=None), observation())
    assert [(i.difference.attribute, i.action) for i in first] == [("final_url", Action.LOG)]


def test_a_header_change_is_an_issue():
    assert decide(csv_header=(*CASPS.columns, "ac_new")) == [("csv_header", Action.ISSUE)]
    assert decide(csv_header=None) == [("csv_header", Action.ISSUE)]


def test_a_charset_other_than_utf8_is_an_issue_and_utf8_again_is_logged():
    assert decide(charset="windows-1252") == [("charset", Action.ISSUE)]
    assert decide(charset="not utf-8") == [("charset", Action.ISSUE)]
    back = classify_source_change(observation(charset="windows-1252"), observation())
    assert [(i.difference.attribute, i.action) for i in back] == [("charset", Action.LOG)]


def test_a_configured_export_no_longer_linked_is_an_issue_other_link_changes_are_logged():
    configured = canonical_url(CASPS.url)
    other = "https://www.esma.europa.eu/sites/default/files/other.csv"
    before = observation(source_id=PAGE_SOURCE_ID, kind="page", linked_csv_urls=(configured, other))
    lost = before.model_copy(update={"linked_csv_urls": (other,)})
    gained = before.model_copy(update={"linked_csv_urls": (configured, other, other + "2")})
    dropped_other = before.model_copy(update={"linked_csv_urls": (configured,)})
    assert classify_source_change(before, lost)[0].action is Action.ISSUE
    assert classify_source_change(before, gained)[0].action is Action.LOG
    assert classify_source_change(before, dropped_other)[0].action is Action.LOG


@pytest.mark.parametrize(
    ("previous", "current", "action"),
    [
        # 10 % of 100 is 10, above 5: a drop of 10 is within, 11 is not.
        (100, 91, Action.LOG),
        (100, 90, Action.LOG),
        (100, 89, Action.ISSUE),
        # 10 % of 30 is 3, so the floor of 5 rows applies.
        (30, 26, Action.LOG),
        (30, 25, Action.LOG),
        (30, 24, Action.ISSUE),
        # 10 % of 50 is exactly 5.
        (50, 45, Action.LOG),
        (50, 44, Action.ISSUE),
        # The live Title II export: 10 % of 1071 is 107.1.
        (1071, 964, Action.LOG),
        (1071, 963, Action.ISSUE),
        # A fall to 0 is an issue however small the register was.
        (3, 0, Action.ISSUE),
        (1, 0, Action.ISSUE),
        # Growth is logged.
        (100, 101, Action.LOG),
        (0, 1, Action.LOG),
    ],
)
def test_row_drops_follow_max_5_or_10_percent(previous: int, current: int, action: Action):
    decided = classify_source_change(
        observation(row_count=previous), observation(row_count=current)
    )
    assert [(i.difference.attribute, i.action) for i in decided] == [("row_count", action)]


def test_an_unreadable_row_count_is_an_issue_and_a_first_count_is_logged():
    assert decide(row_count=None) == [("row_count", Action.ISSUE)]
    first = classify_source_change(observation(row_count=None), observation())
    assert [(i.difference.attribute, i.action) for i in first] == [("row_count", Action.LOG)]


def test_republishing_moves_are_logged():
    assert decide(
        last_modified="Wed, 18 Nov 2026 13:55:41 GMT",
        content_length=1234,
        content_type="text/csv; charset=utf-8",
    ) == [
        ("content_type", Action.LOG),
        ("last_modified", Action.LOG),
        ("content_length", Action.LOG),
    ]
    page = observation(
        source_id=PAGE_SOURCE_ID, kind="page", last_update_line="Last update: 11 November 2026"
    )
    later = page.model_copy(update={"last_update_line": "Last update: 18 November 2026"})
    assert classify_source_change(page, later)[0].action is Action.LOG


def test_a_refusal_by_esma_is_a_logged_state():
    assert decide(via="archive") == [("via", Action.LOG)]
    back = classify_source_change(observation(via="archive"), observation())
    assert [(i.difference.attribute, i.action) for i in back] == [("via", Action.LOG)]


def test_no_difference_no_decision():
    assert classify_source_change(observation(), observation()) == []


def test_an_undecided_difference_is_an_issue_never_a_pass():
    before = observation()

    def raises(previous, current):
        raise RuntimeError("broken")

    def skips(previous, current):
        return []

    def doubles(previous, current):
        item = classify_source_change(previous, current)[0]
        return [item, item]

    for classify in (raises, skips, doubles):
        report = run_monitor(
            [CASPS],
            {"casps": esma(CASPS_BODY)},
            "x",
            [before],
            "2026-11-16",
            classify=classify,
            enforce_floors=False,
        )
        rows = [c for c in report.classified if c.difference.attribute == "row_count"]
        assert rows and all(c.action is Action.ISSUE for c in rows), classify.__name__
        assert rows[0].reason.startswith("not classified")
        assert report.outcome is Outcome.ISSUE


# --- Report and fingerprint ------------------------------------------------------


def test_the_same_findings_have_the_same_fingerprint():
    body = CASPS_BODY.replace(b"ac_lastupdate,ac_legal_basis,", b"ac_lastupdate,")
    one = run({"casps": esma(body)}, enforce_floors=False)
    two = run({"casps": archived(body)}, enforce_floors=False)
    good = run({"casps": esma(CASPS_BODY)}, enforce_floors=False)
    assert one.fingerprint() == two.fingerprint() != good.fingerprint()
    assert f"<!-- {FINGERPRINT_MARKER}: {one.fingerprint()} -->" in one.to_markdown()


def test_an_unobserved_source_changes_the_fingerprint_but_its_error_text_does_not():
    page = page_download("2026-11-14")
    good = run({"casps": esma(CASPS_BODY)}, page=page, enforce_floors=False)
    first = SourceUnavailable(f"{REFUSAL}; Wayback Machine: no archived copy")
    later = SourceUnavailable("HTTP Error 403: Forbidden (request id 2); Wayback Machine: timeout")
    one = run({"casps": first}, page=page, enforce_floors=False)
    two = run({"casps": later}, page=page, enforce_floors=False)
    assert good.outcome is Outcome.OK
    assert one.outcome is two.outcome is Outcome.UNKNOWN
    assert one.unobserved() == ["casps"]
    # An UNKNOWN week is reported once, and again only when another source goes unobserved.
    assert one.fingerprint() == two.fingerprint() != good.fingerprint()
    neither = run({"casps": first}, page=first, enforce_floors=False)
    assert neither.unobserved() == ["casps", PAGE_SOURCE_ID]
    assert neither.fingerprint() != one.fingerprint()


def test_the_report_says_where_the_bytes_came_from_and_quotes_register_text_inertly():
    body = CASPS_BODY.replace(b"ac_legal_basis", b"@someone|x`y")
    report = run({"casps": archived(body)}, enforce_floors=False)
    markdown = report.to_markdown()
    assert "Wayback Machine copy" in markdown
    assert "`Sat, 14 Nov 2026 08:23:57 GMT`" in markdown
    assert "refused: HTTP Error 403" in markdown
    # A code span: no mention, no link, no broken table.
    assert "`missing ['ac_legal_basis']; unexpected ['@someone\\|x'y']`" in markdown
    assert "Runbook" in markdown


# --- Inside the refresh ------------------------------------------------------------


def outputs(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    values: dict[str, str] = {}
    lines = iter(text.splitlines())
    for line in lines:
        if "<<" in line:
            name, delimiter = line.split("<<", 1)
            body = []
            for inner in lines:
                if inner == delimiter:
                    break
                body.append(inner)
            values[name] = "\n".join(body)
        else:
            name, _, value = line.partition("=")
            values[name] = value
    return values


def test_the_refresh_saves_the_observation_and_hands_the_report_to_the_workflow(tmp_path: Path):
    seed_readme(tmp_path)
    (tmp_path / "data").mkdir()
    environ = {"GITHUB_OUTPUT": str(tmp_path / "out"), "GITHUB_STEP_SUMMARY": str(tmp_path / "sum")}
    args = args_for(tmp_path, "2026-11-16", FIXTURES)
    args.monitor_report = str(tmp_path / "report.md")
    assert cmd_refresh(args, environ) == 0
    state = load_state(tmp_path / "data" / STATE_FILE)
    assert state is not None and state.checked_on == "2026-11-16"
    assert {o.source_id for o in state.observations} == {source.slug for source in SOURCES}
    handed = outputs(tmp_path / "out")
    # The page is not fetched in an offline run, so the outcome cannot be ok.
    assert handed["monitor"] == "unknown"
    assert len(handed["fingerprint"]) == 16
    assert handed["report"].startswith("## ESMA source monitor, 2026-11-16: UNKNOWN")
    written = (tmp_path / "report.md").read_text(encoding="utf-8")
    assert written.rstrip("\n") == handed["report"].rstrip("\n")
    assert "ESMA source monitor" in (tmp_path / "sum").read_text(encoding="utf-8")


def test_a_skipped_refresh_says_so_and_checks_nothing(tmp_path: Path):
    seed_readme(tmp_path)
    (tmp_path / "data").mkdir()
    assert cmd_refresh(args_for(tmp_path, "2026-11-16", FIXTURES)) == 0
    environ = {"GITHUB_OUTPUT": str(tmp_path / "out")}
    args = args_for(tmp_path, "2026-11-17", FIXTURES)
    args.monitor_report = str(tmp_path / "report.md")
    assert cmd_refresh(args, environ) == 0
    assert outputs(tmp_path / "out")["monitor"] == "skipped"


def test_a_finding_never_stops_the_refresh(tmp_path: Path):
    seed_readme(tmp_path)
    (tmp_path / "data").mkdir()
    edited = tmp_path / "edited"
    shutil.copytree(FIXTURES, edited)
    casps = edited / "casps.csv"
    casps.write_bytes(
        # A renamed column: the export still parses, and the header check finds it.
        casps.read_bytes().replace(b",ac_legal_basis,", b",ac_legal_basis_v2,")
    )
    environ = {"GITHUB_OUTPUT": str(tmp_path / "out")}
    args = args_for(tmp_path, "2026-11-16", edited)
    args.monitor_report = str(tmp_path / "report.md")
    assert cmd_refresh(args, environ) == 0
    assert outputs(tmp_path / "out")["monitor"] == "issue"
    assert (tmp_path / "data" / "snapshots" / "2026-11-16.json").exists()


def test_a_failed_refresh_reports_but_saves_no_observation(tmp_path: Path):
    seed_readme(tmp_path)
    (tmp_path / "data").mkdir()
    broken = tmp_path / "broken"
    shutil.copytree(FIXTURES, broken)
    (broken / "casps.csv").unlink()
    environ = {"GITHUB_OUTPUT": str(tmp_path / "out")}
    args = args_for(tmp_path, "2026-11-16", broken)
    args.monitor_report = str(tmp_path / "report.md")
    assert cmd_refresh(args, environ) == 1
    assert not (tmp_path / "data" / STATE_FILE).exists()
    assert outputs(tmp_path / "out")["monitor"] == "unknown"


def test_a_refresh_esma_refused_records_the_archive_and_logs_the_refusal(
    tmp_path: Path, monkeypatch, capsys
):
    seed_readme(tmp_path)
    (tmp_path / "data").mkdir()

    def fetch_export(source, archive=True):
        body = (FIXTURES / f"{source.slug}.csv").read_bytes()
        url = f"https://web.archive.org/web/20261116071326id_/{source.url}"
        return Download(
            body=body,
            url=url,
            final_url=url,
            content_type="text/csv",
            last_modified="Wed, 11 Nov 2026 13:55:41 GMT",
            archived_at="Mon, 16 Nov 2026 07:13:26 GMT",
            esma_refusal=REFUSAL,
        )

    monkeypatch.setattr(cli, "fetch_export", fetch_export)
    monkeypatch.setattr(
        cli, "fetch_page", lambda archive=True: page_download("2026-11-14", archived_copy=True)
    )
    monkeypatch.setattr(cli, "SOURCES", [s.model_copy(update={"min_rows": 0}) for s in SOURCES])
    monkeypatch.setattr("observatory.monitor.SOURCES", cli.SOURCES)
    environ = {"GITHUB_OUTPUT": str(tmp_path / "out")}
    args = args_for(tmp_path, "2026-11-16", FIXTURES)
    args.fixtures = None
    args.monitor_report = str(tmp_path / "report.md")
    assert cmd_refresh(args, environ) == 0
    handed = outputs(tmp_path / "out")
    # The floors are lifted for the fixtures, so every check passes on the archived bytes.
    assert handed["monitor"] == "ok", handed["report"]
    state = load_state(tmp_path / "data" / STATE_FILE)
    assert state is not None
    assert {o.via for o in state.observations} == {"archive"}
    assert all(o.esma_refusal == REFUSAL for o in state.observations)
    assert "::notice title=ESMA source monitor::ok: 0 finding(s)" in capsys.readouterr().out


def test_a_classified_difference_is_a_pydantic_model():
    item = classify_source_change(observation(), observation(row_count=50))[0]
    assert isinstance(item, ClassifiedDifference)
    assert json.loads(item.model_dump_json())["action"] == "issue"
