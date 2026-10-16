"""The weekly digest (digests/YYYY-MM-DD.md) and the Atom feed of recorded
snapshots (docs/changes.atom).

Both are derived from the recorded snapshots and the changelog. A digest lists
every change record of one snapshot in prose a person can read; the Atom feed has
one entry per snapshot, newest first, linking to its digest. They state what the
exports show and make no assessment of any named party.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path

from observatory.config import RAW_URL, REPO_URL
from observatory.models import ChangeRecord, Snapshot
from observatory.store import load_snapshot, snapshot_dates

KINDS = ("added", "changed", "missing", "removed", "restored")

ATOM_NS = "http://www.w3.org/2005/Atom"
ATOM_ENTRIES = 52  # a year of weekly snapshots
FEED_ID = "tag:github.com,2026:sebastianfoerste/micar-register-observatory/changes"

MAX_VALUE = 80

_MARKDOWN_SPECIAL = re.compile(r"([\\`*_\[\]<>|~])")
_PLAIN_URL = re.compile(r"https?://[^\s<>]+")


def text(value: str) -> str:
    """Register text as inline Markdown: one line, markup characters escaped."""
    return _MARKDOWN_SPECIAL.sub(r"\\\1", " ".join(value.split()))


def link(url: str) -> str:
    url = " ".join(url.split())
    return f"<{url}>" if _PLAIN_URL.fullmatch(url) else text(url)


def code(value: str) -> str:
    value = " ".join(value.split())
    if not value:
        return "(blank)"
    if len(value) > MAX_VALUE:
        value = value[: MAX_VALUE - 1] + "…"
    return f"`` {value} ``" if "`" in value else f"`{value}`"


def digest_url(snapshot_date: str) -> str:
    return f"{REPO_URL}/blob/main/digests/{snapshot_date}.md"


def _counts(records: list[ChangeRecord]) -> Counter[str]:
    return Counter(record.change for record in records)


def _summary(counts: Counter[str]) -> str:
    return ", ".join(f"{counts[kind]} {kind}" for kind in KINDS if counts[kind])


def _record_line(record: ChangeRecord) -> list[str]:
    head = [f"**{record.register_slug}**", text(record.entity_name) or "(no name)"]
    if record.member_state:
        head.append(text(record.member_state))
    if record.lei:
        head.append(f"LEI {text(record.lei)}")
    if record.wp_url:
        head.append(link(record.wp_url))
    lines = ["- " + " · ".join(head)]
    for change in record.changed_fields:
        lines.append(f"  - `{change.field}`: {code(change.old)} → {code(change.new)}")
    if record.change == "changed" and not record.changed_fields and record.detail:
        lines.append(f"  - {text(record.detail)}")
    if record.subtypes:
        lines.append("  - " + ", ".join(f"`{subtype}`" for subtype in record.subtypes))
    return lines


def render_digest(snapshot: Snapshot, previous_date: str, records: list[ChangeRecord]) -> str:
    """The digest of one snapshot; `records` are the change records it wrote."""
    date = snapshot.snapshot_date
    compared = (
        f"compared with the snapshot of {previous_date}" if previous_date else "the first snapshot"
    )
    lines = [
        f"# MiCAR register changes recorded on {date}",
        "",
        f"The weekly snapshot of the ESMA interim MiCAR register recorded on {date}, {compared}. "
        "It lists what the register exports show and makes no assessment of any issuer, offeror "
        f"or crypto-asset service provider. Generated from `data/snapshots/{date}.json` and "
        "`data/changelog.jsonl`.",
        "",
        "| Register | Rows | Entities | " + " | ".join(kind.capitalize() for kind in KINDS) + " |",
        "| --- | ---: | ---: | " + " | ".join("---:" for _ in KINDS) + " |",
    ]
    by_register: dict[str, list[ChangeRecord]] = defaultdict(list)
    for record in records:
        by_register[record.register_slug].append(record)
    for register in snapshot.registers:
        counts = _counts(by_register[register.slug])
        lines.append(
            f"| {register.title}, `{register.slug}` | {len(register.rows())} "
            f"| {register.entity_count()} | " + " | ".join(str(counts[kind]) for kind in KINDS)
            + " |"
        )
    lines.append("")

    baselines = [record for record in records if record.change == "baseline"]
    for record in baselines:
        lines.append(f"- `{record.register_slug}`: {text(record.detail)}.")
    if baselines:
        lines.append("")
    if not records:
        lines.extend(["No register changes since the previous snapshot.", ""])
    for kind in KINDS:
        of_kind = [record for record in records if record.change == kind]
        if not of_kind:
            continue
        lines.extend([f"## {kind.capitalize()} ({len(of_kind)})", ""])
        for record in of_kind:
            lines.extend(_record_line(record))
        lines.append("")

    absences = [r for r in records if r.change in ("missing", "removed", "restored")]
    if any(record.record_version >= 2 for record in absences):
        lines.append(
            "`missing`: not in this export for the first time. `removed`: not in two "
            "consecutive exports. `restored`: listed again after an absence."
        )
        lines.append("")
    if any(record.record_version < 2 for record in absences):
        lines.append(
            "These records were written before October 2026 (record version 1): `removed` "
            "means not in this export, for the first time, and a row that was listed again "
            "later is `added`."
        )
        lines.append("")
    lines.append(
        "Every record, with old and new values: `data/changelog.jsonl`; as a table: "
        "`data/exports/changes.csv`."
    )
    return "\n".join(lines) + "\n"


def write_digests(folder: Path, data_dir: Path, changes: list[ChangeRecord]) -> list[Path]:
    """Write the digest of every recorded snapshot that has none, and of the latest.

    Digests already written are left alone: they are what was published that week.
    """
    dates = snapshot_dates(data_dir)
    by_date: dict[str, list[ChangeRecord]] = defaultdict(list)
    for record in changes:
        by_date[record.snapshot_date].append(record)
    written = []
    for index, date in enumerate(dates):
        path = folder / f"{date}.md"
        if path.exists() and date != dates[-1]:
            continue
        previous = dates[index - 1] if index else ""
        digest = render_digest(load_snapshot(data_dir, date), previous, by_date[date])
        folder.mkdir(parents=True, exist_ok=True)
        path.write_text(digest, encoding="utf-8")
        written.append(path)
    return written


def _element(parent: ET.Element, tag: str, value: str = "", **attributes: str) -> ET.Element:
    element = ET.SubElement(parent, f"{{{ATOM_NS}}}{tag}", attributes)
    if value:
        element.text = value
    return element


def render_atom(dates: list[str], changes: list[ChangeRecord]) -> str:
    """An Atom feed with one entry per recorded snapshot, newest first."""
    by_date: dict[str, list[ChangeRecord]] = defaultdict(list)
    for record in changes:
        by_date[record.snapshot_date].append(record)
    recent = list(reversed(dates[-ATOM_ENTRIES:]))
    ET.register_namespace("", ATOM_NS)
    feed = ET.Element(f"{{{ATOM_NS}}}feed")
    _element(feed, "id", FEED_ID)
    _element(feed, "title", "MiCAR Register Observatory: weekly register changes")
    _element(
        feed,
        "subtitle",
        "One entry per weekly snapshot of the ESMA interim MiCAR register: what was added, "
        "changed, missing, removed or restored.",
    )
    _element(feed, "updated", f"{recent[0] if recent else '1970-01-01'}T00:00:00Z")
    _element(
        feed, "link", rel="self", type="application/atom+xml", href=f"{RAW_URL}/docs/changes.atom"
    )
    _element(feed, "link", rel="alternate", type="text/html", href=REPO_URL)
    author = _element(feed, "author")
    _element(author, "name", "MiCAR Register Observatory")
    _element(author, "uri", REPO_URL)
    _element(feed, "generator", "micar-register-observatory", uri=REPO_URL)
    for date in recent:
        records = by_date[date]
        rows = [record for record in records if record.change != "baseline"]
        counts = _counts(rows)
        if rows:
            title = f"{date}: {_summary(counts)}"
        elif records:
            title = f"{date}: first snapshot"
        else:
            title = f"{date}: no changes"
        by_register: dict[str, list[ChangeRecord]] = defaultdict(list)
        for record in records:
            by_register[record.register_slug].append(record)
        summary = []
        for slug, of_register in sorted(by_register.items()):
            counts = _counts(of_register)
            summary += [f"{slug}: {record.detail}" for record in of_register
                        if record.change == "baseline"]
            if any(counts[kind] for kind in KINDS):
                summary.append(f"{slug}: {_summary(counts)}")
        entry = _element(feed, "entry")
        _element(entry, "id", f"{FEED_ID}/{date}")
        _element(entry, "title", title)
        _element(entry, "updated", f"{date}T00:00:00Z")
        _element(entry, "link", rel="alternate", type="text/html", href=digest_url(date))
        _element(entry, "summary", "; ".join(summary) or "No register changes.", type="text")
    ET.indent(feed)
    return '<?xml version="1.0" encoding="utf-8"?>\n' + ET.tostring(feed, encoding="unicode") + "\n"


def write_atom(path: Path, data_dir: Path, changes: list[ChangeRecord]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_atom(snapshot_dates(data_dir), changes), encoding="utf-8")
