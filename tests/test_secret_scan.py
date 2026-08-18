"""The secret/PII scan must actually block unsafe output, not just report.

Covers the ECO-003 acceptance criterion "secret/PII scan runs before
publishing artifacts and blocks unsafe output". Blocking is what is under
test here: a non-zero exit is the gate, so every unsafe fixture asserts on
the exit code, not merely on the presence of a finding.

Every unsafe fixture is synthesized at run time into a throwaway git
repository under the OS temp directory. Nothing containing a
secret-shaped string is ever committed to this repository — which would
otherwise make this repo's own `drift-check` gate fail on its own test
suite. For the same reason the sample values below are assembled by
concatenation rather than written as literals: a literal would be matched
by the scanner while it walks `tests/`.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCANNER_PATH = ROOT / "scripts" / "secret_scan.py"
SPEC = importlib.util.spec_from_file_location("secret_scan", SCANNER_PATH)
assert SPEC and SPEC.loader
SCANNER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = SCANNER
SPEC.loader.exec_module(SCANNER)

# Assembled at import time so no secret-shaped literal exists on any single
# line of this file. Values are syntactically valid but deliberately fake.
UNSAFE_SAMPLES = {
    "aws-access-key-id": "static_id = '" + "AKIA" + "IOSFODNN7EXAMPLE" + "'",
    "generic-secret-assignment": "api" + "_key" + " = " + '"' + "not-a-real-value-01" + '"',
    "pem-private-key-header": "-----BEGIN " + "PRIVATE KEY" + "-----",
    "bearer-token": "Authorization: " + "Bearer " + "abcdefghijklmnopqrstuvwxyz012345",
    "slack-token": "xox" + "b-" + "0123456789-placeholder",
    "github-token": "gh" + "p_" + "0123456789abcdefghijklmnopqrstuvwxyz",
}

SAFE_SAMPLE = "def add(left, right):\n    return left + right\n"


def make_repo(tmp: str, files: dict[str, str]) -> Path:
    repo = Path(tmp) / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True, timeout=30)
    for name, content in files.items():
        (repo / name).write_text(content, encoding="utf-8")
    return repo


def run_scanner(*paths: str) -> tuple[int, dict]:
    result = subprocess.run(
        [sys.executable, str(SCANNER_PATH), *paths],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=120,
    )
    return result.returncode, json.loads(result.stdout)


class BlocksUnsafeOutputTests(unittest.TestCase):
    def test_each_rule_blocks_with_nonzero_exit(self) -> None:
        for rule, sample in UNSAFE_SAMPLES.items():
            with self.subTest(rule=rule), tempfile.TemporaryDirectory() as tmp:
                repo = make_repo(tmp, {"artifact.txt": sample + "\n"})
                code, report = run_scanner(str(repo))
                self.assertEqual(code, 1, f"{rule} did not block: {report}")
                self.assertEqual(
                    [finding["rule"] for finding in report["findings"]], [rule]
                )
                self.assertEqual(report["findings"][0]["path"], "artifact.txt")

    def test_clean_repository_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = make_repo(tmp, {"module.py": SAFE_SAMPLE})
            code, report = run_scanner(str(repo))
            self.assertEqual(code, 0, report)
            self.assertEqual(report["findings"], [])

    def test_finding_never_discloses_matched_content(self) -> None:
        sample = UNSAFE_SAMPLES["aws-access-key-id"]
        with tempfile.TemporaryDirectory() as tmp:
            repo = make_repo(tmp, {"artifact.txt": sample + "\n"})
            code, report = run_scanner(str(repo))
            self.assertEqual(code, 1)
            serialized = json.dumps(report)
            self.assertNotIn(sample, serialized)
            self.assertNotIn("AKIA" + "IOSFODNN7EXAMPLE", serialized)
            self.assertEqual(sorted(report["findings"][0]), ["path", "repo", "rule"])

    def test_untracked_but_unignored_artifact_still_blocks(self) -> None:
        """Publishing operates on the working tree, not just the index."""
        with tempfile.TemporaryDirectory() as tmp:
            repo = make_repo(tmp, {"generated.txt": UNSAFE_SAMPLES["github-token"] + "\n"})
            code, report = run_scanner(str(repo))
            self.assertEqual(code, 1, report)
            self.assertEqual(report["findings"][0]["path"], "generated.txt")

    def test_ignored_runtime_state_is_not_scanned(self) -> None:
        """Class-3 runtime state is out of scope and must not create noise."""
        with tempfile.TemporaryDirectory() as tmp:
            repo = make_repo(
                tmp,
                {
                    ".gitignore": "runtime/\n",
                    "module.py": SAFE_SAMPLE,
                },
            )
            (repo / "runtime").mkdir()
            (repo / "runtime" / "state.txt").write_text(
                UNSAFE_SAMPLES["slack-token"] + "\n", encoding="utf-8"
            )
            code, report = run_scanner(str(repo))
            self.assertEqual(code, 0, report)


class ContainmentTests(unittest.TestCase):
    def test_non_repository_directory_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            code, report = run_scanner(tmp)
            self.assertEqual(code, 2)
            self.assertEqual(report["rejected_paths"], [tmp])

    def test_credential_directories_are_forbidden(self) -> None:
        for name in (".omniroute", ".claude"):
            with self.subTest(directory=name):
                self.assertTrue(SCANNER.is_forbidden((Path.home() / name).resolve()))
                self.assertTrue(
                    SCANNER.is_forbidden((Path.home() / name / "nested" / "file").resolve())
                )

    def test_forbidden_directory_is_rejected_even_if_it_is_a_repository(self) -> None:
        self.assertIsNone(SCANNER.resolve_allowed_repo(str(Path.home() / ".claude")))

    def test_rejection_is_blocking(self) -> None:
        """An unscannable target must never be reported as a clean pass."""
        with tempfile.TemporaryDirectory() as tmp:
            repo = make_repo(tmp, {"module.py": SAFE_SAMPLE})
            unscannable = Path(tmp) / "plain"
            unscannable.mkdir()
            code, report = run_scanner(str(repo), str(unscannable))
            self.assertEqual(code, 2)
            self.assertEqual(report["findings"], [])


class ThisRepositoryTests(unittest.TestCase):
    def test_repository_itself_is_clean(self) -> None:
        code, report = run_scanner(str(ROOT))
        self.assertEqual(code, 0, report)


if __name__ == "__main__":
    unittest.main()
