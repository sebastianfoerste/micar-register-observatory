"""Render the README dashboard and the machine-readable feed."""

from __future__ import annotations

import email.utils
import json
import re
from collections import Counter
from pathlib import Path

from pydantic import BaseModel

from observatory.coverage import DEEP_LINT_CLASSES
from observatory.diff import Shrink
from observatory.digest import text
from observatory.models import ChangeRecord, RegisterSnapshot, Snapshot

DASHBOARD_START = "<!-- dashboard:start -->"
DASHBOARD_END = "<!-- dashboard:end -->"

MAX_CHANGE_ROWS = 25

ABSENCE_KINDS = {"missing", "removed", "restored"}

_FORMAT_LABELS = {
    "xhtml/html": "XHTML / HTML",
    "json": "JSON",
    "docx": "DOCX",
    "pdf": "PDF",
    "unspecified": (
        "No recognised file extension (bare domain, landing page or other page)"
    ),
    "none": "No link in register",
}


class Quarantine(BaseModel):
    """An export set aside because a register dropped sharply (diff.export_shrinks)."""

    snapshot_date: str
    shrinks: list[Shrink]


# A single URL: no whitespace and none of the characters that end a Markdown
# link or a table cell. A bare host gets `https://` first (see _linkify).
_LINK_URL = re.compile(r"https?://[^\s<>|]+")
_BARE_HOST = re.compile(r"[^\s/?#<>|]+\.[^\s/?#<>|]+(?:[/?#][^\s<>|]*)?")
MAX_LABEL = 60

# Percent-encoded in the href because they would end the link or the table cell.
# `*`, `_` and `~` stay as they are: encoding them can change the target.
_HREF_ESCAPES = {
    "(": "%28", ")": "%29", "[": "%5B", "]": "%5D", "<": "%3C", ">": "%3E",
    "|": "%7C", "`": "%60", "\\": "%5C", " ": "%20",
}


def _linkify(wp_url: str) -> str:
    """A register link as Markdown; every register value is untrusted text.

    A value that is one URL (or one bare host and path, which gets `https://`)
    becomes `[label](href)`: the label is the value cut at MAX_LABEL characters
    and escaped like any register text; the href percent-encodes only the
    characters that would end the link or the table cell (`_HREF_ESCAPES`).
    Anything else (several URLs in one cell, a code such as `EMT_NO_WP`, text)
    is rendered as escaped text without a link.
    """
    value = " ".join(wp_url.split())
    if not value:
        return ""
    if "://" in value:
        href = value
        linkable = _LINK_URL.fullmatch(value) is not None
    else:
        href = f"https://{value}"
        linkable = _BARE_HOST.fullmatch(value) is not None
    if not linkable:
        return text(value)
    label = value if len(value) <= MAX_LABEL else value[: MAX_LABEL - 3] + "..."
    href = "".join(_HREF_ESCAPES.get(char, char) for char in href)
    return f"[{text(label)}]({href})"


def http_date(value: str) -> str:
    """An HTTP date (the Last-Modified header) as YYYY-MM-DD; "" when unparseable."""
    try:
        return email.utils.parsedate_to_datetime(value).date().isoformat()
    except (TypeError, ValueError, IndexError):
        return ""


def _status(register: RegisterSnapshot) -> str:
    if not register.fetched:
        return f"fetch failed: {text(register.fetch_error)}"
    notes = []
    modified = http_date(register.source_last_modified)
    if modified:
        notes.append(f"file modified {modified}")
    if register.archived_at:
        captured = http_date(register.archived_at) or text(register.archived_at)
        notes.append(f"archived copy from the Wayback Machine, captured {captured}")
    return f"ok ({'; '.join(notes)})" if notes else "ok"


def _casp_line(casps: RegisterSnapshot) -> str:
    line = f"CASP register: {casps.entity_count()} firms in {len(casps.rows())} rows"
    withdrawn = casps.entities_with_withdrawal_date()
    if withdrawn is not None:
        line += f", {withdrawn} of them with a withdrawal date (`ac_authorisationEndDate`)"
    return line + "."


def render_dashboard(
    snapshot: Snapshot, changes: list[ChangeRecord], quarantine: Quarantine | None = None
) -> str:
    lines: list[str] = []
    lines.append(f"**Register snapshot: {snapshot.snapshot_date}** "
                 "(refreshed weekly from the public ESMA interim MiCAR register)")
    lines.append("")
    if quarantine is not None:
        drops = "; ".join(shrink.describe() for shrink in quarantine.shrinks)
        lines.append(
            f"> **The export of {quarantine.snapshot_date} was quarantined:** {drops}. "
            "It is kept under `data/quarantine/` and recorded only if the next export "
            f"shows the same drop. The figures below are from {snapshot.snapshot_date}."
        )
        lines.append("")

    lines.append("### Register totals")
    lines.append("")
    lines.append("| Register | Rows | Entities | Source status |")
    lines.append("| --- | ---: | ---: | --- |")
    for register in snapshot.registers:
        lines.append(
            f"| [{register.title}]({register.source_url}) "
            f"| {len(register.rows())} | {register.entity_count()} | {_status(register)} |"
        )
    lines.append("")
    lines.append(
        "Rows are lines of the register export; entities are distinct LEIs, or names "
        "where a row has none. One entity can have several rows: several white papers, "
        "or a second CASP authorisation."
    )
    casps = snapshot.register("casps")
    if casps is not None and casps.fetched:
        lines.append("")
        lines.append(_casp_line(casps))
    lines.append("")

    wp_entries = [
        entry
        for register in snapshot.registers
        if register.kind == "whitepaper" and register.fetched
        for entry in register.rows()
    ]
    if wp_entries:
        lines.append("### White paper format coverage")
        lines.append("")
        lines.append(
            "Classified by link shape only; a format is a deep-lint candidate, "
            "not a verified fact, until the document is fetched."
        )
        lines.append("")
        lines.append("| Linked format | Count | Deep-lint candidate |")
        lines.append("| --- | ---: | --- |")
        counts = Counter(entry.format_class for entry in wp_entries)
        for format_class, count in counts.most_common():
            candidate = "yes" if format_class in DEEP_LINT_CLASSES else "no"
            label = _FORMAT_LABELS.get(format_class, format_class)
            lines.append(f"| {label} | {count} | {candidate} |")
        lines.append("")

        lines.append("### Home Member States (white papers)")
        lines.append("")
        lines.append("| Member State | White papers |")
        lines.append("| --- | ---: |")
        state_counts = Counter(
            entry.member_state or "?" for entry in wp_entries
        )
        for state, count in state_counts.most_common(10):
            lines.append(f"| {text(state)} | {count} |")
        remainder = len(state_counts) - 10
        if remainder > 0:
            lines.append(f"| ...and {remainder} more | |")
        lines.append("")

    lines.append(f"### Changes in this snapshot ({snapshot.snapshot_date})")
    lines.append("")
    current_changes = [
        change for change in changes if change.snapshot_date == snapshot.snapshot_date
    ]
    if not current_changes:
        lines.append("No register changes since the previous snapshot.")
    else:
        baselines = [c for c in current_changes if c.change == "baseline"]
        rows = [c for c in current_changes if c.change != "baseline"]
        for baseline in baselines:
            lines.append(f"- `{baseline.register_slug}`: {baseline.detail}.")
        if baselines and rows:
            lines.append("")
        if rows:
            lines.append("| Change | Register | Entity | MS | Link |")
            lines.append("| --- | --- | --- | --- | --- |")
            for change in rows[:MAX_CHANGE_ROWS]:
                lines.append(
                    f"| {change.change} | {change.register_slug} "
                    f"| {text(change.entity_name)} | {text(change.member_state)} "
                    f"| {_linkify(change.wp_url)} |"
                )
            if len(rows) > MAX_CHANGE_ROWS:
                lines.append(
                    f"| ...and {len(rows) - MAX_CHANGE_ROWS} more "
                    "(see `data/changelog.jsonl`) | | | | |"
                )
            if any(change.change in ABSENCE_KINDS for change in rows):
                lines.append("")
                lines.append(
                    "`missing`: not in this export for the first time. "
                    "`removed`: not in two consecutive exports. "
                    "`restored`: listed again after an absence."
                )
    lines.append("")
    return "\n".join(lines)


def update_readme(readme_path: Path, dashboard: str) -> None:
    text = readme_path.read_text(encoding="utf-8")
    start = text.index(DASHBOARD_START) + len(DASHBOARD_START)
    end = text.index(DASHBOARD_END)
    readme_path.write_text(
        text[:start] + "\n" + dashboard + text[end:], encoding="utf-8"
    )


def write_feed(
    feed_path: Path,
    snapshot: Snapshot,
    changes: list[ChangeRecord],
    quarantine: Quarantine | None = None,
) -> None:
    recent = [change.model_dump() for change in changes[-200:]]
    payload = {
        "snapshot_date": snapshot.snapshot_date,
        "quarantine": quarantine.model_dump() if quarantine else None,
        "registers": [
            {
                "slug": register.slug,
                "title": register.title,
                "entries": len(register.rows()),
                "entities": register.entity_count(),
                "fetched": register.fetched,
                "source_last_modified": register.source_last_modified,
                "fetched_from": register.fetched_from,
                "archived_at": register.archived_at,
            }
            for register in snapshot.registers
        ],
        "recent_changes": recent,
    }
    feed_path.parent.mkdir(parents=True, exist_ok=True)
    feed_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
