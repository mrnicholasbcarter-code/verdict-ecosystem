"""Class-2 evidence fixtures must be reproducible and test-run-immutable.

Covers the ECO-003 acceptance criterion "stable evidence fixtures remain
reproducible and are not overwritten by tests/demos". The two halves are
tested separately: reproducibility (regenerating from committed source
yields byte-identical output, and the recorded digests match) and
immutability (nothing short of an explicit `--write` mutates `evidence/`,
including this very test module).
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "build_evidence", ROOT / "scripts" / "build_evidence.py"
)
assert SPEC and SPEC.loader
EVIDENCE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = EVIDENCE
SPEC.loader.exec_module(EVIDENCE)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot() -> dict[str, str]:
    return {p.name: digest(p) for p in sorted(EVIDENCE.EVIDENCE_DIR.iterdir()) if p.is_file()}


class EvidenceReproducibilityTests(unittest.TestCase):
    def test_committed_fixtures_match_regeneration(self) -> None:
        code, problems = EVIDENCE.check()
        self.assertEqual(problems, [])
        self.assertEqual(code, 0)

    def test_regeneration_is_deterministic(self) -> None:
        first = EVIDENCE.render()
        second = EVIDENCE.render()
        self.assertEqual(
            {str(k): v for k, v in first.items()},
            {str(k): v for k, v in second.items()},
        )

    def test_recorded_digests_match_artifacts(self) -> None:
        manifest = json.loads(EVIDENCE.MANIFEST.read_text(encoding="utf-8"))
        for artifact in manifest["artifacts"]:
            with self.subTest(artifact=artifact["path"]):
                self.assertEqual(digest(ROOT / artifact["path"]), artifact["sha256"])
        source = manifest["source"]
        self.assertEqual(digest(ROOT / source["path"]), source["sha256"])

    def test_baseline_excludes_machine_local_fields(self) -> None:
        """A fixture carrying local paths would not be reproducible elsewhere."""
        baseline = json.loads(EVIDENCE.BASELINE.read_text(encoding="utf-8"))
        for repo in baseline["repositories"]:
            with self.subTest(repo=repo["id"]):
                self.assertNotIn("path", repo)

    def test_baseline_covers_every_manifest_repository(self) -> None:
        manifest = json.loads(EVIDENCE.SOURCE.read_text(encoding="utf-8"))
        baseline = json.loads(EVIDENCE.BASELINE.read_text(encoding="utf-8"))
        self.assertEqual(
            sorted(repo["id"] for repo in manifest["repositories"]),
            sorted(repo["id"] for repo in baseline["repositories"]),
        )

    def test_stale_fixture_is_reported_with_exact_path(self) -> None:
        """A drifted fixture must fail loudly and name the file."""
        original = EVIDENCE.BASELINE.read_text(encoding="utf-8")
        try:
            EVIDENCE.BASELINE.write_text(original + "\n", encoding="utf-8")
            code, problems = EVIDENCE.check()
            self.assertEqual(code, 1)
            self.assertTrue(
                any("evidence/compatibility-baseline.json" in problem for problem in problems),
                problems,
            )
        finally:
            EVIDENCE.BASELINE.write_text(original, encoding="utf-8")


class EvidenceImmutabilityTests(unittest.TestCase):
    def test_default_invocation_does_not_write(self) -> None:
        before = snapshot()
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "build_evidence.py")],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=60,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(snapshot(), before)

    def test_check_helper_does_not_write(self) -> None:
        before = snapshot()
        EVIDENCE.check()
        self.assertEqual(snapshot(), before)

    def test_this_test_run_leaves_evidence_untouched(self) -> None:
        """Guards the criterion directly: tests/demos must not overwrite class-2 output."""
        before = snapshot()
        with open(os.devnull, "w", encoding="utf-8") as sink:
            unittest.TextTestRunner(stream=sink, verbosity=0).run(
                unittest.TestLoader().loadTestsFromTestCase(EvidenceReproducibilityTests)
            )
        self.assertEqual(snapshot(), before)


if __name__ == "__main__":
    unittest.main()
