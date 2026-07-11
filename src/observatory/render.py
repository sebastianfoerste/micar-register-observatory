"""Render the README dashboard and the machine-readable feed."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from observatory.content_verify import normalise_url
from observatory.coverage import DEEP_LINT_CLASSES
from observatory.models import ChangeRecord, RegisterEntry, Snapshot

DASHBOARD_START = "<!-- dashboard:start -->"
DASHBOARD_END = "<!-- dashboard:end -->"

MAX_CHANGE_ROWS = 25

_FORMAT_LABELS = {
    "xhtml/html": "XHTML / HTML-shaped link",
    "json": "JSON-shaped link",
    "docx": "DOCX-shaped link",
    "pdf": "PDF-shaped link",
    "unspecified": "Unspecified (landing page or bare domain)",
    "none": "No link in register",
}


def _linkify(wp_url: str) -> str:
    url = wp_url.strip()
    if not url:
        return ""
    href = url if "://" in url else f"https://{url}"
    label = url if len(url) <= 60 else url[:57] + "..."
    return f"[{label}]({href})"


def _whitepaper_entries(snapshot: Snapshot) -> list[RegisterEntry]:
    return [
        entry
        for register in snapshot.registers
        if register.kind == "whitepaper" and register.fetched
        for entry in register.entries
    ]


def content_verification_summary(entries: list[RegisterEntry]) -> dict:
    linked = [entry for entry in entries if entry.wp_url]
    checked_rows = [
        entry
        for entry in linked
        if entry.content_verification_status != "not_checked"
    ]
    groups = {}
    for entry in linked:
        groups.setdefault(normalise_url(entry.wp_url), []).append(entry)
    representatives = []
    for group in groups.values():
        checked = [
            entry
            for entry in group
            if entry.content_verification_status != "not_checked"
        ]
        if checked:
            representatives.append(max(checked, key=lambda entry: entry.verified_at))
    complete = [
        entry
        for entry in representatives
        if entry.content_verification_status == "verified"
    ]
    too_large = [
        entry
        for entry in representatives
        if entry.content_verification_status == "too_large"
    ]
    failed = [
        entry
        for entry in representatives
        if entry.content_verification_status not in {"verified", "too_large"}
    ]
    status_counts = Counter(
        entry.content_verification_status for entry in representatives
    )
    format_counts = Counter(
        entry.verified_format or "unknown" for entry in complete
    )
    timestamps = [
        entry.verified_at for entry in representatives if entry.verified_at
    ]
    return {
        "linked_register_rows": len(linked),
        "unique_link_targets": len(groups),
        "checked_register_rows": len(checked_rows),
        "checked_unique_targets": len(representatives),
        "complete_targets": len(complete),
        "too_large_targets": len(too_large),
        "failed_targets": len(failed),
        "inline_xbrl_targets": sum(1 for entry in complete if entry.inline_xbrl),
        "latest_verified_at": max(timestamps) if timestamps else None,
        "status_counts": dict(sorted(status_counts.items())),
        "verified_format_counts": dict(sorted(format_counts.items())),
    }


def render_dashboard(snapshot: Snapshot, changes: list[ChangeRecord]) -> str:
    lines: list[str] = []
    lines.append(
        f"**Register snapshot: {snapshot.snapshot_date}** "
        "(refreshed weekly from the public ESMA interim MiCAR register)"
    )
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

    wp_entries = _whitepaper_entries(snapshot)
    if wp_entries:
        lines.append("### White-paper register-link coverage")
        lines.append("")
        lines.append(
            "These classes describe the URL recorded by ESMA, not the bytes served by "
            "that URL. They identify crawl candidates and must not be reported as "
            "document-format prevalence."
        )
        lines.append("")
        lines.append("| Register-link class | Count | Deep-lint candidate |")
        lines.append("| --- | ---: | --- |")
        counts = Counter(entry.format_class for entry in wp_entries)
        for format_class, count in counts.most_common():
            candidate = "yes" if format_class in DEEP_LINT_CLASSES else "no"
            label = _FORMAT_LABELS.get(format_class, format_class)
            lines.append(f"| {label} | {count} | {candidate} |")
        lines.append("")

        verification = content_verification_summary(wp_entries)
        targets = verification["unique_link_targets"]
        checked_targets = verification["checked_unique_targets"]
        target_pct = checked_targets / targets * 100 if targets else 0
        rows = verification["linked_register_rows"]
        checked_rows = verification["checked_register_rows"]
        lines.append("### Content verification")
        lines.append("")
        lines.append(
            "Byte-level checks use bounded downloads, redirects, response metadata, "
            "file signatures, ZIP structure, JSON parsing, markup signatures, and "
            "Inline XBRL namespace or element markers. URL suffixes and declared "
            "Content-Type are not accepted as proof."
        )
        lines.append("")
        lines.append(
            f"**Checked: {checked_targets}/{targets} unique link targets "
            f"({target_pct:.1f}%), covering {checked_rows}/{rows} linked register rows.**"
        )
        lines.append("")
        lines.append("| Outcome | Count |")
        lines.append("| --- | ---: |")
        lines.append(
            f"| Complete response with SHA-256 | {verification['complete_targets']} |"
        )
        lines.append(
            f"| Exceeded byte limit | {verification['too_large_targets']} |"
        )
        lines.append(
            f"| Fetch or HTTP failure | {verification['failed_targets']} |"
        )
        lines.append(
            f"| Verified Inline XBRL document | {verification['inline_xbrl_targets']} |"
        )
        lines.append("")
        if verification["verified_format_counts"]:
            lines.append("| Verified format (complete responses) | Count |")
            lines.append("| --- | ---: |")
            for detected, count in verification["verified_format_counts"].items():
                lines.append(f"| {detected} | {count} |")
            lines.append("")
        else:
            lines.append(
                "No linked documents have been content-verified in the committed "
                "snapshot yet. Run `python -m observatory verify-content --limit 25` "
                "to create the first auditable batch."
            )
            lines.append("")

        lines.append("### Home Member States (white papers)")
        lines.append("")
        lines.append("| Member State | White papers |")
        lines.append("| --- | ---: |")
        state_counts = Counter(entry.member_state or "?" for entry in wp_entries)
        for state, count in state_counts.most_common(10):
            lines.append(f"| {state} | {count} |")
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


def update_readme(readme_path: Path, dashboard: str) -> None:
    text = readme_path.read_text(encoding="utf-8")
    start = text.index(DASHBOARD_START) + len(DASHBOARD_START)
    end = text.index(DASHBOARD_END)
    readme_path.write_text(
        text[:start] + "\n" + dashboard + text[end:], encoding="utf-8"
    )


def write_feed(feed_path: Path, snapshot: Snapshot, changes: list[ChangeRecord]) -> None:
    recent = [change.model_dump() for change in changes[-200:]]
    wp_entries = _whitepaper_entries(snapshot)
    payload = {
        "snapshot_date": snapshot.snapshot_date,
        "methodology": {
            "register_link_classification_basis": "URL shape only",
            "content_verification_basis": "bounded response bytes and structure",
        },
        "registers": [
            {
                "slug": register.slug,
                "title": register.title,
                "entries": len(register.entries),
                "fetched": register.fetched,
            }
            for register in snapshot.registers
        ],
        "whitepaper_register_link_classes": dict(
            sorted(Counter(entry.format_class for entry in wp_entries).items())
        ),
        "content_verification": content_verification_summary(wp_entries),
        "recent_changes": recent,
    }
    feed_path.parent.mkdir(parents=True, exist_ok=True)
    feed_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
