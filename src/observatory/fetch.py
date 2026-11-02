"""Download register CSVs. Transient failures are retried with backoff; when
ESMA's CDN refuses the request for good, the newest recent copy in the Wayback
Machine is used instead, and the download says so."""

from __future__ import annotations

import datetime
import gzip
import http.client
import json
import re
import time
import urllib.error
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from observatory.config import (
    ARCHIVE_ATTEMPTS,
    ARCHIVE_AVAILABILITY_URL,
    ARCHIVE_BACKOFF,
    ARCHIVE_FILE_URL,
    MAX_ARCHIVE_AGE_DAYS,
    USER_AGENT,
    RegisterSource,
)

# 403 is included: ESMA serves the exports through a CDN whose edge has refused
# GitHub-hosted runners outright (every source, 2026-10-26, as a CloudFront
# "Request blocked" page); such a block is sometimes lifted within seconds, so a
# few more attempts cost nothing. When it is not, the archive fallback follows.
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
_ARCHIVE_TIMESTAMP = "%Y%m%d%H%M%S"


@dataclass(frozen=True)
class Download:
    """One fetched export and what the server said about it."""

    body: bytes
    url: str  # where the bytes were downloaded from: ESMA, or an archived copy
    last_modified: str = ""  # the HTTP Last-Modified header, verbatim
    retrieved_at: str = ""  # UTC, YYYY-MM-DDTHH:MM:SSZ
    # When an archive captured the copy (its Memento-Datetime header, verbatim);
    # empty for a download from ESMA itself.
    archived_at: str = ""


class ArchiveError(Exception):
    """The Wayback Machine has no usable copy of the export."""


class SourceUnavailable(Exception):
    """ESMA refused or failed for every attempt and no archived copy could stand in."""


def utc_now() -> str:
    return datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _now() -> datetime.datetime:
    return datetime.datetime.now(datetime.UTC)


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


def _get(
    url: str,
    timeout: int,
    attempts: int,
    backoff: float,
    opener: Callable[..., Any],
    sleep: Callable[[float], None],
) -> tuple[bytes, Any]:
    """GET `url`, retrying transient errors with exponential backoff.

    Returns the body and the response headers. A gzip-encoded body is decoded:
    the Wayback Machine serves an export exactly as ESMA sent it to the crawler,
    compressed when the crawler asked for compression.
    """
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(1, attempts + 1):
        try:
            with opener(request, timeout=timeout) as response:
                body: bytes = response.read()
                headers = getattr(response, "headers", None)
                encoding = headers.get("Content-Encoding", "") if headers is not None else ""
                if str(encoding or "").lower() == "gzip":
                    try:
                        body = gzip.decompress(body)
                    except (OSError, EOFError):
                        pass  # not gzip after all; the parser judges the bytes
                return body, headers
        except Exception as error:  # noqa: BLE001 — classified below
            if attempt == attempts or not _is_retryable(error):
                if isinstance(error, urllib.error.HTTPError):
                    raise describe_http_error(error) from error
                raise
            sleep(retry_delay(error, attempt, backoff))
    raise AssertionError("unreachable")  # pragma: no cover


def _value(headers: Any, name: str) -> str:
    value = headers.get(name, "") if headers is not None else ""
    return str(value or "")


def download_source(
    source: RegisterSource,
    timeout: int = 60,
    attempts: int = 4,
    backoff: float = 2.0,
    opener: Callable[..., Any] = urllib.request.urlopen,
    sleep: Callable[[float], None] = time.sleep,
) -> Download:
    """Fetch one source from ESMA, retrying transient errors with backoff."""
    body, headers = _get(source.url, timeout, attempts, backoff, opener, sleep)
    return Download(
        body=body,
        url=source.url,
        last_modified=_value(headers, "Last-Modified"),
        retrieved_at=utc_now(),
    )


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


def archive_timestamp(payload: bytes, url: str) -> str:
    """The capture timestamp (YYYYMMDDhhmmss, UTC) in a Wayback availability answer."""
    try:
        closest = json.loads(payload)["archived_snapshots"].get("closest") or {}
    except (ValueError, KeyError, TypeError, AttributeError) as error:
        raise ArchiveError(f"unreadable availability answer for {url}") from error
    timestamp = str(closest.get("timestamp") or "")
    if not closest.get("available") or str(closest.get("status")) != "200" or not timestamp:
        raise ArchiveError(f"no archived copy of {url}")
    try:
        datetime.datetime.strptime(timestamp, _ARCHIVE_TIMESTAMP)
    except ValueError as error:
        raise ArchiveError(f"unreadable capture timestamp {timestamp!r} for {url}") from error
    return timestamp


def download_archived(
    source: RegisterSource,
    timeout: int = 60,
    attempts: int = 4,
    backoff: float = 2.0,
    opener: Callable[..., Any] = urllib.request.urlopen,
    sleep: Callable[[float], None] = time.sleep,
    now: Callable[[], datetime.datetime] = _now,
) -> Download:
    """The newest copy of the export in the Wayback Machine, when it was captured
    within the last MAX_ARCHIVE_AGE_DAYS days; ArchiveError otherwise.

    The download's `url` is the archive URL, `last_modified` the Last-Modified
    header ESMA sent the crawler and `archived_at` the capture time.
    """
    lookup = ARCHIVE_AVAILABILITY_URL.format(url=source.url)
    answer, _ = _get(lookup, timeout, attempts, backoff, opener, sleep)
    timestamp = archive_timestamp(answer, source.url)
    captured = datetime.datetime.strptime(timestamp, _ARCHIVE_TIMESTAMP).replace(
        tzinfo=datetime.UTC
    )
    if now() - captured > datetime.timedelta(days=MAX_ARCHIVE_AGE_DAYS):
        raise ArchiveError(
            f"the newest archived copy of {source.url} was captured on "
            f"{captured:%Y-%m-%d}, more than {MAX_ARCHIVE_AGE_DAYS} days ago"
        )
    url = ARCHIVE_FILE_URL.format(timestamp=timestamp, url=source.url)
    body, headers = _get(url, timeout, attempts, backoff, opener, sleep)
    return Download(
        body=body,
        url=url,
        last_modified=_value(headers, "X-Archive-Orig-Last-Modified"),
        retrieved_at=utc_now(),
        archived_at=_value(headers, "Memento-Datetime")
        or captured.strftime("%a, %d %b %Y %H:%M:%S GMT"),
    )


def fetch_export(
    source: RegisterSource,
    archive: bool = True,
    timeout: int = 60,
    attempts: int = 4,
    backoff: float = 2.0,
    opener: Callable[..., Any] = urllib.request.urlopen,
    sleep: Callable[[float], None] = time.sleep,
    now: Callable[[], datetime.datetime] = _now,
) -> Download:
    """The export from ESMA; when ESMA refuses or fails for every attempt and
    `archive` is set, the newest recent copy in the Wayback Machine.

    A permanent answer from ESMA (404: the file moved) is raised as it is: an
    archived copy would hide a source change. When both fail, the error names
    what ESMA said and why no archived copy could stand in. The archive is
    retried more slowly and fewer times (ARCHIVE_BACKOFF, ARCHIVE_ATTEMPTS):
    archive.org rate-limits with 429, and the whole refresh has a time budget.
    """
    try:
        return download_source(source, timeout, attempts, backoff, opener, sleep)
    except Exception as error:  # noqa: BLE001 — classified below
        if not archive or not _is_retryable(error):
            raise
        slower = max(backoff, ARCHIVE_BACKOFF)
        fewer = min(attempts, ARCHIVE_ATTEMPTS)
        try:
            return download_archived(source, timeout, fewer, slower, opener, sleep, now)
        except Exception as fallback:  # noqa: BLE001 — reported with the first error
            raise SourceUnavailable(f"{error}; Wayback Machine: {fallback}") from error
