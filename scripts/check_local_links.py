#!/usr/bin/env python3
"""Check repository-local Markdown links without network access."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
INLINE_LINK_PATTERN = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
REFERENCE_DEFINITION_PATTERN = re.compile(
    r"^ {0,3}\[[^\]]+\]:\s*(?:<([^>]+)>|(\S+))",
    re.MULTILINE,
)
FENCED_BLOCK_PATTERN = re.compile(r"^ {0,3}(```|~~~).*?^ {0,3}\1\s*$", re.MULTILINE | re.DOTALL)
IGNORED_SCHEMES = {"http", "https", "mailto"}


def markdown_files(root: Path) -> list[Path]:
    files = [root / "README.md"]
    files.extend(sorted((root / "docs").rglob("*.md")))
    files.extend(sorted((root / ".specify").rglob("*.md")))
    return [path for path in files if path.is_file()]


def heading_anchors(path: Path) -> set[str]:
    anchors: set[str] = set()
    counts: dict[str, int] = {}
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not line.startswith("#"):
            continue
        heading = line.lstrip("#").strip().lower()
        anchor = re.sub(r"[^\w\- ]", "", heading).replace(" ", "-")
        anchor = re.sub(r"-+", "-", anchor).strip("-")
        count = counts.get(anchor, 0)
        counts[anchor] = count + 1
        anchors.add(anchor if count == 0 else f"{anchor}-{count}")
    return anchors


def link_destinations(text: str) -> list[str]:
    """Return inline and reference-definition destinations outside fenced code."""
    searchable = FENCED_BLOCK_PATTERN.sub("", text)
    destinations = INLINE_LINK_PATTERN.findall(searchable)
    destinations.extend(left or right for left, right in REFERENCE_DEFINITION_PATTERN.findall(searchable))
    return destinations


def local_link_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for source in markdown_files(root):
        text = source.read_text(encoding="utf-8", errors="ignore")
        for raw in link_destinations(text):
            destination = raw.strip().split(maxsplit=1)[0].strip("<>")
            parsed = urlparse(destination)
            if parsed.scheme in IGNORED_SCHEMES:
                continue
            if parsed.scheme:
                continue
            target = source.resolve() if not parsed.path else (source.parent / unquote(parsed.path)).resolve()
            try:
                target.relative_to(root.resolve())
            except ValueError:
                failures.append(f"{source.relative_to(root)}: link escapes repository: {raw}")
                continue
            if not target.exists():
                failures.append(f"{source.relative_to(root)}: missing local target: {raw}")
                continue
            if parsed.fragment and target.is_file() and target.suffix.lower() == ".md":
                anchor = unquote(parsed.fragment).lower()
                if anchor not in heading_anchors(target):
                    failures.append(f"{source.relative_to(root)}: missing local anchor: {raw}")
    return failures


def main() -> int:
    failures = local_link_failures(ROOT)
    for failure in failures:
        print(failure)
    if failures:
        print(f"local Markdown link check failed: {len(failures)} problem(s)")
        return 1
    print(f"local Markdown link check passed: {len(markdown_files(ROOT))} file(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
