#!/usr/bin/env python3
"""Offline cross-repository compatibility manifest checker."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

SCHEMA_VERSION = "1"
REQUIRED_IDS = {
    "verdict-core",
    "verdict-node",
    "verdict-risk",
    "verdict-strategy",
    "verdict-backtest",
    "verdict-cockpit",
    "verdict-ecosystem",
}


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    manifest_path = root / "compatibility-manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        errors, warnings, rows = validate_manifest(root, manifest)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "error", "errors": [str(exc)]}, indent=2))
        return 2

    report = {"status": "failed" if errors else "passed", "errors": errors, "warnings": warnings, "repositories": rows}
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if errors else 0


def validate_manifest(root: Path, manifest: object) -> tuple[list[str], list[str], list[dict[str, object]]]:
    errors: list[str] = []
    warnings: list[str] = []
    rows: list[dict[str, object]] = []
    if not isinstance(manifest, dict):
        return ["manifest must be an object"], warnings, rows
    if manifest.get("schema_version") != SCHEMA_VERSION:
        errors.append("manifest.schema_version must be '1'")
    repositories = manifest.get("repositories")
    if not isinstance(repositories, list):
        return errors + ["manifest.repositories must be an array"], warnings, rows

    seen: set[str] = set()
    for index, item in enumerate(repositories):
        prefix = f"repositories[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be an object")
            continue
        required = {"id", "path", "package", "contract_version", "test_command", "status"}
        missing = required - set(item)
        if missing:
            errors.append(f"{prefix} missing fields: {sorted(missing)}")
            continue
        repo_id = item["id"]
        if not isinstance(repo_id, str) or not re.fullmatch(r"[a-z][a-z0-9-]+", repo_id):
            errors.append(f"{prefix}.id must be a safe repository identifier")
            continue
        if repo_id in seen:
            errors.append(f"duplicate repository id: {repo_id}")
        seen.add(repo_id)
        path_value = item["path"]
        if not isinstance(path_value, str) or not path_value:
            errors.append(f"{prefix}.path must be non-empty")
            continue
        path = (root / path_value).resolve()
        exists = path.is_dir()
        row: dict[str, object] = {"id": repo_id, "path": str(path), "exists": exists, "status": item["status"]}
        rows.append(row)
        if not exists:
            errors.append(f"{repo_id}: repository path missing: {path}")
        package = item["package"]
        if not isinstance(package, str) or not package.strip():
            errors.append(f"{repo_id}: package must be non-empty")
        if item["contract_version"] != manifest.get("contract_version"):
            errors.append(f"{repo_id}: contract_version differs from manifest")
        if isinstance(package, str) and any(token in package.lower() for token in ("token=", "api_key", "password", "secret")):
            errors.append(f"{repo_id}: secret-bearing package metadata rejected")
        if repo_id == "verdict-strategy" and package != "verdict-edge":
            warnings.append("verdict-strategy: repository/package naming differs (verdict-edge)")
        if repo_id in {"verdict-risk", "verdict-backtest"} and not package.startswith("llm-gate-"):
            warnings.append(f"{repo_id}: package naming differs from current manifest convention")

    missing = REQUIRED_IDS - seen
    errors.extend(f"missing repository: {repo_id}" for repo_id in sorted(missing))
    return errors, warnings, rows


if __name__ == "__main__":
    raise SystemExit(main())
