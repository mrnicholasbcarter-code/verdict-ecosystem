from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "docs" / "SPEC_KIT_LITE.md"
REQUIRED_HEADINGS = (
    "## Problem / desired outcome",
    "## Evidence boundary",
    "## Scope",
    "## Non-goals",
    "## Acceptance criteria",
    "## Affected interfaces / contracts",
    "## Implementation constraints",
    "## Security / trust implications",
    "## Routing / context / memory implications",
    "## Test / proof requirements",
    "## ADR impact",
    "## Documentation impact",
    "## Migration / rollback",
    "## Evidence required for completion",
)

spec = importlib.util.spec_from_file_location("check_local_links", ROOT / "scripts" / "check_local_links.py")
assert spec and spec.loader
LINKS = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = LINKS
spec.loader.exec_module(LINKS)


class SpecKitLiteTests(unittest.TestCase):
    def test_canonical_contract_has_every_required_heading(self) -> None:
        text = SPEC_PATH.read_text(encoding="utf-8")
        for heading in REQUIRED_HEADINGS:
            with self.subTest(heading=heading):
                self.assertIn(heading, text)

    def test_template_has_evidence_labels_and_lifecycle_proof(self) -> None:
        text = SPEC_PATH.read_text(encoding="utf-8")
        for required in ("KNOWN:", "INFERRED:", "NOT AVAILABLE:", "MAIN_VERIFIED", "BOD-16"):
            with self.subTest(required=required):
                self.assertIn(required, text)

    def test_current_local_markdown_links_resolve(self) -> None:
        self.assertEqual(LINKS.local_link_failures(ROOT), [])

    def test_missing_and_escaping_links_fail(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs").mkdir()
            (root / ".specify").mkdir()
            (root / "docs" / "target.md").write_text("# Existing heading\n", encoding="utf-8")
            (root / "README.md").write_text(
                "# Present\n"
                "[valid same](#present)\n"
                "[missing](docs/nope.md)\n"
                "[out](../outside.md)\n"
                "[cross anchor](docs/target.md#absent)\n"
                "[same anchor](#absent)\n"
                "[reference][broken]\n"
                "[broken]: docs/nope-reference.md\n"
                "```markdown\n[example only](docs/not-a-real-file.md)\n```\n",
                encoding="utf-8",
            )
            failures = LINKS.local_link_failures(root)
            self.assertTrue(any("missing local target" in item for item in failures))
            self.assertTrue(any("nope-reference.md" in item for item in failures))
            self.assertTrue(any("escapes repository" in item for item in failures))
            self.assertEqual(sum("missing local anchor" in item for item in failures), 2)
            self.assertFalse(any("not-a-real-file.md" in item for item in failures))


if __name__ == "__main__":
    unittest.main()
