#!/usr/bin/env python3
"""Fail closed when the canonical MiCAR snapshot is incomplete or stale."""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path

EXPECTED_REGISTERS = {"other-wp", "emt-wp", "art-wp", "casps", "ncasp"}
DEFAULT_SNAPSHOT = Path(__file__).resolve().parents[1] / "data" / "latest.json"


def validate(snapshot_path: Path, *, as_of: dt.date, max_age_days: int) -> list[str]:
    errors: list[str] = []
    try:
        payload = json.loads(snapshot_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return [f"cannot read snapshot: {error}"]

    try:
        snapshot_date = dt.date.fromisoformat(payload["snapshot_date"])
    except (KeyError, TypeError, ValueError):
        errors.append("snapshot_date must be an ISO date")
        snapshot_date = None

    registers = payload.get("registers")
    if not isinstance(registers, list):
        errors.append("registers must be a list")
        registers = []

    slugs = {item.get("slug") for item in registers if isinstance(item, dict)}
    if slugs != EXPECTED_REGISTERS:
        missing = sorted(EXPECTED_REGISTERS - slugs)
        extra = sorted(slugs - EXPECTED_REGISTERS)
        errors.append(f"register set mismatch; missing={missing}, extra={extra}")

    failed = [
        item.get("slug", "unknown")
        for item in registers
        if isinstance(item, dict) and item.get("fetched") is not True
    ]
    if failed:
        errors.append(f"upstream fetch failed for: {', '.join(sorted(failed))}")

    if snapshot_date is not None:
        age = (as_of - snapshot_date).days
        if age < 0:
            errors.append(f"snapshot date {snapshot_date} is in the future")
        elif age > max_age_days:
            errors.append(
                f"snapshot is {age} days old, above the {max_age_days}-day limit"
            )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", type=Path, default=DEFAULT_SNAPSHOT)
    parser.add_argument("--as-of", type=dt.date.fromisoformat, default=dt.date.today())
    parser.add_argument("--max-age-days", type=int, default=14)
    args = parser.parse_args()

    errors = validate(args.snapshot, as_of=args.as_of, max_age_days=args.max_age_days)
    if errors:
        for error in errors:
            print(f"PENDING: {error}")
        return 1

    payload = json.loads(args.snapshot.read_text(encoding="utf-8"))
    print(
        "freshness gate passed: "
        f"snapshot={payload['snapshot_date']}, as_of={args.as_of}, "
        f"max_age_days={args.max_age_days}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
