#!/usr/bin/env python3
"""Verify every repository, docs, and registry link the ecosystem publishes.

Scope of network access: HTTPS GET requests to the exact URLs recorded in
`compatibility-manifest.json` and found in `README.md` and `docs/*.md`,
plus a registry version lookup for each *published* artifact so the
manifest's `artifact_version` is checked against the registry's immutable
version list. No credentials are read except an optional `GITHUB_TOKEN`
environment variable, sent only to `github.com`/`api.github.com` to avoid
anonymous rate limits. Nothing is written.

URL collection is pure and offline-testable (`collect_manifest_urls`,
`collect_markdown_urls`); only `main()` touches the network.
"""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import quote, urlparse

ROOT = Path(__file__).resolve().parents[1]
MARKDOWN_SOURCES = ("README.md", "docs")
URL_PATTERN = re.compile(r"https://[^\s)\">\]`]+")
TIMEOUT_SECONDS = 20
USER_AGENT = "verdict-ecosystem-link-check"


def collect_manifest_urls(manifest: dict) -> set[str]:
    urls: set[str] = set()
    for check in manifest["release_train"]["deferred_checks"]:
        urls.add(check["blocked_by"])
    for repo in manifest["repositories"]:
        urls.add(repo["repository_url"])
        if repo["registry_url"]:
            urls.add(repo["registry_url"])
    return urls


def collect_markdown_urls(root: Path) -> set[str]:
    urls: set[str] = set()
    paths: list[Path] = []
    for source in MARKDOWN_SOURCES:
        candidate = root / source
        if candidate.is_dir():
            paths.extend(sorted(candidate.glob("*.md")))
        elif candidate.is_file():
            paths.append(candidate)
    for path in paths:
        text = path.read_text(encoding="utf-8", errors="ignore")
        for match in URL_PATTERN.findall(text):
            urls.add(match.rstrip(".,;:!?"))
    return urls


def registry_probes(manifest: dict) -> list[dict[str, str]]:
    """Immutable-version lookups for every published artifact."""
    probes: list[dict[str, str]] = []
    for repo in manifest["repositories"]:
        if repo["publication_status"] != "published":
            continue
        host = urlparse(repo["registry_url"]).hostname or ""
        package = str(repo["package"])
        if host.endswith("npmjs.com"):
            url = "https://registry.npmjs.org/" + quote(package, safe="@")
        elif host.endswith("pypi.org"):
            url = f"https://pypi.org/pypi/{quote(package)}/json"
        else:
            probes.append({"id": repo["id"], "url": repo["registry_url"], "error": f"unsupported registry host: {host}"})
            continue
        probes.append({"id": repo["id"], "url": url, "version": str(repo["artifact_version"])})
    return probes


def probe_url(url: str) -> str:
    """npmjs.com package pages 403 scripted GETs; probe the registry API
    for the same package name instead — it proves the same availability."""
    parsed = urlparse(url)
    if parsed.hostname in {"www.npmjs.com", "npmjs.com"} and parsed.path.startswith("/package/"):
        name = parsed.path[len("/package/"):].strip("/")
        return "https://registry.npmjs.org/" + quote(name, safe="@")
    return url


def fetch(url: str) -> tuple[int, bytes]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    hostname = urlparse(url).hostname or ""
    token = os.environ.get("GITHUB_TOKEN", "")
    if token and hostname in {"github.com", "api.github.com"}:
        request.add_header("Authorization", "Bearer " + token)
    with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
        return response.status, response.read()


def check_url(url: str, attempts: int = 2) -> str | None:
    target = probe_url(url)
    for attempt in range(attempts):
        try:
            status, _ = fetch(target)
        except (urllib.error.URLError, OSError, ValueError) as exc:
            if attempt + 1 == attempts:
                return f"{url}: {exc}"
            continue
        if 200 <= status < 400:
            return None
        if attempt + 1 == attempts:
            return f"{url}: HTTP {status}"
    return f"{url}: unreachable"


def check_registry_version(probe: dict[str, str]) -> str | None:
    if "error" in probe:
        return f"{probe['id']}: {probe['error']}"
    try:
        status, body = fetch(probe["url"])
        payload = json.loads(body)
    except (urllib.error.URLError, OSError, ValueError) as exc:
        return f"{probe['id']}: {probe['url']}: {exc}"
    if status != 200:
        return f"{probe['id']}: {probe['url']}: HTTP {status}"
    versions = payload.get("versions") or payload.get("releases") or {}
    if probe["version"] not in versions:
        return (
            f"{probe['id']}: version {probe['version']} not found in registry"
            f" (available: {sorted(versions)})"
        )
    return None


def main() -> int:
    manifest = json.loads((ROOT / "compatibility-manifest.json").read_text(encoding="utf-8"))
    urls = sorted(collect_manifest_urls(manifest) | collect_markdown_urls(ROOT))
    failures = [problem for url in urls if (problem := check_url(url))]
    probes = registry_probes(manifest)
    failures.extend(problem for probe in probes if (problem := check_registry_version(probe)))
    report = {
        "status": "failed" if failures else "passed",
        "checked_urls": len(urls),
        "registry_version_probes": [probe.get("url") for probe in probes],
        "failures": failures,
    }
    print(json.dumps(report, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
