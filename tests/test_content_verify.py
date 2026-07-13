import io
import socket
import zipfile

import observatory.content_verify as content_verify
from observatory.content_verify import detect_document_format, normalise_url, verify_url


def test_detects_pdf_by_signature_not_suffix():
    result = detect_document_format(b"%PDF-1.7\nbody", "application/octet-stream")
    assert result["verified_format"] == "pdf"
    assert result["detection_basis"] == "file_signature"


def test_detects_inline_xbrl_xhtml():
    data = b'<html xmlns:ix="http://www.xbrl.org/2013/inlineXBRL"><ix:header/></html>'
    result = detect_document_format(data, "text/html")
    assert result["verified_format"] == "inline-xbrl-xhtml"
    assert result["inline_xbrl"] is True


def test_plain_html_is_not_inline_xbrl():
    result = detect_document_format(b"<html><body>White paper</body></html>", "text/html")
    assert result["verified_format"] == "xhtml/html"
    assert result["inline_xbrl"] is False


def test_detects_json_by_parse():
    result = detect_document_format(b'{"whitepaper": true}', "text/plain")
    assert result["verified_format"] == "json"


def test_strips_only_a_complete_utf8_bom():
    assert detect_document_format(b"\xef\xbb\xbf%PDF-1.7")["verified_format"] == "pdf"
    assert detect_document_format(b"\xef%PDF-1.7")["verified_format"] == "unknown"


def test_detects_docx_by_zip_structure():
    target = io.BytesIO()
    with zipfile.ZipFile(target, "w") as archive:
        archive.writestr("word/document.xml", "<w:document/>")
    result = detect_document_format(target.getvalue(), "application/octet-stream")
    assert result["verified_format"] == "docx"


def test_unknown_bytes_remain_unknown_despite_declared_pdf_type():
    result = detect_document_format(b"not a recognised document", "application/pdf")
    assert result["verified_format"] == "unknown"
    assert result["declared_content_type"] == "application/pdf"


def test_non_http_scheme_is_rejected_without_a_request():
    result = verify_url("file:///etc/passwd")
    assert result["content_verification_status"] == "fetch_error"
    assert "http(s)" in result["verification_error"]


def test_loopback_target_is_rejected_without_a_request():
    result = verify_url("http://127.0.0.1/document.pdf")
    assert result["content_verification_status"] == "fetch_error"
    assert "non-public" in result["verification_error"]


def test_scheme_and_hostname_are_canonicalized_for_url_deduplication():
    assert normalise_url(" HTTPS://Example.COM/path#fragment ") == "https://example.com/path"
    assert normalise_url("example.com/path") == "https://example.com/path"
    assert normalise_url("https://example.com/") == normalise_url("example.com")


def test_approved_numeric_address_is_dialed_without_dns_rebinding(monkeypatch):
    resolutions = 0

    def resolve(*args, **kwargs):
        nonlocal resolutions
        resolutions += 1
        address = "93.184.216.34" if resolutions == 1 else "127.0.0.1"
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", (address, 443))]

    captured = []

    def request(parsed, addresses, **kwargs):
        captured.append((parsed.hostname, addresses))
        return {"status": 200, "headers": {"Content-Type": "application/pdf"}, "body": b"%PDF-1.7"}

    monkeypatch.setattr(content_verify.socket, "getaddrinfo", resolve)
    monkeypatch.setattr(content_verify, "_request_approved_address", request)
    result = verify_url("https://EXAMPLE.com/document")
    assert result["content_verification_status"] == "verified"
    assert captured == [("example.com", ["93.184.216.34"])]
    assert resolutions == 1


def test_redirect_target_is_resolved_and_validated_again(monkeypatch):
    resolved_hosts = []

    def resolve(host, *args, **kwargs):
        resolved_hosts.append(host)
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 443))]

    responses = iter(
        [
            {"status": 302, "headers": {"Location": "https://FILES.example/whitepaper"}, "body": b""},
            {"status": 200, "headers": {"Content-Type": "application/pdf"}, "body": b"%PDF-1.7"},
        ]
    )
    monkeypatch.setattr(content_verify.socket, "getaddrinfo", resolve)
    monkeypatch.setattr(
        content_verify,
        "_request_approved_address",
        lambda *args, **kwargs: next(responses),
    )
    result = verify_url("https://example.com/start")
    assert result["final_url"] == "https://files.example/whitepaper"
    assert resolved_hosts == ["example.com", "files.example"]
