"""Snapshot, changelog and raw export persistence under data/."""

from __future__ import annotations

import gzip
import hashlib
import json
from collections.abc import Mapping
from pathlib import Path

from observatory.fetch import Download
from observatory.models import ChangeRecord, Snapshot

RAW_MANIFEST = "manifest.json"


def load_latest(data_dir: Path) -> Snapshot | None:
    latest = data_dir / "latest.json"
    if not latest.exists():
        return None
    return Snapshot.model_validate_json(latest.read_text(encoding="utf-8"))


def snapshot_dates(data_dir: Path) -> list[str]:
    """Dates of the recorded snapshots under data/snapshots/, oldest first."""
    return sorted(path.stem for path in (data_dir / "snapshots").glob("*.json"))


def quarantine_dates(data_dir: Path) -> list[str]:
    """Dates of the exports set aside under data/quarantine/, oldest first."""
    return sorted(path.stem for path in (data_dir / "quarantine").glob("*.json"))


def load_snapshot(data_dir: Path, snapshot_date: str) -> Snapshot:
    path = data_dir / "snapshots" / f"{snapshot_date}.json"
    return Snapshot.model_validate_json(path.read_text(encoding="utf-8"))


def _snapshot_json(snapshot: Snapshot) -> str:
    return json.dumps(snapshot.model_dump(), ensure_ascii=False, indent=1) + "\n"


def save_snapshot(data_dir: Path, snapshot: Snapshot) -> None:
    payload = _snapshot_json(snapshot)
    (data_dir / "snapshots").mkdir(parents=True, exist_ok=True)
    (data_dir / "snapshots" / f"{snapshot.snapshot_date}.json").write_text(
        payload, encoding="utf-8"
    )
    (data_dir / "latest.json").write_text(payload, encoding="utf-8")


def save_quarantine(data_dir: Path, snapshot: Snapshot) -> Path:
    """Keep an export that was set aside, in the format of data/snapshots/."""
    path = data_dir / "quarantine" / f"{snapshot.snapshot_date}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_snapshot_json(snapshot), encoding="utf-8")
    return path


def latest_quarantine(data_dir: Path, after: str) -> Snapshot | None:
    """The newest quarantined export dated after `after` (YYYY-MM-DD), if any."""
    paths = sorted(
        path for path in (data_dir / "quarantine").glob("*.json") if path.stem > after
    )
    if not paths:
        return None
    return Snapshot.model_validate_json(paths[-1].read_text(encoding="utf-8"))


def save_raw(
    data_dir: Path, snapshot_date: str, downloads: Mapping[str, Download], recorded_as: str
) -> Path:
    """Keep the downloaded bytes, gzipped, with a manifest under data/raw/<date>/.

    `recorded_as` says where the export went: "snapshot" or "quarantine". The
    manifest's SHA-256 is of the bytes as downloaded, before compression. `url`
    is where the bytes were downloaded from; `archived_at` is set when that was
    an archived copy (the Wayback Machine's capture time) and empty otherwise.
    """
    folder = data_dir / "raw" / snapshot_date
    folder.mkdir(parents=True, exist_ok=True)
    files = []
    for slug, download in downloads.items():
        name = f"{slug}.csv.gz"
        (folder / name).write_bytes(gzip.compress(download.body, mtime=0))
        files.append(
            {
                "slug": slug,
                "file": name,
                "url": download.url,
                "sha256": hashlib.sha256(download.body).hexdigest(),
                "bytes": len(download.body),
                "last_modified": download.last_modified,
                "retrieved_at": download.retrieved_at,
                "archived_at": download.archived_at,
            }
        )
    manifest = {"snapshot_date": snapshot_date, "recorded_as": recorded_as, "files": files}
    (folder / RAW_MANIFEST).write_text(json.dumps(manifest, indent=1) + "\n", encoding="utf-8")
    return folder


def load_raw(data_dir: Path, snapshot_date: str, slug: str) -> bytes:
    """The archived bytes of one export, checked against the manifest's SHA-256."""
    folder = data_dir / "raw" / snapshot_date
    manifest = json.loads((folder / RAW_MANIFEST).read_text(encoding="utf-8"))
    record = next((item for item in manifest["files"] if item["slug"] == slug), None)
    if record is None:
        raise KeyError(f"no {slug} export archived for {snapshot_date}")
    body = gzip.decompress((folder / record["file"]).read_bytes())
    if hashlib.sha256(body).hexdigest() != record["sha256"]:
        raise ValueError(f"{folder / record['file']} does not match its manifest SHA-256")
    return body


def append_changelog(data_dir: Path, changes: list[ChangeRecord]) -> None:
    if not changes:
        return
    with (data_dir / "changelog.jsonl").open("a", encoding="utf-8") as handle:
        for change in changes:
            handle.write(json.dumps(change.model_dump(), ensure_ascii=False) + "\n")


def read_changelog(data_dir: Path) -> list[ChangeRecord]:
    path = data_dir / "changelog.jsonl"
    if not path.exists():
        return []
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            records.append(ChangeRecord.model_validate_json(line))
    return records
