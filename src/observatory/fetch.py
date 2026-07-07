"""Download register CSVs. Per-source failures are isolated, not fatal."""

from __future__ import annotations

import urllib.request

from observatory.config import USER_AGENT, RegisterSource


def fetch_source(source: RegisterSource, timeout: int = 60) -> bytes:
    request = urllib.request.Request(source.url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()
