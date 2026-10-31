"""Download register CSVs. Transient failures are retried with backoff."""

from __future__ import annotations

import datetime
import http.client
import re
import time
import urllib.error
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from observatory.config import USER_AGENT, RegisterSource

# 403 is included: ESMA serves the exports through a CDN whose bot control has
# refused a GitHub-hosted runner outright (every source, 2026-10-26); such a
# block is often lifted within seconds, so a few more attempts cost nothing.
RETRYABLE_STATUS = {403, 408, 425, 429, 500, 502, 503, 504}

# A Retry-After header (in seconds) replaces the backoff when it is this short.
MAX_RETRY_AFTER = 120.0

# Response headers worth keeping when a download fails: they say which server
# or CDN answered and, for a block, which rule did it.
DIAGNOSTIC_HEADERS = (
    "server",
    "via",
    "x-cache",
    "x-amz-cf-id",
    "x-amzn-waf-action",
    "x-amzn-requestid",
    "content-type",
    "retry-after",
)
BODY_EXCERPT = 160
_TAG = re.compile(r"<[^>]+>")


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


def _header(error: urllib.error.HTTPError, name: str) -> str:
    headers = getattr(error, "headers", None)
    value = headers.get(name) if headers is not None else None
    return " ".join(str(value).split()) if value else ""


def retry_delay(error: Exception, attempt: int, backoff: float) -> float:
    """The pause before the next attempt: the server's Retry-After when it is
    short enough, else exponential backoff."""
    if isinstance(error, urllib.error.HTTPError):
        try:
            seconds = float(_header(error, "retry-after"))
        except ValueError:
            seconds = 0.0
        if 0.0 < seconds <= MAX_RETRY_AFTER:
            return seconds
    return backoff * 2.0 ** (attempt - 1)


def describe_http_error(error: urllib.error.HTTPError) -> urllib.error.HTTPError:
    """The same error with what the server said in its message.

    `HTTP Error 403: Forbidden` alone does not say whether a CDN, a WAF rule or
    the origin refused the request; the diagnostic headers and a short excerpt
    of the body do. The result is still an HTTPError with the same code.
    """
    headers = {name: _header(error, name) for name in DIAGNOSTIC_HEADERS}
    parts = [f"{name}={value}" for name, value in headers.items() if value]
    try:
        raw = error.read(4096)
    except Exception:  # noqa: BLE001 — a body that cannot be read is no body
        raw = b""
    body = " ".join(_TAG.sub(" ", raw.decode("utf-8", errors="replace")).split())
    if body:
        parts.append(f'body="{body[:BODY_EXCERPT]}"')
    detail = f" ({'; '.join(parts)})" if parts else ""
    return urllib.error.HTTPError(
        error.url, error.code, f"{error.reason}{detail}", error.headers, None
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
                if isinstance(error, urllib.error.HTTPError):
                    raise describe_http_error(error) from error
                raise
            sleep(retry_delay(error, attempt, backoff))
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
