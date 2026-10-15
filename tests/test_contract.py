"""The published files must keep matching contracts/: eu-reg-mcp and other
consumers read them from main, so schema changes only ever add fields."""

import json
import shutil
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from referencing import Registry, Resource

from observatory.__main__ import cmd_refresh
from observatory.fetch import Download
from observatory.models import ChangeRecord, RegisterEntry, RegisterSnapshot
from observatory.store import load_raw, save_raw
from test_pipeline import FIXTURES, args_for, seed_readme

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = ROOT / "contracts"
SCHEMAS = {
    path.name: json.loads(path.read_text(encoding="utf-8"))
    for path in sorted(CONTRACTS.glob("*.schema.json"))
}
REGISTRY = Registry().with_resources(
    (schema["$id"], Resource.from_contents(schema)) for schema in SCHEMAS.values()
)
SNAPSHOT_V1 = "micar-register.snapshot.v1.schema.json"
SNAPSHOT_V2 = "micar-register.snapshot.v2.schema.json"
CHANGELOG = "changelog.v1.schema.json"
FEED = "feed.v1.schema.json"
RAW_MANIFEST = "raw-manifest.v1.schema.json"


def errors(schema_name: str, instance: object) -> list[str]:
    validator = Draft202012Validator(
        SCHEMAS[schema_name],
        registry=REGISTRY,
        format_checker=Draft202012Validator.FORMAT_CHECKER,
    )
    return [
        f"{'/'.join(str(part) for part in error.absolute_path)}: {error.message}"
        for error in validator.iter_errors(instance)
    ][:5]


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def is_v2(snapshot: dict) -> bool:
    return all("columns" in register for register in snapshot["registers"])


@pytest.mark.parametrize("name", sorted(SCHEMAS))
def test_every_contract_is_a_valid_schema(name: str) -> None:
    Draft202012Validator.check_schema(SCHEMAS[name])


def test_v2_only_adds_to_v1() -> None:
    v1, v2 = SCHEMAS[SNAPSHOT_V1], SCHEMAS[SNAPSHOT_V2]
    assert v2["required"] == v1["required"] and v2["additionalProperties"] is False
    v1_register = v1["properties"]["registers"]["items"]
    v1_entry = v1_register["properties"]["entries"]["items"]
    assert set(v1_register["required"]) <= set(v2["$defs"]["register"]["required"])
    assert set(v1_entry["required"]) <= set(v2["$defs"]["entry"]["required"])


def test_the_contracts_describe_every_field_the_code_writes() -> None:
    v2 = SCHEMAS[SNAPSHOT_V2]["$defs"]
    assert set(v2["entry"]["properties"]) == set(RegisterEntry.model_fields)
    assert set(v2["entry"]["required"]) == set(RegisterEntry.model_fields)
    assert set(v2["register"]["properties"]) == set(RegisterSnapshot.model_fields)
    assert set(SCHEMAS[CHANGELOG]["properties"]) == set(ChangeRecord.model_fields)


def test_the_raw_manifest_contract_describes_what_save_raw_writes(tmp_path: Path) -> None:
    download = Download(body=b"a,b\n", url="u", retrieved_at="2026-10-19T06:17:03Z")
    folder = save_raw(tmp_path, "2026-10-19", {"casps": download}, recorded_as="snapshot")
    manifest = read_json(folder / "manifest.json")
    schema = SCHEMAS[RAW_MANIFEST]
    assert set(manifest) == set(schema["properties"])
    assert set(manifest["files"][0]) == set(schema["properties"]["files"]["items"]["properties"])
    assert errors(RAW_MANIFEST, manifest) == []


def test_the_committed_snapshot_matches_the_contract() -> None:
    latest = read_json(ROOT / "data" / "latest.json")
    assert errors(SNAPSHOT_V1, latest) == []
    if is_v2(latest):
        assert errors(SNAPSHOT_V2, latest) == []


def test_every_committed_snapshot_matches_v1() -> None:
    for path in sorted((ROOT / "data" / "snapshots").glob("*.json")):
        assert errors(SNAPSHOT_V1, read_json(path)) == [], path.name


def check_raw_archives(data: Path) -> int:
    """Check every archived export against its manifest and the snapshot it became."""
    manifests = sorted((data / "raw").glob("*/manifest.json"))
    for path in manifests:
        manifest = read_json(path)
        assert errors(RAW_MANIFEST, manifest) == [], path
        date = manifest["snapshot_date"]
        assert path.parent.name == date
        folder = "snapshots" if manifest["recorded_as"] == "snapshot" else "quarantine"
        snapshot = read_json(data / folder / f"{date}.json")
        recorded = {r["slug"]: r.get("source_sha256") for r in snapshot["registers"]}
        for item in manifest["files"]:
            load_raw(data, date, item["slug"])  # raises when the bytes do not match
            assert recorded[item["slug"]] == item["sha256"], f"{path}: {item['slug']}"
    return len(manifests)


def test_every_committed_raw_archive_matches_its_manifest_and_snapshot() -> None:
    check_raw_archives(ROOT / "data")


def test_the_committed_changelog_and_feed_match_the_contract() -> None:
    for number, record in enumerate(read_jsonl(ROOT / "data" / "changelog.jsonl"), start=1):
        assert errors(CHANGELOG, record) == [], f"changelog.jsonl line {number}"
    assert errors(FEED, read_json(ROOT / "docs" / "feed.json")) == []


def test_pipeline_output_matches_v1_and_v2(tmp_path: Path) -> None:
    seed_readme(tmp_path)
    (tmp_path / "data").mkdir()
    edited = tmp_path / "edited"
    shutil.copytree(FIXTURES, edited)
    casps = edited / "casps.csv"
    casps.write_text(
        casps.read_text(encoding="utf-8").replace("FR|BE|DE", "FR|BE|DE|IT"), encoding="utf-8"
    )
    other = edited / "other-wp.csv"
    other.write_text(
        "".join(
            line
            for line in other.read_text(encoding="utf-8").splitlines(keepends=True)
            if "SKYGATE" not in line
        ),
        encoding="utf-8",
    )
    for date, fixtures in (("2026-10-19", FIXTURES), ("2026-10-26", edited)):
        assert cmd_refresh(args_for(tmp_path, date, fixtures)) == 0

    latest = read_json(tmp_path / "data" / "latest.json")
    assert is_v2(latest)
    assert errors(SNAPSHOT_V1, latest) == []
    assert errors(SNAPSHOT_V2, latest) == []
    records = read_jsonl(tmp_path / "data" / "changelog.jsonl")
    assert {record["change"] for record in records} == {"baseline", "changed", "missing"}
    assert any(record["changed_fields"] for record in records)
    for record in records:
        assert errors(CHANGELOG, record) == []
    assert errors(FEED, read_json(tmp_path / "docs" / "feed.json")) == []
    assert check_raw_archives(tmp_path / "data") == 2
