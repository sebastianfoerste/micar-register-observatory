"""Download register CSVs. Transient failures are retried with backoff."""

from __future__ import annotations

import datetime
import http.client
import time
import urllib.error
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from observatory.config import USER_AGENT, RegisterSource

RETRYABLE_STATUS = {408, 425, 429, 500, 502, 503, 504}


@dataclass(frozen=True)
class Download:
    """One fetched export and what the server said about it."""

    body: bytes
    url: str
    last_modified: str = ""  # the HTTP Last-Modified header, verbatim
    retrieved_at: str = ""  # UTC, YYYY-MM-DDTHH:MM:SSZ


def utc_now() -> str:
    return datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _is_retryable(error: Exception) -> bool:
    if isinstance(error, urllib.error.HTTPError):
        return error.code in RETRYABLE_STATUS
    return isinstance(
        error, (urllib.error.URLError, TimeoutError, ConnectionError, http.client.HTTPException)
    )


def download_source(
    source: RegisterSource,
    timeout: int = 60,
    attempts: int = 4,
    backoff: float = 2.0,
    opener: Callable[..., Any] = urllib.request.urlopen,
    sleep: Callable[[float], None] = time.sleep,
) -> Download:
    """Fetch one source, retrying transient errors with exponential backoff."""
    request = urllib.request.Request(source.url, headers={"User-Agent": USER_AGENT})
    for attempt in range(1, attempts + 1):
        try:
            with opener(request, timeout=timeout) as response:
                body: bytes = response.read()
                headers = getattr(response, "headers", None)
                last_modified = headers.get("Last-Modified", "") if headers is not None else ""
                return Download(
                    body=body,
                    url=source.url,
                    last_modified=str(last_modified or ""),
                    retrieved_at=utc_now(),
                )
        except Exception as error:  # noqa: BLE001 — classified below
            if attempt == attempts or not _is_retryable(error):
                raise
            sleep(backoff * 2 ** (attempt - 1))
    raise AssertionError("unreachable")  # pragma: no cover


def fetch_source(
    source: RegisterSource,
    timeout: int = 60,
    attempts: int = 4,
    backoff: float = 2.0,
    opener: Callable[..., Any] = urllib.request.urlopen,
    sleep: Callable[[float], None] = time.sleep,
) -> bytes:
    """The body of `download_source`."""
    return download_source(source, timeout, attempts, backoff, opener, sleep).body
