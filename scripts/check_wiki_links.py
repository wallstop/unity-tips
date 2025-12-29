#!/usr/bin/env python3
"""Validate wiki links in generated wiki files.

This script checks that all wiki-style links ([[PageName|text]]) in the wiki/
directory point to existing wiki pages, and that no markdown-style links
remain outside of code blocks.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Set, Tuple, List

# Import shared link utilities
from link_utils import find_code_fence_ranges, find_inline_code_ranges, in_ranges

WIKI_DIR = Path("wiki")


def extract_wiki_links(content: str) -> List[Tuple[str, str, int]]:
    """Extract wiki-style links from content, skipping code blocks.

    Returns:
        List of (page_name, anchor, line_number) tuples.
        anchor is empty string if no anchor present.
    """
    # Get code ranges to skip
    code_ranges = find_code_fence_ranges(content)
    inline_code_ranges = find_inline_code_ranges(content)
    skip_ranges = code_ranges + inline_code_ranges

    links = []
    # Match [[PageName|text]] or [[PageName#anchor|text]] or [[PageName]]
    pattern = re.compile(r"\[\[([^\]|#]+)(#[^\]|]*)?\|?[^\]]*\]\]")

    for match in pattern.finditer(content):
        if in_ranges(match.start(), skip_ranges):
            continue
        page_name = match.group(1).strip()
        anchor = match.group(2) or ""
        # Calculate line number
        line_num = content[:match.start()].count("\n") + 1
        links.append((page_name, anchor, line_num))

    return links


def find_unconverted_links(content: str, file_path: Path) -> List[Tuple[str, int]]:
    """Find markdown-style links that should have been converted to wiki format.

    Returns:
        List of (link, line_number) tuples for links outside code blocks.
    """
    # Get code ranges to skip
    code_ranges = find_code_fence_ranges(content)
    inline_code_ranges = find_inline_code_ranges(content)
    skip_ranges = code_ranges + inline_code_ranges

    unconverted = []
    # Match [text](path.md) style links to local markdown files
    pattern = re.compile(r"\[([^\]]+)\]\((\.\.?/[^)]+\.md[^)]*)\)")

    for match in pattern.finditer(content):
        if in_ranges(match.start(), skip_ranges):
            continue
        href = match.group(2)
        # Skip external links
        if href.startswith(("http://", "https://", "mailto:")):
            continue
        line_num = content[:match.start()].count("\n") + 1
        unconverted.append((href, line_num))

    return unconverted


def get_wiki_pages() -> Set[str]:
    """Get all wiki page names from the wiki directory."""
    pages = set()
    for md_file in WIKI_DIR.glob("*.md"):
        # Remove .md extension to get page name
        page_name = md_file.stem
        pages.add(page_name)
    return pages


def validate_wiki(verbose: bool = False) -> int:
    """Validate all wiki links.

    Returns:
        0 if all links are valid, 1 if there are errors.
    """
    if not WIKI_DIR.exists():
        print(f"Error: Wiki directory '{WIKI_DIR}' does not exist.")
        print("Run 'python scripts/sync-wiki.py' first to generate wiki files.")
        return 1

    wiki_pages = get_wiki_pages()
    if not wiki_pages:
        print(f"Warning: No wiki pages found in '{WIKI_DIR}'")
        return 1

    errors = []
    warnings = []
    total_links = 0

    for md_file in sorted(WIKI_DIR.glob("*.md")):
        content = md_file.read_text(encoding="utf-8")

        # Check wiki links
        wiki_links = extract_wiki_links(content)
        total_links += len(wiki_links)

        for page_name, anchor, line_num in wiki_links:
            if page_name not in wiki_pages:
                errors.append(
                    f"{md_file.name}:{line_num}: Broken link to non-existent page "
                    f"'[[{page_name}]]'"
                )

        # Check for unconverted markdown links
        unconverted = find_unconverted_links(content, md_file)
        for href, line_num in unconverted:
            warnings.append(
                f"{md_file.name}:{line_num}: Unconverted markdown link: [{href}]"
            )

    # Report results
    if verbose or errors or warnings:
        print(f"\nWiki Link Validation Report")
        print(f"{'=' * 40}")
        print(f"Wiki pages found: {len(wiki_pages)}")
        print(f"Total wiki links checked: {total_links}")
        print()

    if errors:
        print(f"ERRORS ({len(errors)}):")
        for error in errors:
            print(f"  ❌ {error}")
        print()

    if warnings:
        print(f"WARNINGS ({len(warnings)}):")
        for warning in warnings:
            print(f"  ⚠️  {warning}")
        print()

    if errors:
        print(f"❌ Validation failed with {len(errors)} error(s)")
        return 1

    if warnings:
        print(f"✓ Validation passed with {len(warnings)} warning(s)")
    else:
        print(f"✓ All {total_links} wiki links are valid")

    return 0


def main() -> int:
    """Main entry point."""
    verbose = "-v" in sys.argv or "--verbose" in sys.argv
    return validate_wiki(verbose)


if __name__ == "__main__":
    raise SystemExit(main())
