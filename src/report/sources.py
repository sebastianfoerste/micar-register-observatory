"""Data source: the MiCAR Register Observatory's committed snapshot.

The report never touches ESMA directly. It reads the observatory's public,
version-controlled snapshot, so every edition is reproducible from a commit.
"""

from __future__ import annotations

import json
import urllib.request

OBSERVATORY_RAW = (
    "https://raw.githubusercontent.com/sebastianfoerste/micar-register-observatory/main"
)
LATEST_URL = f"{OBSERVATORY_RAW}/data/latest.json"

USER_AGENT = (
    "state-of-the-micar-register/0.1 "
    "(+https://github.com/sebastianfoerste/state-of-the-micar-register)"
)


def fetch_latest() -> dict:
    request = urllib.request.Request(LATEST_URL, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))
