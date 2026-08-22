from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

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
        cls.validation_root = ROOT

    def validate(self, mutate, *, use_local_paths: bool = False) -> list[str]:
        manifest = copy.deepcopy(self.manifest)
        mutate(manifest)
        if not use_local_paths:
            for repository in manifest["repositories"]:
                repository["path"] = CHECKER.CANONICAL_PATHS[repository["id"]]
        with patch.object(Path, "is_dir", return_value=True), patch.object(
            CHECKER, "validate_source_pin", return_value=([], "a" * 40, "a" * 40)
        ):
            errors, _, _ = CHECKER.validate_manifest(self.validation_root, manifest)
        return errors

    def test_current_manifest_passes(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        for repository in manifest["repositories"]:
            repository["path"] = CHECKER.CANONICAL_PATHS[repository["id"]]
        with patch.object(Path, "is_dir", return_value=True), patch.object(
            CHECKER, "validate_source_pin", return_value=([], "a" * 40, "a" * 40)
        ):
            errors, _, rows = CHECKER.validate_manifest(self.validation_root, manifest)
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
            lambda value: value["repositories"][0].update(path="../../outside"),
            use_local_paths=True,
        )
        self.assertTrue(any("workspace root or one sibling" in error for error in errors))

    def test_external_repository_cannot_claim_current_manifest_path(self) -> None:
        errors = self.validate(
            lambda value: value["repositories"][0].update(path="."),
            use_local_paths=True,
        )
        self.assertTrue(any("must use its canonical workspace path" in error for error in errors))

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

    def test_missing_legacy_aliases_field_fails(self) -> None:
        errors = self.validate(lambda value: value["repositories"][0].pop("legacy_aliases"))
        self.assertTrue(any("missing fields" in error for error in errors))

    def test_legacy_alias_requires_exact_fields(self) -> None:
        errors = self.validate(
            lambda value: value["repositories"][0].update(legacy_aliases=[{"name": "old-name"}])
        )
        self.assertTrue(any("must contain exactly" in error for error in errors))

    def test_legacy_alias_invalid_kind_and_sunset_fail(self) -> None:
        alias = {
            "name": "llm-gate-core",
            "kind": "branding",
            "replacement": "verdict-core",
            "migration_instructions": "docs/COMPATIBILITY_MIGRATION.md#verdict-core",
            "sunset_date": "someday",
        }
        errors = self.validate(
            lambda value: value["repositories"][0].update(legacy_aliases=[alias])
        )
        self.assertTrue(any(".kind must be one of" in error for error in errors))
        self.assertTrue(any("calendar date" in error for error in errors))

    def test_legacy_alias_replacement_must_differ(self) -> None:
        alias = {
            "name": "same-name",
            "kind": "package",
            "replacement": "same-name",
            "migration_instructions": "docs/COMPATIBILITY_MIGRATION.md#verdict-core",
            "sunset_date": "2026-12-31",
        }
        errors = self.validate(
            lambda value: value["repositories"][0].update(legacy_aliases=[alias])
        )
        self.assertTrue(any("differing from the alias" in error for error in errors))

    def test_duplicate_legacy_alias_fails(self) -> None:
        alias = {
            "name": "llm-gate-core",
            "kind": "package",
            "replacement": "verdict-core",
            "migration_instructions": "docs/COMPATIBILITY_MIGRATION.md#verdict-core",
            "sunset_date": "2026-12-31",
        }
        errors = self.validate(
            lambda value: value["repositories"][0].update(legacy_aliases=[alias, dict(alias)])
        )
        self.assertTrue(any("duplicate legacy alias" in error for error in errors))

    def test_deferred_checks_and_blockers_are_fixed(self) -> None:
        errors = self.validate(
            lambda value: value["release_train"]["deferred_checks"].clear()
        )
        self.assertTrue(any("ratified REL-001 blockers" in error for error in errors))


class SourcePinResolutionTests(unittest.TestCase):
    def create_repository(self, directory: Path) -> tuple[str, str]:
        directory.mkdir()
        self.run_git(directory, "init", "--quiet")
        self.run_git(directory, "config", "user.email", "compatibility@example.test")
        self.run_git(directory, "config", "user.name", "Compatibility Test")
        (directory / "state.txt").write_text("pinned\n", encoding="utf-8")
        self.run_git(directory, "add", "state.txt")
        self.run_git(directory, "commit", "--quiet", "-m", "pinned state")
        pinned_revision = self.run_git(directory, "rev-parse", "HEAD")
        (directory / "state.txt").write_text("different\n", encoding="utf-8")
        self.run_git(directory, "commit", "--quiet", "-am", "different state")
        current_revision = self.run_git(directory, "rev-parse", "HEAD")
        return pinned_revision, current_revision

    def run_git(self, directory: Path, *arguments: str) -> str:
        completed = subprocess.run(
            ["git", "-C", str(directory), *arguments],
            check=True,
            capture_output=True,
            text=True,
        )
        return completed.stdout.strip()

    def test_exact_source_pin_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repository = Path(temporary_directory) / "repository"
            pinned_revision, _ = self.create_repository(repository)
            self.run_git(repository, "checkout", "--quiet", "--detach", pinned_revision)

            errors, resolved_revision, checked_out_revision = CHECKER.validate_source_pin(
                "verdict-core", repository, pinned_revision
            )

        self.assertEqual(errors, [])
        self.assertEqual(resolved_revision, pinned_revision)
        self.assertEqual(checked_out_revision, pinned_revision)

    def test_incompatible_checked_out_revision_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repository = Path(temporary_directory) / "repository"
            pinned_revision, current_revision = self.create_repository(repository)

            errors, resolved_revision, checked_out_revision = CHECKER.validate_source_pin(
                "verdict-core", repository, pinned_revision
            )

        self.assertTrue(any("checked-out revision differs" in error for error in errors))
        self.assertEqual(resolved_revision, pinned_revision)
        self.assertEqual(checked_out_revision, current_revision)

    def test_missing_source_pin_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repository = Path(temporary_directory) / "repository"
            self.create_repository(repository)

            errors, resolved_revision, checked_out_revision = CHECKER.validate_source_pin(
                "verdict-core", repository, "a" * 40
            )

        self.assertTrue(any("release-train pin is unavailable" in error for error in errors))
        self.assertIsNone(resolved_revision)
        self.assertIsNotNone(checked_out_revision)

    def test_non_git_directory_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory) / "not-a-repository"
            directory.mkdir()

            errors, resolved_revision, checked_out_revision = CHECKER.validate_source_pin(
                "verdict-core", directory, "a" * 40
            )

        self.assertTrue(any("not a readable Git checkout" in error for error in errors))
        self.assertIsNone(resolved_revision)
        self.assertIsNone(checked_out_revision)


class CheckoutManifestSourcesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        spec = importlib.util.spec_from_file_location(
            "checkout_manifest_sources",
            ROOT / "scripts" / "checkout_manifest_sources.py",
        )
        assert spec and spec.loader
        cls.checkout = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = cls.checkout
        spec.loader.exec_module(cls.checkout)

    def test_pin_checkout_fetches_exact_revision_then_detaches(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            manifest = {
                "repositories": [
                    {
                        "id": "verdict-core",
                        "path": "../verdict-core",
                        "release_train_pin": "a" * 40,
                    }
                ]
            }
            (directory / "compatibility-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            (directory.parent / "verdict-core").mkdir(exist_ok=True)

            calls: list[tuple[Path, tuple[str, ...]]] = []
            with patch.object(
                self.checkout, "run_git", side_effect=lambda path, *arguments: calls.append((path, arguments))
            ):
                exit_code = self.checkout.main(directory)

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            calls,
            [
                (directory.parent / "verdict-core", ("fetch", "--depth=1", "origin", "a" * 40)),
                (directory.parent / "verdict-core", ("checkout", "--detach", "--quiet", "a" * 40)),
            ],
        )

    def test_current_manifest_repository_is_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory) / "verdict-ecosystem"
            root.mkdir()
            manifest = {
                "repositories": [
                    {
                        "id": "verdict-ecosystem",
                        "path": ".",
                        "release_train_pin": "a" * 40,
                    }
                ]
            }
            (root / "compatibility-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            with patch.object(self.checkout, "run_git") as run_git:
                exit_code = self.checkout.main(root)

        self.assertEqual(exit_code, 0)
        run_git.assert_not_called()

    def test_external_repository_cannot_claim_current_manifest_path(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory) / "verdict-ecosystem"
            root.mkdir()
            manifest = {
                "repositories": [
                    {
                        "id": "verdict-core",
                        "path": ".",
                        "release_train_pin": "a" * 40,
                    }
                ]
            }
            (root / "compatibility-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            with patch.object(self.checkout, "run_git") as run_git:
                exit_code = self.checkout.main(root)

        self.assertEqual(exit_code, 1)
        run_git.assert_not_called()

    def test_manifest_path_cannot_escape_the_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            workspace = Path(temporary_directory) / "workspace"
            root = workspace / "verdict-ecosystem"
            root.mkdir(parents=True)
            outside = Path(temporary_directory) / "outside"
            outside.mkdir()
            manifest = {
                "repositories": [
                    {
                        "id": "verdict-core",
                        "path": "../../outside",
                        "release_train_pin": "a" * 40,
                    }
                ]
            }
            (root / "compatibility-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            with patch.object(self.checkout, "run_git") as run_git:
                exit_code = self.checkout.main(root)

        self.assertEqual(exit_code, 1)
        run_git.assert_not_called()

    def test_symlinked_sibling_cannot_escape_the_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            workspace = Path(temporary_directory) / "workspace"
            root = workspace / "verdict-ecosystem"
            root.mkdir(parents=True)
            outside = Path(temporary_directory) / "outside"
            outside.mkdir()
            (workspace / "verdict-core").symlink_to(outside, target_is_directory=True)
            manifest = {
                "repositories": [
                    {
                        "id": "verdict-core",
                        "path": "../verdict-core",
                        "release_train_pin": "a" * 40,
                    }
                ]
            }
            (root / "compatibility-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            with patch.object(self.checkout, "run_git") as run_git:
                exit_code = self.checkout.main(root)

        self.assertEqual(exit_code, 1)
        run_git.assert_not_called()


if __name__ == "__main__":
    unittest.main()
