#!/usr/bin/env python3
"""Verify ADR lifecycle sources from an immutable manifest or exact Git objects.

Default CI uses the checked-in, independently generated manifest. Passing
``--repo-root`` enables the live exact-Git refresh and audit mode.
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
SOURCE_MANIFEST = ROOT / "evidence" / "ADR_SOURCE_MANIFEST.json"
EXPECTED_SOURCE_MANIFEST_SHA256 = "eacff31469f1d25c08ebe4334742845f274ce1f5c19ddcef950ab2fa636bdcda"


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



def verify_manifest(data: dict, manifest: dict, manifest_bytes: bytes) -> list[str]:
    """Verify the immutable, independently generated source manifest.

    This credential-free mode binds every reviewed source, citation, fixture, and
    ADR inventory entry to an exact repository commit and content hash. The
    separately pinned manifest-file digest makes coordinated evidence/manifest
    edits fail closed. Live Git mode remains the refresh and audit authority.
    """
    errors: list[str] = []
    if hashlib.sha256(manifest_bytes).hexdigest() != EXPECTED_SOURCE_MANIFEST_SHA256:
        errors.append("source manifest differs from the independently reviewed digest")
    if manifest.get("schema_version") != 1 or not isinstance(manifest.get("repositories"), dict):
        return errors + ["source manifest has invalid schema"]
    repositories = manifest["repositories"]
    if set(repositories) != set(data["source_snapshots"]):
        errors.append("source manifest repository set differs from lifecycle snapshots")

    required: dict[str, set[str]] = {name: set() for name in data["source_snapshots"]}
    for record in data["lifecycle_index"]:
        required.setdefault(record["repository"], set()).add(record["path"])
        for citation in record["citations"]:
            repo, separator, path = citation.partition("/")
            if not separator:
                errors.append(f"invalid citation locator: {citation}")
            else:
                required.setdefault(repo, set()).add(path)
    for fixture in data["excluded_files"]:
        required.setdefault(fixture["repository"], set()).add(fixture["path"])

    hashes: dict[tuple[str, str], str] = {}
    inventories: dict[str, set[str]] = {}
    for name, expected_commit in data["source_snapshots"].items():
        entry = repositories.get(name)
        if not isinstance(entry, dict):
            errors.append(f"source manifest missing repository: {name}")
            continue
        if entry.get("commit") != expected_commit:
            errors.append(f"source manifest commit mismatch: {name}")
        if entry.get("repository_url") != data["source_repository_urls"].get(name):
            errors.append(f"source manifest repository URL mismatch: {name}")
        inventory = entry.get("adr_inventory")
        paths = entry.get("required_paths")
        if not isinstance(inventory, list) or any(not isinstance(path, str) for path in inventory):
            errors.append(f"source manifest ADR inventory invalid: {name}")
            inventory = []
        if inventory != sorted(set(inventory)):
            errors.append(f"source manifest ADR inventory is not unique and sorted: {name}")
        inventories[name] = set(inventory)
        if not isinstance(paths, list):
            errors.append(f"source manifest required paths invalid: {name}")
            paths = []
        seen: set[str] = set()
        for item in paths:
            if not isinstance(item, dict) or set(item) != {"path", "sha256"}:
                errors.append(f"source manifest required path entry invalid: {name}")
                continue
            path, digest = item.get("path"), item.get("sha256")
            if not isinstance(path, str) or not isinstance(digest, str):
                errors.append(f"source manifest required path entry invalid: {name}")
                continue
            if path in seen:
                errors.append(f"source manifest duplicate required path: {name}/{path}")
            seen.add(path)
            hashes[(name, path)] = digest
        if seen != required.get(name, set()):
            errors.append(f"source manifest required path set mismatch: {name}")

    declared = {(r["repository"], r["path"]) for r in data["lifecycle_index"]}
    excluded = {(r["repository"], r["path"]) for r in data["excluded_files"]}
    for name in data["source_snapshots"]:
        expected_inventory = {path for repo, path in declared | excluded if repo == name}
        if inventories.get(name, set()) != expected_inventory:
            errors.append(f"source manifest ADR inventory mismatch: {name}")
    for record in data["lifecycle_index"]:
        key = (record["repository"], record["path"])
        if hashes.get(key) != record["content_sha256"]:
            errors.append(f"source manifest content hash mismatch: {key[0]}/{key[1]}")
        for citation in record["citations"]:
            repo, _, path = citation.partition("/")
            if (repo, path) not in hashes:
                errors.append(f"citation absent from source manifest: {citation}")
    for fixture in data["excluded_files"]:
        key = (fixture["repository"], fixture["path"])
        if hashes.get(key) != fixture["content_sha256"]:
            errors.append(f"source manifest excluded fixture hash mismatch: {key[0]}/{key[1]}")

    by_digest: dict[str, list[str]] = defaultdict(list)
    for record in data["lifecycle_index"]:
        key = (record["repository"], record["path"])
        digest = hashes.get(key)
        if digest:
            by_digest[digest].append(f"{key[0]}/{key[1]}")
    derived = {(digest, tuple(sorted(files))) for digest, files in by_digest.items() if len(files) > 1}
    declared_groups = {(g["sha256"], tuple(sorted(g["files"]))) for g in data["duplicate_groups"]}
    if derived != declared_groups:
        errors.append("duplicate groups differ from source manifest hashes")
    return sorted(set(errors))



def verify_content_hashes_from_repos(data: dict, repos: dict[str, Path]) -> list[str]:
    """Verify content_sha256 values match actual file content at pinned snapshots.
    
    This ensures that when lifecycle index is regenerated with a new snapshot SHA,
    the content hashes are recomputed from actual Git objects, not copied from old
    snapshots. Prevents stale hash values from passing undetected.
    """
    errors: list[str] = []
    snapshots = data["source_snapshots"]
    
    for record in data["lifecycle_index"]:
        repo, path = record["repository"], record["path"]
        try:
            content = git_bytes(repos[repo], snapshots[repo], path)
            actual_digest = hashlib.sha256(content).hexdigest()
            recorded_digest = record.get("content_sha256")
            if actual_digest != recorded_digest:
                errors.append(
                    f"content hash stale: {repo}/{path} "
                    f"recorded={recorded_digest[:8]}… actual={actual_digest[:8]}…"
                )
        except (KeyError, RuntimeError) as exc:
            # File doesn't exist in this snapshot or repo not available - OK to skip
            pass
    
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, help="use exact local Git objects instead of the checked-in immutable manifest")
    args = parser.parse_args()
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    if args.repo_root:
        repos = {name: args.repo_root / name for name in data["source_snapshots"]}
        errors = verify(data, repos)
        hash_errors = verify_content_hashes_from_repos(data, repos)
        errors.extend(hash_errors)
        mode = "exact Git"
    else:
        manifest_bytes = SOURCE_MANIFEST.read_bytes()
        manifest = json.loads(manifest_bytes)
        errors = verify_manifest(data, manifest, manifest_bytes)
        mode = "immutable manifest"
    for error in errors: print(f"FAIL: {error}")
    if errors: return 1
    print(f"ADR source verification passed ({mode}): {len(data['lifecycle_index'])} records and all citations")
    return 0

if __name__ == "__main__":
    sys.exit(main())
