#!/usr/bin/env python3
"""Cross-language contract matrix: install released artifacts in isolated consumers.

For every manifest entry with `publication_status: "published"`, this script
creates an isolated throwaway consumer project (a temp directory that is not
a workspace member), installs the exact pinned `artifact_version` from the
public registry, asserts the installed version matches the manifest, and
runs a minimal import snippet against the released artifact.

Entries without a released artifact are *visibly marked as skipped* with the
reason recorded in the report — they are never silently treated as passing
installs. Planning (`plan_actions`) is pure and offline-testable; only the
executors touch the network.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSTALL_TIMEOUT_SECONDS = 300


def infer_ecosystem(repo: dict) -> str:
    runtimes = set(repo["runtime_constraints"])
    if "node" in runtimes:
        return "npm"
    if "python" in runtimes:
        return "pypi"
    return "unknown"


def plan_actions(manifest: dict) -> list[dict[str, object]]:
    actions: list[dict[str, object]] = []
    for repo in manifest["repositories"]:
        ecosystem = infer_ecosystem(repo)
        if repo["publication_status"] != "published":
            actions.append(
                {
                    "id": repo["id"],
                    "ecosystem": ecosystem,
                    "action": "skipped",
                    "reason": f"no released artifact (publication_status={repo['publication_status']})",
                }
            )
            continue
        actions.append(
            {
                "id": repo["id"],
                "ecosystem": ecosystem,
                "action": "install",
                "package": repo["package"],
                "version": repo["artifact_version"],
                "import_name": repo["import_name"],
            }
        )
    return actions


def run(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command, cwd=cwd, capture_output=True, text=True, timeout=INSTALL_TIMEOUT_SECONDS
    )


def install_npm(action: dict[str, object], consumer: Path) -> list[str]:
    package = str(action["package"])
    version = str(action["version"])
    (consumer / "package.json").write_text(
        json.dumps({"name": "verdict-consumer-smoke", "private": True}) + "\n",
        encoding="utf-8",
    )
    install = run(
        ["npm", "install", f"{package}@{version}", "--no-audit", "--no-fund", "--loglevel=error"],
        consumer,
    )
    if install.returncode != 0:
        return [f"npm install failed: {install.stderr.strip()[:500]}"]

    installed_manifest = consumer / "node_modules" / package / "package.json"
    installed_version = json.loads(installed_manifest.read_text(encoding="utf-8"))["version"]
    problems: list[str] = []
    if installed_version != version:
        problems.append(f"installed version {installed_version} != manifest version {version}")

    snippet = (
        f"import({json.dumps(package)}).then((module) => {{"
        " if (Object.keys(module).length === 0) { console.error('no exports'); process.exit(1); }"
        " }).catch((error) => { console.error(String(error)); process.exit(1); });"
    )
    imported = run(["node", "-e", snippet], consumer)
    if imported.returncode != 0:
        problems.append(f"import snippet failed: {imported.stderr.strip()[:500]}")
    return problems


def install_pypi(action: dict[str, object], consumer: Path) -> list[str]:
    package = str(action["package"])
    version = str(action["version"])
    venv = consumer / "venv"
    created = run([sys.executable, "-m", "venv", str(venv)], consumer)
    if created.returncode != 0:
        return [f"venv creation failed: {created.stderr.strip()[:500]}"]
    pip = venv / "bin" / "pip"
    python = venv / "bin" / "python"
    installed = run([str(pip), "install", "--quiet", f"{package}=={version}"], consumer)
    if installed.returncode != 0:
        return [f"pip install failed: {installed.stderr.strip()[:500]}"]
    import_name = action["import_name"]
    if not import_name:
        return ["published Python artifact has no import_name to smoke-test"]
    imported = run([str(python), "-c", f"import {import_name}"], consumer)
    if imported.returncode != 0:
        return [f"import snippet failed: {imported.stderr.strip()[:500]}"]
    return []


def execute(action: dict[str, object]) -> dict[str, object]:
    result = dict(action)
    if action["action"] == "skipped":
        result["outcome"] = "skipped"
        return result
    with tempfile.TemporaryDirectory(prefix=f"consumer-{action['id']}-") as tmp:
        consumer = Path(tmp)
        if action["ecosystem"] == "npm":
            problems = install_npm(action, consumer)
        elif action["ecosystem"] == "pypi":
            problems = install_pypi(action, consumer)
        else:
            problems = [f"unsupported ecosystem: {action['ecosystem']}"]
    result["outcome"] = "failed" if problems else "installed"
    if problems:
        result["problems"] = problems
    return result


def main() -> int:
    manifest = json.loads((ROOT / "compatibility-manifest.json").read_text(encoding="utf-8"))
    results = [execute(action) for action in plan_actions(manifest)]
    failed = [result for result in results if result["outcome"] == "failed"]
    report = {
        "status": "failed" if failed else "passed",
        "installed": sum(1 for result in results if result["outcome"] == "installed"),
        "skipped_unreleased": sum(1 for result in results if result["outcome"] == "skipped"),
        "matrix": results,
    }
    print(json.dumps(report, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
