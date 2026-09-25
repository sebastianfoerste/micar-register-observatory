"""Compute report metrics from an observatory snapshot. Pure functions."""

from __future__ import annotations

from collections import Counter

# Formats the micar-whitepaper-linter can parse deterministically. These are the
# "structured machine-readable" documents; PDF and bare landing pages are not.
MACHINE_READABLE = {"xhtml/html", "json", "docx"}


def whitepaper_entries(snapshot: dict) -> list[dict]:
    return [
        entry
        for register in snapshot.get("registers", [])
        if register.get("kind") == "whitepaper" and register.get("fetched")
        for entry in register.get("entries", [])
    ]


def analyze(snapshot: dict) -> dict:
    whitepapers = whitepaper_entries(snapshot)
    total = len(whitepapers)

    def pct(n: int) -> float:
        return round(100 * n / total, 1) if total else 0.0

    formats = Counter(entry.get("format_class", "none") for entry in whitepapers)
    machine_readable = sum(formats.get(fmt, 0) for fmt in MACHINE_READABLE)
    landing = formats.get("unspecified", 0)

    member_states = Counter(
        (entry.get("member_state") or "?") for entry in whitepapers
    )

    register_totals = {
        register["slug"]: len(register.get("entries", []))
        for register in snapshot.get("registers", [])
        if register.get("fetched")
    }

    return {
        "snapshot_date": snapshot.get("snapshot_date"),
        "total_whitepapers": total,
        "format_counts": dict(formats.most_common()),
        "machine_readable": machine_readable,
        "machine_readable_pct": pct(machine_readable),
        "pdf": formats.get("pdf", 0),
        "pdf_pct": pct(formats.get("pdf", 0)),
        "landing_page": landing,
        "landing_page_pct": pct(landing),
        "member_states": member_states.most_common(),
        "register_totals": register_totals,
    }
