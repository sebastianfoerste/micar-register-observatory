"""Download register CSVs. Transient failures are retried with backoff."""

from __future__ import annotations

import http.client
import time
import urllib.error
import urllib.request
from collections.abc import Callable

from observatory.config import USER_AGENT, RegisterSource

RETRYABLE_STATUS = {408, 425, 429, 500, 502, 503, 504}


def _is_retryable(error: Exception) -> bool:
    if isinstance(error, urllib.error.HTTPError):
        return error.code in RETRYABLE_STATUS
    return isinstance(
        error, (urllib.error.URLError, TimeoutError, ConnectionError, http.client.HTTPException)
    )


def fetch_source(
    source: RegisterSource,
    timeout: int = 60,
    attempts: int = 4,
    backoff: float = 2.0,
    opener: Callable[..., object] = urllib.request.urlopen,
    sleep: Callable[[float], None] = time.sleep,
) -> bytes:
    """Fetch one source, retrying transient errors with exponential backoff."""
    request = urllib.request.Request(source.url, headers={"User-Agent": USER_AGENT})
    for attempt in range(1, attempts + 1):
        try:
            with opener(request, timeout=timeout) as response:  # type: ignore[operator]
                return response.read()
        except Exception as error:  # noqa: BLE001 — classified below
            if attempt == attempts or not _is_retryable(error):
                raise
            sleep(backoff * 2 ** (attempt - 1))
    raise AssertionError("unreachable")  # pragma: no cover
