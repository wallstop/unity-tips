#!/usr/bin/env python3
"""Check for orphaned documents that are not linked from any other document."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import List, Optional, Sequence, Set
from urllib.parse import unquote, urlparse


def extract_local_links(content: str) -> Set[str]:
    """Extract all local markdown links from content."""
    links: Set[str] = set()
    # Match [text](link) pattern
    pattern = r"\[(?:[^\]]*)\]\(([^)]+)\)"
    for match in re.finditer(pattern, content):
        href = match.group(1).strip()
        # Skip external links and anchors-only
        parsed = urlparse(href)
        if parsed.scheme in {"http", "https", "mailto", "tel"}:
            continue
        # Remove anchor part
        path = href.split("#")[0]
        if path:
            links.add(unquote(path))
    return links


def find_all_docs(docs_dir: Path) -> Set[Path]:
    """Find all markdown files in docs directory."""
    return {p for p in docs_dir.rglob("*.md")}


def get_entry_points(docs_dir: Path) -> Set[Path]:
    """Get documents that are entry points (READMEs and main files)."""
    entry_points: Set[Path] = set()

    # Root README is always an entry point
    root_readme = docs_dir.parent / "README.md"
    if root_readme.exists():
        entry_points.add(root_readme.resolve())

    # All README.md files in docs are entry points
    for readme in docs_dir.rglob("README.md"):
        entry_points.add(readme.resolve())

    return entry_points


def check_orphaned(docs_dir: Path) -> List[Path]:
    """Find orphaned documents."""
    all_docs = find_all_docs(docs_dir)

    # Start with entry points as "linked"
    entry_points = get_entry_points(docs_dir)

    # Add root-level docs as entry points
    root_docs = {
        docs_dir.parent / "README.md",
        docs_dir.parent / "CONTRIBUTING.md",
        docs_dir.parent / "AGENTS.md",
    }
    for doc in root_docs:
        if doc.exists():
            entry_points.add(doc.resolve())

    # Find all linked docs (recursive from entry points)
    visited: Set[Path] = set()
    to_visit = list(entry_points)

    while to_visit:
        current = to_visit.pop()
        if current in visited:
            continue
        visited.add(current)

        if not current.exists():
            continue

        content = current.read_text(encoding="utf-8")
        for link in extract_local_links(content):
            if link.startswith("/"):
                target = (docs_dir.parent / link.lstrip("/")).resolve()
            else:
                target = (current.parent / link).resolve()

            if target.is_dir():
                target = target / "README.md"

            if (
                target.exists()
                and target.suffix.lower() == ".md"
                and target not in visited
            ):
                to_visit.append(target)

    # Find orphaned docs
    orphaned = []
    for doc in sorted(all_docs):
        resolved = doc.resolve()
        if resolved not in visited:
            orphaned.append(doc)

    return orphaned


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check for orphaned documents")
    parser.add_argument(
        "docs_dir",
        nargs="?",
        default="docs",
        help="Documentation directory to check (default: docs)",
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    docs_dir = Path(args.docs_dir)

    if not docs_dir.exists():
        print(f"Error: Directory '{docs_dir}' does not exist", file=sys.stderr)
        return 1

    orphaned = check_orphaned(docs_dir)

    if orphaned:
        print("Orphaned documents (not linked from any other document):")
        for doc in orphaned:
            print(f"  - {doc}")
        return 1

    print("No orphaned documents found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
