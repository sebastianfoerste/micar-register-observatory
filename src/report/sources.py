"""Data source: the observatory's committed snapshots in this repository.

The report never touches ESMA directly. It reads a dated snapshot under
data/snapshots/ or data/latest.json, which the weekly refresh commits, so every
edition is reproducible from a commit.
"""

from __future__ import annotations

import json
from pathlib import Path

DATA_DIR = Path("data")
LATEST_SNAPSHOT = DATA_DIR / "latest.json"


def dated_snapshot(snapshot_date: str, data_dir: Path = DATA_DIR) -> Path:
    """The path of the snapshot the weekly refresh recorded on that date."""
    return data_dir / "snapshots" / f"{snapshot_date}.json"


def load_latest(path: Path = LATEST_SNAPSHOT) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))
