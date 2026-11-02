import datetime
import email.message
import gzip
import io
import json
import re
import urllib.error

import pytest

from observatory.config import SOURCES
from observatory.fetch import (
    ArchiveError,
    SourceUnavailable,
    archive_timestamp,
    download_archived,
    download_source,
    fetch_export,
    fetch_source,
)

SOURCE = SOURCES[0]
AVAILABILITY_URL = f"https://archive.org/wayback/available?url={SOURCE.url}"


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
        return outcome if isinstance(outcome, FakeResponse) else FakeResponse(outcome)

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


# --- the Wayback Machine as the fallback ---------------------------------------

NOW = datetime.datetime(2026, 11, 2, 13, 15, 0, tzinfo=datetime.UTC)
BODY = (
    "\ufeffae_competentAuthority,ae_homeMemberState,ae_lei_name,ae_lei\nNCA,DE,Issuer,L1\n"
).encode("utf-8")
CAPTURE = "20261102071326"
ARCHIVE_URL = f"https://web.archive.org/web/{CAPTURE}id_/{SOURCE.url}"
BLOCKED = (403, {"Server": "CloudFront", "X-Cache": "Error from cloudfront"}, b"Request blocked.")


def now() -> datetime.datetime:
    return NOW


def availability(timestamp: str = CAPTURE, status: str = "200", available: bool = True) -> bytes:
    closest = {
        "status": status,
        "available": available,
        "url": f"http://web.archive.org/web/{timestamp}/{SOURCE.url}",
        "timestamp": timestamp,
    }
    return json.dumps({"url": SOURCE.url, "archived_snapshots": {"closest": closest}}).encode()


def response(body: bytes, headers: dict[str, str]) -> FakeResponse:
    answer = FakeResponse(body)
    answer.headers = headers
    return answer


def archived_copy() -> FakeResponse:
    # As the Wayback Machine serves it: ESMA's bytes as the crawler received
    # them (gzip-compressed), ESMA's headers as x-archive-orig-*, the capture
    # time as Memento-Datetime.
    return response(
        gzip.compress(BODY),
        {
            "Content-Encoding": "gzip",
            "Content-Type": "text/csv",
            "Memento-Datetime": "Mon, 02 Nov 2026 07:13:26 GMT",
            "X-Archive-Orig-Last-Modified": "Fri, 30 Oct 2026 11:27:08 GMT",
        },
    )


def test_an_export_esma_keeps_refusing_is_taken_from_the_wayback_machine() -> None:
    blocked = http_error_with(*BLOCKED)
    opener, calls = scripted_opener([blocked] * 4 + [availability(), archived_copy()])
    download = fetch_export(SOURCE, opener=opener, sleep=lambda _: None, now=now)
    assert download.body == BODY
    assert download.url == ARCHIVE_URL
    assert download.archived_at == "Mon, 02 Nov 2026 07:13:26 GMT"
    assert download.last_modified == "Fri, 30 Oct 2026 11:27:08 GMT"
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", download.retrieved_at)
    assert [call.full_url for call in calls] == [SOURCE.url] * 4 + [AVAILABILITY_URL, ARCHIVE_URL]
    assert all("micar-register-observatory" in c.get_header("User-agent") for c in calls)


def test_a_download_from_esma_itself_carries_no_archive_provenance() -> None:
    opener, calls = scripted_opener([http_error(503), b"ok"])
    download = fetch_export(SOURCE, opener=opener, sleep=lambda _: None, now=now)
    assert download.body == b"ok" and download.url == SOURCE.url
    assert download.archived_at == "" and len(calls) == 2


def test_an_archived_copy_older_than_the_limit_is_not_used() -> None:
    blocked = http_error_with(*BLOCKED)
    opener, calls = scripted_opener([blocked] * 4 + [availability("20261029121040")])
    with pytest.raises(SourceUnavailable) as raised:
        fetch_export(SOURCE, opener=opener, sleep=lambda _: None, now=now)
    message = str(raised.value)
    assert message.startswith("HTTP Error 403: Forbidden (server=CloudFront; x-cache=Error from")
    assert "Wayback Machine: the newest archived copy of " in message
    assert "was captured on 2026-10-29, more than 3 days ago" in message
    assert len(calls) == 5  # the stale file itself is never fetched


def test_no_archived_copy_at_all_is_reported_with_esma_s_answer() -> None:
    none = json.dumps({"url": SOURCE.url, "archived_snapshots": {}}).encode()
    opener, calls = scripted_opener([http_error(503)] * 4 + [none])
    expected = r"HTTP Error 503: err; Wayback Machine: no archived copy of"
    with pytest.raises(SourceUnavailable, match=expected):
        fetch_export(SOURCE, opener=opener, sleep=lambda _: None, now=now)
    assert len(calls) == 5


def test_a_failing_archive_lookup_is_reported_too() -> None:
    opener, _ = scripted_opener([TimeoutError()] * 4 + [urllib.error.URLError("dns")] * 4)
    with pytest.raises(SourceUnavailable, match=r"Wayback Machine: <urlopen error dns>"):
        fetch_export(SOURCE, opener=opener, sleep=lambda _: None, now=now)


def test_the_archive_is_retried_more_slowly_and_fewer_times_than_esma() -> None:
    # archive.org answers 429 for a while when asked too often; 2, 4 and 8
    # seconds would not outlast it. Three attempts per archive request keep five
    # refused sources (ESMA 14 s, archive 2 x 45 s each) within the job's budget.
    limited = http_error_with(429, {"Server": "nginx"}, b"429 Too Many Requests")
    opener, calls = scripted_opener(
        [http_error(503)] * 4 + [limited] * 2 + [availability(), limited, limited, archived_copy()]
    )
    sleeps: list[float] = []
    download = fetch_export(SOURCE, opener=opener, sleep=sleeps.append, now=now)
    assert download.archived_at == "Mon, 02 Nov 2026 07:13:26 GMT"
    assert sleeps == [2.0, 4.0, 8.0, 15.0, 30.0, 15.0, 30.0]
    assert len(calls) == 10

    opener, calls = scripted_opener([http_error(503)] * 4 + [limited] * 3)
    with pytest.raises(SourceUnavailable, match="Wayback Machine: HTTP Error 429"):
        fetch_export(SOURCE, opener=opener, sleep=lambda _: None, now=now)
    assert len(calls) == 7


def test_a_permanent_answer_from_esma_is_not_papered_over_by_the_archive() -> None:
    # 404: the file moved. An archived copy would hide the source change.
    opener, calls = scripted_opener([http_error(404), availability(), archived_copy()])
    with pytest.raises(urllib.error.HTTPError) as raised:
        fetch_export(SOURCE, opener=opener, sleep=lambda _: None, now=now)
    assert raised.value.code == 404 and len(calls) == 1


def test_the_archive_can_be_switched_off() -> None:
    blocked = http_error_with(*BLOCKED)
    opener, calls = scripted_opener([blocked] * 4 + [availability(), archived_copy()])
    with pytest.raises(urllib.error.HTTPError) as raised:
        fetch_export(SOURCE, archive=False, opener=opener, sleep=lambda _: None, now=now)
    assert raised.value.code == 403 and len(calls) == 4


def test_the_archive_s_capture_time_is_derived_when_the_memento_header_is_missing() -> None:
    copy = response(BODY, {"X-Archive-Orig-Last-Modified": "Fri, 30 Oct 2026 11:27:08 GMT"})
    opener, _ = scripted_opener([availability(), copy])
    download = download_archived(SOURCE, opener=opener, sleep=lambda _: None, now=now)
    assert download.body == BODY  # not gzip-encoded: left as it is
    assert download.archived_at == "Mon, 02 Nov 2026 07:13:26 GMT"


def test_an_unreadable_availability_answer_is_an_archive_error() -> None:
    for payload in (b"<html>offline</html>", b"{}", b'{"archived_snapshots": null}'):

        def opener(request, timeout, payload=payload):
            if "archive.org" in request.full_url:
                return FakeResponse(payload)
            raise http_error(503)

        with pytest.raises(SourceUnavailable) as raised:
            fetch_export(SOURCE, opener=opener, sleep=lambda _: None, now=now)
        assert re.search(
            r"Wayback Machine: (unreadable availability answer|no archived copy)", str(raised.value)
        ), payload


def test_archive_timestamp_checks_the_answer() -> None:
    assert archive_timestamp(availability(), SOURCE.url) == CAPTURE
    with pytest.raises(ArchiveError, match="no archived copy"):
        archive_timestamp(availability(available=False), SOURCE.url)
    with pytest.raises(ArchiveError, match="no archived copy"):
        archive_timestamp(availability(status="403"), SOURCE.url)
    with pytest.raises(ArchiveError, match="unreadable capture timestamp"):
        archive_timestamp(availability(timestamp="2026-11-02"), SOURCE.url)


def test_a_gzip_encoded_answer_from_esma_is_decoded() -> None:
    opener, _ = scripted_opener([response(gzip.compress(BODY), {"Content-Encoding": "gzip"})])
    assert download_source(SOURCE, opener=opener, sleep=lambda _: None).body == BODY


def test_a_body_that_only_claims_to_be_gzip_is_kept_as_it_is() -> None:
    opener, _ = scripted_opener([response(BODY, {"Content-Encoding": "gzip"})])
    assert download_source(SOURCE, opener=opener, sleep=lambda _: None).body == BODY
