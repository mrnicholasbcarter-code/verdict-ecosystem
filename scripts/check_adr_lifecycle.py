#!/usr/bin/env python3
"""Validate the evidence-bounded Verdict V2 ADR lifecycle index."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "ADR_LIFECYCLE.json"
DOC = ROOT / "docs" / "ADR_LIFECYCLE.md"

VALID_CLASSES = {"CURRENT", "PARTIALLY_TRUE", "SUPERSEDED", "DUPLICATE", "STALE", "MISSING_SUCCESSOR", "INVALID"}
VALID_LEVELS = {"VERIFIED", "INFERRED", "NOT_VERIFIED"}
EXPECTED_SNAPSHOTS = {
    "verdict-core": "e17a92062bc5ba9d7d0d8709535bc3412be31ba9",
    "verdict-core-memory": "c8935bb5222f3962f48e36567114d0a3e5f9d1b4",
    "verdict-node": "3e1a5ba78ba3a24de85d48e663113a3a7bf7e3c2",
    "verdict-continuity": "9d07081661efa51f7570b13b1e54f69975de7cfb",
}
EXPECTED_REFS = {
    "verdict-core": "origin/main",
    "verdict-core-memory": "origin/main",
    "verdict-node": "origin/master",
    "verdict-continuity": "origin/main",
}
EXPECTED_CLASSIFICATIONS = {
    "PARTIALLY_TRUE": 37,
    "DUPLICATE": 23,
    "STALE": 8,
    "MISSING_SUCCESSOR": 0,
    "SUPERSEDED": 2,
    "INVALID": 1,
}
EXPECTED_EVIDENCE_LEVELS = {"VERIFIED": 57, "NOT_VERIFIED": 8, "INFERRED": 6}
EXPECTED_DUPLICATE_GROUPS = 21
EXPECTED_DUPLICATE_FILES = 42
EXPECTED_REPOSITORY_URLS = {
    "verdict-core": "https://github.com/mrnicholasbcarter-code/verdict-core",
    "verdict-core-memory": "https://github.com/mrnicholasbcarter-code/verdict-core-memory",
    "verdict-node": "https://github.com/mrnicholasbcarter-code/verdict-node",
    "verdict-continuity": "https://github.com/mrnicholasbcarter-code/verdict-continuity",
}
SHA256 = re.compile(r"[0-9a-f]{64}")
# Immutable authority for the independently reviewed canonical semantic payload.
# Evidence metadata is a redundant copy, not the trust root.
EXPECTED_REVIEWED_AUDIT_SHA256 = "dbf24ab9f60276955b53fff59ec1a87a38f0e7616c79c98978679e9485b50838"


def load() -> dict:
    return json.loads(EVIDENCE.read_text(encoding="utf-8"))


def reviewed_audit_digest(data: dict) -> str:
    payload = {
        "source_snapshots": data.get("source_snapshots"),
        "source_snapshot_refs": data.get("source_snapshot_refs"),
        "excluded_files": data.get("excluded_files"),
        "duplicate_groups": data.get("duplicate_groups"),
        "lifecycle_index": data.get("lifecycle_index"),
        "limitations": data.get("limitations"),
    }
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def validate(data: dict) -> list[str]:
    errors: list[str] = []
    records = data.get("lifecycle_index", [])
    counts = data.get("corrected_counts", {})

    if data.get("source_snapshots") != EXPECTED_SNAPSHOTS:
        errors.append("source snapshots differ from the audited exact SHAs")
    if data.get("source_snapshot_refs") != EXPECTED_REFS:
        errors.append("source snapshot refs differ from the audited refs")
    if data.get("source_repository_urls") != EXPECTED_REPOSITORY_URLS:
        errors.append("source repository URLs differ from the audited repositories")
    if not data.get("metadata", {}).get("source_captured_at"):
        errors.append("source capture timestamp is missing")
    if data.get("metadata", {}).get("base_sha") != "7de8fc2e85e3ed07829583e30c848bb44d75bc21":
        errors.append("ecosystem base SHA is not the verified BOD-167 baseline")
    metadata_digest = data.get("metadata", {}).get("reviewed_audit_sha256")
    if not SHA256.fullmatch(metadata_digest or ""):
        errors.append("reviewed audit digest is missing or malformed")
    elif metadata_digest != EXPECTED_REVIEWED_AUDIT_SHA256:
        errors.append("reviewed audit metadata digest differs from the trusted validator constant")
    calculated_digest = reviewed_audit_digest(data)
    if calculated_digest != EXPECTED_REVIEWED_AUDIT_SHA256:
        errors.append("semantic audit content differs from the independently reviewed digest")
    if SHA256.fullmatch(metadata_digest or "") and calculated_digest != metadata_digest:
        errors.append("reviewed audit digest does not match semantic audit content")

    expected_counts = {"raw_files": 72, "excluded_fixtures": 1, "production_files": 71}
    for key, expected in expected_counts.items():
        if counts.get(key) != expected:
            errors.append(f"{key} expected {expected}, got {counts.get(key)}")
    if len(records) != 71:
        errors.append(f"lifecycle_index expected 71 records, got {len(records)}")
    if counts.get("exact_duplicate_hash_groups") != EXPECTED_DUPLICATE_GROUPS:
        errors.append("duplicate-group summary differs from reviewed baseline")
    if counts.get("files_in_exact_duplicate_groups") != EXPECTED_DUPLICATE_FILES:
        errors.append("duplicate-file summary differs from reviewed baseline")

    classifications = Counter(r.get("classification") for r in records)
    evidence_levels = Counter(r.get("evidence_level") for r in records)
    if classifications != Counter(counts.get("classifications", {})):
        errors.append("classification counts do not match lifecycle records")
    if evidence_levels != Counter(counts.get("evidence_levels", {})):
        errors.append("evidence-level counts do not match lifecycle records")
    if classifications != Counter(EXPECTED_CLASSIFICATIONS):
        errors.append("classification distribution differs from the reviewed audit baseline")
    if evidence_levels != Counter(EXPECTED_EVIDENCE_LEVELS):
        errors.append("evidence-level distribution differs from the reviewed audit baseline")
    if classifications.get("CURRENT", 0):
        errors.append("CURRENT must not be assigned without executable semantic proof")

    seen: set[tuple[str, str]] = set()
    for record in records:
        repo = record.get("repository")
        path = record.get("path")
        key = (repo, path)
        if key in seen:
            errors.append(f"duplicate lifecycle record: {repo}/{path}")
        seen.add(key)
        if record.get("classification") not in VALID_CLASSES:
            errors.append(f"invalid classification: {repo}/{path}")
        if record.get("evidence_level") not in VALID_LEVELS:
            errors.append(f"invalid evidence level: {repo}/{path}")
        digest = record.get("content_sha256", "")
        if not SHA256.fullmatch(digest):
            errors.append(f"invalid content SHA-256: {repo}/{path}")
        expected_url = f"{EXPECTED_REPOSITORY_URLS.get(repo)}/blob/{EXPECTED_SNAPSHOTS.get(repo)}/{path}"
        if record.get("source_url") != expected_url:
            errors.append(f"source URL is not pinned to exact SHA: {repo}/{path}")
        expected_locator = f"{repo}@{EXPECTED_SNAPSHOTS.get(repo)}:{path}"
        if record.get("source_locator") != expected_locator:
            errors.append(f"source locator is not pinned to exact SHA: {repo}/{path}")
        citations = record.get("citations") or []
        if not citations:
            errors.append(f"record has no citations: {repo}/{path}")
        for citation in citations:
            citation_repo, separator, citation_path = citation.partition("/")
            if not separator or citation_repo not in EXPECTED_SNAPSHOTS or not citation_path:
                errors.append(f"invalid citation locator: {repo}/{path}: {citation}")

    excluded = data.get("excluded_files", [])
    fixture_path = "benchmarks/fixtures/legit_workspace/docs/adr/ADR-001-spend.md"
    if len(excluded) != 1 or excluded[0].get("path") != fixture_path or excluded[0].get("repository") != "verdict-core":
        errors.append("the one benchmark fixture exclusion is not explicit and exact")
    if excluded and excluded[0].get("content_sha256") != "a3ec2752e48d3d22f9fff0530529647d64c2c64b6f5540623799bfdb8579db6c":
        errors.append("excluded fixture content SHA-256 differs from pinned source")
    if any("fixtures/" in str(r.get("path")) for r in records):
        errors.append("fixture appears in production lifecycle records")

    groups = data.get("duplicate_groups", [])
    if len(groups) != EXPECTED_DUPLICATE_GROUPS or sum(len(g.get("files", [])) for g in groups) != EXPECTED_DUPLICATE_FILES:
        errors.append(
            f"expected {EXPECTED_DUPLICATE_GROUPS} exact duplicate groups "
            f"covering {EXPECTED_DUPLICATE_FILES} files"
        )
    record_by_file = {f"{r['repository']}/{r['path']}": r for r in records}
    grouped_files: set[str] = set()
    for group in groups:
        digest = group.get("sha256", "")
        files = group.get("files", [])
        if not SHA256.fullmatch(digest) or len(files) < 2:
            errors.append("malformed exact duplicate group")
        for name in files:
            if name in grouped_files:
                errors.append(f"file appears in multiple duplicate groups: {name}")
            grouped_files.add(name)
            if name not in record_by_file or record_by_file[name].get("content_sha256") != digest:
                errors.append(f"duplicate hash does not bind lifecycle record: {name}")

    memory_duplicates = [
        r for r in records
        if r.get("repository") == "verdict-core-memory" and r.get("classification") == "DUPLICATE"
    ]
    for record in memory_duplicates:
        successor = record.get("successor") or ""
        if record.get("evidence_level") == "VERIFIED" and not successor.startswith("verdict-core/docs/"):
            errors.append(f"verified Core-memory duplicate lacks Core canonical owner: {record['path']}")
    legacy = [r for r in records if "/architecture/" in f"/{r.get('path', '')}"]
    if not legacy or any(r.get("classification") != "DUPLICATE" for r in legacy):
        errors.append("legacy docs/architecture copies must be non-canonical DUPLICATE records")

    continuity = [r for r in records if r.get("repository") == "verdict-continuity"]
    if not continuity or any(r.get("v2_relevance") != "V3_DEFERRED" for r in continuity):
        errors.append("all Continuity decisions must remain V3_DEFERRED")
    adr023 = [r for r in records if r.get("repository") == "verdict-core" and "ADR-023" in r.get("path", "")]
    if len(adr023) != 1 or adr023[0].get("classification") != "SUPERSEDED" or adr023[0].get("successor") != "verdict-core/docs/adr/ADR-035-authorized-selected-route-dispatch.md":
        errors.append("Core ADR-023 must be SUPERSEDED with ADR-035 as successor (BOD-193 closes MISSING_SUCCESSOR)")

    document = DOC.read_text(encoding="utf-8") if DOC.exists() else ""
    if not document:
        errors.append("docs/ADR_LIFECYCLE.md is missing or empty")
    for label, expected in EXPECTED_CLASSIFICATIONS.items():
        if f"| {label} | {expected} |" not in document:
            errors.append(f"rendered classification count differs: {label}")
    for label, expected in EXPECTED_EVIDENCE_LEVELS.items():
        if f"| {label} |" not in document or f"| {expected} |" not in document:
            errors.append(f"rendered evidence-level count differs: {label}")
    expected_rows = [
        f"| `{r['source_locator']}` | {r['classification']} | {r['evidence_level']} | {r['v2_relevance']} |"
        for r in records
    ]
    actual_rows = [
        line for line in document.splitlines()
        if line.startswith("| `") and "@" in line and line.count("|") == 5
    ]
    if actual_rows != expected_rows:
        errors.append("rendered lifecycle rows differ in content, order, or multiplicity from machine-readable records")
    return errors


def main() -> int:
    if not EVIDENCE.exists():
        print(f"MISSING: {EVIDENCE}")
        return 1
    try:
        data = load()
    except (json.JSONDecodeError, OSError) as exc:
        print(f"Unable to load lifecycle evidence: {exc}")
        return 1
    errors = validate(data)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    counts = Counter(r["classification"] for r in data["lifecycle_index"])
    print(
        f"ADR lifecycle index valid: {len(data['lifecycle_index'])} records, "
        f"{counts['PARTIALLY_TRUE']} PARTIALLY_TRUE, "
        f"{len(data['duplicate_groups'])} duplicate groups."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
