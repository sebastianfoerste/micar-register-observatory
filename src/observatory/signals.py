"""Review-gated integrity and movement signals for one register snapshot."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from observatory.coverage import DEEP_LINT_CLASSES
from observatory.models import ChangeRecord, Snapshot

SCHEMA = "micar-register-observatory.signal-room.v1"


def _canonical_sha256(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _register_signal(
    register,
    current_changes: list[ChangeRecord],
) -> dict[str, Any]:
    changes = [
        change
        for change in current_changes
        if change.register_slug == register.slug and change.change != "baseline"
    ]
    counts = Counter(change.change for change in changes)
    entry_ids = [entry.entry_id for entry in register.entries]
    duplicate_ids = len(entry_ids) - len(set(entry_ids))
    estimated_previous = max(
        0,
        len(register.entries) - counts["added"] + counts["removed"],
    )
    denominator = max(1, estimated_previous)
    removal_rate = counts["removed"] / denominator
    churn_rate = sum(counts.values()) / denominator

    reasons = []
    if not register.fetched:
        severity = "critical"
        reasons.append("source fetch failed")
    elif duplicate_ids:
        severity = "review"
        reasons.append(
            f"{duplicate_ids} non-unique stable entry IDs handled by multiset diff"
        )
    elif counts["removed"] >= 10 or removal_rate >= 0.05:
        severity = "review"
        reasons.append("removal volume crosses the review threshold")
    elif sum(counts.values()) >= 25 or churn_rate >= 0.15:
        severity = "review"
        reasons.append("row churn crosses the review threshold")
    elif changes:
        severity = "monitor"
        reasons.append("register movement detected")
    else:
        severity = "stable"
        reasons.append("no row movement detected")

    return {
        "signal_id": f"REGISTER.MOVEMENT.{register.slug.upper()}",
        "register_slug": register.slug,
        "severity": severity,
        "reasons": reasons,
        "current_entries": len(register.entries),
        "estimated_previous_entries": estimated_previous,
        "added": counts["added"],
        "changed": counts["changed"],
        "removed": counts["removed"],
        "removal_rate": round(removal_rate, 4),
        "churn_rate": round(churn_rate, 4),
        "duplicate_entry_ids": duplicate_ids,
        "source_fetched": register.fetched,
    }


def build_signal_room(
    snapshot: Snapshot,
    changes: list[ChangeRecord],
) -> dict[str, Any]:
    """Build factual movement indicators with explicit human-review boundaries."""

    current_changes = [
        change for change in changes if change.snapshot_date == snapshot.snapshot_date
    ]
    register_signals = [
        _register_signal(register, current_changes) for register in snapshot.registers
    ]
    whitepapers = [
        entry
        for register in snapshot.registers
        if register.kind == "whitepaper" and register.fetched
        for entry in register.entries
    ]
    state_counts = Counter(entry.member_state or "?" for entry in whitepapers)
    top_state, top_state_count = (
        state_counts.most_common(1)[0] if state_counts else ("-", 0)
    )
    whitepaper_count = len(whitepapers)
    top_state_share = top_state_count / whitepaper_count if whitepaper_count else 0.0
    hhi = (
        sum((count / whitepaper_count) ** 2 for count in state_counts.values())
        if whitepaper_count
        else 0.0
    )
    deep_lint_candidates = sum(
        entry.format_class in DEEP_LINT_CLASSES for entry in whitepapers
    )
    deep_lint_share = (
        deep_lint_candidates / whitepaper_count if whitepaper_count else 0.0
    )
    concentration_signal = {
        "signal_id": "WHITEPAPER.HOME_STATE.CONCENTRATION",
        "severity": "review" if top_state_share >= 0.5 else "information",
        "top_member_state": top_state,
        "top_member_state_entries": top_state_count,
        "top_member_state_share": round(top_state_share, 4),
        "herfindahl_hirschman_index": round(hhi, 4),
        "interpretation": (
            "Descriptive register concentration only. It is not a market-share "
            "or supervisory conclusion."
        ),
    }
    format_signal = {
        "signal_id": "WHITEPAPER.FORMAT.DEEP_LINT_CANDIDATES",
        "severity": "information",
        "whitepapers": whitepaper_count,
        "deep_lint_candidates": deep_lint_candidates,
        "deep_lint_candidate_share": round(deep_lint_share, 4),
        "interpretation": (
            "Candidate status is inferred from URL shape and requires document fetch verification."
        ),
    }
    severities = {signal["severity"] for signal in register_signals}
    if "critical" in severities or "review" in severities:
        status = "REVIEW_REQUIRED"
    elif "monitor" in severities:
        status = "MONITOR"
    else:
        status = "STABLE"
    input_payload = {
        "snapshot": snapshot.model_dump(mode="json"),
        "changes": [
            change.model_dump(mode="json")
            for change in sorted(
                current_changes,
                key=lambda item: (
                    item.register_slug,
                    item.change,
                    item.entry_id,
                ),
            )
        ],
    }
    payload = {
        "schema": SCHEMA,
        "snapshot_date": snapshot.snapshot_date,
        "status": status,
        "summary": {
            "critical_signals": sum(
                signal["severity"] == "critical" for signal in register_signals
            ),
            "review_signals": sum(
                signal["severity"] == "review" for signal in register_signals
            ),
            "monitor_signals": sum(
                signal["severity"] == "monitor" for signal in register_signals
            ),
            "source_failures": sum(not register.fetched for register in snapshot.registers),
            "current_change_records": sum(
                change.change != "baseline" for change in current_changes
            ),
        },
        "register_signals": register_signals,
        "market_structure_signals": [concentration_signal, format_signal],
        "input_sha256": _canonical_sha256(input_payload),
        "review_gate": (
            "Signals describe register movement and data integrity. Any conclusion "
            "about an issuer, service provider, market, or authority requires human review."
        ),
        "external_actions_allowed": False,
    }
    return {**payload, "signal_room_sha256": _canonical_sha256(payload)}


def write_signal_room(path: Path, signal_room: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(signal_room, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8",
    )
