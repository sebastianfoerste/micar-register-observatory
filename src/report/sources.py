"""Data source: the observatory's committed snapshot in this repository.

The report never touches ESMA directly. It reads data/latest.json, which the
weekly refresh commits, so every edition is reproducible from a commit.
"""

from __future__ import annotations

import json
from pathlib import Path

LATEST_SNAPSHOT = Path("data/latest.json")


def load_latest(path: Path = LATEST_SNAPSHOT) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))
