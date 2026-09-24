#!/usr/bin/env python3
"""
Deterministic validator for OpenSpec verdict-change-v1 changes.

Usage: python3 scripts/validate_openspec_change.py <change-dir>

Validates that a change directory contains all required artifacts and fields
for the verdict-change-v1 schema, enforcing the full BOD-167 field mapping.

Exit codes:
  0 - Valid change
  1 - Invalid change (prints reason to stderr)
  2 - Usage error
"""
from __future__ import annotations

import re
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

# Evidence boundary labels (proposal must use these)
EVIDENCE_LABELS = ["KNOWN", "INFERRED", "NOT AVAILABLE"]


class ValidationError(NamedTuple):
    artifact: str
    reason: str


def has_routing_context_memory_content(content: str) -> bool:
    """
    Check if design.md addresses routing/context/memory implications.
    Must have either:
    - Explicit mention of routing/context/memory in a relevant way
    - Statement that it's "Not applicable" or "N/A"
    """
    content_lower = content.lower()

    # Check for explicit mentions of routing
    routing_pattern = r'routing[^a-z]'
    if re.search(routing_pattern, content_lower):
        return True

    # Check for "not applicable" or "n/a" related to routing/context/memory
    na_patterns = [
        r'routing.*not applicable',
        r'routing.*n/a',
        r'context.*memory.*not applicable',
        r'not applicable.*routing',
        r'n/a.*routing',
    ]
    if any(re.search(pattern, content_lower) for pattern in na_patterns):
        return True

    # Check for substantive discussion of context/memory semantics
    # (not just section headings like "## Context")
    substantive_patterns = [
        r'context\s+(budget|provenance|management|handling|semantics)',
        r'memory\s+(reads?|writes?|retention|semantics)',
    ]
    if any(re.search(pattern, content_lower) for pattern in substantive_patterns):
        return True

    return False


def check_requirements_have_scenarios(content: str, rel_path: str) -> list[ValidationError]:
    """Check that each requirement has at least one scenario."""
    errors: list[ValidationError] = []

    lines = content.split('\n')
    in_requirement = False
    requirement_num = 0
    requirement_name = ""
    has_scenario = False

    for line in lines:
        if line.startswith("### Requirement:"):
            # If we were in a previous requirement and it had no scenario, error
            if in_requirement and not has_scenario:
                errors.append(
                    ValidationError(
                        rel_path,
                        f"Requirement {requirement_num} must have at least one '#### Scenario:' (BOD-167 field 6)"
                    )
                )

            # Start new requirement
            in_requirement = True
            requirement_num += 1
            requirement_name = line.replace("### Requirement:", "").strip()
            has_scenario = False

        elif line.startswith("####") and "Scenario:" in line:
            if in_requirement:
                has_scenario = True

        elif line.startswith("##") and not line.startswith("###") and not line.startswith("####"):
            # New major section, close out current requirement
            if in_requirement and not has_scenario:
                errors.append(
                    ValidationError(
                        rel_path,
                        f"Requirement {requirement_num} must have at least one '#### Scenario:' (BOD-167 field 6)"
                    )
                )
            in_requirement = False

    # Check last requirement
    if in_requirement and not has_scenario:
        errors.append(
            ValidationError(
                rel_path,
                f"Requirement {requirement_num} must have at least one '#### Scenario:' (BOD-167 field 6)"
            )
        )

    return errors


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
        content_lower = content.lower()

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

            # Check for at least one of New Capabilities or Modified Capabilities
            has_new = "### New Capabilities" in content or "###New Capabilities" in content
            has_modified = "### Modified Capabilities" in content or "###Modified Capabilities" in content
            if not (has_new or has_modified):
                errors.append(
                    ValidationError(
                        artifact,
                        "Must have at least one of '### New Capabilities' or '### Modified Capabilities'"
                    )
                )

        # Additional checks for design.md (BOD-167 field mapping)
        if artifact == "design.md":
            # Security/trust implications (field 8)
            has_security = any(keyword in content_lower for keyword in ["security", "trust"])
            if not has_security:
                errors.append(
                    ValidationError(
                        artifact,
                        "Must address security/trust implications (BOD-167 field 8)"
                    )
                )

            # Routing/context/memory implications (field 9)
            if not has_routing_context_memory_content(content):
                errors.append(
                    ValidationError(
                        artifact,
                        "Must address routing/context/memory implications or state 'Not applicable' (BOD-167 field 9)"
                    )
                )

            # Migration/rollback (field 13)
            has_migration = any(keyword in content_lower for keyword in ["migration", "rollback"])
            if not has_migration:
                errors.append(
                    ValidationError(
                        artifact,
                        "Must address migration/rollback or state 'Not applicable' (BOD-167 field 13)"
                    )
                )

            # ADR impact (field 11)
            has_adr = "adr" in content_lower or "architecture decision" in content_lower
            if not has_adr:
                errors.append(
                    ValidationError(
                        artifact,
                        "Must document ADR impact (BOD-167 field 11)"
                    )
                )

        # Additional checks for tasks.md (BOD-167 field mapping)
        if artifact == "tasks.md":
            # Check for verification/proof in task descriptions (fields 10, 14)
            # Tasks must state how to verify completion
            has_verification = "verify" in content_lower or "proof" in content_lower or "test" in content_lower

            if not has_verification:
                errors.append(
                    ValidationError(
                        artifact,
                        "Task descriptions must state verification method (BOD-167 field 10, 14)"
                    )
                )

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
                rel_path = str(spec_file.relative_to(change_dir))

                # Check for required heading
                if "# Spec Delta" not in content:
                    errors.append(
                        ValidationError(
                            rel_path,
                            "Missing required heading: # Spec Delta"
                        )
                    )

                # Check for at least one Requirement block
                if "### Requirement:" not in content:
                    errors.append(
                        ValidationError(
                            rel_path,
                            "Must have at least one '### Requirement:' block (BOD-167 field 6)"
                        )
                    )
                else:
                    # Check that each requirement has at least one scenario
                    scenario_errors = check_requirements_have_scenarios(content, rel_path)
                    errors.extend(scenario_errors)

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
