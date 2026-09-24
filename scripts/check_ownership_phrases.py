#!/usr/bin/env python3
"""
Guard script to prevent regression of Prime ownership orchestration claims.
Fails if README.md or docs/*.md files match problematic patterns about
Prime owning orchestration/routing, excluding historical audit/gap/history files.
"""

import re
import sys
from pathlib import Path

# Pattern to match: "prime owns ... orchestration" (case-insensitive)
# Exclude files with AUDIT, GAP, HISTORY, ARCHIVE in their name
OWNERSHIP_PATTERN = re.compile(
    r"prime\s+owns[^.\n]{0,60}orchestration",
    re.IGNORECASE | re.MULTILINE
)

EXCLUDE_PATTERNS = ["AUDIT", "GAP", "HISTORY", "ARCHIVE"]

def should_check_file(file_path: Path) -> bool:
    """Returns True if the file should be checked."""
    name = file_path.name.upper()
    for pattern in EXCLUDE_PATTERNS:
        if pattern in name:
            return False
    return True

def check_file(file_path: Path) -> list:
    """Check a file for problematic patterns. Returns list of (line_num, line_text)."""
    issues = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for line_num, line in enumerate(lines, 1):
            if OWNERSHIP_PATTERN.search(line):
                issues.append((line_num, line.rstrip()))
    except Exception as e:
        print(f"Error reading {file_path}: {e}", file=sys.stderr)
    
    return issues

def main():
    """Check README.md and docs/*.md for problematic patterns."""
    all_issues = {}
    
    # Check README.md
    readme_path = Path("README.md")
    if readme_path.exists() and should_check_file(readme_path):
        issues = check_file(readme_path)
        if issues:
            all_issues[str(readme_path)] = issues
    
    # Check docs/*.md
    docs_dir = Path("docs")
    if docs_dir.exists():
        for md_file in docs_dir.glob("*.md"):
            if should_check_file(md_file):
                issues = check_file(md_file)
                if issues:
                    all_issues[str(md_file)] = issues
    
    # Report findings
    if all_issues:
        print("ERROR: Found problematic Prime ownership phrases:", file=sys.stderr)
        for file_path, issues in sorted(all_issues.items()):
            print(f"\n  {file_path}:", file=sys.stderr)
            for line_num, line_text in issues:
                print(f"    Line {line_num}: {line_text}", file=sys.stderr)
        return 1
    
    print("OK: No problematic Prime ownership phrases found.", file=sys.stdout)
    return 0

if __name__ == "__main__":
    sys.exit(main())
