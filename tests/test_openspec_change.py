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
                "# Proposal\n\n## Why\nTest\n\n## What Changes\nTest\n\n"
                "## Capabilities\nTest\n\n## Impact\nTest\n\n"
                "## Acceptance criteria\n- [ ] Test\n\nKNOWN: evidence\n",
                encoding="utf-8"
            )
            (change_dir / "tasks.md").write_text("# Tasks\n\n## 1. Test\n- [ ] Task\n", encoding="utf-8")
            
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
                "# Proposal\n\n## Why\nTest\n\n## What Changes\nTest\n\n"
                "## Capabilities\nTest\n\n## Impact\nTest\n\n"
                "## Acceptance criteria\n- [ ] Test\n\nKNOWN: evidence\n",
                encoding="utf-8"
            )
            (change_dir / "design.md").write_text(
                "# Design\n\n## Context\nTest\n\n## Goals / Non-Goals\nTest\n\n"
                "## Decisions\nTest\n\n## Risks / Trade-offs\nTest\n",
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
                "# Proposal\n\n## Why\nTest\n\n## What Changes\nTest\n\n"
                "## Acceptance criteria\n- [ ] Test\n\nKNOWN: evidence\n",
                encoding="utf-8"
            )
            
            # Design missing Decisions
            (change_dir / "design.md").write_text(
                "# Design\n\n## Context\nTest\n\n## Goals / Non-Goals\nTest\n\n"
                "## Risks / Trade-offs\nTest\n",
                encoding="utf-8"
            )
            
            (change_dir / "tasks.md").write_text("# Tasks\n\n## 1. Test\n- [ ] Task\n", encoding="utf-8")
            
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
                "# Proposal\n\n## Why\nTest\n\n## What Changes\nTest\n\n"
                "## Capabilities\nTest\n\n## Impact\nTest\n\n"
                "## Acceptance criteria\n- [ ] Test\n",
                encoding="utf-8"
            )
            (change_dir / "design.md").write_text(
                "# Design\n\n## Context\nTest\n\n## Goals / Non-Goals\nTest\n\n"
                "## Decisions\nTest\n\n## Risks / Trade-offs\nTest\n",
                encoding="utf-8"
            )
            (change_dir / "tasks.md").write_text("# Tasks\n\n## 1. Test\n- [ ] Task\n", encoding="utf-8")
            
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
                "# Proposal\n\n## Why\nTest\n\n## What Changes\nTest\n\n"
                "## Capabilities\nTest\n\n## Impact\nTest\n\n"
                "## Acceptance criteria\n- [ ] Test\n\nKNOWN: evidence\n",
                encoding="utf-8"
            )
            (change_dir / "design.md").write_text(
                "# Design\n\n## Context\nTest\n\n## Goals / Non-Goals\nTest\n\n"
                "## Decisions\nTest\n\n## Risks / Trade-offs\nTest\n",
                encoding="utf-8"
            )
            (change_dir / "tasks.md").write_text("# Tasks\n\n## 1. Test\n- [ ] Task\n", encoding="utf-8")
            
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
                "# Proposal\n\n## Why\nTest\n\n## What Changes\nTest\n\n"
                "## Capabilities\nTest\n\n## Impact\nTest\n\n"
                "## Acceptance criteria\n- [ ] Test\n\nKNOWN: evidence\n",
                encoding="utf-8"
            )
            (change_dir / "design.md").write_text(
                "# Design\n\n## Context\nTest\n\n## Goals / Non-Goals\nTest\n\n"
                "## Decisions\nTest\n\n## Risks / Trade-offs\nTest\n",
                encoding="utf-8"
            )
            (change_dir / "tasks.md").write_text("# Tasks\n\n## 1. Test\n- [ ] Task\n", encoding="utf-8")
            
            errors = validator.validate_change(change_dir)
            self.assertTrue(
                any("spec" in e.artifact.lower() and "No spec files found" in e.reason for e in errors),
                "Should require specs/ or skip_specs: true"
            )


if __name__ == "__main__":
    unittest.main()
