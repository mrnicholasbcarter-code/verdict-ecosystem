"""Offline tests for the generated matrix, link collection, and consumer planning.

These tests never touch the network: they exercise the pure planning and
rendering functions plus the committed generated document.
"""

from __future__ import annotations

import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MATRIX = load("generate_compatibility_matrix")
LINKS = load("verify_links")
SMOKE = load("consumer_smoke")
MANIFEST = json.loads((ROOT / "compatibility-manifest.json").read_text(encoding="utf-8"))


class MatrixGenerationTests(unittest.TestCase):
    def test_committed_matrix_matches_manifest(self) -> None:
        expected = MATRIX.render(MANIFEST)
        actual = (ROOT / "docs" / "COMPATIBILITY_MATRIX.md").read_text(encoding="utf-8")
        self.assertEqual(actual, expected)

    def test_rendering_is_deterministic(self) -> None:
        self.assertEqual(MATRIX.render(MANIFEST), MATRIX.render(copy.deepcopy(MANIFEST)))

    def test_unreleased_components_are_visibly_marked(self) -> None:
        rendered = MATRIX.render(MANIFEST)
        self.assertIn("**not published**", rendered)
        self.assertIn("**unreleased**", rendered)
        self.assertIn("GENERATED FILE", rendered)

    def test_legacy_aliases_render_with_sunset_dates(self) -> None:
        rendered = MATRIX.render(MANIFEST)
        self.assertIn("llm-gate-risk-benchmark", rendered)
        self.assertIn("Sunset date", rendered)


class LinkCollectionTests(unittest.TestCase):
    def test_manifest_urls_cover_repositories_registries_and_blockers(self) -> None:
        urls = LINKS.collect_manifest_urls(MANIFEST)
        self.assertIn("https://github.com/mrnicholasbcarter-code/verdict-core", urls)
        self.assertIn("https://pypi.org/project/verdict-core/0.2.0/", urls)
        self.assertIn("https://www.npmjs.com/package/@bodanglin/verdict-node", urls)
        self.assertTrue(any("/issues/" in url for url in urls))

    def test_markdown_urls_are_collected_and_trimmed(self) -> None:
        urls = LINKS.collect_markdown_urls(ROOT)
        self.assertTrue(urls)
        self.assertTrue(all(url.startswith("https://") for url in urls))
        self.assertFalse(any(url.endswith((".", ",", ")")) for url in urls))

    def test_npm_page_probes_registry_api(self) -> None:
        probed = LINKS.probe_url("https://www.npmjs.com/package/@bodanglin/verdict-node")
        self.assertEqual(probed, "https://registry.npmjs.org/@bodanglin%2Fverdict-node")
        untouched = LINKS.probe_url("https://github.com/mrnicholasbcarter-code/verdict-core")
        self.assertEqual(untouched, "https://github.com/mrnicholasbcarter-code/verdict-core")

    def test_registry_probe_pins_published_version(self) -> None:
        probes = LINKS.registry_probes(MANIFEST)
        self.assertEqual([probe["id"] for probe in probes], ["verdict-core", "verdict-node"])
        self.assertEqual(probes[0]["version"], "0.2.0")
        self.assertEqual(probes[1]["version"], "0.1.0")


class ConsumerPlanTests(unittest.TestCase):
    def test_plan_covers_all_repositories(self) -> None:
        actions = SMOKE.plan_actions(MANIFEST)
        self.assertEqual(len(actions), 7)

    def test_only_published_artifacts_are_installed(self) -> None:
        actions = SMOKE.plan_actions(MANIFEST)
        installs = [action for action in actions if action["action"] == "install"]
        self.assertEqual(
            [action["id"] for action in installs],
            ["verdict-core", "verdict-node"],
        )
        self.assertEqual(installs[1]["version"], "0.1.0")

    def test_unreleased_entries_are_skipped_with_reason(self) -> None:
        actions = SMOKE.plan_actions(MANIFEST)
        skipped = [action for action in actions if action["action"] == "skipped"]
        self.assertEqual(len(skipped), 5)
        self.assertTrue(all("no released artifact" in str(action["reason"]) for action in skipped))

    def test_cross_language_matrix_spans_python_and_node(self) -> None:
        ecosystems = {action["ecosystem"] for action in SMOKE.plan_actions(MANIFEST)}
        self.assertIn("npm", ecosystems)
        self.assertIn("pypi", ecosystems)


if __name__ == "__main__":
    unittest.main()
