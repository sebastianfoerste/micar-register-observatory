"""Content-level verification for public white-paper URLs."""

from __future__ import annotations

import hashlib
import http.client
import io
import ipaddress
import json
import socket
import urllib.parse
import zipfile
from datetime import UTC, datetime
from typing import Any

from observatory.config import USER_AGENT

DEFAULT_MAX_BYTES = 25 * 1024 * 1024


def detect_document_format(data: bytes, content_type: str = "") -> dict[str, Any]:
    """Detect the byte-level format without trusting a URL suffix or MIME claim."""
    content_type = content_type.partition(";")[0].strip().lower()
    sample = data[:2_000_000]
    if sample.startswith(b"\xef\xbb\xbf"):
        sample = sample[3:]
    stripped = sample.lstrip(b"\x00\t\r\n ")
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
            or b"inlinexbrl" in lowered
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
    requested_url = normalise_url(url)
    verified_at = datetime.now(UTC).isoformat()
    try:
        response = _fetch_public_url(
            requested_url,
            timeout=timeout,
            max_bytes=max_bytes,
        )
        if response["status"] >= 400:
            return _error_result(
                requested_url,
                verified_at,
                f"http_{response['status']}",
                f"HTTP {response['status']}",
            )
        body = response["body"]
        truncated = len(body) > max_bytes
        inspected = body[:max_bytes]
        content_type = response["headers"].get("Content-Type", "")
        detection = detect_document_format(inspected, content_type)
        return {
            "content_verification_status": "too_large" if truncated else "verified",
            "verified_at": verified_at,
            "requested_url": requested_url,
            "final_url": response["url"],
            "http_status": response["status"],
            "content_type": content_type,
            "declared_content_length": _as_int(response["headers"].get("Content-Length")),
            "bytes_read": len(inspected),
            "content_truncated": truncated,
            "content_sha256": None if truncated else hashlib.sha256(inspected).hexdigest(),
            **detection,
            "verification_error": (
                "response exceeded max_bytes; no complete-content hash recorded"
                if truncated
                else ""
            ),
        }
    except (TimeoutError, OSError, ValueError, http.client.HTTPException) as error:
        return _error_result(requested_url, verified_at, "fetch_error", str(error))


class _PinnedHTTPSConnection(http.client.HTTPSConnection):
    """Connect to an approved address while retaining hostname TLS verification."""

    def __init__(self, host: str, address: str, port: int, timeout: float):
        super().__init__(host, port=port, timeout=timeout)
        self._approved_address = address

    def connect(self) -> None:
        sock = socket.create_connection(
            (self._approved_address, self.port),
            self.timeout,
            self.source_address,
        )
        if self._tunnel_host:
            self.sock = sock
            self._tunnel()
        self.sock = self._context.wrap_socket(sock, server_hostname=self.host)


def _fetch_public_url(
    url: str,
    *,
    timeout: float,
    max_bytes: int,
    max_redirects: int = 10,
) -> dict[str, Any]:
    current_url = url
    for redirect_count in range(max_redirects + 1):
        parsed = urllib.parse.urlsplit(current_url)
        addresses = _validate_public_url(current_url)
        response = _request_approved_address(
            parsed,
            addresses,
            timeout=timeout,
            max_bytes=max_bytes,
        )
        location = response["headers"].get("Location")
        if response["status"] in {301, 302, 303, 307, 308} and location:
            if redirect_count == max_redirects:
                raise ValueError("too many redirects")
            current_url = normalise_url(urllib.parse.urljoin(current_url, location))
            continue
        return {**response, "url": current_url}
    raise ValueError("too many redirects")


def _request_approved_address(
    parsed: urllib.parse.SplitResult,
    addresses: list[str],
    *,
    timeout: float,
    max_bytes: int,
) -> dict[str, Any]:
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    path = urllib.parse.urlunsplit(("", "", parsed.path or "/", parsed.query, ""))
    host_header = parsed.hostname or ""
    if parsed.port and parsed.port != (443 if parsed.scheme == "https" else 80):
        host_header = f"{host_header}:{parsed.port}"
    last_error: OSError | None = None
    for address in addresses:
        connection: http.client.HTTPConnection
        if parsed.scheme == "https":
            connection = _PinnedHTTPSConnection(
                parsed.hostname or "",
                address,
                port,
                timeout,
            )
        else:
            connection = http.client.HTTPConnection(address, port=port, timeout=timeout)
        try:
            connection.putrequest("GET", path, skip_host=True)
            connection.putheader("Host", host_header)
            connection.putheader("User-Agent", USER_AGENT)
            connection.putheader(
                "Accept",
                "application/xhtml+xml,text/html,application/pdf,application/json,*/*;q=0.5",
            )
            connection.putheader("Connection", "close")
            connection.endheaders()
            response = connection.getresponse()
            return {
                "status": response.status,
                "headers": response.headers,
                "body": response.read(max_bytes + 1),
            }
        except OSError as error:
            last_error = error
        finally:
            connection.close()
    raise last_error or OSError("could not connect to an approved public address")


def _validate_public_url(url: str) -> list[str]:
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("only public http(s) URLs may be fetched")
    if not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("URL must contain a hostname and no user credentials")

    try:
        addresses = {
            item[4][0]
            for item in socket.getaddrinfo(
                parsed.hostname,
                parsed.port or (443 if parsed.scheme == "https" else 80),
                type=socket.SOCK_STREAM,
            )
        }
    except socket.gaierror as error:
        raise ValueError(f"hostname did not resolve: {parsed.hostname}") from error
    if not addresses:
        raise ValueError(f"hostname did not resolve: {parsed.hostname}")
    for address in addresses:
        ip = ipaddress.ip_address(address)
        if not ip.is_global:
            raise ValueError("URL resolved to a non-public IP address")
    return sorted(addresses)


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
        "declared_content_type": "",
        "declared_content_length": None,
        "bytes_read": 0,
        "content_truncated": False,
        "content_sha256": None,
        "verified_format": "",
        "inline_xbrl": False,
        "detection_basis": "",
        "verification_error": message[:500],
    }


def normalise_url(url: str) -> str:
    """Return the canonical request target used for grouping and evidence."""
    value = url.strip()
    if value and "://" not in value:
        value = "https://" + value
    parsed = urllib.parse.urlsplit(value)
    scheme = parsed.scheme.lower()
    hostname = (parsed.hostname or "").lower()
    if ":" in hostname and not hostname.startswith("["):
        hostname = f"[{hostname}]"
    netloc = hostname
    if parsed.port is not None:
        netloc = f"{netloc}:{parsed.port}"
    path = "" if parsed.path == "/" and not parsed.query else parsed.path
    return urllib.parse.urlunsplit((scheme, netloc, path, parsed.query, ""))


def _as_int(value: str | None) -> int | None:
    if not value:
        return None
    try:
        return int(value)
    except ValueError:
        return None
