import importlib.util
import json
import shutil
from datetime import date
from pathlib import Path

from observatory.__main__ import cmd_refresh, cmd_render
from observatory.diff import Shrink, export_shrinks
from observatory.models import RegisterEntry, RegisterSnapshot, Snapshot
from observatory.render import DASHBOARD_END, DASHBOARD_START
from observatory.store import load_latest, read_changelog
from test_pipeline import FIXTURES, args_for, seed_readme

ROOT = Path(__file__).resolve().parents[1]
OTHER_HEADER = (FIXTURES / "other-wp.csv").read_text(encoding="utf-8").splitlines()[0]


def other_wp_rows(count: int) -> str:
    """A Title II export with `count` synthetic rows."""
    rows = [
        f"NCA,DE,Issuer {n} GmbH,LEI{n:017d},DE,,,DE,,,https://issuer{n}.example/wp.pdf,,"
        "01/01/2026"
        for n in range(count)
    ]
    return "\n".join([OTHER_HEADER, *rows]) + "\n"


def fixtures_with(tmp_path: Path, name: str, other_wp_count: int) -> Path:
    folder = tmp_path / name
    shutil.copytree(FIXTURES, folder)
    (folder / "other-wp.csv").write_text(other_wp_rows(other_wp_count), encoding="utf-8")
    return folder


def register(slug: str, rows: int) -> RegisterSnapshot:
    entries = [
        RegisterEntry(
            entry_id=f"e{n}", register_slug=slug, authority="NCA", member_state="DE",
            entity_name=f"E{n}", lei="", wp_url="", last_update="", format_class="none",
            row_hash=f"h{n}",
        )
        for n in range(rows)
    ]
    return RegisterSnapshot(
        slug=slug, title="t", kind="whitepaper", source_url="u", fetched=True, entries=entries
    )


def test_export_shrinks_needs_both_a_share_and_a_number_of_rows():
    def shrinks(before: int, after: int) -> list[Shrink]:
        return export_shrinks(
            Snapshot(snapshot_date="2026-07-27", registers=[register("other-wp", before)]),
            Snapshot(snapshot_date="2026-08-03", registers=[register("other-wp", after)]),
        )

    assert shrinks(941, 783) == [Shrink(slug="other-wp", before=941, after=783)]
    assert shrinks(941, 900) == []  # 4.4%: ordinary churn
    assert shrinks(50, 41) == []  # 18%, but only 9 rows
    assert shrinks(50, 30) == [Shrink(slug="other-wp", before=50, after=30)]
    assert shrinks(0, 0) == [] and shrinks(10, 20) == []
    assert "fell from 941 to 783 rows (-16.8%)" in shrinks(941, 783)[0].describe()


def test_a_sharp_drop_is_quarantined_and_history_is_left_alone(tmp_path: Path, capsys) -> None:
    seed_readme(tmp_path)
    (tmp_path / "data").mkdir()
    data = tmp_path / "data"
    assert cmd_refresh(args_for(tmp_path, "2026-07-27", fixtures_with(tmp_path, "a", 100))) == 0
    changelog_before = (data / "changelog.jsonl").read_text(encoding="utf-8")

    dip = fixtures_with(tmp_path, "dip", 80)
    assert cmd_refresh(args_for(tmp_path, "2026-08-03", dip)) == 0
    out = capsys.readouterr().out
    assert "::warning title=Register export quarantined::other-wp fell from 100 to 80" in out
    latest = load_latest(data)
    assert latest is not None and latest.snapshot_date == "2026-07-27"
    assert (data / "quarantine" / "2026-08-03.json").exists()
    assert not (data / "snapshots" / "2026-08-03.json").exists()
    manifest = json.loads((data / "raw" / "2026-08-03" / "manifest.json").read_text("utf-8"))
    assert manifest["recorded_as"] == "quarantine"
    assert (data / "changelog.jsonl").read_text(encoding="utf-8") == changelog_before
    readme = (tmp_path / "README.md").read_text(encoding="utf-8")
    assert "The export of 2026-08-03 was quarantined:** other-wp fell from 100 to 80" in readme
    feed = json.loads((tmp_path / "docs" / "feed.json").read_text(encoding="utf-8"))
    assert feed["snapshot_date"] == "2026-07-27"
    assert feed["quarantine"]["shrinks"] == [{"slug": "other-wp", "before": 100, "after": 80}]

    # Re-rendering keeps the note while the quarantine is pending.
    (tmp_path / "README.md").write_text(
        f"# head\n\n{DASHBOARD_START}\n{DASHBOARD_END}\n", encoding="utf-8"
    )
    assert cmd_render(args_for(tmp_path, "", dip)) == 0
    assert "2026-08-03 was quarantined" in (tmp_path / "README.md").read_text(encoding="utf-8")

    # The export recovers: recorded against the last good snapshot, no removals.
    assert cmd_refresh(args_for(tmp_path, "2026-08-10", fixtures_with(tmp_path, "b", 101))) == 0
    records = [c for c in read_changelog(data) if c.snapshot_date == "2026-08-10"]
    assert [(c.change, c.entity_name) for c in records] == [("added", "Issuer 100 GmbH")]
    assert "quarantined" not in (tmp_path / "README.md").read_text(encoding="utf-8")
    feed = json.loads((tmp_path / "docs" / "feed.json").read_text(encoding="utf-8"))
    assert feed["quarantine"] is None


def test_a_quarantine_rewrites_the_published_files_from_the_last_snapshot(
    tmp_path: Path,
) -> None:
    # The weekly workflow commits digests/ and docs/changes.atom: they must exist
    # even when the first refresh that writes them sets its export aside.
    seed_readme(tmp_path)
    (tmp_path / "data").mkdir()
    assert cmd_refresh(args_for(tmp_path, "2026-07-27", fixtures_with(tmp_path, "a", 100))) == 0
    shutil.rmtree(tmp_path / "digests")
    shutil.rmtree(tmp_path / "data" / "exports")
    (tmp_path / "docs" / "changes.atom").unlink()

    assert cmd_refresh(args_for(tmp_path, "2026-08-03", fixtures_with(tmp_path, "dip", 80))) == 0
    assert sorted(path.name for path in (tmp_path / "digests").iterdir()) == ["2026-07-27.md"]
    assert "<updated>2026-07-27T00:00:00Z</updated>" in (
        (tmp_path / "docs" / "changes.atom").read_text(encoding="utf-8")
    )
    whitepapers = (tmp_path / "data" / "exports" / "whitepapers.csv").read_text("utf-8")
    assert whitepapers.count("\n2026-07-27,other-wp,") == 100


def test_the_same_drop_in_the_next_export_is_recorded(tmp_path: Path, capsys) -> None:
    seed_readme(tmp_path)
    (tmp_path / "data").mkdir()
    assert cmd_refresh(args_for(tmp_path, "2026-07-27", fixtures_with(tmp_path, "a", 100))) == 0
    dip = fixtures_with(tmp_path, "dip", 80)
    assert cmd_refresh(args_for(tmp_path, "2026-08-03", dip)) == 0
    assert cmd_refresh(args_for(tmp_path, "2026-08-10", dip)) == 0
    assert "::notice title=Register drop confirmed::other-wp" in capsys.readouterr().out
    latest = load_latest(tmp_path / "data")
    assert latest is not None and latest.snapshot_date == "2026-08-10"
    records = [c for c in read_changelog(tmp_path / "data") if c.snapshot_date == "2026-08-10"]
    assert len(records) == 20 and {c.change for c in records} == {"missing"}


def test_a_maintainer_can_accept_a_drop_at_once(tmp_path: Path) -> None:
    seed_readme(tmp_path)
    (tmp_path / "data").mkdir()
    assert cmd_refresh(args_for(tmp_path, "2026-07-27", fixtures_with(tmp_path, "a", 100))) == 0
    dip = fixtures_with(tmp_path, "dip", 80)
    assert cmd_refresh(args_for(tmp_path, "2026-08-03", dip, accept_shrink=True)) == 0
    latest = load_latest(tmp_path / "data")
    assert latest is not None and latest.snapshot_date == "2026-08-03"
    assert not (tmp_path / "data" / "quarantine").exists()


def load_freshness_script():
    path = ROOT / "scripts" / "check_snapshot_freshness.py"
    spec = importlib.util.spec_from_file_location("check_snapshot_freshness", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_the_freshness_gate_reports_a_pending_quarantine(tmp_path: Path) -> None:
    seed_readme(tmp_path)
    (tmp_path / "data").mkdir()
    assert cmd_refresh(args_for(tmp_path, "2026-07-27", fixtures_with(tmp_path, "a", 100))) == 0
    script = load_freshness_script()
    latest = tmp_path / "data" / "latest.json"
    assert script.pending_quarantines(latest) == []

    assert cmd_refresh(args_for(tmp_path, "2026-08-03", fixtures_with(tmp_path, "d", 80))) == 0
    as_of = date(2026, 8, 3)
    assert script.validate(latest, as_of=as_of, max_age_days=14) == []  # not a failure
    quarantined = tmp_path / "data" / "quarantine" / "2026-08-03.json"
    assert script.pending_quarantines(latest) == [quarantined]
