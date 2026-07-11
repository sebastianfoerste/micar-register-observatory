"""Content-level verification for public white-paper URLs."""

from __future__ import annotations

import hashlib
import io
import json
import urllib.error
import urllib.request
import zipfile
from datetime import UTC, datetime
from typing import Any

from observatory.config import USER_AGENT

DEFAULT_MAX_BYTES = 25 * 1024 * 1024


def detect_document_format(data: bytes, content_type: str = "") -> dict[str, Any]:
    """Detect the byte-level format without trusting a URL suffix."""
    content_type = content_type.partition(";")[0].strip().lower()
    sample = data[:2_000_000]
    stripped = sample.lstrip(b"\xef\xbb\xbf\x00\t\r\n ")
    lowered = stripped.lower()

    if stripped.startswith(b"%PDF-"):
        return _detection("pdf", False, "file_signature", content_type)

    if stripped.startswith(b"PK\x03\x04"):
        try:
            with zipfile.ZipFile(io.BytesIO(data)) as archive:
                names = set(archive.namelist())
            if "word/document.xml" in names:
                return _detection("docx", False, "zip_structure", content_type)
            return _detection("zip", False, "zip_structure", content_type)
        except (OSError, zipfile.BadZipFile):
            return _detection("unknown", False, "invalid_zip_signature", content_type)

    if lowered.startswith((b"{", b"[")):
        try:
            json.loads(data.decode("utf-8-sig"))
            return _detection("json", False, "json_parse", content_type)
        except (UnicodeDecodeError, json.JSONDecodeError):
            pass

    if lowered.startswith((b"<", b"<?xml")):
        ixbrl_markers = (
            b"<ix:" in lowered
            or b"xmlns:ix=" in lowered
            or b"inlineXBRL".lower() in lowered
            or b"www.xbrl.org/2013/inlinexbrl" in lowered
        )
        detected = "inline-xbrl-xhtml" if ixbrl_markers else "xhtml/html"
        basis = "inline_xbrl_marker" if ixbrl_markers else "markup_signature"
        return _detection(detected, ixbrl_markers, basis, content_type)

    return _detection("unknown", False, "no_known_signature", content_type)


def verify_url(
    url: str,
    *,
    timeout: float = 30,
    max_bytes: int = DEFAULT_MAX_BYTES,
) -> dict[str, Any]:
    """Fetch one public URL and return bounded, hash-based verification metadata."""
    requested_url = _normalise_url(url)
    verified_at = datetime.now(UTC).isoformat()
    request = urllib.request.Request(
        requested_url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/xhtml+xml,text/html,application/pdf,application/json,*/*;q=0.5",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read(max_bytes + 1)
            truncated = len(body) > max_bytes
            inspected = body[:max_bytes]
            content_type = response.headers.get("Content-Type", "")
            detection = detect_document_format(inspected, content_type)
            return {
                "content_verification_status": "too_large" if truncated else "verified",
                "verified_at": verified_at,
                "requested_url": requested_url,
                "final_url": response.geturl(),
                "http_status": getattr(response, "status", response.getcode()),
                "content_type": content_type,
                "declared_content_length": _as_int(response.headers.get("Content-Length")),
                "bytes_read": len(inspected),
                "content_truncated": truncated,
                "content_sha256": (
                    None if truncated else hashlib.sha256(inspected).hexdigest()
                ),
                **detection,
                "verification_error": (
                    "response exceeded max_bytes; no complete-content hash recorded"
                    if truncated
                    else ""
                ),
            }
    except urllib.error.HTTPError as error:
        return _error_result(requested_url, verified_at, f"http_{error.code}", str(error))
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        return _error_result(requested_url, verified_at, "fetch_error", str(error))


def _detection(
    detected_format: str,
    inline_xbrl: bool,
    detection_basis: str,
    content_type: str,
) -> dict[str, Any]:
    return {
        "verified_format": detected_format,
        "inline_xbrl": inline_xbrl,
        "detection_basis": detection_basis,
        "declared_content_type": content_type,
    }


def _error_result(
    requested_url: str,
    verified_at: str,
    status: str,
    message: str,
) -> dict[str, Any]:
    return {
        "content_verification_status": status,
        "verified_at": verified_at,
        "requested_url": requested_url,
        "final_url": "",
        "http_status": None,
        "content_type": "",
        "declared_content_length": None,
        "bytes_read": 0,
        "content_truncated": False,
        "content_sha256": None,
        "verified_format": "",
        "inline_xbrl": False,
        "detection_basis": "",
        "declared_content_type": "",
        "verification_error": message[:500],
    }


def _normalise_url(url: str) -> str:
    value = url.strip()
    if value and "://" not in value:
        return "https://" + value
    return value


def _as_int(value: str | None) -> int | None:
    if not value:
        return None
    try:
        return int(value)
    except ValueError:
        return None
