"""ESMA source monitor: checks what each refresh actually used.

Since 26 October 2026 ESMA's CDN has refused GitHub-hosted runners at times, and
a refresh then takes the Wayback Machine's recent copy of an export
(fetch.fetch_export). The monitor therefore does not fetch the register files
itself. It observes the downloads the refresh used, from ESMA or from the
archive, and records which, with the capture time and what ESMA answered.
ESMA's MiCA page is fetched the same way: ESMA first, then a recent copy.

For each source it

- runs the hard checks on the bytes actually used: the media type, the charset,
  the CSV header against `columns` in config.py and the row count against the
  source's floor; for the MiCA page, its media type, charset, "Last update"
  line and a link to every configured export;
- compares the observation with the previous one (data/source-monitor.json),
  and classify_source_change decides which differences open an issue.

Outcomes:

- ISSUE: a hard check failed, or a difference was classified as an issue. The
  weekly workflow opens an issue, or comments on the open one when the findings
  changed.
- UNKNOWN: nothing calls for an issue, but a source could not be observed at
  all (neither ESMA nor a recent archived copy answered), so its checks did not
  run. This is reported, never counted as a pass.
- OK: every source was observed, every check passed and every difference was
  logged.

A refusal by ESMA is a logged state, not an issue: the refresh goes on with the
archive's copy. The monitor never changes the refresh's exit status or what the
refresh records; the refresh's own fail-closed checks decide that. When the
monitor itself fails (an unreadable data/source-monitor.json, say), the refresh
gets a failed_report: UNKNOWN, nothing checked, and the saved observation left
as it was.

Everything here is pure except load_state and save_state: observations are made
from Download objects, and the check date is a parameter.
"""

from __future__ import annotations

import csv
import hashlib
import html
import io
import re
from collections import Counter
from collections.abc import Callable, Iterable, Mapping, Sequence
from enum import StrEnum
from pathlib import Path
from typing import Literal
from urllib.parse import urljoin, urlsplit, urlunsplit

from pydantic import BaseModel, ConfigDict

from observatory.config import MICA_PAGE_URL, SOURCES, RegisterSource
from observatory.fetch import Download, is_permanent

PAGE_SOURCE_ID = "mica-page"
STATE_FILE = "source-monitor.json"
RUNBOOK_URL = (
    "https://github.com/sebastianfoerste/micar-register-observatory/blob/main/"
    "docs/runbook-esma-source-change.md"
)
FINGERPRINT_MARKER = "monitor-fingerprint"

ALLOWED_CSV_MEDIA_TYPES = frozenset({"text/csv"})
ALLOWED_PAGE_MEDIA_TYPES = frozenset({"text/html"})
UTF8 = "utf-8"
_UTF8_NAMES = frozenset({"utf-8", "utf8"})

# Row drops at or below max(MIN_ROW_DROP, ROW_DROP_SHARE of the previous count)
# are logged; larger drops, and any fall to zero, open an issue.
MIN_ROW_DROP = 5
ROW_DROP_SHARE_DENOMINATOR = 10  # 10 %

# ESMA's page reads "<p><em>Last update: 11 November 2026</em></p>" (snapshot of
# 14 November 2026). The value is kept as served, without parsing the date.
_LAST_UPDATE = re.compile(r"Last update:\s*([^<]{1,80}?)\s*<", re.IGNORECASE)
_CSV_LINK = re.compile(r"""href=["']([^"']+?\.csv)["']""", re.IGNORECASE)
# An archive URL names the URL it is a copy of after the capture timestamp.
_ARCHIVED = re.compile(r"^https?://web\.archive\.org/web/\d{14}[a-z_]*/(?P<original>.+)$")


class Action(StrEnum):
    ISSUE = "issue"
    LOG = "log"


class Outcome(StrEnum):
    ISSUE = "issue"
    UNKNOWN = "unknown"
    OK = "ok"


DifferenceAttribute = Literal[
    "via",
    "final_url",
    "content_type",
    "charset",
    "last_modified",
    "content_length",
    "csv_header",
    "row_count",
    "last_update_line",
    "linked_csv_urls",
]

COMPARED_ATTRIBUTES: tuple[DifferenceAttribute, ...] = (
    "via",
    "final_url",
    "content_type",
    "charset",
    "last_modified",
    "content_length",
    "csv_header",
    "row_count",
    "last_update_line",
    "linked_csv_urls",
)

ObservedValue = int | str | tuple[str, ...] | None


class SourceObservation(BaseModel):
    """What the bytes a refresh used for one source showed. None: not observed."""

    model_config = ConfigDict(frozen=True)

    source_id: str  # register slug, or PAGE_SOURCE_ID
    kind: Literal["csv", "page"]
    url: str  # the configured ESMA URL
    observed: bool
    # Where the bytes came from: ESMA, the Wayback Machine's copy, or a fixture.
    via: Literal["esma", "archive", "fixture"] | None = None
    fetched_from: str = ""
    archived_at: str = ""
    esma_refusal: str = ""  # what ESMA answered when the archive stood in
    error: str = ""  # why nothing was observed
    permanent: bool = False  # ESMA answered with an error retrying cannot cure
    final_url: str | None = None  # the ESMA URL the bytes belong to, after redirects
    content_type: str | None = None  # raw header value
    charset: str | None = None  # "utf-8", a declared other charset, or "not utf-8"
    last_modified: str | None = None  # raw header value
    content_length: int | None = None  # bytes used
    csv_header: tuple[str, ...] | None = None  # named columns, in order
    row_count: int | None = None  # non-blank rows after the header, without header echoes
    last_update_line: str | None = None  # page only
    linked_csv_urls: tuple[str, ...] | None = None  # page only: canonical, sorted


class ObservedDifference(BaseModel):
    model_config = ConfigDict(frozen=True)

    source_id: str
    attribute: DifferenceAttribute
    previous: ObservedValue
    current: ObservedValue


class ClassifiedDifference(BaseModel):
    model_config = ConfigDict(frozen=True)

    difference: ObservedDifference
    action: Action
    reason: str


class CheckResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    source_id: str
    check: str
    passed: bool
    detail: str


class MonitorReport(BaseModel):
    checked_on: str
    previous_checked_on: str = ""
    outcome: Outcome
    checks: list[CheckResult]
    classified: list[ClassifiedDifference]
    observations: list[SourceObservation]
    # Sources not observed this time: their previous observation stays the baseline.
    carried_over: list[SourceObservation] = []
    # Set when the monitor itself failed ("ErrorType: message"): nothing was
    # checked, and save_state keeps the previous observation.
    failure: str = ""

    def issue_items(self) -> list[str]:
        failed = [f"{c.source_id}: {c.check}: {c.detail}" for c in self.checks if not c.passed]
        differences = [
            f"{c.difference.source_id}: {c.difference.attribute}: {c.reason}"
            for c in self.classified
            if c.action is Action.ISSUE
        ]
        return failed + differences

    def unobserved(self) -> list[str]:
        """Sources no check ran on: neither ESMA nor a recent archived copy gave
        bytes, and ESMA's answer was not a permanent one (that is a finding)."""
        return sorted(o.source_id for o in self.observations if not o.observed and not o.permanent)

    def fingerprint(self) -> str:
        """Identifies the findings and the unobserved sources, so that the
        workflow reports the same state once. The error texts are left out:
        they carry times and request ids that change with every run."""
        items = sorted(self.issue_items()) + [f"{s}: not observed" for s in self.unobserved()]
        if self.failure:
            # The error type only: its message may carry paths or positions.
            items.append(f"monitor failed: {self.failure.split(':', 1)[0]}")
        return hashlib.sha256("\n".join(items).encode("utf-8")).hexdigest()[:16]

    def to_markdown(self) -> str:
        return render_report(self)


class MonitorState(BaseModel):
    checked_on: str
    observations: list[SourceObservation]


# --- Observation -------------------------------------------------------------


def canonical_url(url: str) -> str:
    """`url` with scheme https and a lower-case host, so that the http copy the
    archive names and ESMA's https URL compare equal."""
    parts = urlsplit(url.strip())
    if parts.scheme not in {"http", "https"} or not parts.netloc:
        return url.strip()
    host = parts.netloc.lower().removesuffix(":443").removesuffix(":80")
    return urlunsplit(("https", host, parts.path, parts.query, ""))


def original_url(url: str) -> str:
    """The URL an archive URL is a copy of; any other URL unchanged."""
    match = _ARCHIVED.match(url.strip())
    if not match:
        return url.strip()
    original = match["original"]
    # The archive sometimes collapses "https://" to "https:/".
    return re.sub(r"^(https?):/(?!/)", r"\1://", original)


def media_type(content_type: str | None) -> str | None:
    if not content_type:
        return None
    return content_type.split(";", 1)[0].strip().lower() or None


def _declared_charset(content_type: str | None) -> str:
    for parameter in (content_type or "").split(";")[1:]:
        name, _, value = parameter.partition("=")
        if name.strip().lower() == "charset":
            return value.strip().strip('"').lower()
    return ""


def effective_charset(content_type: str | None, body: bytes) -> str:
    """ "utf-8" when the bytes are UTF-8 and no other charset is declared; the
    declared charset when it is another; "not utf-8" for undeclared bytes that
    do not decode as UTF-8."""
    declared = _declared_charset(content_type)
    if declared and declared not in _UTF8_NAMES:
        return declared
    try:
        body.decode("utf-8-sig")
    except UnicodeDecodeError:
        return "not utf-8"
    return UTF8


def csv_shape(body: bytes) -> tuple[tuple[str, ...] | None, int | None]:
    """The named header columns and the number of data rows (non-blank rows
    after the header, without repeated header lines)."""
    text = body.decode("utf-8-sig", errors="replace")
    try:
        rows = [row for row in csv.reader(io.StringIO(text)) if any(c.strip() for c in row)]
    except csv.Error:
        return None, None
    if not rows:
        return None, None
    header = tuple(name for name in (cell.strip() for cell in rows[0]) if name)
    if not header:
        return None, None
    data = [row for row in rows[1:] if tuple(c.strip() for c in row if c.strip()) != header]
    return header, len(data)


def _via(download: Download) -> Literal["esma", "archive", "fixture"]:
    if download.archived_at:
        return "archive"
    if download.url.startswith("fixture:"):
        return "fixture"
    return "esma"


def _unobserved(
    source_id: str, kind: Literal["csv", "page"], url: str, error: BaseException | str
) -> SourceObservation:
    if isinstance(error, BaseException):
        text = " ".join(f"{type(error).__name__}: {error}".split())[:300]
        permanent = is_permanent(error)
    else:
        text, permanent = error, False
    return SourceObservation(
        source_id=source_id, kind=kind, url=url, observed=False, error=text, permanent=permanent
    )


def _common(download: Download) -> dict[str, object]:
    final = download.final_url or ("" if download.url.startswith("fixture:") else download.url)
    return {
        "observed": True,
        "via": _via(download),
        "fetched_from": download.url,
        "archived_at": download.archived_at,
        "esma_refusal": download.esma_refusal,
        "final_url": canonical_url(original_url(final)) if final else None,
        "content_type": download.content_type or None,
        "charset": effective_charset(download.content_type, download.body),
        "last_modified": download.last_modified or None,
        "content_length": len(download.body),
    }


def observe_csv(
    source: RegisterSource, result: Download | BaseException | None
) -> SourceObservation:
    if result is None:
        return _unobserved(source.slug, "csv", source.url, "not fetched")
    if isinstance(result, BaseException):
        return _unobserved(source.slug, "csv", source.url, result)
    header, rows = csv_shape(result.body)
    return SourceObservation(
        source_id=source.slug,
        kind="csv",
        url=source.url,
        csv_header=header,
        row_count=rows,
        **_common(result),
    )


def observe_page(url: str, result: Download | BaseException | str | None) -> SourceObservation:
    if result is None or isinstance(result, (BaseException, str)):
        return _unobserved(PAGE_SOURCE_ID, "page", url, result or "not fetched")
    text = result.body.decode("utf-8", errors="replace")
    match = _LAST_UPDATE.search(text)
    last_update = None
    if match:
        value = " ".join(html.unescape(match.group(1)).split())
        last_update = f"Last update: {value}" if value else None
    # Links are resolved against ESMA's URL: in the archive's `id_` mode the page
    # comes back as ESMA served it, with ESMA's relative links.
    links = tuple(
        sorted(
            {canonical_url(original_url(urljoin(url, href))) for href in _CSV_LINK.findall(text)}
        )
    )
    return SourceObservation(
        source_id=PAGE_SOURCE_ID,
        kind="page",
        url=url,
        last_update_line=last_update,
        linked_csv_urls=links,
        **_common(result),
    )


# --- Hard checks -------------------------------------------------------------


def _describe_header(expected: tuple[str, ...], observed: tuple[str, ...] | None) -> str:
    if observed is None:
        return "no header row read"
    missing = [c for c in expected if c not in observed]
    unexpected = [c for c in observed if c not in expected]
    parts = []
    if missing:
        parts.append(f"missing {missing}")
    if unexpected:
        parts.append(f"unexpected {unexpected}")
    if not parts:
        parts.append("same columns in a different order")
    return "; ".join(parts)


def _unavailable(observation: SourceObservation) -> list[CheckResult]:
    """A source with no bytes: a permanent answer from ESMA is a finding; a
    refusal the archive could not cover leaves the checks undone (UNKNOWN)."""
    if observation.permanent:
        return [
            CheckResult(
                source_id=observation.source_id,
                check="available",
                passed=False,
                detail=f"ESMA answered {observation.error}; the file may have moved",
            )
        ]
    return []


def _media_checks(observation: SourceObservation, allowed: frozenset[str]) -> list[CheckResult]:
    sid = observation.source_id
    return [
        CheckResult(
            source_id=sid,
            check="content_type",
            passed=media_type(observation.content_type) in allowed,
            detail=f"Content-Type {observation.content_type!r}",
        ),
        CheckResult(
            source_id=sid,
            check="charset",
            passed=observation.charset == UTF8,
            detail=f"charset {observation.charset}",
        ),
    ]


def check_csv(
    observation: SourceObservation, source: RegisterSource, enforce_floor: bool = True
) -> list[CheckResult]:
    if not observation.observed:
        return _unavailable(observation)
    results = _media_checks(observation, ALLOWED_CSV_MEDIA_TYPES)
    if source.columns:
        header_ok = observation.csv_header == source.columns
        results.append(
            CheckResult(
                source_id=source.slug,
                check="csv_header",
                passed=header_ok,
                detail=(
                    f"{len(source.columns)} named columns as expected"
                    if header_ok
                    else _describe_header(source.columns, observation.csv_header)
                ),
            )
        )
    rows = observation.row_count
    floor = source.min_rows if enforce_floor else 0
    results.append(
        CheckResult(
            source_id=source.slug,
            check="row_count",
            passed=rows is not None and rows >= floor,
            detail="no header row read" if rows is None else f"{rows} rows (floor {floor})",
        )
    )
    return results


def check_page(observation: SourceObservation, configured_urls: Iterable[str]) -> list[CheckResult]:
    if not observation.observed:
        return _unavailable(observation)
    results = _media_checks(observation, ALLOWED_PAGE_MEDIA_TYPES)
    results.append(
        CheckResult(
            source_id=PAGE_SOURCE_ID,
            check="last_update_line",
            passed=observation.last_update_line is not None,
            detail=observation.last_update_line or "no 'Last update:' line found",
        )
    )
    linked = set(observation.linked_csv_urls or ())
    missing = sorted(
        url for url in (canonical_url(u) for u in configured_urls) if url not in linked
    )
    results.append(
        CheckResult(
            source_id=PAGE_SOURCE_ID,
            check="links_every_export",
            passed=not missing,
            detail=f"not linked: {missing}" if missing else "every configured export is linked",
        )
    )
    return results


# --- Differences -------------------------------------------------------------


def observed_differences(
    previous: SourceObservation, current: SourceObservation
) -> list[ObservedDifference]:
    """Every compared attribute whose value changed between two observations."""
    differences = []
    for attribute in COMPARED_ATTRIBUTES:
        before = getattr(previous, attribute)
        after = getattr(current, attribute)
        if before != after:
            differences.append(
                ObservedDifference(
                    source_id=current.source_id,
                    attribute=attribute,
                    previous=before,
                    current=after,
                )
            )
    return differences


CONFIGURED_URLS = frozenset(canonical_url(source.url) for source in SOURCES)


def _decide(difference: ObservedDifference, configured_urls: frozenset[str]) -> tuple[Action, str]:
    """Issue or log for one difference, and why. The rules, decided on
    10 November 2026 under the owner's delegation:

    - ISSUE: the final URL moved; a configured export is no longer linked on
      ESMA's MiCA page; the header changed; the charset is not UTF-8; the rows
      dropped by more than max(5, 10 % of the previous count), or fell to 0.
    - LOG: last_modified, last_update_line and content_length, any growth in
      rows, smaller drops, and where the bytes came from (ESMA or the archive).

    An attribute seen for the first time (previous None) is logged, except a row
    count or header that can no longer be read, which is an issue: an unknown
    count is never a pass.
    """
    attribute, before, after = difference.attribute, difference.previous, difference.current
    if attribute in {"last_modified", "last_update_line", "content_length"}:
        return Action.LOG, "expected to change when ESMA republishes"
    if attribute == "via":
        if after == "archive":
            return Action.LOG, "ESMA refused the download; the archive's recent copy was used"
        return Action.LOG, f"the bytes came from {after} (previously {before})"
    if attribute == "content_type":
        return Action.LOG, "the media type and the charset are checked on their own"
    if attribute == "charset":
        if after != UTF8:
            return Action.ISSUE, f"the charset is {after}, not UTF-8"
        return Action.LOG, "UTF-8"
    if attribute == "final_url":
        if before is None:
            return Action.LOG, "first observation"
        return Action.ISSUE, "the file now resolves to a different URL; ESMA may have moved it"
    if attribute == "csv_header":
        if after is None:
            return Action.ISSUE, "the header row can no longer be read"
        if before is None:
            return Action.LOG, "first observation"
        return Action.ISSUE, "the header row changed"
    if attribute == "linked_csv_urls":
        lost = sorted((configured_urls & _strings(before)) - _strings(after))
        if lost:
            return Action.ISSUE, f"a configured export is no longer linked on ESMA's page: {lost}"
        return Action.LOG, "links added, or a link the observatory does not read removed"
    if attribute == "row_count":
        return _decide_rows(before, after)
    return Action.ISSUE, "an attribute the classifier does not know changed"


def _strings(value: ObservedValue) -> set[str]:
    return set(value) if isinstance(value, tuple) else set()


def _decide_rows(before: ObservedValue, after: ObservedValue) -> tuple[Action, str]:
    if not isinstance(after, int):
        return Action.ISSUE, "the row count can no longer be read"
    if not isinstance(before, int):
        return Action.LOG, "first observation"
    if after >= before:
        return Action.LOG, f"grew by {after - before} rows"
    drop = before - after
    if after == 0:
        return Action.ISSUE, f"fell from {before} rows to 0"
    if drop > MIN_ROW_DROP and drop * ROW_DROP_SHARE_DENOMINATOR > before:
        return Action.ISSUE, f"dropped by {drop} rows, more than max(5, 10 % of {before})"
    return Action.LOG, f"dropped by {drop} rows, within max(5, 10 % of {before})"


def classify_source_change(
    previous: SourceObservation,
    current: SourceObservation,
    configured_urls: frozenset[str] = CONFIGURED_URLS,
) -> list[ClassifiedDifference]:
    """Decide, for each difference since the previous observation of a source,
    whether it opens an issue or is only logged (rules: _decide)."""
    return [
        ClassifiedDifference(difference=difference, action=action, reason=reason)
        for difference in observed_differences(previous, current)
        for action, reason in [_decide(difference, configured_urls)]
    ]


Classifier = Callable[[SourceObservation, SourceObservation], list[ClassifiedDifference]]


def _classify(
    previous: SourceObservation,
    current: SourceObservation,
    classify: Classifier,
) -> list[ClassifiedDifference]:
    """Run the classifier; a difference it does not decide cleanly is an issue."""
    differences = observed_differences(previous, current)
    if not differences:
        return []
    try:
        result = classify(previous, current)
        decided = Counter(item.difference.model_dump_json() for item in result)
    except Exception as error:  # noqa: BLE001 — an undecided difference is an issue, never a pass
        reason = f"not classified: {type(error).__name__}: {error}"[:300]
        return [
            ClassifiedDifference(difference=d, action=Action.ISSUE, reason=reason)
            for d in differences
        ]
    if decided != Counter(d.model_dump_json() for d in differences):
        reason = "not classified: the classifier did not decide each difference exactly once"
        return [
            ClassifiedDifference(difference=d, action=Action.ISSUE, reason=reason)
            for d in differences
        ]
    return result


# --- Run ---------------------------------------------------------------------


def run_monitor(
    sources: Sequence[RegisterSource],
    fetched: Mapping[str, Download | BaseException],
    page: Download | BaseException | str | None,
    previous: Sequence[SourceObservation],
    checked_on: str,
    previous_checked_on: str = "",
    page_url: str = MICA_PAGE_URL,
    classify: Classifier = classify_source_change,
    enforce_floors: bool = True,
) -> MonitorReport:
    """Check what a refresh fetched: `fetched` maps each register slug to the
    download the refresh used, or to the error that left it without one; `page`
    is the MiCA page's download, its error, or a reason it was not fetched."""
    observations: list[SourceObservation] = []
    checks: list[CheckResult] = []
    for source in sources:
        observation = observe_csv(source, fetched.get(source.slug))
        observations.append(observation)
        checks.extend(check_csv(observation, source, enforce_floors))
    page_observation = observe_page(page_url, page)
    observations.append(page_observation)
    checks.extend(check_page(page_observation, (source.url for source in sources)))

    earlier = {(o.source_id, o.kind): o for o in previous}
    classified: list[ClassifiedDifference] = []
    carried_over: list[SourceObservation] = []
    for current in observations:
        before = earlier.get((current.source_id, current.kind))
        if not current.observed:
            if before is not None:
                carried_over.append(before)
            continue
        if before is not None:
            classified.extend(_classify(before, current, classify))

    if any(not c.passed for c in checks) or any(c.action is Action.ISSUE for c in classified):
        outcome = Outcome.ISSUE
    elif any(not o.observed for o in observations):
        outcome = Outcome.UNKNOWN
    else:
        outcome = Outcome.OK
    return MonitorReport(
        checked_on=checked_on,
        previous_checked_on=previous_checked_on,
        outcome=outcome,
        checks=checks,
        classified=classified,
        observations=observations,
        carried_over=carried_over,
    )


def failed_report(checked_on: str, error: BaseException) -> MonitorReport:
    """The report when the monitor itself failed: nothing was checked, which is
    UNKNOWN, never a pass. The refresh goes on, and save_state keeps the
    previous observation."""
    return MonitorReport(
        checked_on=checked_on,
        outcome=Outcome.UNKNOWN,
        checks=[],
        classified=[],
        observations=[],
        failure=" ".join(f"{type(error).__name__}: {error}".split())[:300],
    )


# --- State -------------------------------------------------------------------


def load_state(path: Path) -> MonitorState | None:
    if not path.exists():
        return None
    return MonitorState.model_validate_json(path.read_text(encoding="utf-8"))


def next_state(report: MonitorReport) -> MonitorState:
    """This run's observations, with the previous observation kept for every
    source this run could not observe."""
    observed = [o for o in report.observations if o.observed]
    return MonitorState(checked_on=report.checked_on, observations=observed + report.carried_over)


def save_state(path: Path, report: MonitorReport) -> None:
    """Save this run's observation. A failed run observed nothing, so it saves
    nothing: the previous observation stays the baseline."""
    if report.failure:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(next_state(report).model_dump_json(indent=1) + "\n", encoding="utf-8")


# --- Report ------------------------------------------------------------------


def _cell(value: object, limit: int = 120) -> str:
    """A table cell as a code span: register text cannot format the issue, link
    or mention anyone."""
    if value is None or value == "":
        return "(none)"
    if isinstance(value, tuple):
        text = ", ".join(value) if value else "(empty)"
    else:
        text = str(value)
    text = " ".join(text.replace("`", "'").split())
    if len(text) > limit:
        text = text[: limit - 3] + "..."
    return "`" + text.replace("|", "\\|") + "`"


_HEADLINES = {
    Outcome.OK: "every source was observed, every check passed and no difference needs attention.",
    Outcome.UNKNOWN: (
        "no finding, but at least one source could not be read from ESMA or from a recent "
        "archived copy, so its checks did not run."
    ),
    Outcome.ISSUE: (
        "a check failed or a difference since the previous run needs the owner. The refresh "
        "itself went on; what it recorded is decided by its own checks."
    ),
}

_VIA = {"esma": "ESMA", "archive": "Wayback Machine copy", "fixture": "fixture"}


def render_report(report: MonitorReport) -> str:
    title = f"## ESMA source monitor, {report.checked_on}: {report.outcome.value.upper()}"
    if report.failure:
        return "\n".join(
            [
                title,
                "",
                "Outcome: the source monitor itself failed, so no source was checked. The "
                "refresh went on; what it recorded is decided by its own checks. "
                "`data/source-monitor.json` was left as it was.",
                "",
                f"Error: {_cell(report.failure, 300)}",
                "",
                f"Runbook: [docs/runbook-esma-source-change.md]({RUNBOOK_URL}).",
                "",
                f"<!-- {FINGERPRINT_MARKER}: {report.fingerprint()} -->",
                "",
            ]
        )
    lines = [
        title,
        "",
        f"Outcome: {_HEADLINES[report.outcome]}",
        "",
        "### Sources used",
        "",
        "| Source | Bytes from | Captured | ESMA's answer | Last-Modified | Rows |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for o in report.observations:
        if o.observed:
            used = _VIA.get(o.via or "", "?")
            answer = f"refused: {o.esma_refusal}" if o.esma_refusal else "answered"
            if o.via == "fixture":
                answer = "not asked (offline run)"
        else:
            used = "nothing"
            answer = o.error
        lines.append(
            f"| {_cell(o.source_id)} | {used} | {_cell(o.archived_at)} | {_cell(answer)} "
            f"| {_cell(o.last_modified)} | {_cell(o.row_count)} |"
        )
    lines.append("")

    failed = [c for c in report.checks if not c.passed]
    lines.append(f"### Checks ({len(report.checks) - len(failed)} of {len(report.checks)} passed)")
    lines.append("")
    lines.append("| Source | Check | Result | Detail |")
    lines.append("| --- | --- | --- | --- |")
    for check in sorted(report.checks, key=lambda c: c.passed):
        result = "pass" if check.passed else "FAIL"
        lines.append(
            f"| {_cell(check.source_id)} | {check.check} | {result} | {_cell(check.detail)} |"
        )
    lines.append("")

    since = f" ({report.previous_checked_on})" if report.previous_checked_on else ""
    lines.append(f"### Differences since the previous run{since}")
    lines.append("")
    if not report.classified:
        lines.append("None, or no previous run to compare with.")
    else:
        lines.append("| Source | Attribute | Previous | Current | Decision |")
        lines.append("| --- | --- | --- | --- | --- |")
        for item in sorted(report.classified, key=lambda c: c.action is not Action.ISSUE):
            d = item.difference
            lines.append(
                f"| {_cell(d.source_id)} | {d.attribute} | {_cell(d.previous)} "
                f"| {_cell(d.current)} | {item.action.value}: {_cell(item.reason)} |"
            )
    if report.carried_over:
        kept = ", ".join(o.source_id for o in report.carried_over)
        lines.append("")
        lines.append(f"Not observed this time, previous observation kept as the baseline: {kept}.")
    lines.append("")
    if report.outcome is Outcome.ISSUE:
        lines.append(
            f"Runbook: [docs/runbook-esma-source-change.md]({RUNBOOK_URL}). The owner "
            "updates the source within one week, source-first."
        )
        lines.append("")
    lines.append(f"<!-- {FINGERPRINT_MARKER}: {report.fingerprint()} -->")
    lines.append("")
    return "\n".join(lines)


def annotation_lines(report: MonitorReport) -> list[str]:
    """GitHub Actions annotations: one summary line, and one per finding."""
    summary = (
        f"::notice title=ESMA source monitor::{report.outcome.value}: "
        f"{len(report.issue_items())} finding(s); the report is in the job summary"
    )
    lines = [summary]
    if report.failure:
        lines.append(
            "::error title=ESMA source monitor::the monitor failed and checked nothing; "
            f"the refresh went on: {' '.join(report.failure.split())[:400]}"
        )
    for item in report.issue_items():
        lines.append(f"::warning title=ESMA source monitor::{' '.join(item.split())[:400]}")
    for observation in report.observations:
        if not observation.observed and not observation.permanent:
            lines.append(
                f"::warning title=ESMA source monitor::{observation.source_id} not observed: "
                f"{' '.join(observation.error.split())[:400]}"
            )
    return lines
