#!/usr/bin/env python3
"""Tests for OpenSpec verdict-change-v1 validation."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any

# Import the validator
import importlib.util
import sys

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "validate_openspec_change",
    ROOT / "scripts" / "validate_openspec_change.py"
)
assert spec and spec.loader
validator = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = validator
spec.loader.exec_module(validator)


class OpenSpecValidationTests(unittest.TestCase):
    """Test verdict-change-v1 change validation."""

    def test_valid_sample_change_passes(self) -> None:
        """The bod-204 sample change should be valid."""
        sample_dir = ROOT / "openspec" / "changes" / "bod-204-openspec-foundation"
        self.assertTrue(sample_dir.exists(), f"Sample change not found: {sample_dir}")

        errors = validator.validate_change(sample_dir)
        self.assertEqual(
            errors, [],
            f"Valid sample should have no errors, got: {errors}"
        )

    def test_malformed_fixture_fails(self) -> None:
        """The malformed fixture should fail validation."""
        malformed_dir = ROOT / "tests" / "fixtures" / "openspec" / "malformed-change"
        self.assertTrue(malformed_dir.exists(), f"Malformed fixture not found: {malformed_dir}")

        errors = validator.validate_change(malformed_dir)
        self.assertGreater(
            len(errors), 0,
            "Malformed fixture should have validation errors"
        )

        # Check for expected errors
        error_messages = [e.reason for e in errors]
        self.assertTrue(
            any("Capabilities" in msg for msg in error_messages),
            "Should report missing Capabilities section"
        )
        self.assertTrue(
            any("evidence boundary" in msg for msg in error_messages),
            "Should report missing evidence labels"
        )

    def test_missing_proposal_fails(self) -> None:
        """Change without proposal.md should fail."""
        with tempfile.TemporaryDirectory() as tmpdir:
            change_dir = Path(tmpdir)
            (change_dir / "design.md").write_text("# Design\n\n## Context\nTest\n", encoding="utf-8")
            (change_dir / "tasks.md").write_text("# Tasks\n\n## 1. Test\n- [ ] Task\n", encoding="utf-8")

            errors = validator.validate_change(change_dir)
            self.assertTrue(
                any(e.artifact == "proposal.md" and "Missing required artifact" in e.reason for e in errors),
                f"Should report missing proposal.md, got: {errors}"
            )

    def test_missing_design_fails(self) -> None:
        """Change without design.md should fail."""
        with tempfile.TemporaryDirectory() as tmpdir:
            change_dir = Path(tmpdir)
            (change_dir / "proposal.md").write_text(
                "# Proposal\n\n## Why\nContent\n\n## What Changes\nContent\n\n"
                "## Capabilities\n### New Capabilities\nContent\n\n## Impact\nContent\n\n"
                "## Acceptance criteria\n- [ ] Item\n\nKNOWN: evidence\n",
                encoding="utf-8"
            )
            (change_dir / "tasks.md").write_text("# Tasks\n\n## 1. Test\n- [ ] Verify test\n", encoding="utf-8")

            errors = validator.validate_change(change_dir)
            self.assertTrue(
                any(e.artifact == "design.md" and "Missing required artifact" in e.reason for e in errors),
                f"Should report missing design.md, got: {errors}"
            )

    def test_missing_tasks_fails(self) -> None:
        """Change without tasks.md should fail."""
        with tempfile.TemporaryDirectory() as tmpdir:
            change_dir = Path(tmpdir)
            (change_dir / "proposal.md").write_text(
                "# Proposal\n\n## Why\nContent\n\n## What Changes\nContent\n\n"
                "## Capabilities\n### New Capabilities\nContent\n\n## Impact\nContent\n\n"
                "## Acceptance criteria\n- [ ] Item\n\nKNOWN: evidence\n",
                encoding="utf-8"
            )
            (change_dir / "design.md").write_text(
                "# Design\n\n## Context\nBackground\n\n## Goals / Non-Goals\nContent\n\n"
                "## Decisions\nTest\n\nSecurity: handled.\nMigration: not needed.\nADR: none.\n\n"
                "## Risks / Trade-offs\nContent\n",
                encoding="utf-8"
            )

            errors = validator.validate_change(change_dir)
            self.assertTrue(
                any(e.artifact == "tasks.md" and "Missing required artifact" in e.reason for e in errors),
                f"Should report missing tasks.md, got: {errors}"
            )

    def test_missing_required_headings_fails(self) -> None:
        """Missing required headings should be reported individually."""
        with tempfile.TemporaryDirectory() as tmpdir:
            change_dir = Path(tmpdir)

            # Proposal missing Capabilities and Impact
            (change_dir / "proposal.md").write_text(
                "# Proposal\n\n## Why\nContent\n\n## What Changes\nContent\n\n"
                "## Acceptance criteria\n- [ ] Item\n\nKNOWN: evidence\n",
                encoding="utf-8"
            )

            # Design missing Decisions
            (change_dir / "design.md").write_text(
                "# Design\n\n## Context\nBackground\n\n## Goals / Non-Goals\nContent\n\n"
                "## Risks / Trade-offs\nContent\n",
                encoding="utf-8"
            )

            (change_dir / "tasks.md").write_text("# Tasks\n\n## 1. Test\n- [ ] Verify task\n", encoding="utf-8")

            errors = validator.validate_change(change_dir)

            # Check specific missing headings
            with self.subTest(heading="Capabilities"):
                self.assertTrue(
                    any("## Capabilities" in e.reason for e in errors),
                    "Should report missing Capabilities heading"
                )

            with self.subTest(heading="Impact"):
                self.assertTrue(
                    any("## Impact" in e.reason for e in errors),
                    "Should report missing Impact heading"
                )

            with self.subTest(heading="Decisions"):
                self.assertTrue(
                    any("## Decisions" in e.reason for e in errors),
                    "Should report missing Decisions heading"
                )

    def test_missing_evidence_labels_fails(self) -> None:
        """Proposal without evidence labels should fail."""
        with tempfile.TemporaryDirectory() as tmpdir:
            change_dir = Path(tmpdir)
            (change_dir / "proposal.md").write_text(
                "# Proposal\n\n## Why\nContent\n\n## What Changes\nContent\n\n"
                "## Capabilities\n### New Capabilities\nContent\n\n## Impact\nContent\n\n"
                "## Acceptance criteria\n- [ ] Test\n",
                encoding="utf-8"
            )
            (change_dir / "design.md").write_text(
                "# Design\n\n## Context\nBackground\n\n## Goals / Non-Goals\nContent\n\n"
                "## Decisions\nTest\n\nSecurity: ok. Migration: none. ADR: none.\n\n"
                "## Risks / Trade-offs\nContent\n",
                encoding="utf-8"
            )
            (change_dir / "tasks.md").write_text("# Tasks\n\n## 1. Test\n- [ ] Verify task\n", encoding="utf-8")

            errors = validator.validate_change(change_dir)
            self.assertTrue(
                any("evidence boundary" in e.reason for e in errors),
                "Should require evidence labels (KNOWN/INFERRED/NOT AVAILABLE)"
            )

    def test_skip_specs_allows_no_specs(self) -> None:
        """Change with skip_specs: true should not require specs/."""
        with tempfile.TemporaryDirectory() as tmpdir:
            change_dir = Path(tmpdir)
            (change_dir / ".openspec.yaml").write_text("skip_specs: true\n", encoding="utf-8")
            (change_dir / "proposal.md").write_text(
                "# Proposal\n\n## Why\nContent\n\n## What Changes\nContent\n\n"
                "## Capabilities\n### New Capabilities\nContent\n\n## Impact\nContent\n\n"
                "## Acceptance criteria\n- [ ] Item\n\nKNOWN: evidence\n",
                encoding="utf-8"
            )
            (change_dir / "design.md").write_text(
                "# Design\n\n## Context\nBackground\n\n## Goals / Non-Goals\nContent\n\n"
                "## Decisions\nContent\n\nSecurity: ok. Migration: none. ADR: none. Routing: N/A.\n\n"
                "## Risks / Trade-offs\nContent\n",
                encoding="utf-8"
            )
            (change_dir / "tasks.md").write_text("# Tasks\n\n## 1. Test\n- [ ] Verify task\n", encoding="utf-8")

            errors = validator.validate_change(change_dir)
            # Should not complain about missing specs
            self.assertFalse(
                any("spec" in e.reason.lower() for e in errors),
                f"With skip_specs, should not require specs, got: {errors}"
            )

    def test_missing_specs_without_skip_fails(self) -> None:
        """Change without specs/ and without skip_specs should fail."""
        with tempfile.TemporaryDirectory() as tmpdir:
            change_dir = Path(tmpdir)
            (change_dir / "proposal.md").write_text(
                "# Proposal\n\n## Why\nContent\n\n## What Changes\nContent\n\n"
                "## Capabilities\n### New Capabilities\nContent\n\n## Impact\nContent\n\n"
                "## Acceptance criteria\n- [ ] Item\n\nKNOWN: evidence\n",
                encoding="utf-8"
            )
            (change_dir / "design.md").write_text(
                "# Design\n\n## Context\nBackground\n\n## Goals / Non-Goals\nContent\n\n"
                "## Decisions\nContent\n\nSecurity: ok. Migration: none. ADR: none. Routing: N/A.\n\n"
                "## Risks / Trade-offs\nContent\n",
                encoding="utf-8"
            )
            (change_dir / "tasks.md").write_text("# Tasks\n\n## 1. Test\n- [ ] Verify task\n", encoding="utf-8")

            errors = validator.validate_change(change_dir)
            self.assertTrue(
                any("spec" in e.artifact.lower() and "No spec files found" in e.reason for e in errors),
                "Should require specs/ or skip_specs: true"
            )

    def test_bod167_field_8_security_trust_required(self) -> None:
        """BOD-167 field 8: Security/trust implications must be addressed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            change_dir = Path(tmpdir)
            (change_dir / ".openspec.yaml").write_text("skip_specs: true\n", encoding="utf-8")
            (change_dir / "proposal.md").write_text(
                "# Proposal\n\n## Why\nContent\n\n## What Changes\nContent\n\n"
                "## Capabilities\n### New Capabilities\nContent\n\n## Impact\nContent\n\n"
                "## Acceptance criteria\n- [ ] Item\n\nKNOWN: evidence\n",
                encoding="utf-8"
            )
            # Design without security/trust mention
            (change_dir / "design.md").write_text(
                "# Design\n\n## Context\nBackground\n\n## Goals / Non-Goals\nContent\n\n"
                "## Decisions\nTest\n\nMigration: none. ADR: none.\n\n"
                "## Risks / Trade-offs\nContent\n",
                encoding="utf-8"
            )
            (change_dir / "tasks.md").write_text("# Tasks\n\n## 1. Test\n- [ ] Verify task\n", encoding="utf-8")

            errors = validator.validate_change(change_dir)
            self.assertTrue(
                any("Security / trust implications" in e.reason and "BOD-167 field 8" in e.reason for e in errors),
                "Should require Security / trust implications section (BOD-167 field 8)"
            )

    def test_bod167_field_9_routing_context_memory_required(self) -> None:
        """BOD-167 field 9: Routing/context/memory implications must be addressed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            change_dir = Path(tmpdir)
            (change_dir / ".openspec.yaml").write_text("skip_specs: true\n", encoding="utf-8")
            (change_dir / "proposal.md").write_text(
                "# Proposal\n\n## Why\nContent\n\n## What Changes\nContent\n\n"
                "## Capabilities\n### New Capabilities\nContent\n\n## Impact\nContent\n\n"
                "## Acceptance criteria\n- [ ] Item\n\nKNOWN: evidence\n",
                encoding="utf-8"
            )
            # Design without routing/context/memory mention
            (change_dir / "design.md").write_text(
                "# Design\n\n## Context\nBackground\n\n## Goals / Non-Goals\nContent\n\n"
                "## Decisions\nTest\n\nSecurity: ok. Migration: none. ADR: none.\n\n"
                "## Risks / Trade-offs\nContent\n",
                encoding="utf-8"
            )
            (change_dir / "tasks.md").write_text("# Tasks\n\n## 1. Test\n- [ ] Verify task\n", encoding="utf-8")

            errors = validator.validate_change(change_dir)
            self.assertTrue(
                any("routing" in e.reason.lower() and "BOD-167 field 9" in e.reason for e in errors),
                "Should require routing/context/memory implications (BOD-167 field 9)"
            )

    def test_bod167_field_11_adr_impact_required(self) -> None:
        """BOD-167 field 11: ADR impact must be documented."""
        with tempfile.TemporaryDirectory() as tmpdir:
            change_dir = Path(tmpdir)
            (change_dir / ".openspec.yaml").write_text("skip_specs: true\n", encoding="utf-8")
            (change_dir / "proposal.md").write_text(
                "# Proposal\n\n## Why\nContent\n\n## What Changes\nContent\n\n"
                "## Capabilities\n### New Capabilities\nContent\n\n## Impact\nContent\n\n"
                "## Acceptance criteria\n- [ ] Item\n\nKNOWN: evidence\n",
                encoding="utf-8"
            )
            # Design without ADR mention
            (change_dir / "design.md").write_text(
                "# Design\n\n## Context\nBackground\n\n## Goals / Non-Goals\nContent\n\n"
                "## Decisions\nTest\n\nSecurity: ok. Migration: none. Routing: N/A.\n\n"
                "## Risks / Trade-offs\nContent\n",
                encoding="utf-8"
            )
            (change_dir / "tasks.md").write_text("# Tasks\n\n## 1. Test\n- [ ] Verify task\n", encoding="utf-8")

            errors = validator.validate_change(change_dir)
            self.assertTrue(
                any("ADR impact" in e.reason and "BOD-167 field 11" in e.reason for e in errors),
                "Should require ADR impact documentation (BOD-167 field 11)"
            )

    def test_bod167_field_13_migration_rollback_required(self) -> None:
        """BOD-167 field 13: Migration/rollback must be addressed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            change_dir = Path(tmpdir)
            (change_dir / ".openspec.yaml").write_text("skip_specs: true\n", encoding="utf-8")
            (change_dir / "proposal.md").write_text(
                "# Proposal\n\n## Why\nContent\n\n## What Changes\nContent\n\n"
                "## Capabilities\n### New Capabilities\nContent\n\n## Impact\nContent\n\n"
                "## Acceptance criteria\n- [ ] Item\n\nKNOWN: evidence\n",
                encoding="utf-8"
            )
            # Design without migration/rollback mention
            (change_dir / "design.md").write_text(
                "# Design\n\n## Context\nBackground\n\n## Goals / Non-Goals\nContent\n\n"
                "## Decisions\nTest\n\nSecurity: ok. ADR: none. Routing: N/A.\n\n"
                "## Risks / Trade-offs\nContent\n",
                encoding="utf-8"
            )
            (change_dir / "tasks.md").write_text("# Tasks\n\n## 1. Test\n- [ ] Verify task\n", encoding="utf-8")

            errors = validator.validate_change(change_dir)
            self.assertTrue(
                any("migration" in e.reason.lower() and "BOD-167 field 13" in e.reason for e in errors),
                "Should require migration/rollback (BOD-167 field 13)"
            )

    def test_bod167_field_6_requirements_must_have_scenarios(self) -> None:
        """BOD-167 field 6: Each requirement must have at least one scenario."""
        with tempfile.TemporaryDirectory() as tmpdir:
            change_dir = Path(tmpdir)
            (change_dir / "proposal.md").write_text(
                "# Proposal\n\n## Why\nContent\n\n## What Changes\nContent\n\n"
                "## Capabilities\n### New Capabilities\nContent\n\n## Impact\nContent\n\n"
                "## Acceptance criteria\n- [ ] Item\n\nKNOWN: evidence\n",
                encoding="utf-8"
            )
            (change_dir / "design.md").write_text(
                "# Design\n\n## Context\nBackground\n\n## Goals / Non-Goals\nContent\n\n"
                "## Decisions\nContent\n\nSecurity: ok. Migration: none. ADR: none. Routing: N/A.\n\n"
                "## Risks / Trade-offs\nContent\n",
                encoding="utf-8"
            )
            (change_dir / "tasks.md").write_text("# Tasks\n\n## 1. Test\n- [ ] Verify task\n", encoding="utf-8")

            # Spec with requirement but no scenario
            specs_dir = change_dir / "specs" / "test-capability"
            specs_dir.mkdir(parents=True)
            (specs_dir / "spec.md").write_text(
                "# Spec Delta\n\n## Purpose\nTest purpose.\n\n"
                "## ADDED Requirements\n\n### Requirement: Test\nTest requirement.\n",
                encoding="utf-8"
            )

            errors = validator.validate_change(change_dir)
            self.assertTrue(
                any("Scenario" in e.reason and "BOD-167 field 6" in e.reason for e in errors),
                "Should require at least one scenario per requirement (BOD-167 field 6)"
            )

    def test_bod167_field_10_14_verification_required(self) -> None:
        """BOD-167 fields 10, 14: Tasks must state verification method."""
        with tempfile.TemporaryDirectory() as tmpdir:
            change_dir = Path(tmpdir)
            (change_dir / ".openspec.yaml").write_text("skip_specs: true\n", encoding="utf-8")
            (change_dir / "proposal.md").write_text(
                "# Proposal\n\n## Why\nContent\n\n## What Changes\nContent\n\n"
                "## Capabilities\n### New Capabilities\nContent\n\n## Impact\nContent\n\n"
                "## Acceptance criteria\n- [ ] Item\n\nKNOWN: evidence\n",
                encoding="utf-8"
            )
            (change_dir / "design.md").write_text(
                "# Design\n\n## Context\nBackground\n\n## Goals / Non-Goals\nContent\n\n"
                "## Decisions\nContent\n\nSecurity: ok. Migration: none. ADR: none. Routing: N/A.\n\n"
                "## Risks / Trade-offs\nContent\n",
                encoding="utf-8"
            )
            # Tasks without verification mention
            (change_dir / "tasks.md").write_text("# Tasks\n\n## 1. Work\n- [ ] Do something\n", encoding="utf-8")

            errors = validator.validate_change(change_dir)
            self.assertTrue(
                any("verification" in e.reason.lower() and "BOD-167 field" in e.reason for e in errors),
                "Should require verification method in tasks (BOD-167 fields 10, 14)"
            )

    def test_capabilities_subsections_at_least_one_required(self) -> None:
        """At least one of New Capabilities or Modified Capabilities must be present."""
        with tempfile.TemporaryDirectory() as tmpdir:
            change_dir = Path(tmpdir)
            (change_dir / ".openspec.yaml").write_text("skip_specs: true\n", encoding="utf-8")
            # Proposal with Capabilities section but neither New nor Modified subsections
            (change_dir / "proposal.md").write_text(
                "# Proposal\n\n## Why\nContent\n\n## What Changes\nContent\n\n"
                "## Capabilities\n\nSome text but no subsections.\n\n## Impact\nTest\n\n"
                "## Acceptance criteria\n- [ ] Item\n\nKNOWN: evidence\n",
                encoding="utf-8"
            )
            (change_dir / "design.md").write_text(
                "# Design\n\n## Context\nBackground\n\n## Goals / Non-Goals\nContent\n\n"
                "## Decisions\nContent\n\nSecurity: ok. Migration: none. ADR: none. Routing: N/A.\n\n"
                "## Risks / Trade-offs\nContent\n",
                encoding="utf-8"
            )
            (change_dir / "tasks.md").write_text("# Tasks\n\n## 1. Test\n- [ ] Verify task\n", encoding="utf-8")

            errors = validator.validate_change(change_dir)
            self.assertTrue(
                any("New Capabilities" in e.reason and "Modified Capabilities" in e.reason for e in errors),
                "Should require at least one of New Capabilities or Modified Capabilities"
            )

    def test_leak_security_section_removed_word_elsewhere_fails(self) -> None:
        """Leak test: removing ## Security section but keeping word 'security' elsewhere should FAIL."""
        with tempfile.TemporaryDirectory() as tmpdir:
            change_dir = Path(tmpdir)
            (change_dir / ".openspec.yaml").write_text("skip_specs: true\n", encoding="utf-8")
            (change_dir / "proposal.md").write_text(
                "# Proposal\n\n## Why\nContent\n\n## What Changes\nContent\n\n"
                "## Capabilities\n### New Capabilities\nContent\n\n## Impact\nContent\n\n"
                "## Acceptance criteria\n- [ ] Item\n\nKNOWN: evidence\n",
                encoding="utf-8"
            )
            # Design with Security word in Decisions but NO ## Security / trust implications section
            (change_dir / "design.md").write_text(
                "# Design\n\n## Context\nBackground\n\n## Goals / Non-Goals\nContent\n\n"
                "## Decisions\nNo security impact was analysed here.\n\n"
                "## Risks / Trade-offs\nContent\n\n"
                "## Routing / context / memory implications\nNot applicable.\n\n"
                "## Migration / rollback\nNone.\n\n"
                "## ADR impact\nNone.\n",
                encoding="utf-8"
            )
            (change_dir / "tasks.md").write_text("# Tasks\n\n## 1. Work\n- [ ] Do something and verify\n", encoding="utf-8")

            errors = validator.validate_change(change_dir)
            self.assertTrue(
                any("Security / trust implications" in e.reason for e in errors),
                f"Should require ## Security / trust implications section, got: {errors}"
            )

    def test_section_with_empty_body_fails(self) -> None:
        """Section present but with empty body should fail."""
        with tempfile.TemporaryDirectory() as tmpdir:
            change_dir = Path(tmpdir)
            (change_dir / ".openspec.yaml").write_text("skip_specs: true\n", encoding="utf-8")
            (change_dir / "proposal.md").write_text(
                "# Proposal\n\n## Why\nContent\n\n## What Changes\nContent\n\n"
                "## Capabilities\n### New Capabilities\nContent\n\n## Impact\nContent\n\n"
                "## Acceptance criteria\n- [ ] Item\n\nKNOWN: evidence\n",
                encoding="utf-8"
            )
            # Design with Security section but EMPTY body (next section immediately follows)
            (change_dir / "design.md").write_text(
                "# Design\n\n## Context\nBackground\n\n## Goals / Non-Goals\nContent\n\n"
                "## Decisions\nContent\n\n"
                "## Risks / Trade-offs\nContent\n\n"
                "## Security / trust implications\n\n## Routing / context / memory implications\nContent\n\n"
                "## Migration / rollback\nNone.\n\n"
                "## ADR impact\nNone.\n",
                encoding="utf-8"
            )
            (change_dir / "tasks.md").write_text("# Tasks\n\n## 1. Work\n- [ ] Do something and verify\n", encoding="utf-8")

            errors = validator.validate_change(change_dir)
            self.assertTrue(
                any("empty body" in e.reason.lower() and "Security / trust implications" in e.reason for e in errors),
                f"Should fail on empty Security section body, got: {errors}"
            )

    def test_task_group_without_own_proof_fails(self) -> None:
        """One task group without proof should fail even if another has proof."""
        with tempfile.TemporaryDirectory() as tmpdir:
            change_dir = Path(tmpdir)
            (change_dir / ".openspec.yaml").write_text("skip_specs: true\n", encoding="utf-8")
            (change_dir / "proposal.md").write_text(
                "# Proposal\n\n## Why\nContent\n\n## What Changes\nContent\n\n"
                "## Capabilities\n### New Capabilities\nContent\n\n## Impact\nContent\n\n"
                "## Acceptance criteria\n- [ ] Item\n\nKNOWN: evidence\n",
                encoding="utf-8"
            )
            (change_dir / "design.md").write_text(
                "# Design\n\n## Context\nBackground\n\n## Goals / Non-Goals\nContent\n\n"
                "## Decisions\nContent\n\n"
                "## Risks / Trade-offs\nContent\n\n"
                "## Security / trust implications\nNone.\n\n"
                "## Routing / context / memory implications\nNot applicable.\n\n"
                "## Migration / rollback\nNone.\n\n"
                "## ADR impact\nNone.\n",
                encoding="utf-8"
            )
            # Tasks with group 1 having proof, but group 2 without proof
            (change_dir / "tasks.md").write_text(
                "# Tasks\n\n"
                "## 1. First Group\n- [ ] Do something and verify\n\n"
                "## 2. Second Group\n- [ ] Do another thing\n",
                encoding="utf-8"
            )

            errors = validator.validate_change(change_dir)
            self.assertTrue(
                any("## 2. Second Group" in e.reason and "verification" in e.reason.lower() for e in errors),
                f"Should fail on group 2 missing verification, got: {errors}"
            )



class AblationTests(unittest.TestCase):
    """Ablation tests: removing each required section should fail validation."""

    def setUp(self) -> None:
        """Load the valid sample change."""
        self.sample_dir = ROOT / "openspec" / "changes" / "bod-204-openspec-foundation"
        self.assertTrue(self.sample_dir.exists())

        # Load all artifact contents
        self.proposal = (self.sample_dir / "proposal.md").read_text(encoding="utf-8")
        self.design = (self.sample_dir / "design.md").read_text(encoding="utf-8")
        self.tasks = (self.sample_dir / "tasks.md").read_text(encoding="utf-8")
        self.spec = (self.sample_dir / "specs" / "openspec-integration" / "spec.md").read_text(encoding="utf-8")

    def _create_change_with_modified_content(self, tmpdir: str, **modifications: str) -> Path:
        """Create a change directory with modified artifact content."""
        change_dir = Path(tmpdir)

        # Write proposal
        proposal_content = modifications.get("proposal", self.proposal)
        (change_dir / "proposal.md").write_text(proposal_content, encoding="utf-8")

        # Write design
        design_content = modifications.get("design", self.design)
        (change_dir / "design.md").write_text(design_content, encoding="utf-8")

        # Write tasks
        tasks_content = modifications.get("tasks", self.tasks)
        (change_dir / "tasks.md").write_text(tasks_content, encoding="utf-8")

        # Write spec
        if "skip_specs" not in modifications:
            specs_dir = change_dir / "specs" / "openspec-integration"
            specs_dir.mkdir(parents=True)
            spec_content = modifications.get("spec", self.spec)
            (specs_dir / "spec.md").write_text(spec_content, encoding="utf-8")
        else:
            (change_dir / ".openspec.yaml").write_text("skip_specs: true\n", encoding="utf-8")

        return change_dir

    def test_ablation_proposal_why_section(self) -> None:
        """Removing ## Why from proposal should fail."""
        with tempfile.TemporaryDirectory() as tmpdir:
            modified_proposal = self.proposal.replace("## Why", "## Removed")
            change_dir = self._create_change_with_modified_content(tmpdir, proposal=modified_proposal)

            errors = validator.validate_change(change_dir)
            self.assertTrue(
                any("## Why" in e.reason for e in errors),
                "Should fail when ## Why is removed"
            )

    def test_ablation_proposal_what_changes_section(self) -> None:
        """Removing ## What Changes from proposal should fail."""
        with tempfile.TemporaryDirectory() as tmpdir:
            modified_proposal = self.proposal.replace("## What Changes", "## Removed")
            change_dir = self._create_change_with_modified_content(tmpdir, proposal=modified_proposal)

            errors = validator.validate_change(change_dir)
            self.assertTrue(
                any("## What Changes" in e.reason for e in errors),
                "Should fail when ## What Changes is removed"
            )

    def test_ablation_proposal_capabilities_section(self) -> None:
        """Removing ## Capabilities from proposal should fail."""
        with tempfile.TemporaryDirectory() as tmpdir:
            modified_proposal = self.proposal.replace("## Capabilities", "## Removed")
            change_dir = self._create_change_with_modified_content(tmpdir, proposal=modified_proposal)

            errors = validator.validate_change(change_dir)
            self.assertTrue(
                any("## Capabilities" in e.reason for e in errors),
                "Should fail when ## Capabilities is removed"
            )

    def test_ablation_proposal_impact_section(self) -> None:
        """Removing ## Impact from proposal should fail."""
        with tempfile.TemporaryDirectory() as tmpdir:
            modified_proposal = self.proposal.replace("## Impact", "## Removed")
            change_dir = self._create_change_with_modified_content(tmpdir, proposal=modified_proposal)

            errors = validator.validate_change(change_dir)
            self.assertTrue(
                any("## Impact" in e.reason for e in errors),
                "Should fail when ## Impact is removed"
            )

    def test_ablation_proposal_acceptance_criteria(self) -> None:
        """Removing acceptance criteria from proposal should fail."""
        with tempfile.TemporaryDirectory() as tmpdir:
            modified_proposal = self.proposal.replace("## Acceptance criteria", "## Removed")
            change_dir = self._create_change_with_modified_content(tmpdir, proposal=modified_proposal)

            errors = validator.validate_change(change_dir)
            self.assertTrue(
                any("acceptance criteria" in e.reason.lower() for e in errors),
                "Should fail when acceptance criteria is removed"
            )

    def test_ablation_proposal_evidence_labels(self) -> None:
        """Removing evidence labels from proposal should fail."""
        with tempfile.TemporaryDirectory() as tmpdir:
            modified_proposal = self.proposal.replace("KNOWN", "").replace("INFERRED", "").replace("NOT AVAILABLE", "")
            change_dir = self._create_change_with_modified_content(tmpdir, proposal=modified_proposal)

            errors = validator.validate_change(change_dir)
            self.assertTrue(
                any("evidence boundary" in e.reason.lower() for e in errors),
                "Should fail when evidence labels are removed"
            )

    def test_ablation_design_context_section(self) -> None:
        """Removing ## Context from design should fail."""
        with tempfile.TemporaryDirectory() as tmpdir:
            modified_design = self.design.replace("## Context", "## Removed")
            change_dir = self._create_change_with_modified_content(tmpdir, design=modified_design)

            errors = validator.validate_change(change_dir)
            self.assertTrue(
                any("## Context" in e.reason for e in errors),
                "Should fail when ## Context is removed"
            )

    def test_ablation_design_goals_section(self) -> None:
        """Removing ## Goals / Non-Goals from design should fail."""
        with tempfile.TemporaryDirectory() as tmpdir:
            modified_design = self.design.replace("## Goals / Non-Goals", "## Removed")
            change_dir = self._create_change_with_modified_content(tmpdir, design=modified_design)

            errors = validator.validate_change(change_dir)
            self.assertTrue(
                any("## Goals / Non-Goals" in e.reason for e in errors),
                "Should fail when ## Goals / Non-Goals is removed"
            )

    def test_ablation_design_decisions_section(self) -> None:
        """Removing ## Decisions from design should fail."""
        with tempfile.TemporaryDirectory() as tmpdir:
            modified_design = self.design.replace("## Decisions", "## Removed")
            change_dir = self._create_change_with_modified_content(tmpdir, design=modified_design)

            errors = validator.validate_change(change_dir)
            self.assertTrue(
                any("## Decisions" in e.reason for e in errors),
                "Should fail when ## Decisions is removed"
            )

    def test_ablation_design_risks_section(self) -> None:
        """Removing ## Risks / Trade-offs from design should fail."""
        with tempfile.TemporaryDirectory() as tmpdir:
            modified_design = self.design.replace("## Risks / Trade-offs", "## Removed")
            change_dir = self._create_change_with_modified_content(tmpdir, design=modified_design)

            errors = validator.validate_change(change_dir)
            self.assertTrue(
                any("## Risks / Trade-offs" in e.reason for e in errors),
                "Should fail when ## Risks / Trade-offs is removed"
            )

    def test_ablation_design_security_mention(self) -> None:
        """Removing Security / trust implications section from design should fail."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Remove the entire Security section from design
            lines = self.design.split("\n")
            modified_lines = []
            skip_section = False
            for line in lines:
                if "## Security / trust implications" in line or "## Security/trust implications" in line:
                    skip_section = True
                elif line.startswith("##") and not line.startswith("###"):
                    skip_section = False
                    modified_lines.append(line)
                elif not skip_section:
                    modified_lines.append(line)

            modified_design = "\n".join(modified_lines)
            change_dir = self._create_change_with_modified_content(tmpdir, design=modified_design)

            errors = validator.validate_change(change_dir)
            self.assertTrue(
                any("Security / trust implications" in e.reason for e in errors),
                "Should fail when Security / trust implications section is removed"
            )

    def test_ablation_design_migration_mention(self) -> None:
        """Removing Migration / rollback section from design should fail."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Remove the entire Migration section from design
            lines = self.design.split("\n")
            modified_lines = []
            skip_section = False
            for line in lines:
                if "## Migration" in line or "## migration" in line.lower():
                    skip_section = True
                elif line.startswith("##") and not line.startswith("###"):
                    skip_section = False
                    modified_lines.append(line)
                elif not skip_section:
                    modified_lines.append(line)

            modified_design = "\n".join(modified_lines)
            change_dir = self._create_change_with_modified_content(tmpdir, design=modified_design)

            errors = validator.validate_change(change_dir)
            self.assertTrue(
                any("Migration / rollback" in e.reason for e in errors),
                "Should fail when Migration / rollback section is removed"
            )

    def test_ablation_design_adr_mention(self) -> None:
        """Removing ADR mentions from design should fail."""
        with tempfile.TemporaryDirectory() as tmpdir:
            modified_design = self.design.replace("ADR", "removed").replace("adr", "removed")
            change_dir = self._create_change_with_modified_content(tmpdir, design=modified_design)

            errors = validator.validate_change(change_dir)
            self.assertTrue(
                any("ADR impact" in e.reason for e in errors),
                "Should fail when ADR mentions are removed"
            )

    def test_ablation_spec_added_requirements(self) -> None:
        """Removing all requirements from spec should fail."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a spec with sections but no requirements
            modified_spec = "# Spec Delta\n\n## Purpose\n\nContent.\n\n## ADDED Requirements\n\nNo requirements here.\n"
            change_dir = self._create_change_with_modified_content(tmpdir, spec=modified_spec)

            errors = validator.validate_change(change_dir)
            self.assertTrue(
                any("Requirement:" in e.reason for e in errors),
                "Should fail when all requirements are removed"
            )

    def test_ablation_spec_requirement_scenario(self) -> None:
        """Removing scenarios from a requirement should fail."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Remove the first scenario block
            lines = self.spec.split("\n")
            modified_lines = []
            skip_until_next_req = False
            for line in lines:
                if skip_until_next_req:
                    if line.startswith("### Requirement:") or line.startswith("##"):
                        skip_until_next_req = False
                        modified_lines.append(line)
                    # Skip scenario lines
                elif "#### Scenario:" in line:
                    skip_until_next_req = True
                else:
                    modified_lines.append(line)

            modified_spec = "\n".join(modified_lines)
            change_dir = self._create_change_with_modified_content(tmpdir, spec=modified_spec)

            errors = validator.validate_change(change_dir)
            self.assertTrue(
                any("Scenario" in e.reason for e in errors),
                "Should fail when requirement scenarios are removed"
            )

    def test_ablation_tasks_verification(self) -> None:
        """Removing verification mentions from tasks should fail."""
        with tempfile.TemporaryDirectory() as tmpdir:
            modified_tasks = self.tasks.replace("verify", "removed").replace("Verify", "Removed").replace("test", "removed").replace("Test", "Removed").replace("proof", "removed").replace("Proof", "Removed")
            change_dir = self._create_change_with_modified_content(tmpdir, tasks=modified_tasks)

            errors = validator.validate_change(change_dir)
            self.assertTrue(
                any("verification" in e.reason.lower() for e in errors),
                "Should fail when verification mentions are removed from tasks"
            )


if __name__ == "__main__":
    unittest.main()
