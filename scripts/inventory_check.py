#!/usr/bin/env python3
"""Read-only local artifact inventory for one repository.

Prints tracked/untracked/modified counts and the untracked path list so a
human can classify them against ARTIFACT_HYGIENE_POLICY.md. Never writes,
stages, commits, or deletes anything in the target repository.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

# Same containment rule as scripts/secret_scan.py: never touch these
# directories, and only accept targets git itself recognizes as a
# repository. No hard-coded workspace path, so this runs unchanged in CI.
FORBIDDEN_DIRS = [Path.home() / ".omniroute", Path.home() / ".claude"]


def is_forbidden(candidate: Path) -> bool:
    for forbidden in FORBIDDEN_DIRS:
        try:
            forbidden_resolved = forbidden.resolve()
        except OSError:
            continue
        if candidate == forbidden_resolved or forbidden_resolved in candidate.parents:
            return True
    return False


def resolve_allowed_repo(raw_path: str) -> Path | None:
    candidate = Path(raw_path).resolve()
    if not candidate.is_dir() or is_forbidden(candidate):
        return None
    result = subprocess.run(
        ["git", "-C", str(candidate), "rev-parse", "--git-dir"],
        capture_output=True, text=True, timeout=10,
    )
    return candidate if result.returncode == 0 else None


def run_git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, timeout=30,
    )
    return result.stdout if result.returncode == 0 else ""


def inspect_repo(repo: Path) -> dict[str, object]:
    is_bare = run_git(repo, "rev-parse", "--is-bare-repository").strip()
    if is_bare == "true":
        worktrees = [line for line in run_git(repo, "worktree", "list").splitlines() if line]
        return {
            "repo": repo.name,
            "bare": True,
            "worktree_count": len(worktrees),
            "note": "bare repository; no working tree to inspect at this path",
        }

    branch = run_git(repo, "rev-parse", "--abbrev-ref", "HEAD").strip()
    porcelain = run_git(repo, "status", "--porcelain=2", "--branch")
    untracked = [line[2:].strip() for line in porcelain.splitlines() if line.startswith("?")]
    modified = [line for line in porcelain.splitlines() if line.startswith(("1", "2"))]
    tracked_count = len([line for line in run_git(repo, "ls-files").splitlines() if line])

    return {
        "repo": repo.name,
        "bare": False,
        "branch": branch,
        "tracked_count": tracked_count,
        "untracked_count": len(untracked),
        "untracked_paths": untracked,
        "modified_count": len(modified),
    }


def main() -> int:
    raw_paths = sys.argv[1:] or ["."]
    rejected: list[str] = []
    reports: list[dict[str, object]] = []
    for raw_path in raw_paths:
        repo = resolve_allowed_repo(raw_path)
        if repo is None:
            rejected.append(raw_path)
            continue
        reports.append(inspect_repo(repo))

    print(json.dumps({"repositories": reports, "rejected_paths": rejected}, indent=2, sort_keys=True))
    return 2 if rejected else 0


if __name__ == "__main__":
    raise SystemExit(main())
