#!/usr/bin/env python3
"""Check out external compatibility sources at their manifest pins for CI."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


def main(root: Path | None = None) -> int:
    root = root or Path(__file__).resolve().parents[1]
    manifest_path = root / "compatibility-manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "error", "errors": [str(exc)]}, indent=2))
        return 2

    repositories = manifest.get("repositories") if isinstance(manifest, dict) else None
    if not isinstance(repositories, list):
        print(json.dumps({"status": "error", "errors": ["manifest.repositories must be an array"]}, indent=2))
        return 2

    checked_out: list[dict[str, str]] = []
    errors: list[str] = []
    for repository in repositories:
        if not isinstance(repository, dict):
            errors.append("manifest repository entry must be an object")
            continue

        repo_id = repository.get("id")
        relative_path = repository.get("path")
        release_train_pin = repository.get("release_train_pin")
        if not isinstance(repo_id, str) or not isinstance(relative_path, str):
            errors.append("manifest repository id and path must be text")
            continue
        if not isinstance(release_train_pin, str) or not re.fullmatch(r"[0-9a-f]{40}", release_train_pin):
            errors.append(f"{repo_id}: release-train pin must be a full lowercase Git commit SHA")
            continue

        relative = Path(relative_path)
        if relative == Path("."):
            continue
        if relative.is_absolute() or not relative.parts or relative.parts[0] != ".." or ".." in relative.parts[1:]:
            errors.append(f"{repo_id}: local repository path must name the workspace root or one sibling")
            continue
        path = root.parent / Path(*relative.parts[1:])
        if path == root:
            continue
        if not path.is_dir():
            errors.append(f"{repo_id}: local repository directory missing: {path}")
            continue

        try:
            run_git(path, "fetch", "--depth=1", "origin", release_train_pin)
            run_git(path, "checkout", "--detach", "--quiet", release_train_pin)
        except subprocess.CalledProcessError as exc:
            detail = exc.stderr.strip() or exc.stdout.strip() or "git command failed"
            errors.append(f"{repo_id}: could not check out release-train pin: {detail}")
            continue

        checked_out.append({"id": repo_id, "release_train_pin": release_train_pin})

    report = {
        "status": "failed" if errors else "passed",
        "checked_out": checked_out,
        "errors": errors,
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if errors else 0


def run_git(path: Path, *arguments: str) -> None:
    subprocess.run(
        ["git", "-C", str(path), *arguments],
        check=True,
        capture_output=True,
        text=True,
    )


if __name__ == "__main__":
    sys.exit(main())
