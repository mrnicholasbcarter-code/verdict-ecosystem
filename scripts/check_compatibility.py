#!/usr/bin/env python3
"""Validate compatibility metadata against local repository directories only."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

SCHEMA_VERSION = "3"
VALIDATION_SCOPE = "local-source-directories"
REQUIRED_IDS = {
    "verdict-core",
    "verdict-node",
    "verdict-risk",
    "verdict-strategy",
    "verdict-backtest",
    "verdict-cockpit",
    "verdict-ecosystem",
}
CANONICAL_PATHS = {repo_id: ("." if repo_id == "verdict-ecosystem" else f"../{repo_id}") for repo_id in REQUIRED_IDS}
REQUIRED_FIELDS = {
    "id",
    "path",
    "repository_url",
    "registry_url",
    "package",
    "import_name",
    "cli_name",
    "artifact_version",
    "publication_status",
    "contract_version",
    "policy_version",
    "runtime_constraints",
    "provider_compatibility",
    "maturity",
    "support_level",
    "evidence_timestamp",
    "release_train_pin",
    "legacy_aliases",
    "migration_instructions",
    "rollback_instructions",
    "test_command",
    "status",
}
LEGACY_ALIAS_FIELDS = {"name", "kind", "replacement", "migration_instructions", "sunset_date"}
LEGACY_ALIAS_KINDS = {"package", "import", "cli", "repository"}
PUBLICATION_STATUSES = {
    "published",
    "source-only",
    "private-application",
    "documentation-only",
}
MATURITY_LEVELS = {"experimental", "alpha", "beta", "stable", "deprecated"}
SUPPORT_LEVELS = {"experimental", "community", "maintained", "long-term", "unsupported"}
RUNTIME_NAMES = {"python", "node"}
DEFERRED_CHECKS = {
    "schema-hashes": "https://github.com/mrnicholasbcarter-code/verdict-core/issues/220",
    "cross-repository-contract-smoke-tests": "https://github.com/mrnicholasbcarter-code/verdict-node/issues/31",
}
SECRET_TOKENS = ("token=", "api_key", "password", "secret")


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    manifest_path = root / "compatibility-manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        errors, warnings, rows = validate_manifest(root, manifest)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "error", "errors": [str(exc)]}, indent=2))
        return 2

    report = {
        "status": "failed" if errors else "passed",
        "validation_scope": VALIDATION_SCOPE,
        "released_artifacts_validated": False,
        "deferred_checks": sorted(DEFERRED_CHECKS),
        "errors": errors,
        "warnings": warnings,
        "repositories": rows,
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if errors else 0


def validate_manifest(
    root: Path,
    manifest: object,
) -> tuple[list[str], list[str], list[dict[str, object]]]:
    errors: list[str] = []
    warnings: list[str] = []
    rows: list[dict[str, object]] = []
    if not isinstance(manifest, dict):
        return ["manifest must be an object"], warnings, rows

    if manifest.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"manifest.schema_version must be '{SCHEMA_VERSION}'")
    if manifest.get("validation_scope") != VALIDATION_SCOPE:
        errors.append(f"manifest.validation_scope must be '{VALIDATION_SCOPE}'")
    contract_version = validate_version_field(manifest, "contract_version", "manifest", errors)
    policy_version = validate_version_field(manifest, "policy_version", "manifest", errors)
    validate_timestamp(manifest.get("evidence_timestamp"), "manifest.evidence_timestamp", errors)
    validate_release_train(root, manifest.get("release_train"), errors)

    repositories = manifest.get("repositories")
    if not isinstance(repositories, list):
        return errors + ["manifest.repositories must be an array"], warnings, rows

    seen: set[str] = set()
    for index, item in enumerate(repositories):
        prefix = f"repositories[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be an object")
            continue
        missing = REQUIRED_FIELDS - set(item)
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

        if item["path"] != CANONICAL_PATHS.get(repo_id):
            errors.append(f"{repo_id}: path must use its canonical workspace path {CANONICAL_PATHS.get(repo_id)!r}")

        path = validate_local_path(root, item["path"], f"{prefix}.path", errors)
        exists = path.is_dir() if path is not None else False
        row: dict[str, object] = {
            "id": repo_id,
            "path": str(path) if path else None,
            "exists": exists,
            "release_train_pin": item["release_train_pin"],
            "publication_status": item["publication_status"],
            "status": item["status"],
        }
        rows.append(row)
        if path is not None and not exists:
            errors.append(f"{repo_id}: local repository directory missing: {path}")
        elif path is not None and path != root:
            pin_errors, resolved_revision, checked_out_revision = validate_source_pin(
                repo_id,
                path,
                item["release_train_pin"],
            )
            errors.extend(pin_errors)
            row["resolved_release_train_pin"] = resolved_revision
            row["checked_out_revision"] = checked_out_revision
        elif path == root:
            row["source_pin_validation"] = "not-applicable-current-manifest"

        validate_repository(item, prefix, repo_id, contract_version, policy_version, root, errors)
        if repo_id == "verdict-strategy" and item["package"] != "verdict-edge":
            warnings.append("verdict-strategy: repository/package naming differs (verdict-edge)")
        if repo_id in {"verdict-risk", "verdict-backtest"} and not str(item["package"]).startswith("llm-gate-"):
            warnings.append(f"{repo_id}: package naming differs from current manifest convention")

    missing_ids = REQUIRED_IDS - seen
    unexpected_ids = seen - REQUIRED_IDS
    errors.extend(f"missing repository: {repo_id}" for repo_id in sorted(missing_ids))
    errors.extend(f"unexpected repository: {repo_id}" for repo_id in sorted(unexpected_ids))
    return errors, warnings, rows


def validate_source_pin(
    repo_id: str,
    path: Path,
    release_train_pin: object,
) -> tuple[list[str], str | None, str | None]:
    if not isinstance(release_train_pin, str) or not re.fullmatch(r"[0-9a-f]{40}", release_train_pin):
        return [], None, None

    def git(*arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", "-C", str(path), *arguments],
            capture_output=True,
            text=True,
            check=False,
        )

    checked_out = git("rev-parse", "HEAD")
    if checked_out.returncode != 0:
        return [f"{repo_id}: local repository is not a readable Git checkout"], None, None
    checked_out_revision = checked_out.stdout.strip()

    resolved = git("rev-parse", "--verify", f"{release_train_pin}^{{commit}}")
    if resolved.returncode != 0:
        return [f"{repo_id}: release-train pin is unavailable in local checkout"], None, checked_out_revision
    resolved_revision = resolved.stdout.strip()
    if checked_out_revision != resolved_revision:
        return [
            f"{repo_id}: checked-out revision differs from release-train pin "
            f"({checked_out_revision} != {resolved_revision})"
        ], resolved_revision, checked_out_revision
    return [], resolved_revision, checked_out_revision


def validate_repository(
    item: dict[str, object],
    prefix: str,
    repo_id: str,
    contract_version: str | None,
    policy_version: str | None,
    root: Path,
    errors: list[str],
) -> None:
    validate_https_url(item["repository_url"], f"{prefix}.repository_url", errors, github_only=True)
    registry_url = item["registry_url"]
    if registry_url is not None:
        validate_https_url(registry_url, f"{prefix}.registry_url", errors)

    for field in ("package", "test_command", "status"):
        validate_non_empty_string(item[field], f"{prefix}.{field}", errors)
    for field in ("import_name", "cli_name"):
        if item[field] is not None:
            validate_non_empty_string(item[field], f"{prefix}.{field}", errors)
    if any(token in str(item["package"]).lower() for token in SECRET_TOKENS):
        errors.append(f"{repo_id}: secret-bearing package metadata rejected")

    artifact_version = item["artifact_version"]
    if not isinstance(artifact_version, str) or not (
        artifact_version == "unreleased" or re.fullmatch(r"\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?", artifact_version)
    ):
        errors.append(f"{prefix}.artifact_version must be semantic version text or 'unreleased'")

    publication_status = item["publication_status"]
    if publication_status not in PUBLICATION_STATUSES:
        errors.append(f"{prefix}.publication_status must be one of {sorted(PUBLICATION_STATUSES)}")
    elif publication_status == "published" and registry_url is None:
        errors.append(f"{prefix}.registry_url is required for a published artifact")
    elif publication_status != "published" and registry_url is not None:
        errors.append(f"{prefix}.registry_url must be null unless publication_status is 'published'")

    if item["contract_version"] != contract_version:
        errors.append(f"{repo_id}: contract_version differs from manifest")
    if item["policy_version"] != policy_version:
        errors.append(f"{repo_id}: policy_version differs from manifest")
    validate_runtime_constraints(item["runtime_constraints"], f"{prefix}.runtime_constraints", errors)
    validate_provider_compatibility(item["provider_compatibility"], f"{prefix}.provider_compatibility", errors)

    if item["maturity"] not in MATURITY_LEVELS:
        errors.append(f"{prefix}.maturity must be one of {sorted(MATURITY_LEVELS)}")
    if item["support_level"] not in SUPPORT_LEVELS:
        errors.append(f"{prefix}.support_level must be one of {sorted(SUPPORT_LEVELS)}")
    validate_timestamp(item["evidence_timestamp"], f"{prefix}.evidence_timestamp", errors)
    if not isinstance(item["release_train_pin"], str) or not re.fullmatch(r"[0-9a-f]{40}", item["release_train_pin"]):
        errors.append(f"{prefix}.release_train_pin must be a full lowercase Git commit SHA")

    validate_instruction(root, item["migration_instructions"], f"{prefix}.migration_instructions", errors)
    validate_instruction(root, item["rollback_instructions"], f"{prefix}.rollback_instructions", errors)
    validate_legacy_aliases(root, item["legacy_aliases"], f"{prefix}.legacy_aliases", errors)


def validate_legacy_aliases(root: Path, value: object, field: str, errors: list[str]) -> None:
    if not isinstance(value, list):
        errors.append(f"{field} must be an array")
        return
    seen: set[str] = set()
    for index, entry in enumerate(value):
        prefix = f"{field}[{index}]"
        if not isinstance(entry, dict) or set(entry) != LEGACY_ALIAS_FIELDS:
            errors.append(f"{prefix} must contain exactly {sorted(LEGACY_ALIAS_FIELDS)}")
            continue
        name = entry["name"]
        if not isinstance(name, str) or not re.fullmatch(r"[a-z][a-z0-9-]+", name):
            errors.append(f"{prefix}.name must be a safe legacy identifier")
            continue
        if name in seen:
            errors.append(f"{field}: duplicate legacy alias: {name}")
        seen.add(name)
        if entry["kind"] not in LEGACY_ALIAS_KINDS:
            errors.append(f"{prefix}.kind must be one of {sorted(LEGACY_ALIAS_KINDS)}")
        replacement = entry["replacement"]
        if (
            not isinstance(replacement, str)
            or not re.fullmatch(r"[a-z][a-z0-9-]+", replacement)
            or replacement == name
        ):
            errors.append(f"{prefix}.replacement must be a canonical name differing from the alias")
        validate_instruction(root, entry["migration_instructions"], f"{prefix}.migration_instructions", errors)
        validate_sunset_date(entry["sunset_date"], f"{prefix}.sunset_date", errors)


def validate_sunset_date(value: object, field: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        errors.append(f"{field} must be a calendar date (YYYY-MM-DD)")
        return
    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        errors.append(f"{field} must be a calendar date (YYYY-MM-DD)")


def validate_release_train(root: Path, value: object, errors: list[str]) -> None:
    if not isinstance(value, dict):
        errors.append("manifest.release_train must be an object")
        return
    required = {"id", "migration_instructions", "rollback_instructions", "deferred_checks"}
    missing = required - set(value)
    if missing:
        errors.append(f"manifest.release_train missing fields: {sorted(missing)}")
        return
    validate_non_empty_string(value["id"], "manifest.release_train.id", errors)
    validate_instruction(root, value["migration_instructions"], "manifest.release_train.migration_instructions", errors)
    validate_instruction(root, value["rollback_instructions"], "manifest.release_train.rollback_instructions", errors)
    deferred = value["deferred_checks"]
    if not isinstance(deferred, list):
        errors.append("manifest.release_train.deferred_checks must be an array")
        return
    actual: dict[str, object] = {}
    for index, entry in enumerate(deferred):
        prefix = f"manifest.release_train.deferred_checks[{index}]"
        if not isinstance(entry, dict) or set(entry) != {"name", "blocked_by"}:
            errors.append(f"{prefix} must contain only name and blocked_by")
            continue
        name = entry["name"]
        if not isinstance(name, str):
            errors.append(f"{prefix}.name must be text")
            continue
        if name in actual:
            errors.append(f"duplicate deferred check: {name}")
        actual[name] = entry["blocked_by"]
        validate_https_url(entry["blocked_by"], f"{prefix}.blocked_by", errors, github_only=True)
    if actual != DEFERRED_CHECKS:
        errors.append("manifest.release_train.deferred_checks must name the ratified REL-001 blockers")


def validate_local_path(root: Path, value: object, field: str, errors: list[str]) -> Path | None:
    if not isinstance(value, str) or not value:
        errors.append(f"{field} must be non-empty")
        return None
    path = Path(value)
    if path.is_absolute():
        errors.append(f"{field} must be a relative repository path")
        return None
    resolved = root / path
    normalized_parts: list[str] = []
    for part in resolved.parts:
        if part == "..":
            if normalized_parts and normalized_parts[-1] != "..":
                normalized_parts.pop()
            else:
                normalized_parts.append(part)
        elif part != ".":
            normalized_parts.append(part)
    resolved = Path(*normalized_parts)
    if resolved != root and resolved.parent != root.parent:
        errors.append(f"{field} must resolve to the workspace root or one sibling")
        return None
    return resolved


def validate_https_url(value: object, field: str, errors: list[str], *, github_only: bool = False) -> None:
    if not isinstance(value, str):
        errors.append(f"{field} must be an HTTPS URL")
        return
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password:
        errors.append(f"{field} must be an HTTPS URL without credentials")
    elif any(token in value.lower() for token in SECRET_TOKENS):
        errors.append(f"{field} contains secret-bearing metadata")
    elif github_only and parsed.hostname != "github.com":
        errors.append(f"{field} must use github.com")


def validate_timestamp(value: object, field: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not value.endswith("Z"):
        errors.append(f"{field} must be an RFC 3339 UTC timestamp")
        return
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError:
        errors.append(f"{field} must be an RFC 3339 UTC timestamp")
        return
    if parsed > datetime.now(timezone.utc):
        errors.append(f"{field} must not be in the future")


def validate_runtime_constraints(value: object, field: str, errors: list[str]) -> None:
    if not isinstance(value, dict) or not value:
        errors.append(f"{field} must be a non-empty object")
        return
    for runtime, constraint in value.items():
        if runtime not in RUNTIME_NAMES:
            errors.append(f"{field} contains unsupported runtime: {runtime}")
        if not isinstance(constraint, str) or not (
            constraint == "unspecified" or re.fullmatch(r">=\d+(?:\.\d+){0,2}", constraint)
        ):
            errors.append(f"{field}.{runtime} must be a minimum-version constraint or 'unspecified'")


def validate_provider_compatibility(value: object, field: str, errors: list[str]) -> None:
    if not isinstance(value, list) or not value:
        errors.append(f"{field} must be a non-empty array")
        return
    if any(not isinstance(entry, str) or not re.fullmatch(r"[a-z][a-z0-9-]+", entry) for entry in value):
        errors.append(f"{field} entries must be safe capability identifiers")
    if len(value) != len(set(map(str, value))):
        errors.append(f"{field} entries must be unique")


def validate_instruction(root: Path, value: object, field: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not value:
        errors.append(f"{field} must be a non-empty local documentation reference")
        return
    file_part, _, fragment = value.partition("#")
    path = Path(file_part)
    if path.is_absolute() or ".." in path.parts or path.suffix != ".md":
        errors.append(f"{field} must be a safe relative Markdown path")
        return
    if not (root / path).is_file():
        errors.append(f"{field} file does not exist: {file_part}")
    if "#" in value and not re.fullmatch(r"[a-z0-9-]+", fragment):
        errors.append(f"{field} has an invalid heading fragment")


def validate_non_empty_string(value: object, field: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{field} must be non-empty text")


def validate_version_field(value: dict[str, object], field: str, prefix: str, errors: list[str]) -> str | None:
    candidate = value.get(field)
    if not isinstance(candidate, str) or not re.fullmatch(r"\d+", candidate):
        errors.append(f"{prefix}.{field} must be a numeric version string")
        return None
    return candidate


if __name__ == "__main__":
    raise SystemExit(main())
