#!/usr/bin/env python3
"""Build and verify the stable published evidence fixtures (ECO-003 class 2).

Class-2 artifacts are *published evidence*: committed, reproducible, and
never silently overwritten by a test or demo run. This script is the only
supported writer for `evidence/`, and it writes only when explicitly asked
with `--write`. The default mode is `--check`, which regenerates the
fixture in memory and compares it against what is committed, so any caller
that runs the script without arguments — CI, a test, a demo — is
structurally incapable of mutating the fixture.

Reproducibility rests on the fixture being a pure function of committed
source: it is derived from `compatibility-manifest.json` only. No
timestamps, no absolute paths, no filesystem probing, no environment. The
same commit therefore always produces byte-identical evidence on any
machine, which is what makes the recorded SHA-256 digests meaningful as
provenance rather than as a snapshot of one developer's laptop.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "compatibility-manifest.json"
EVIDENCE_DIR = ROOT / "evidence"
BASELINE = EVIDENCE_DIR / "compatibility-baseline.json"
MANIFEST = EVIDENCE_DIR / "EVIDENCE_MANIFEST.json"

# Fields projected into the baseline. Deliberately excludes `path` (a
# machine-local relative path) and anything else that could differ between
# a developer checkout and a CI runner.
BASELINE_FIELDS = (
    "id",
    "package",
    "artifact_version",
    "contract_version",
    "policy_version",
    "publication_status",
    "release_train_pin",
    "maturity",
    "support_level",
    "status",
)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def serialize(payload: object) -> str:
    """Canonical JSON: sorted keys, fixed indent, trailing newline."""
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def build_baseline(manifest: dict) -> dict:
    repositories = []
    for repo in manifest.get("repositories", []):
        repositories.append({field: repo.get(field) for field in BASELINE_FIELDS})
    repositories.sort(key=lambda row: row["id"] or "")
    return {
        "contract_version": manifest.get("contract_version"),
        "policy_version": manifest.get("policy_version"),
        "schema_version": manifest.get("schema_version"),
        "release_train": manifest.get("release_train"),
        "evidence_timestamp": manifest.get("evidence_timestamp"),
        "repositories": repositories,
    }


def build_manifest(source_text: str, baseline_text: str) -> dict:
    return {
        "generator": "scripts/build_evidence.py",
        "policy": "docs/ARTIFACT_HYGIENE_POLICY.md",
        "class": "2-stable-published-evidence",
        "source": {
            "path": "compatibility-manifest.json",
            "sha256": sha256_text(source_text),
        },
        "artifacts": [
            {
                "path": "evidence/compatibility-baseline.json",
                "sha256": sha256_text(baseline_text),
            }
        ],
    }


def render() -> dict[Path, str]:
    """Return the full evidence set as {path: canonical text}."""
    source_text = SOURCE.read_text(encoding="utf-8")
    baseline_text = serialize(build_baseline(json.loads(source_text)))
    manifest_text = serialize(build_manifest(source_text, baseline_text))
    return {BASELINE: baseline_text, MANIFEST: manifest_text}


def check() -> tuple[int, list[str]]:
    problems: list[str] = []
    for path, expected in render().items():
        rel = path.relative_to(ROOT)
        if not path.exists():
            problems.append(f"{rel}: missing; run scripts/build_evidence.py --write")
            continue
        actual = path.read_text(encoding="utf-8")
        if actual != expected:
            problems.append(
                f"{rel}: stale or hand-edited "
                f"(committed sha256 {sha256_text(actual)[:12]}, "
                f"expected {sha256_text(expected)[:12]}); "
                "regenerate with scripts/build_evidence.py --write"
            )
    return (1 if problems else 0), problems


def write() -> list[str]:
    EVIDENCE_DIR.mkdir(exist_ok=True)
    changed: list[str] = []
    for path, text in render().items():
        previous = path.read_text(encoding="utf-8") if path.exists() else None
        if previous != text:
            path.write_text(text, encoding="utf-8")
            changed.append(str(path.relative_to(ROOT)))
    return changed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write",
        action="store_true",
        help="regenerate the evidence fixtures (the only mode that writes)",
    )
    args = parser.parse_args()

    if args.write:
        changed = write()
        print(json.dumps({"mode": "write", "changed": changed}, indent=2, sort_keys=True))
        return 0

    code, problems = check()
    print(
        json.dumps(
            {
                "mode": "check",
                "status": "failed" if problems else "passed",
                "problems": problems,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return code


if __name__ == "__main__":
    raise SystemExit(main())
