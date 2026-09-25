#!/usr/bin/env python3
"""Generate ADR_SOURCE_MANIFEST.json deterministically from exact Git objects.

This script reads evidence/ADR_LIFECYCLE.json to identify all required paths
(lifecycle records and their citations), then records the content hash and
commit SHA for each path from the pinned snapshot SHA in each repository.

Output follows the same schema as the input manifest, enabling bitwise
verification of independence: a rerun produces byte-identical output if the
underlying Git objects have not changed.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "ADR_LIFECYCLE.json"
MANIFEST = ROOT / "evidence" / "ADR_SOURCE_MANIFEST.json"

# Repository URLs
REPOSITORIES = {
    "verdict-core": "https://github.com/mrnicholasbcarter-code/verdict-core",
    "verdict-core-memory": "https://github.com/mrnicholasbcarter-code/verdict-core-memory",
    "verdict-node": "https://github.com/mrnicholasbcarter-code/verdict-node",
    "verdict-continuity": "https://github.com/mrnicholasbcarter-code/verdict-continuity",
}


def is_adr_source(path: str) -> bool:
    """The reviewed inventory rule. It intentionally includes the one fixture."""
    return path.endswith(".md") and (
        path.startswith("docs/adr/")
        or path.startswith("docs/architecture/ADR-")
        or ("/fixtures/" in f"/{path}" and "/docs/adr/" in f"/{path}")
    )


def git_show_sha256(repo: Path, commit: str, path: str) -> str:
    """Get SHA256 of a file at a given commit."""
    result = subprocess.run(
        ["git", "-C", str(repo), "show", f"{commit}:{path}"],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        raise RuntimeError(f"missing {repo.name}@{commit}:{path}")
    return hashlib.sha256(result.stdout).hexdigest()


def git_ls_tree(repo: Path, commit: str) -> set[str]:
    """List all ADR files in a git tree at a given commit (including fixtures)."""
    result = subprocess.run(
        ["git", "-C", str(repo), "ls-tree", "-r", "--name-only", commit],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"cannot ls-tree {repo.name}@{commit}")
    
    files = set(result.stdout.strip().split("\n")) if result.stdout.strip() else set()
    # Filter to ADR files and fixtures using the same rule as the verifier
    return sorted(set(p for p in files if is_adr_source(p)))


def ensure_commit(repo: Path, commit: str) -> None:
    """Ensure the repo is at the given commit (fetch if needed)."""
    # Check current commit
    result = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
    )
    current = result.stdout.strip()
    
    if current == commit:
        return  # Already at right commit
    
    # Fetch to make sure we have the commit
    subprocess.run(
        ["git", "-C", str(repo), "fetch", "origin", commit],
        capture_output=True,
    )
    
    # Checkout the commit
    subprocess.run(
        ["git", "-C", str(repo), "checkout", "-q", commit],
        capture_output=True,
    )


def main() -> int:
    # Load lifecycle evidence
    try:
        lifecycle_data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"ERROR: cannot load {EVIDENCE}: {exc}", file=sys.stderr)
        return 1

    # Load old manifest to preserve schema/format
    try:
        old_manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except Exception:
        old_manifest = {"schema_version": 1, "repositories": {}}

    # Collect all required paths (lifecycle records + citations)
    required: dict[str, set[str]] = {name: set() for name in REPOSITORIES}
    for record in lifecycle_data.get("lifecycle_index", []):
        repo = record.get("repository")
        path = record.get("path")
        if repo and path:
            required[repo].add(path)
        for citation in record.get("citations", []):
            cite_repo, _, cite_path = citation.partition("/")
            if cite_repo and cite_path:
                required[cite_repo].add(cite_path)

    for fixture in lifecycle_data.get("excluded_files", []):
        repo = fixture.get("repository")
        path = fixture.get("path")
        if repo and path:
            required[repo].add(path)

    # Build the new manifest
    manifest: dict[str, object] = {
        "schema_version": old_manifest.get("schema_version", 1),
        "repositories": {},
    }

    source_snapshots = lifecycle_data.get("source_snapshots", {})

    errors: list[str] = []
    for repo_name in sorted(REPOSITORIES.keys()):
        url = REPOSITORIES[repo_name]
        commit = source_snapshots.get(repo_name)
        if not commit:
            errors.append(f"no pinned commit for {repo_name}")
            continue

        # Get the local repo path (sibling directory)
        repo_path = ROOT.parent / repo_name
        if not repo_path.is_dir():
            errors.append(f"repository not found: {repo_path}")
            continue

        try:
            # Ensure we're at the right commit
            ensure_commit(repo_path, commit)
            
            # Discover all ADRs in the repository at this commit (including fixtures)
            adr_inventory = git_ls_tree(repo_path, commit)

            # Record all required paths with their hashes
            required_paths = []
            for path in sorted(required.get(repo_name, set())):
                try:
                    sha256 = git_show_sha256(repo_path, commit, path)
                    required_paths.append({
                        "path": path,
                        "sha256": sha256,
                    })
                except RuntimeError as exc:
                    errors.append(str(exc))

            manifest["repositories"][repo_name] = {
                "repository_url": url,
                "commit": commit,
                "adr_inventory": adr_inventory,
                "required_paths": required_paths,
            }
        except RuntimeError as exc:
            errors.append(str(exc))

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    # Write manifest with consistent formatting
    manifest_json = json.dumps(manifest, indent=2, sort_keys=True)
    manifest_bytes = (manifest_json + "\n").encode("utf-8")

    MANIFEST.write_bytes(manifest_bytes)
    manifest_sha = hashlib.sha256(manifest_bytes).hexdigest()
    print(f"Generated {MANIFEST}")
    print(f"  SHA256: {manifest_sha}")
    print(f"  Repositories: {len(manifest['repositories'])}")
    print(f"  Required paths: {sum(len(r.get('required_paths', [])) for r in manifest['repositories'].values())}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
