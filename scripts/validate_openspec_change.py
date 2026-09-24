#!/usr/bin/env python3
"""
Deterministic validator for OpenSpec verdict-change-v1 changes.

Usage: python3 scripts/validate_openspec_change.py <change-dir>

Validates that a change directory contains all required artifacts and fields
for the verdict-change-v1 schema.

Exit codes:
  0 - Valid change
  1 - Invalid change (prints reason to stderr)
  2 - Usage error
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import NamedTuple

# Required artifacts for verdict-change-v1
REQUIRED_ARTIFACTS = {
    "proposal.md": [
        "## Why",
        "## What Changes",
        "## Capabilities",
        "## Impact",
    ],
    "design.md": [
        "## Context",
        "## Goals / Non-Goals",
        "## Decisions",
        "## Risks / Trade-offs",
    ],
    "tasks.md": [
        "# Tasks",
        "## 1.",
    ],
}

# Spec files are dynamic (under specs/ directory), but must exist unless skip_specs is set
# Required spec headings when present
SPEC_REQUIRED_HEADINGS = [
    "# Spec Delta",
]

# Evidence boundary labels (proposal must use these)
EVIDENCE_LABELS = ["KNOWN", "INFERRED", "NOT AVAILABLE"]


class ValidationError(NamedTuple):
    artifact: str
    reason: str


def validate_change(change_dir: Path) -> list[ValidationError]:
    """Validate a change directory for verdict-change-v1 compliance."""
    errors: list[ValidationError] = []
    
    if not change_dir.is_dir():
        errors.append(ValidationError("", f"Change directory does not exist: {change_dir}"))
        return errors
    
    # Check for .openspec.yaml to see if specs are skipped
    openspec_yaml = change_dir / ".openspec.yaml"
    skip_specs = False
    if openspec_yaml.exists():
        content = openspec_yaml.read_text(encoding="utf-8")
        skip_specs = "skip_specs: true" in content or "skip_specs:true" in content
    
    # Validate required artifacts
    for artifact, required_headings in REQUIRED_ARTIFACTS.items():
        artifact_path = change_dir / artifact
        
        if not artifact_path.exists():
            errors.append(ValidationError(artifact, f"Missing required artifact: {artifact}"))
            continue
        
        content = artifact_path.read_text(encoding="utf-8")
        
        # Check for required headings
        for heading in required_headings:
            if heading not in content:
                errors.append(ValidationError(artifact, f"Missing required heading: {heading}"))
        
        # Additional checks for proposal.md
        if artifact == "proposal.md":
            # Check for evidence boundary labels
            has_evidence = any(label in content for label in EVIDENCE_LABELS)
            if not has_evidence:
                errors.append(
                    ValidationError(
                        artifact,
                        "Must include evidence boundary using KNOWN/INFERRED/NOT AVAILABLE labels"
                    )
                )
            
            # Check for acceptance criteria section
            if "## Acceptance criteria" not in content and "## Acceptance Criteria" not in content:
                errors.append(ValidationError(artifact, "Missing acceptance criteria section"))
    
    # Validate spec files (unless skipped)
    specs_dir = change_dir / "specs"
    if not skip_specs:
        if not specs_dir.exists() or not any(specs_dir.rglob("*.md")):
            errors.append(
                ValidationError(
                    "specs/",
                    "No spec files found. Either add spec files or set skip_specs: true in .openspec.yaml"
                )
            )
        else:
            # Validate each spec file
            for spec_file in specs_dir.rglob("*.md"):
                content = spec_file.read_text(encoding="utf-8")
                for heading in SPEC_REQUIRED_HEADINGS:
                    if heading not in content:
                        errors.append(
                            ValidationError(
                                str(spec_file.relative_to(change_dir)),
                                f"Missing required heading: {heading}"
                            )
                        )
    
    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/validate_openspec_change.py <change-dir>", file=sys.stderr)
        return 2
    
    change_dir = Path(sys.argv[1])
    errors = validate_change(change_dir)
    
    if errors:
        print(f"Validation failed for {change_dir}:", file=sys.stderr)
        for error in errors:
            if error.artifact:
                print(f"  [{error.artifact}] {error.reason}", file=sys.stderr)
            else:
                print(f"  {error.reason}", file=sys.stderr)
        return 1
    
    print(f"✓ Valid verdict-change-v1 change: {change_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
