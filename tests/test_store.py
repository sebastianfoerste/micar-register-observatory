import json
from pathlib import Path

from observatory.models import ChangeRecord, Snapshot
from observatory.store import append_changelog, load_latest, read_changelog, save_snapshot


def change(entry_id: str) -> ChangeRecord:
    return ChangeRecord(
        snapshot_date="2026-07-07",
        register_slug="casps",
        change="added",
        entry_id=entry_id,
        entity_name="Ünï Ltd",
        member_state="DE",
    )


def test_load_latest_missing_returns_none(tmp_path: Path) -> None:
    assert load_latest(tmp_path) is None


def test_save_snapshot_writes_dated_and_latest_copies(tmp_path: Path) -> None:
    snapshot = Snapshot(snapshot_date="2026-07-07", registers=[])
    save_snapshot(tmp_path, snapshot)
    dated = tmp_path / "snapshots" / "2026-07-07.json"
    assert dated.read_text(encoding="utf-8") == (tmp_path / "latest.json").read_text(
        encoding="utf-8"
    )
    assert json.loads(dated.read_text(encoding="utf-8"))["snapshot_date"] == "2026-07-07"
    assert load_latest(tmp_path) == snapshot


def test_changelog_appends_and_roundtrips(tmp_path: Path) -> None:
    assert read_changelog(tmp_path) == []
    append_changelog(tmp_path, [])
    assert not (tmp_path / "changelog.jsonl").exists()
    append_changelog(tmp_path, [change("a")])
    append_changelog(tmp_path, [change("b")])
    assert [c.entry_id for c in read_changelog(tmp_path)] == ["a", "b"]
    assert read_changelog(tmp_path)[0].entity_name == "Ünï Ltd"
