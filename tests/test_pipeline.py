import argparse
import hashlib
import json
import shutil
from pathlib import Path

import observatory.__main__ as cli
from observatory.__main__ import cmd_refresh
from observatory.config import SOURCES
from observatory.fetch import Download, SourceUnavailable
from observatory.normalize import parse_register
from observatory.render import DASHBOARD_END, DASHBOARD_START
from observatory.store import load_latest, load_raw, read_changelog

FIXTURES = Path(__file__).parent / "fixtures"


def args_for(
    tmp_path: Path, date: str, fixtures: Path, accept_shrink: bool = False, force: bool = False
) -> argparse.Namespace:
    return argparse.Namespace(
        data_dir=str(tmp_path / "data"),
        readme=str(tmp_path / "README.md"),
        feed=str(tmp_path / "docs" / "feed.json"),
        atom=str(tmp_path / "docs" / "changes.atom"),
        digests=str(tmp_path / "digests"),
        date=date,
        fixtures=str(fixtures),
        accept_shrink=accept_shrink,
        force=force,
    )


def tree_digest(folder: Path) -> dict[str, str]:
    """Every file under `folder` with the SHA-256 of its bytes."""
    return {
        str(path.relative_to(folder)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(folder.rglob("*"))
        if path.is_file()
    }


def seed_readme(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text(
        f"# head\n\n{DASHBOARD_START}\n{DASHBOARD_END}\n\ntail\n", encoding="utf-8"
    )


def test_refresh_twice_renders_dashboard_and_changelog(tmp_path: Path) -> None:
    seed_readme(tmp_path)
    (tmp_path / "data").mkdir()

    assert cmd_refresh(args_for(tmp_path, "2026-07-07", FIXTURES)) == 0
    readme = (tmp_path / "README.md").read_text(encoding="utf-8")
    assert "Register snapshot: 2026-07-07" in readme
    assert "baseline established" in readme
    assert readme.startswith("# head")
    assert readme.rstrip().endswith("tail")

    # Second run against edited fixtures: one new row in other-wp.
    edited = tmp_path / "fixtures2"
    shutil.copytree(FIXTURES, edited)
    with (edited / "other-wp.csv").open("a", encoding="utf-8") as handle:
        handle.write(
            "Malta Financial Services Authority (MFSA),MT,New Issuer Ltd,"
            "529900NEWISSUER00001,MT,,,MT,,,https://new.example/wp.pdf,,01/07/2026\n"
        )

    assert cmd_refresh(args_for(tmp_path, "2026-07-14", edited)) == 0
    readme = (tmp_path / "README.md").read_text(encoding="utf-8")
    assert "Register snapshot: 2026-07-14" in readme
    assert "New Issuer Ltd" in readme

    changes = read_changelog(tmp_path / "data")
    assert any(c.change == "added" and c.entity_name == "New Issuer Ltd" for c in changes)
    assert (tmp_path / "docs" / "feed.json").exists()
    assert (tmp_path / "data" / "snapshots" / "2026-07-14.json").exists()


def test_refresh_fails_closed_when_a_source_fails(tmp_path: Path) -> None:
    seed_readme(tmp_path)
    (tmp_path / "data").mkdir()
    broken = tmp_path / "broken"
    shutil.copytree(FIXTURES, broken)
    (broken / "casps.csv").unlink()

    assert cmd_refresh(args_for(tmp_path, "2026-07-07", broken)) == 1
    assert not (tmp_path / "data" / "latest.json").exists()
    assert not (tmp_path / "data" / "snapshots").exists()
    assert not (tmp_path / "data" / "raw").exists()


def test_refresh_rejects_csv_with_wrong_schema(tmp_path: Path) -> None:
    seed_readme(tmp_path)
    (tmp_path / "data").mkdir()
    bad = tmp_path / "bad"
    shutil.copytree(FIXTURES, bad)
    (bad / "ncasp.csv").write_text("<html>maintenance</html>\n", encoding="utf-8")

    assert cmd_refresh(args_for(tmp_path, "2026-07-07", bad)) == 1
    assert not (tmp_path / "data" / "latest.json").exists()


def test_snapshot_records_the_export_header(tmp_path: Path) -> None:
    seed_readme(tmp_path)
    (tmp_path / "data").mkdir()
    assert cmd_refresh(args_for(tmp_path, "2026-07-07", FIXTURES)) == 0
    snapshot = load_latest(tmp_path / "data")
    assert snapshot is not None
    casps = snapshot.register("casps")
    assert casps is not None and casps.columns[-1] == "ac_lastupdate"
    assert casps.entries[0].fields["ac_lastupdate"] == "15/01/2026"


def test_refresh_archives_the_exports_it_recorded(tmp_path: Path) -> None:
    seed_readme(tmp_path)
    data = tmp_path / "data"
    data.mkdir()
    assert cmd_refresh(args_for(tmp_path, "2026-10-19", FIXTURES)) == 0
    manifest = json.loads((data / "raw" / "2026-10-19" / "manifest.json").read_text("utf-8"))
    assert manifest["snapshot_date"] == "2026-10-19"
    assert manifest["recorded_as"] == "snapshot"
    assert [item["slug"] for item in manifest["files"]] == [source.slug for source in SOURCES]
    snapshot = load_latest(data)
    assert snapshot is not None
    for source in SOURCES:
        body = load_raw(data, "2026-10-19", source.slug)
        assert body == (FIXTURES / f"{source.slug}.csv").read_bytes()
        register = snapshot.register(source.slug)
        assert register is not None
        assert register.source_sha256 == hashlib.sha256(body).hexdigest()
        # The archive is enough to parse the export again: same rows, same order.
        reparsed = parse_register(source, body).entries
        assert [entry.row_hash for entry in reparsed] == [e.row_hash for e in register.entries]


def test_column_drift_is_reported_without_failing(tmp_path: Path, capsys) -> None:
    seed_readme(tmp_path)
    (tmp_path / "data").mkdir()
    drifted = tmp_path / "drifted"
    shutil.copytree(FIXTURES, drifted)
    ncasp = drifted / "ncasp.csv"
    ncasp.write_text(
        ncasp.read_text(encoding="utf-8").replace("ae_reason", "ae_reason_v2", 1), encoding="utf-8"
    )

    assert cmd_refresh(args_for(tmp_path, "2026-07-07", drifted)) == 0
    out = capsys.readouterr().out
    assert "::warning title=ESMA source change::ncasp" in out
    assert "'ae_reason_v2'" in out and "dropped ['ae_reason']" in out


def test_a_row_must_be_absent_twice_before_it_is_removed(tmp_path: Path) -> None:
    seed_readme(tmp_path)
    (tmp_path / "data").mkdir()
    without = tmp_path / "without-skygate"
    shutil.copytree(FIXTURES, without)
    other = without / "other-wp.csv"
    other.write_text(
        "".join(
            line
            for line in other.read_text(encoding="utf-8").splitlines(keepends=True)
            if "SKYGATE" not in line
        ),
        encoding="utf-8",
    )

    weeks = [
        ("2026-07-07", FIXTURES),
        ("2026-07-14", without),
        ("2026-07-21", without),
        ("2026-07-28", FIXTURES),
    ]
    for date, fixtures in weeks:
        assert cmd_refresh(args_for(tmp_path, date, fixtures)) == 0
        if date == "2026-07-21":
            readme = (tmp_path / "README.md").read_text(encoding="utf-8")
            assert "| removed | other-wp | SKYGATE Network GmbH |" in readme
            assert "`removed`: not in two consecutive exports." in readme
    skygate = [
        (c.snapshot_date, c.change)
        for c in read_changelog(tmp_path / "data")
        if c.entity_name == "SKYGATE Network GmbH"
    ]
    assert skygate == [
        ("2026-07-14", "missing"),
        ("2026-07-21", "removed"),
        ("2026-07-28", "restored"),
    ]


def test_a_second_refresh_within_the_week_records_nothing(tmp_path: Path, capsys) -> None:
    seed_readme(tmp_path)
    (tmp_path / "data").mkdir()
    assert cmd_refresh(args_for(tmp_path, "2026-07-07", FIXTURES)) == 0
    edited = tmp_path / "fixtures2"
    shutil.copytree(FIXTURES, edited)
    (edited / "casps.csv").unlink()  # fetching this would fail: it must not be read
    before = tree_digest(tmp_path)

    # The fallback slot, a delayed run after midnight, or `make refresh` on a
    # Wednesday: within five days of the last export nothing is fetched.
    for date in ("2026-07-07", "2026-07-08", "2026-07-12"):
        assert cmd_refresh(args_for(tmp_path, date, edited)) == 0
        assert "::notice title=Export already fetched this week::" in capsys.readouterr().out
    assert tree_digest(tmp_path) == before
    assert not (tmp_path / "data" / "snapshots" / "2026-07-12.json").exists()

    # Six days on, the next weekly run proceeds (and here fails closed, as the
    # missing source demands).
    assert cmd_refresh(args_for(tmp_path, "2026-07-13", edited)) == 1
    assert cmd_refresh(args_for(tmp_path, "2026-07-13", FIXTURES)) == 0
    assert (tmp_path / "data" / "snapshots" / "2026-07-13.json").exists()


def test_force_fetches_within_the_week(tmp_path: Path) -> None:
    seed_readme(tmp_path)
    (tmp_path / "data").mkdir()
    assert cmd_refresh(args_for(tmp_path, "2026-07-07", FIXTURES)) == 0
    assert cmd_refresh(args_for(tmp_path, "2026-07-09", FIXTURES, force=True)) == 0
    assert (tmp_path / "data" / "snapshots" / "2026-07-09.json").exists()


def test_the_snapshot_and_the_manifest_say_where_each_export_came_from(tmp_path: Path) -> None:
    seed_readme(tmp_path)
    (tmp_path / "data").mkdir()
    assert cmd_refresh(args_for(tmp_path, "2026-10-19", FIXTURES)) == 0
    snapshot = load_latest(tmp_path / "data")
    assert snapshot is not None
    for register in snapshot.registers:
        assert register.fetched_from == f"fixture:{register.slug}.csv"
        assert register.archived_at == ""
    manifest = json.loads((tmp_path / "data" / "raw" / "2026-10-19" / "manifest.json").read_text())
    assert {item["archived_at"] for item in manifest["files"]} == {""}
    feed = json.loads((tmp_path / "docs" / "feed.json").read_text(encoding="utf-8"))
    assert feed["registers"][0]["fetched_from"] == "fixture:other-wp.csv"
    assert feed["registers"][0]["archived_at"] == ""


def fetch_from(fixtures: Path, archived: set[str], seen: list[bool]):
    """A stand-in for fetch_export: fixture bytes, from "ESMA" or from the archive."""

    def fetch_export(source, archive=True):
        seen.append(archive)
        body = (fixtures / f"{source.slug}.csv").read_bytes()
        if source.slug in archived:
            return Download(
                body=body,
                url=f"https://web.archive.org/web/20261102071326id_/{source.url}",
                last_modified="Fri, 30 Oct 2026 11:27:08 GMT",
                retrieved_at="2026-11-02T13:15:00Z",
                archived_at="Mon, 02 Nov 2026 07:13:26 GMT",
            )
        return Download(
            body=body,
            url=source.url,
            last_modified="Fri, 30 Oct 2026 11:27:08 GMT",
            retrieved_at="2026-11-02T13:15:00Z",
        )

    return fetch_export


def test_an_archived_export_is_recorded_with_its_provenance(tmp_path: Path, monkeypatch, capsys):
    seed_readme(tmp_path)
    (tmp_path / "data").mkdir()
    seen: list[bool] = []
    monkeypatch.setattr(cli, "fetch_export", fetch_from(FIXTURES, {"casps"}, seen))
    # The fixtures are far below the live row floors; the floors are not under test.
    monkeypatch.setattr(cli, "SOURCES", [s.model_copy(update={"min_rows": 0}) for s in SOURCES])
    args = args_for(tmp_path, "2026-11-02", FIXTURES)
    args.fixtures = None
    assert cmd_refresh(args) == 0
    assert seen == [True] * len(SOURCES)
    out = capsys.readouterr().out
    assert (
        "::warning title=Archived copy used::casps: ESMA refused the download; using the "
        "Wayback Machine's copy captured Mon, 02 Nov 2026 07:13:26 GMT "
        "(https://web.archive.org/web/20261102071326id_/" in out
    )
    assert out.count("Archived copy used") == 1

    snapshot = load_latest(tmp_path / "data")
    assert snapshot is not None
    casps = snapshot.register("casps")
    other = snapshot.register("other-wp")
    assert casps is not None and other is not None
    assert casps.source_url == SOURCES[3].url  # the ESMA export it is a copy of
    assert casps.fetched_from == f"https://web.archive.org/web/20261102071326id_/{casps.source_url}"
    assert casps.archived_at == "Mon, 02 Nov 2026 07:13:26 GMT"
    assert casps.source_last_modified == "Fri, 30 Oct 2026 11:27:08 GMT"
    assert other.fetched_from == other.source_url and other.archived_at == ""

    manifest = json.loads((tmp_path / "data" / "raw" / "2026-11-02" / "manifest.json").read_text())
    by_slug = {item["slug"]: item for item in manifest["files"]}
    assert by_slug["casps"]["url"] == casps.fetched_from
    assert by_slug["casps"]["archived_at"] == "Mon, 02 Nov 2026 07:13:26 GMT"
    assert by_slug["other-wp"]["url"] == other.source_url
    assert by_slug["other-wp"]["archived_at"] == ""
    archived = load_raw(tmp_path / "data", "2026-11-02", "casps")
    assert archived == (FIXTURES / "casps.csv").read_bytes()

    readme = (tmp_path / "README.md").read_text(encoding="utf-8")
    assert (
        "| 4 | 3 | ok (file modified 2026-10-30; archived copy from the Wayback Machine, "
        "captured 2026-11-02) |" in readme
    )
    assert readme.count("archived copy") == 1
    feed = json.loads((tmp_path / "docs" / "feed.json").read_text(encoding="utf-8"))
    by_slug = {item["slug"]: item for item in feed["registers"]}
    assert by_slug["casps"]["archived_at"] == "Mon, 02 Nov 2026 07:13:26 GMT"
    assert by_slug["casps"]["fetched_from"] == casps.fetched_from
    assert by_slug["other-wp"]["archived_at"] == ""


def test_no_archive_is_passed_down_to_the_fetch(tmp_path: Path, monkeypatch) -> None:
    seed_readme(tmp_path)
    (tmp_path / "data").mkdir()
    seen: list[bool] = []
    monkeypatch.setattr(cli, "fetch_export", fetch_from(FIXTURES, set(), seen))
    monkeypatch.setattr(cli, "SOURCES", [s.model_copy(update={"min_rows": 0}) for s in SOURCES])
    args = args_for(tmp_path, "2026-11-02", FIXTURES)
    args.fixtures = None
    args.no_archive = True
    assert cmd_refresh(args) == 0
    assert seen == [False] * len(SOURCES)


def test_the_refusal_and_the_archive_s_reason_both_reach_the_failure_line(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    """A real CloudFront 403 description is over 400 characters; the archive's
    reason follows it and must not be cut off: the workflow's failure text
    tells the maintainer to read it."""
    refusal = (
        "HTTP Error 403: Forbidden (server=CloudFront; "
        "via=1.1 31f2299ace8ebc27c9e8f771714b4bcc.cloudfront.net (CloudFront); "
        "x-cache=Error from cloudfront; "
        "x-amz-cf-id=isx7Z0kb3JKrNiM9Vw_zQM-ssLVCB6NEaQZAFUZSC4PlcjPA6wtSdg==; "
        'content-type=text/html; body="ERROR: The request could not be satisfied 403 ERROR '
        "The request could not be satisfied. Request blocked. We can't connect to the server "
        'for this app or website at this time. There might be too much traffic or a config")'
    )
    reason = (
        "Wayback Machine: the newest archived copy of "
        f"{SOURCES[0].url} was captured on 2026-10-29, more than 3 days ago"
    )

    def refused(source, archive=True):
        raise SourceUnavailable(f"{refusal}; {reason}")

    monkeypatch.setattr(cli, "fetch_export", refused)
    seed_readme(tmp_path)
    (tmp_path / "data").mkdir()
    args = args_for(tmp_path, "2026-11-02", FIXTURES)
    args.fixtures = None
    assert cmd_refresh(args) == 1
    err = capsys.readouterr().err
    assert "refresh failed: other-wp: " + refusal + "; " + reason in err
    assert not (tmp_path / "data" / "latest.json").exists()
