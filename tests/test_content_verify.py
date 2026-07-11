import io
import zipfile

from observatory.content_verify import detect_document_format, verify_url


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
