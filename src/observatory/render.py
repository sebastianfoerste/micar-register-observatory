"""Render the README dashboard and the machine-readable feed."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from observatory.coverage import DEEP_LINT_CLASSES
from observatory.diff import removal_churn
from observatory.models import ChangeRecord, Snapshot

DASHBOARD_START = "<!-- dashboard:start -->"
DASHBOARD_END = "<!-- dashboard:end -->"

MAX_CHANGE_ROWS = 25

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


def _linkify(wp_url: str) -> str:
    url = wp_url.strip()
    if not url:
        return ""
    href = url if "://" in url else f"https://{url}"
    label = url if len(url) <= 60 else url[:57] + "..."
    return f"[{label}]({href})"


def render_dashboard(snapshot: Snapshot, changes: list[ChangeRecord]) -> str:
    lines: list[str] = []
    lines.append(f"**Register snapshot: {snapshot.snapshot_date}** "
                 "(refreshed weekly from the public ESMA interim MiCAR register)")
    lines.append("")

    lines.append("### Register totals")
    lines.append("")
    lines.append("| Register | Entries | Source status |")
    lines.append("| --- | ---: | --- |")
    for register in snapshot.registers:
        status = "ok" if register.fetched else f"fetch failed: {register.fetch_error}"
        lines.append(
            f"| [{register.title}]({register.source_url}) "
            f"| {len(register.entries)} | {status} |"
        )
    lines.append("")

    wp_entries = [
        entry
        for register in snapshot.registers
        if register.kind == "whitepaper" and register.fetched
        for entry in register.entries
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
            lines.append(f"| {state} | {count} |")
        remainder = len(state_counts) - 10
        if remainder > 0:
            lines.append(f"| ...and {remainder} more | |")
        lines.append("")

    lines.extend(_removal_lines(snapshot, changes))

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
                    f"| {change.entity_name} | {change.member_state} "
                    f"| {_linkify(change.wp_url)} |"
                )
            if len(rows) > MAX_CHANGE_ROWS:
                lines.append(
                    f"| ...and {len(rows) - MAX_CHANGE_ROWS} more "
                    "(see `data/changelog.jsonl`) | | | | |"
                )
    lines.append("")
    return "\n".join(lines)


def _removal_lines(snapshot: Snapshot, changes: list[ChangeRecord]) -> list[str]:
    if not changes:
        return []
    since = min(change.snapshot_date for change in changes)
    churn = removal_churn(changes, snapshot)
    lines = ["### Entries no longer listed", ""]
    if not churn:
        lines.append(f"No register entry has dropped out of the export since {since}.")
        lines.append("")
        return lines
    lines.append(
        f"Counted since the first snapshot ({since}). A removal is an entry that "
        "the previous weekly export listed and the next one does not. It is a "
        "temporary drop when the same entry is "
        "listed again in a later snapshot, and a net removal when it has not been "
        f"listed again as of {snapshot.snapshot_date}. A net removal can be a "
        "withdrawal, an upstream correction or a changed white-paper URL (shown as "
        "removed + added); the export does not say which."
    )
    lines.append("")
    lines.append("| Register | Removals | Listed again later | Net removals |")
    lines.append("| --- | ---: | ---: | ---: |")
    for item in churn:
        lines.append(
            f"| {item.register_slug} | {item.removed} | {item.relisted} "
            f"| {item.net} |"
        )
    if len(churn) > 1:
        lines.append(
            f"| all registers | {sum(item.removed for item in churn)} "
            f"| {sum(item.relisted for item in churn)} "
            f"| {sum(item.net for item in churn)} |"
        )
    lines.append("")
    return lines


def update_readme(readme_path: Path, dashboard: str) -> None:
    text = readme_path.read_text(encoding="utf-8")
    start = text.index(DASHBOARD_START) + len(DASHBOARD_START)
    end = text.index(DASHBOARD_END)
    readme_path.write_text(
        text[:start] + "\n" + dashboard + text[end:], encoding="utf-8"
    )


def write_feed(feed_path: Path, snapshot: Snapshot, changes: list[ChangeRecord]) -> None:
    recent = [change.model_dump() for change in changes[-200:]]
    payload = {
        "snapshot_date": snapshot.snapshot_date,
        "registers": [
            {
                "slug": register.slug,
                "title": register.title,
                "entries": len(register.entries),
                "fetched": register.fetched,
            }
            for register in snapshot.registers
        ],
        "recent_changes": recent,
    }
    feed_path.parent.mkdir(parents=True, exist_ok=True)
    feed_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
