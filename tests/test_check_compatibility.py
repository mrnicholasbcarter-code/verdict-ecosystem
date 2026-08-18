from __future__ import annotations

import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "check_compatibility",
    ROOT / "scripts" / "check_compatibility.py",
)
assert SPEC and SPEC.loader
CHECKER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CHECKER
SPEC.loader.exec_module(CHECKER)


class CompatibilityManifestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = json.loads(
            (ROOT / "compatibility-manifest.json").read_text(encoding="utf-8")
        )

    def validate(self, mutate) -> list[str]:
        manifest = copy.deepcopy(self.manifest)
        mutate(manifest)
        errors, _, _ = CHECKER.validate_manifest(ROOT, manifest)
        return errors

    def test_current_manifest_passes(self) -> None:
        errors, _, rows = CHECKER.validate_manifest(ROOT, self.manifest)
        self.assertEqual(errors, [])
        self.assertEqual(len(rows), 7)

    def test_missing_enriched_field_fails(self) -> None:
        errors = self.validate(lambda value: value["repositories"][0].pop("repository_url"))
        self.assertTrue(any("missing fields" in error for error in errors))

    def test_invalid_repository_url_fails(self) -> None:
        errors = self.validate(
            lambda value: value["repositories"][0].update(
                repository_url="http://user:password@example.com/repository"
            )
        )
        self.assertTrue(any("repository_url must be an HTTPS URL" in error for error in errors))

    def test_parent_escape_path_fails(self) -> None:
        errors = self.validate(
            lambda value: value["repositories"][0].update(path="../../outside")
        )
        self.assertTrue(any("workspace root or one sibling" in error for error in errors))

    def test_secret_bearing_url_metadata_fails(self) -> None:
        errors = self.validate(
            lambda value: value["repositories"][0].update(
                repository_url="https://github.com/example/repository?token=not-a-secret-value"
            )
        )
        self.assertTrue(any("secret-bearing metadata" in error for error in errors))

    def test_invalid_timestamp_fails(self) -> None:
        errors = self.validate(
            lambda value: value["repositories"][0].update(evidence_timestamp="not-a-date")
        )
        self.assertTrue(any("RFC 3339 UTC timestamp" in error for error in errors))

    def test_invalid_release_train_pin_fails(self) -> None:
        errors = self.validate(
            lambda value: value["repositories"][0].update(release_train_pin="main")
        )
        self.assertTrue(any("full lowercase Git commit SHA" in error for error in errors))

    def test_invalid_maturity_and_support_fail(self) -> None:
        def mutate(value) -> None:
            value["repositories"][0]["maturity"] = "production-ready"
            value["repositories"][0]["support_level"] = "guaranteed"

        errors = self.validate(mutate)
        self.assertTrue(any(".maturity must be one of" in error for error in errors))
        self.assertTrue(any(".support_level must be one of" in error for error in errors))

    def test_invalid_runtime_and_provider_metadata_fail(self) -> None:
        def mutate(value) -> None:
            value["repositories"][0]["runtime_constraints"] = {"python": "any"}
            value["repositories"][0]["provider_compatibility"] = ["OpenAI API"]

        errors = self.validate(mutate)
        self.assertTrue(any("minimum-version constraint" in error for error in errors))
        self.assertTrue(any("safe capability identifiers" in error for error in errors))

    def test_published_artifact_requires_registry_url(self) -> None:
        errors = self.validate(
            lambda value: value["repositories"][1].update(registry_url=None)
        )
        self.assertTrue(any("registry_url is required" in error for error in errors))

    def test_deferred_checks_and_blockers_are_fixed(self) -> None:
        errors = self.validate(
            lambda value: value["release_train"]["deferred_checks"].clear()
        )
        self.assertTrue(any("ratified REL-001 blockers" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
