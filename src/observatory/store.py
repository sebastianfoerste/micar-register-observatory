"""Snapshot and changelog persistence under data/."""

from __future__ import annotations

import json
from pathlib import Path

from observatory.models import ChangeRecord, Snapshot


def load_latest(data_dir: Path) -> Snapshot | None:
    latest = data_dir / "latest.json"
    if not latest.exists():
        return None
    return Snapshot.model_validate_json(latest.read_text(encoding="utf-8"))


def save_snapshot(data_dir: Path, snapshot: Snapshot) -> None:
    payload = json.dumps(snapshot.model_dump(), ensure_ascii=False, indent=1) + "\n"
    (data_dir / "snapshots").mkdir(parents=True, exist_ok=True)
    (data_dir / "snapshots" / f"{snapshot.snapshot_date}.json").write_text(
        payload, encoding="utf-8"
    )
    (data_dir / "latest.json").write_text(payload, encoding="utf-8")


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
