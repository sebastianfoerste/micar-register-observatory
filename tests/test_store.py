import gzip
import hashlib
import json
from pathlib import Path

import pytest

from observatory.fetch import Download
from observatory.models import ChangeRecord, Snapshot
from observatory.store import (
    append_changelog,
    load_latest,
    load_raw,
    load_snapshot,
    read_changelog,
    save_raw,
    save_snapshot,
    snapshot_dates,
)


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


def download(body: bytes) -> Download:
    return Download(
        body=body,
        url="https://esma.example/CASPS.csv",
        last_modified="Tue, 07 Oct 2026 09:12:44 GMT",
        retrieved_at="2026-10-19T06:17:03Z",
    )


def test_raw_exports_are_archived_gzipped_with_a_manifest(tmp_path: Path) -> None:
    body = "\ufeffae_lei_name,ae_lei\nÜnï Ltd,L1\n".encode()
    folder = save_raw(tmp_path, "2026-10-19", {"casps": download(body)}, recorded_as="snapshot")
    assert folder == tmp_path / "raw" / "2026-10-19"
    assert gzip.decompress((folder / "casps.csv.gz").read_bytes()) == body
    manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    assert manifest == {
        "snapshot_date": "2026-10-19",
        "recorded_as": "snapshot",
        "files": [
            {
                "slug": "casps",
                "file": "casps.csv.gz",
                "url": "https://esma.example/CASPS.csv",
                "sha256": hashlib.sha256(body).hexdigest(),
                "bytes": len(body),
                "last_modified": "Tue, 07 Oct 2026 09:12:44 GMT",
                "retrieved_at": "2026-10-19T06:17:03Z",
                "archived_at": "",
            }
        ],
    }
    assert load_raw(tmp_path, "2026-10-19", "casps") == body
    # The archive does not depend on when it was written.
    first = (folder / "casps.csv.gz").read_bytes()
    save_raw(tmp_path, "2026-10-19", {"casps": download(body)}, recorded_as="snapshot")
    assert (folder / "casps.csv.gz").read_bytes() == first


def test_load_raw_checks_the_manifest(tmp_path: Path) -> None:
    folder = save_raw(tmp_path, "2026-10-19", {"casps": download(b"a,b\n")}, "quarantine")
    with pytest.raises(KeyError, match="no ncasp export archived for 2026-10-19"):
        load_raw(tmp_path, "2026-10-19", "ncasp")
    (folder / "casps.csv.gz").write_bytes(gzip.compress(b"a,b\nedited\n"))
    with pytest.raises(ValueError, match="does not match its manifest SHA-256"):
        load_raw(tmp_path, "2026-10-19", "casps")


def test_snapshot_dates_and_load_snapshot(tmp_path: Path) -> None:
    assert snapshot_dates(tmp_path) == []
    for date in ("2026-07-14", "2026-07-07"):
        save_snapshot(tmp_path, Snapshot(snapshot_date=date, registers=[]))
    assert snapshot_dates(tmp_path) == ["2026-07-07", "2026-07-14"]
    assert load_snapshot(tmp_path, "2026-07-07").snapshot_date == "2026-07-07"
