"""Compute report metrics from an observatory snapshot. Pure functions."""

from __future__ import annotations

from collections import Counter

# Link classes whose URL extension names a format the micar-whitepaper-linter can
# parse (XHTML/HTML, JSON, DOCX). The class comes from the URL alone: it is a proxy
# for a structured document, not a check that the file is Inline XBRL. Shared with
# the dashboard so the two cannot drift apart.
from observatory.coverage import DEEP_LINT_CLASSES as DEEP_LINT_CANDIDATE_CLASSES
from observatory.models import Snapshot


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
    deep_lint_candidates = sum(
        formats.get(fmt, 0) for fmt in DEEP_LINT_CANDIDATE_CLASSES
    )
    no_extension = formats.get("unspecified", 0)

    member_states = Counter(
        (entry.get("member_state") or "?") for entry in whitepapers
    )

    register_totals = {
        register["slug"]: len(register.get("entries", []))
        for register in snapshot.get("registers", [])
        if register.get("fetched")
    }

    metrics = {
        "snapshot_date": snapshot.get("snapshot_date"),
        "total_whitepapers": total,
        "format_counts": dict(formats.most_common()),
        "deep_lint_candidates": deep_lint_candidates,
        "deep_lint_candidate_pct": pct(deep_lint_candidates),
        "pdf": formats.get("pdf", 0),
        "pdf_pct": pct(formats.get("pdf", 0)),
        "no_recognised_extension": no_extension,
        "no_recognised_extension_pct": pct(no_extension),
        "member_states": member_states.most_common(),
        "register_totals": register_totals,
    }
    metrics["entity_totals"] = entity_totals(snapshot)
    return metrics


def entity_totals(snapshot: dict) -> dict:
    """Rows and distinct entities per fetched register. A firm can have several
    rows (a second CASP authorisation, several white papers); the CASP register
    also gives the firms with a withdrawal date (None before v2 snapshots)."""
    totals: dict[str, dict] = {}
    for register in Snapshot.model_validate(snapshot).registers:
        if not register.fetched:
            continue
        totals[register.slug] = {"rows": len(register.rows()), "entities": register.entity_count()}
        if register.slug == "casps":
            totals[register.slug]["with_withdrawal_date"] = (
                register.entities_with_withdrawal_date()
            )
    return totals
