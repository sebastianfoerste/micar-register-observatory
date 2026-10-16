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
