from __future__ import annotations

import json
import tempfile
import unittest
from unittest import mock
from collections import Counter
from pathlib import Path

import scripts.check_adr_lifecycle as checker
import scripts.verify_adr_sources as source_verifier
from scripts.check_adr_lifecycle import EXPECTED_SNAPSHOTS, validate

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "ADR_LIFECYCLE.json"


def load() -> dict:
    return json.loads(EVIDENCE.read_text(encoding="utf-8"))


class ADRLifecycleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.data = load()
        self.records = self.data["lifecycle_index"]

    def test_authoritative_validator_accepts_checked_in_index(self) -> None:
        self.assertEqual(validate(self.data), [])

    def test_exact_snapshots_and_71_production_records(self) -> None:
        self.assertEqual(self.data["source_snapshots"], EXPECTED_SNAPSHOTS)
        self.assertEqual(len(self.records), 71)
        self.assertEqual(self.data["corrected_counts"]["production_files"], 71)

    def test_fixture_exclusion_is_explicit(self) -> None:
        self.assertEqual(len(self.data["excluded_files"]), 1)
        excluded = self.data["excluded_files"][0]
        self.assertEqual(excluded["repository"], "verdict-core")
        self.assertEqual(excluded["path"], "benchmarks/fixtures/legit_workspace/docs/adr/ADR-001-spend.md")
        self.assertTrue(all("fixtures/" not in record["path"] for record in self.records))

    def test_counts_are_internally_consistent(self) -> None:
        self.assertEqual(
            Counter(record["classification"] for record in self.records),
            Counter(self.data["corrected_counts"]["classifications"]),
        )
        self.assertEqual(
            Counter(record["evidence_level"] for record in self.records),
            Counter(self.data["corrected_counts"]["evidence_levels"]),
        )

    def test_no_current_without_runtime_proof(self) -> None:
        self.assertFalse(any(record["classification"] == "CURRENT" for record in self.records))

    def test_exact_duplicate_groups_bind_content_hashes(self) -> None:
        self.assertEqual(len(self.data["duplicate_groups"]), 23)
        self.assertEqual(sum(len(group["files"]) for group in self.data["duplicate_groups"]), 46)
        records = {f"{r['repository']}/{r['path']}": r for r in self.records}
        for group in self.data["duplicate_groups"]:
            for name in group["files"]:
                self.assertEqual(records[name]["content_sha256"], group["sha256"])

    def test_core_memory_verified_duplicates_name_core_owner(self) -> None:
        duplicates = [
            r for r in self.records
            if r["repository"] == "verdict-core-memory"
            and r["classification"] == "DUPLICATE"
            and r["evidence_level"] == "VERIFIED"
        ]
        self.assertTrue(duplicates)
        self.assertTrue(all((r["successor"] or "").startswith("verdict-core/docs/") for r in duplicates))

    def test_legacy_architecture_copies_are_noncanonical(self) -> None:
        legacy = [r for r in self.records if r["path"].startswith("docs/architecture/")]
        self.assertTrue(legacy)
        self.assertTrue(all(r["classification"] == "DUPLICATE" for r in legacy))

    def test_continuity_is_v3_deferred(self) -> None:
        continuity = [r for r in self.records if r["repository"] == "verdict-continuity"]
        self.assertTrue(continuity)
        self.assertTrue(all(r["v2_relevance"] == "V3_DEFERRED" for r in continuity))

    def test_adr023_has_no_invented_successor(self) -> None:
        adr023 = next(r for r in self.records if r["repository"] == "verdict-core" and "ADR-023" in r["path"])
        self.assertEqual(adr023["classification"], "MISSING_SUCCESSOR")
        self.assertIsNone(adr023["successor"])

    def test_every_record_has_hash_and_exact_sha_link(self) -> None:
        for record in self.records:
            self.assertEqual(len(record["content_sha256"]), 64)
            self.assertIn(self.data["source_snapshots"][record["repository"]], record["source_url"])

    def test_reviewed_distributions_are_pinned(self) -> None:
        tampered = json.loads(json.dumps(self.data))
        record = next(r for r in tampered["lifecycle_index"] if r["classification"] == "PARTIALLY_TRUE")
        record["classification"] = "STALE"
        tampered["corrected_counts"]["classifications"]["PARTIALLY_TRUE"] -= 1
        tampered["corrected_counts"]["classifications"]["STALE"] += 1
        errors = validate(tampered)
        self.assertIn(
            "classification distribution differs from the reviewed audit baseline",
            errors,
        )
        self.assertIn("reviewed audit digest does not match semantic audit content", errors)

    def test_superseded_orchestrator_record_names_verified_successor(self) -> None:
        record = next(
            r for r in self.records
            if r["repository"] == "verdict-core"
            and r["path"] == "docs/adr/ADR-ORCHESTRATOR-ROUTING.md"
        )
        self.assertEqual(record["classification"], "SUPERSEDED")
        self.assertEqual(record["successor"], "verdict-core/verdict/dispatcher.py")
        self.assertIn("BOD-104", record["rationale"])
        self.assertNotIn("ADR-023", record["rationale"])

    def test_reviewed_summary_and_authority_fields_are_pinned(self) -> None:
        cases = []
        tampered = json.loads(json.dumps(self.data))
        tampered["corrected_counts"]["exact_duplicate_hash_groups"] = 999
        cases.append((tampered, "duplicate-group summary differs from reviewed baseline"))
        tampered = json.loads(json.dumps(self.data))
        tampered["source_repository_urls"]["verdict-core"] = "https://example.invalid/core"
        cases.append((tampered, "source repository URLs differ from the audited repositories"))
        tampered = json.loads(json.dumps(self.data))
        tampered["excluded_files"][0]["content_sha256"] = "0" * 64
        cases.append((tampered, "excluded fixture content SHA-256 differs from pinned source"))
        tampered = json.loads(json.dumps(self.data))
        tampered["lifecycle_index"][0]["citations"] = ["invented/path"]
        cases.append((tampered, "invalid citation locator"))
        tampered = json.loads(json.dumps(self.data))
        tampered["lifecycle_index"][0]["content_sha256"] = "0" * 64
        cases.append((tampered, "reviewed audit digest does not match semantic audit content"))
        tampered = json.loads(json.dumps(self.data))
        tampered["duplicate_groups"][0]["sha256"] = "0" * 64
        cases.append((tampered, "reviewed audit digest does not match semantic audit content"))
        tampered = json.loads(json.dumps(self.data))
        tampered["lifecycle_index"].pop()
        cases.append((tampered, "lifecycle_index expected 71 records"))
        tampered = json.loads(json.dumps(self.data))
        extra = json.loads(json.dumps(tampered["lifecycle_index"][0]))
        extra["path"] = "docs/adr/ADR-999-invented.md"
        tampered["lifecycle_index"].append(extra)
        cases.append((tampered, "lifecycle_index expected 71 records"))
        for data, expected in cases:
            with self.subTest(expected=expected):
                self.assertTrue(any(expected in error for error in validate(data)))


    def test_coordinated_semantic_mutation_and_metadata_refresh_fails(self) -> None:
        tampered = json.loads(json.dumps(self.data))
        tampered["lifecycle_index"][0]["rationale"] = "attacker-controlled replacement"
        tampered["metadata"]["reviewed_audit_sha256"] = checker.reviewed_audit_digest(tampered)
        errors = validate(tampered)
        self.assertIn(
            "semantic audit content differs from the independently reviewed digest",
            errors,
        )
        self.assertIn(
            "reviewed audit metadata digest differs from the trusted validator constant",
            errors,
        )

    def test_coordinated_required_citation_omission_fails(self) -> None:
        tampered = json.loads(json.dumps(self.data))
        record = next(r for r in tampered["lifecycle_index"] if len(r["citations"]) > 1)
        record["citations"] = record["citations"][:1]
        tampered["metadata"]["reviewed_audit_sha256"] = checker.reviewed_audit_digest(tampered)
        self.assertIn(
            "semantic audit content differs from the independently reviewed digest",
            validate(tampered),
        )

    def test_rendered_row_order_and_multiplicity_are_exact(self) -> None:
        original_doc = checker.DOC
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "ADR_LIFECYCLE.md"
            text = original_doc.read_text(encoding="utf-8")
            first_row = next(line for line in text.splitlines() if line.startswith("| `"))
            bad.write_text(text + first_row + "\n", encoding="utf-8")
            checker.DOC = bad
            try:
                self.assertIn(
                    "rendered lifecycle rows differ in content, order, or multiplicity from machine-readable records",
                    validate(self.data),
                )
            finally:
                checker.DOC = original_doc

    def test_declared_status_extraction_is_not_corrupt(self) -> None:
        expected = {
            "docs/adr/ADR-003-platform-neutral-guidance-boundary.md": "proposed for issue #107",
            "docs/adr/ADR-024-cross-repo-compatibility-gate.md": "Partially Implemented — `verdict-core` side complete (manifest + fail-closed gate CLI); downstream repo declarations and CI wiring still open",
            "docs/adr/ADR-030-proof-carrying-decision-plane.md": "Accepted — implementation tracked in GitHub Project #6",
            "docs/adr/ADR-032-core-model-metadata-store.md": "Accepted — implemented with BOD-108",
            "docs/adr/README.md": None,
        }
        records = {r["path"]: r for r in self.records if r["repository"] == "verdict-core"}
        for path, status in expected.items():
            self.assertEqual(records[path]["declared_status"], status)
        multiline = [
            r for r in self.records
            if r["path"] == "docs/adr/ADR-007-omniroute-catalog-qualification.md"
        ]
        self.assertEqual(len(multiline), 2)
        self.assertTrue(all(
            r["declared_status"] == "Accepted — implemented and merged in PR #155; refresh in #162 is diagnostic and remains partial under the recorded baseline policy"
            for r in multiline
        ))
        nulls = {(r["repository"], r["path"]) for r in self.records if r["declared_status"] is None}
        self.assertEqual(
            nulls,
            {
                ("verdict-core", "docs/adr/README.md"),
                ("verdict-core-memory", "docs/adr/ADR-008-infinite-context-and-observability.md"),
                ("verdict-core-memory", "docs/adr/ADR-009-governed-learning-and-retirement.md"),
            },
        )


class ADRSourceVerifierNegativeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.data = load()
        self.repos = {name: Path("/") / name for name in self.data["source_snapshots"]}
        self.trees = {name: set() for name in self.repos}
        for item in self.data["lifecycle_index"] + self.data["excluded_files"]:
            self.trees[item["repository"]].add(item["path"])
        for record in self.data["lifecycle_index"]:
            for citation in record["citations"]:
                repo, path = citation.split("/", 1)
                self.trees[repo].add(path)

    def run_verify(self, data=None, trees=None, content=b"forged"):
        trees = trees or self.trees
        with mock.patch.object(source_verifier, "git_paths", side_effect=lambda repo, sha: trees[repo.name]), \
             mock.patch.object(source_verifier, "git_bytes", return_value=content):
            return source_verifier.verify(data or self.data, self.repos)

    def test_forged_record_and_fixture_hashes_fail(self) -> None:
        errors = self.run_verify()
        self.assertTrue(any("content hash mismatch" in e for e in errors))
        self.assertTrue(any("excluded fixture hash mismatch" in e for e in errors))

    def test_missing_citation_fails(self) -> None:
        tampered = json.loads(json.dumps(self.data))
        tampered["lifecycle_index"][0]["citations"] = ["verdict-core/docs/adr/DOES-NOT-EXIST.md"]
        errors = self.run_verify(tampered)
        self.assertTrue(any("citation absent from pinned tree" in e for e in errors))

    def test_omitted_reviewed_citation_with_refreshed_metadata_fails(self) -> None:
        tampered = json.loads(json.dumps(self.data))
        record = next(r for r in tampered["lifecycle_index"] if len(r["citations"]) > 1)
        record["citations"] = record["citations"][:1]
        tampered["metadata"]["reviewed_audit_sha256"] = checker.reviewed_audit_digest(tampered)
        errors = self.run_verify(tampered)
        self.assertIn(
            "semantic audit content differs from the independently reviewed digest",
            errors,
        )

    def test_missing_and_extra_source_adrs_fail(self) -> None:
        trees = {name: set(paths) for name, paths in self.trees.items()}
        missing = self.data["lifecycle_index"][0]
        trees[missing["repository"]].remove(missing["path"])
        trees["verdict-core"].add("docs/adr/ADR-999-unindexed.md")
        errors = self.run_verify(trees=trees)
        self.assertTrue(any("indexed ADR absent from pinned tree" in e for e in errors))
        self.assertTrue(any("unindexed ADR source" in e for e in errors))

    def test_forged_duplicate_groups_fail_source_derivation(self) -> None:
        tampered = json.loads(json.dumps(self.data))
        tampered["duplicate_groups"][0]["sha256"] = "0" * 64
        errors = self.run_verify(tampered)
        self.assertIn("duplicate groups differ from pinned source bytes", errors)


if __name__ == "__main__":
    unittest.main()
