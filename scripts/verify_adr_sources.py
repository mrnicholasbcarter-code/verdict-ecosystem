#!/usr/bin/env python3
"""Verify ADR lifecycle hashes and citations against exact local Git snapshots.

This is an evidence-refresh/review tool, not a default CI dependency: callers pass
or configure local repositories that contain the pinned commits.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

try:
    from scripts.check_adr_lifecycle import (
        EXPECTED_REVIEWED_AUDIT_SHA256,
        reviewed_audit_digest,
    )
except ModuleNotFoundError:  # Direct execution places scripts/ on sys.path.
    from check_adr_lifecycle import (  # type: ignore[no-redef]
        EXPECTED_REVIEWED_AUDIT_SHA256,
        reviewed_audit_digest,
    )

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "ADR_LIFECYCLE.json"


def git_bytes(repo: Path, sha: str, path: str) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(repo), "show", f"{sha}:{path}"],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode:
        raise RuntimeError(f"missing pinned source {repo.name}@{sha}:{path}")
    return result.stdout


def git_paths(repo: Path, sha: str) -> set[str]:
    result = subprocess.run(
        ["git", "-C", str(repo), "ls-tree", "-r", "--name-only", sha],
        check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )
    if result.returncode:
        raise RuntimeError(f"missing pinned tree {repo.name}@{sha}")
    return set(result.stdout.splitlines())


def is_adr_source(path: str) -> bool:
    """The reviewed inventory rule. It intentionally includes the one fixture."""
    return path.endswith(".md") and (
        path.startswith("docs/adr/")
        or path.startswith("docs/architecture/ADR-")
        or ("/fixtures/" in f"/{path}" and "/docs/adr/" in f"/{path}")
    )


def verify(data: dict, repos: dict[str, Path]) -> list[str]:
    errors: list[str] = []
    # Citation selection and all other reviewed semantics are authoritative only
    # when they match the independently reviewed digest pinned in trusted code.
    calculated_digest = reviewed_audit_digest(data)
    metadata_digest = data.get("metadata", {}).get("reviewed_audit_sha256")
    if calculated_digest != EXPECTED_REVIEWED_AUDIT_SHA256:
        errors.append("semantic audit content differs from the independently reviewed digest")
    if metadata_digest != EXPECTED_REVIEWED_AUDIT_SHA256:
        errors.append("reviewed audit metadata digest differs from the trusted validator constant")
    records = data["lifecycle_index"]
    snapshots = data["source_snapshots"]
    declared = {(r["repository"], r["path"]) for r in records}
    excluded = {(r["repository"], r["path"]) for r in data["excluded_files"]}
    trees: dict[str, set[str]] = {}

    # Completeness comes from the immutable Git trees, not JSON summary counts.
    for name, sha in snapshots.items():
        try:
            trees[name] = git_paths(repos[name], sha)
        except (KeyError, RuntimeError) as exc:
            errors.append(str(exc))
            continue
        actual = {(name, path) for path in trees[name] if is_adr_source(path)}
        indexed = {item for item in declared | excluded if item[0] == name}
        for _, path in sorted(actual - indexed):
            errors.append(f"unindexed ADR source: {name}/{path}")
        for _, path in sorted(indexed - actual):
            errors.append(f"indexed ADR absent from pinned tree: {name}/{path}")

    actual_digests: dict[str, str] = {}
    for record in records:
        repo, path = record["repository"], record["path"]
        try:
            content = git_bytes(repos[repo], snapshots[repo], path)
        except (KeyError, RuntimeError) as exc:
            errors.append(str(exc)); continue
        digest = hashlib.sha256(content).hexdigest()
        actual_digests[f"{repo}/{path}"] = digest
        if digest != record["content_sha256"]:
            errors.append(f"content hash mismatch: {repo}/{path}")
        for citation in record["citations"]:
            citation_repo, separator, citation_path = citation.partition("/")
            if not separator or citation_repo not in trees or citation_path not in trees[citation_repo]:
                errors.append(f"citation absent from pinned tree: {repo}/{path}: {citation}")

    for fixture in data["excluded_files"]:
        repo, path = fixture["repository"], fixture["path"]
        try:
            content = git_bytes(repos[repo], snapshots[repo], path)
            if hashlib.sha256(content).hexdigest() != fixture["content_sha256"]:
                errors.append(f"excluded fixture hash mismatch: {repo}/{path}")
        except (KeyError, RuntimeError) as exc:
            errors.append(str(exc))

    # Duplicate groups are independently derived from bytes in the pinned trees.
    by_digest: dict[str, list[str]] = defaultdict(list)
    for name, digest in actual_digests.items():
        by_digest[digest].append(name)
    derived = {(digest, tuple(sorted(files))) for digest, files in by_digest.items() if len(files) > 1}
    declared_groups = {
        (group["sha256"], tuple(sorted(group["files"])))
        for group in data["duplicate_groups"]
    }
    if derived != declared_groups:
        errors.append("duplicate groups differ from pinned source bytes")
    return sorted(set(errors))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True, help="directory containing verdict-* repositories")
    args = parser.parse_args()
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    repos = {name: args.repo_root / name for name in data["source_snapshots"]}
    errors = verify(data, repos)
    for error in errors: print(f"FAIL: {error}")
    if errors: return 1
    print(f"ADR source verification passed: {len(data['lifecycle_index'])} records and all citations")
    return 0

if __name__ == "__main__":
    sys.exit(main())
