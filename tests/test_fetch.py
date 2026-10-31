import email.message
import io
import re
import urllib.error

import pytest

from observatory.config import SOURCES
from observatory.fetch import download_source, fetch_source

SOURCE = SOURCES[0]


class FakeResponse(io.BytesIO):
    headers: dict[str, str] = {}

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def scripted_opener(outcomes):
    calls = []

    def opener(request, timeout):
        calls.append(request)
        outcome = outcomes[len(calls) - 1]
        if isinstance(outcome, Exception):
            raise outcome
        return FakeResponse(outcome)

    return opener, calls


def http_error(code):
    return urllib.error.HTTPError(SOURCE.url, code, "err", {}, None)


def test_retries_transient_errors_then_succeeds() -> None:
    opener, calls = scripted_opener([http_error(503), urllib.error.URLError("dns"), b"ok"])
    sleeps: list[float] = []
    assert fetch_source(SOURCE, opener=opener, sleep=sleeps.append) == b"ok"
    assert len(calls) == 3
    assert sleeps == [2.0, 4.0]
    assert "micar-register-observatory" in calls[0].get_header("User-agent")


def test_gives_up_after_all_attempts() -> None:
    opener, calls = scripted_opener([TimeoutError()] * 3)
    with pytest.raises(TimeoutError):
        fetch_source(SOURCE, attempts=3, opener=opener, sleep=lambda _: None)
    assert len(calls) == 3


def test_does_not_retry_permanent_errors() -> None:
    opener, calls = scripted_opener([http_error(404), b"never"])
    with pytest.raises(urllib.error.HTTPError):
        fetch_source(SOURCE, opener=opener, sleep=lambda _: None)
    assert len(calls) == 1


def test_download_keeps_the_last_modified_header_and_retrieval_time() -> None:
    response = FakeResponse(b"body")
    response.headers = {"Last-Modified": "Tue, 07 Oct 2026 09:12:44 GMT"}
    download = download_source(SOURCE, opener=lambda request, timeout: response)
    assert download.body == b"body"
    assert download.url == SOURCE.url
    assert download.last_modified == "Tue, 07 Oct 2026 09:12:44 GMT"
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", download.retrieved_at)


def test_a_missing_last_modified_header_is_left_empty() -> None:
    opener, _ = scripted_opener([b"body"])
    assert download_source(SOURCE, opener=opener, sleep=lambda _: None).last_modified == ""


def http_error_with(code, headers=None, body=b""):
    message = email.message.Message()
    for name, value in (headers or {}).items():
        message[name] = value
    return urllib.error.HTTPError(SOURCE.url, code, "Forbidden", message, io.BytesIO(body))


def test_a_403_is_retried_like_any_transient_refusal() -> None:
    opener, calls = scripted_opener([http_error(403), b"ok"])
    sleeps: list[float] = []
    assert fetch_source(SOURCE, opener=opener, sleep=sleeps.append) == b"ok"
    assert len(calls) == 2 and sleeps == [2.0]


def test_a_persistent_403_says_which_server_refused_and_what_it_sent() -> None:
    blocked = http_error_with(
        403,
        {"Server": "CloudFront", "Via": "1.1 abc.cloudfront.net (CloudFront)", "X-Cache": "Error"},
        b"<html><body><h1>403 Forbidden</h1><p>Request blocked.</p></body></html>",
    )
    opener, calls = scripted_opener([blocked] * 4)
    with pytest.raises(urllib.error.HTTPError) as raised:
        fetch_source(SOURCE, opener=opener, sleep=lambda _: None)
    assert len(calls) == 4
    assert raised.value.code == 403
    assert str(raised.value) == (
        "HTTP Error 403: Forbidden (server=CloudFront; via=1.1 abc.cloudfront.net (CloudFront); "
        'x-cache=Error; body="403 Forbidden Request blocked.")'
    )


def test_a_short_retry_after_header_sets_the_pause() -> None:
    opener, _ = scripted_opener([http_error_with(429, {"Retry-After": "3"}), b"ok"])
    sleeps: list[float] = []
    assert fetch_source(SOURCE, opener=opener, sleep=sleeps.append) == b"ok"
    assert sleeps == [3.0]


def test_a_long_retry_after_header_is_ignored_for_the_backoff() -> None:
    opener, _ = scripted_opener([http_error_with(503, {"Retry-After": "3600"}), b"ok"])
    sleeps: list[float] = []
    assert fetch_source(SOURCE, opener=opener, sleep=sleeps.append) == b"ok"
    assert sleeps == [2.0]


def test_a_permanent_error_keeps_its_code_and_reason() -> None:
    opener, _ = scripted_opener([http_error(404)])
    with pytest.raises(urllib.error.HTTPError) as raised:
        fetch_source(SOURCE, opener=opener, sleep=lambda _: None)
    assert raised.value.code == 404 and str(raised.value) == "HTTP Error 404: err"
