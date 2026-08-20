#!/usr/bin/env python3
"""Generate the human compatibility matrix from compatibility-manifest.json.

The committed `docs/COMPATIBILITY_MATRIX.md` is a pure function of the
manifest: no timestamps of generation, no environment probing, no absolute
paths, so the same commit renders byte-identical output on any machine.
The default mode is `--check`, which regenerates the matrix in memory and
compares it against the committed file, so CI cannot mutate the document.
Only `--write` writes.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "compatibility-manifest.json"
TARGET = ROOT / "docs" / "COMPATIBILITY_MATRIX.md"

PUBLICATION_LABELS = {
    "published": "published",
    "source-only": "source-only — no released artifact",
    "private-application": "private application — not distributed",
    "documentation-only": "documentation only — not distributed",
}

HEADER = """# Verdict Ecosystem Compatibility Matrix

> **GENERATED FILE — do not edit by hand.**
> Source of truth: [`compatibility-manifest.json`](../compatibility-manifest.json).
> Regenerate with `python3 scripts/generate_compatibility_matrix.py --write`;
> CI fails if this file drifts from the manifest.
"""


def code(value: object) -> str:
    return f"`{value}`" if value is not None else "—"


def render(manifest: dict) -> str:
    train = manifest["release_train"]
    lines = [HEADER]
    lines.append(
        f"Release train {code(train['id'])} · schema {code(manifest['schema_version'])}"
        f" · contract {code(manifest['contract_version'])}"
        f" · policy {code(manifest['policy_version'])}"
        f" · validation scope {code(manifest['validation_scope'])}"
        f" · evidence timestamp {code(manifest['evidence_timestamp'])}"
    )
    lines.append("")
    lines.append("## Repositories")
    lines.append("")
    lines.append(
        "| Repository | Package | Import | CLI | Version | Publication | Registry |"
        " Runtime | Maturity | Support | Evidence date | Release-train pin |"
    )
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for repo in manifest["repositories"]:
        runtime = ", ".join(
            f"{name} {constraint}" for name, constraint in sorted(repo["runtime_constraints"].items())
        )
        registry = (
            f"[registry]({repo['registry_url']})" if repo["registry_url"] else "**not published**"
        )
        version = repo["artifact_version"]
        version_cell = "**unreleased**" if version == "unreleased" else code(version)
        lines.append(
            f"| [{repo['id']}]({repo['repository_url']}) | {code(repo['package'])} |"
            f" {code(repo['import_name'])} | {code(repo['cli_name'])} | {version_cell} |"
            f" {PUBLICATION_LABELS[repo['publication_status']]} | {registry} | {runtime} |"
            f" {repo['maturity']} | {repo['support_level']} | {repo['evidence_timestamp']} |"
            f" {code(repo['release_train_pin'])} |"
        )
    lines.append("")
    lines.append(
        "Rows marked **not published** or **unreleased** have no released artifact;"
        " they are validated from pinned local source only."
    )

    lines.append("")
    lines.append("## Legacy names and migration deadlines")
    lines.append("")
    alias_rows = [
        (repo["id"], alias) for repo in manifest["repositories"] for alias in repo["legacy_aliases"]
    ]
    if alias_rows:
        lines.append("| Repository | Legacy name | Kind | Replacement | Sunset date | Migration |")
        lines.append("|---|---|---|---|---|---|")
        for repo_id, alias in alias_rows:
            lines.append(
                f"| {repo_id} | {code(alias['name'])} | {alias['kind']} |"
                f" {code(alias['replacement'])} | {alias['sunset_date']} |"
                f" [migration](../{alias['migration_instructions']}) |"
            )
    else:
        lines.append("No legacy aliases are recorded in the manifest.")

    lines.append("")
    lines.append("## Deferred checks")
    lines.append("")
    lines.append("| Check | Blocked by |")
    lines.append("|---|---|")
    for check in train["deferred_checks"]:
        lines.append(f"| {code(check['name'])} | {check['blocked_by']} |")

    lines.append("")
    lines.append("## Migration and rollback")
    lines.append("")
    migration = train["migration_instructions"]
    rollback = train["rollback_instructions"]
    lines.append(f"- Migration guide: [{Path(migration).name}](../{migration})")
    lines.append(f"- Rollback guide: [{Path(rollback).name}](../{rollback})")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write",
        action="store_true",
        help="regenerate docs/COMPATIBILITY_MATRIX.md (the only mode that writes)",
    )
    args = parser.parse_args()

    expected = render(json.loads(SOURCE.read_text(encoding="utf-8")))
    if args.write:
        changed = not TARGET.exists() or TARGET.read_text(encoding="utf-8") != expected
        if changed:
            TARGET.write_text(expected, encoding="utf-8")
        print(json.dumps({"mode": "write", "changed": changed}, indent=2))
        return 0

    if not TARGET.exists():
        print(json.dumps({"mode": "check", "status": "failed", "problems": ["docs/COMPATIBILITY_MATRIX.md missing"]}, indent=2))
        return 1
    actual = TARGET.read_text(encoding="utf-8")
    problems = (
        []
        if actual == expected
        else ["docs/COMPATIBILITY_MATRIX.md is stale or hand-edited; regenerate with scripts/generate_compatibility_matrix.py --write"]
    )
    print(json.dumps({"mode": "check", "status": "failed" if problems else "passed", "problems": problems}, indent=2))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
