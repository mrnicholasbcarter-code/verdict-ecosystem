#!/usr/bin/env python3
"""Read-only secret/PII scan for Verdict Portfolio repositories.

Reports path + rule name only. Never prints, logs, or returns matched
content. Refuses to scan any explicitly denied credential directory
(e.g. ~/.omniroute, ~/.claude) and refuses any target that is not itself
a git repository, so it cannot wander into arbitrary home-directory paths
such as ~/.omniroute/.env or ~/.claude/.credentials.json. This containment
check is machine-portable (no hard-coded workspace path) so the same
script runs unchanged in CI, where checkouts live under a runner-specific
path rather than a developer's local `/home/<user>/dev`.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

# Absolute directories that must never be scanned or read, regardless of
# how they are named or referenced. Denying the whole directory (not just
# the specific known-sensitive files inside it) is deliberately
# conservative.
FORBIDDEN_DIRS = [Path.home() / ".omniroute", Path.home() / ".claude"]
MAX_FILE_BYTES = 2 * 1024 * 1024  # skip anything larger; not a fixture dump

RULES: list[tuple[str, re.Pattern[str]]] = [
    ("aws-access-key-id", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("generic-secret-assignment", re.compile(r"(?i)\b(api[_-]?key|secret|password|token)\b\s*[:=]\s*['\"][^'\"\s]{8,}['\"]")),
    ("pem-private-key-header", re.compile(r"-----BEGIN (RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----")),
    ("bearer-token", re.compile(r"(?i)bearer\s+[a-z0-9\-_.]{20,}")),
    ("slack-token", re.compile(r"xox[baprs]-[0-9A-Za-z-]{10,}")),
    ("github-token", re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}")),
]

BINARY_SUFFIXES = {
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".pdf", ".zip", ".gz", ".tar",
    ".whl", ".db", ".sqlite", ".ruvector", ".woff", ".woff2", ".ttf", ".otf",
}


def is_forbidden(candidate: Path) -> bool:
    for forbidden in FORBIDDEN_DIRS:
        try:
            forbidden_resolved = forbidden.resolve()
        except OSError:
            continue
        if candidate == forbidden_resolved or forbidden_resolved in candidate.parents:
            return True
    return False


def resolve_allowed_repo(raw_path: str) -> Path | None:
    candidate = Path(raw_path).resolve()
    if not candidate.is_dir():
        return None
    if is_forbidden(candidate):
        return None
    # Containment: only scan directories git itself recognizes as a
    # repository (worktree or bare). This keeps the check portable across
    # machines/CI without hard-coding any specific workspace path, while
    # still refusing arbitrary non-repository directories.
    try:
        result = subprocess.run(
            ["git", "-C", str(candidate), "rev-parse", "--git-dir"],
            capture_output=True, text=True, timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    return candidate


def list_scan_targets(repo: Path) -> list[Path]:
    """Tracked files plus untracked-but-not-ignored files, via git plumbing.

    Never walks into ignored directories (class 3 runtime state) or .git/.
    """
    targets: list[str] = []
    for args in (["git", "ls-files"], ["git", "ls-files", "--others", "--exclude-standard"]):
        try:
            result = subprocess.run(
                args, cwd=repo, capture_output=True, text=True, check=True, timeout=30,
            )
        except (subprocess.CalledProcessError, OSError, subprocess.TimeoutExpired):
            continue
        targets.extend(line for line in result.stdout.splitlines() if line)
    return [repo / rel for rel in dict.fromkeys(targets)]


def scan_file(path: Path) -> list[str]:
    if path.suffix.lower() in BINARY_SUFFIXES:
        return []
    try:
        if path.stat().st_size > MAX_FILE_BYTES:
            return []
        content = path.read_text(encoding="utf-8", errors="ignore")
    except (OSError, UnicodeError):
        return []
    matched_rules = []
    for rule_name, pattern in RULES:
        if pattern.search(content):
            matched_rules.append(rule_name)
    return matched_rules


def scan_repo(repo: Path) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for target in list_scan_targets(repo):
        if not target.is_file():
            continue
        for rule_name in scan_file(target):
            findings.append({"repo": repo.name, "path": str(target.relative_to(repo)), "rule": rule_name})
    return findings


def main() -> int:
    raw_paths = sys.argv[1:] or ["."]
    findings: list[dict[str, str]] = []
    rejected: list[str] = []
    for raw_path in raw_paths:
        repo = resolve_allowed_repo(raw_path)
        if repo is None:
            rejected.append(raw_path)
            continue
        findings.extend(scan_repo(repo))

    report = {
        "status": "failed" if findings else "passed",
        "findings": findings,
        "rejected_paths": rejected,
        "note": "findings report path + rule name only; matched content is never captured",
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    if rejected:
        return 2
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
