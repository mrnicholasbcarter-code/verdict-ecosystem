"""
Tests for the ownership phrase guard script.
Ensures CI can run the guard via unittest, preventing regression of
Prime ownership claims over Verdict orchestration.
"""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class TestOwnershipPhraseGuard(unittest.TestCase):
    """Test the check_ownership_phrases.py guard script."""

    @classmethod
    def setUpClass(cls):
        """Locate the guard script relative to this test file."""
        cls.guard_script = (
            Path(__file__).resolve().parents[1]
            / "scripts"
            / "check_ownership_phrases.py"
        )
        assert cls.guard_script.exists(), f"Guard script not found at {cls.guard_script}"

    def test_repo_docs_have_no_prime_orchestration_claim(self):
        """Repo should pass: no Prime owns orchestration claims."""
        result = subprocess.run(
            ["python3", str(self.guard_script)],
            cwd=Path(__file__).resolve().parents[1],
            capture_output=True,
            text=True,
        )
        self.assertEqual(
            result.returncode,
            0,
            f"Guard script failed in repo root. Stderr: {result.stderr}",
        )

    def test_guard_detects_reintroduced_claim(self):
        """Guard should fail when bad phrase is reintroduced."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Create a README.md with the problematic claim
            readme = tmpdir_path / "README.md"
            readme.write_text(
                "# Test\n\n"
                "Prime owns the agent experience and work orchestration.\n"
            )
            
            result = subprocess.run(
                ["python3", str(self.guard_script)],
                cwd=tmpdir_path,
                capture_output=True,
                text=True,
            )
            self.assertEqual(
                result.returncode,
                1,
                f"Guard should have failed but returned {result.returncode}. "
                f"Stdout: {result.stdout}",
            )

    def test_guard_ignores_historical_files(self):
        """Guard should ignore historical files with the phrase."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Create docs directory
            docs_dir = tmpdir_path / "docs"
            docs_dir.mkdir()
            
            # Create a historical file with the problematic phrase
            # The guard should ignore files with AUDIT, GAP, HISTORY, or ARCHIVE in name
            audit_file = docs_dir / "CURRENT_STATE_AUDIT.md"
            audit_file.write_text(
                "# Audit Document\n\n"
                "Prime owns the agent experience and work orchestration.\n"
            )
            
            # Create a README.md without the phrase
            readme = tmpdir_path / "README.md"
            readme.write_text("# Test Repository\n\nThis is fine.\n")
            
            result = subprocess.run(
                ["python3", str(self.guard_script)],
                cwd=tmpdir_path,
                capture_output=True,
                text=True,
            )
            self.assertEqual(
                result.returncode,
                0,
                f"Guard should pass when historical files contain phrase. "
                f"Returncode: {result.returncode}. Stderr: {result.stderr}",
            )


if __name__ == "__main__":
    unittest.main()
