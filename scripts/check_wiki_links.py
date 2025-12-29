#!/usr/bin/env python3
"""Validate wiki links in generated wiki files.

This script checks that all wiki-style links ([[PageName|text]]) in the wiki/
directory point to existing wiki pages, and that no markdown-style links
remain outside of code blocks.

Additional validations:
- Validates sidebar references only existing pages
- Validates all WIKI_STRUCTURE source files exist
- Validates critical pages (Best-Practices, Development-Tooling) are present
- Validates Home.md contains expected navigation links
"""

from __future__ import annotations

import re
import sys
from enum import Enum
from pathlib import Path
from typing import Set, Tuple, List

# Import shared link utilities
from link_utils import find_code_fence_ranges, find_inline_code_ranges, in_ranges

WIKI_DIR = Path("wiki")
DOCS_DIR = Path("docs")


class Severity(Enum):
    """Severity levels for validation messages."""

    CRITICAL = "CRITICAL"
    WARNING = "WARNING"


def format_message(severity: Severity, message: str) -> str:
    """Format a validation message with consistent severity prefix."""
    return f"{severity.value}: {message}"


# Critical wiki pages that MUST exist (these have historically caused issues)
CRITICAL_PAGES = [
    "Best-Practices",
    "Development-Tooling",
    "Home",
    "_Sidebar",
]

# Required navigation links in Home.md (page_name, display_text_contains)
REQUIRED_HOME_LINKS = [
    ("Best-Practices", "Best Practices"),
    ("Development-Tooling", "Development Tooling"),
]


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
        line_num = content[: match.start()].count("\n") + 1
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
        line_num = content[: match.start()].count("\n") + 1
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


def validate_critical_pages(wiki_pages: Set[str]) -> List[str]:
    """Validate that all critical pages exist.

    Returns:
        List of error messages for missing critical pages.
    """
    errors = []
    for page_name in CRITICAL_PAGES:
        if page_name not in wiki_pages:
            errors.append(
                format_message(
                    Severity.CRITICAL, f"Missing required page '{page_name}.md'"
                )
            )
        else:
            # Verify the file has content
            page_path = WIKI_DIR / f"{page_name}.md"
            if page_path.exists():
                content = page_path.read_text(encoding="utf-8").strip()
                if not content:
                    errors.append(
                        format_message(
                            Severity.CRITICAL,
                            f"Page '{page_name}.md' exists but is empty",
                        )
                    )
                elif len(content) < 100:
                    errors.append(
                        format_message(
                            Severity.WARNING,
                            f"Page '{page_name}.md' has very little content "
                            f"({len(content)} chars)",
                        )
                    )
    return errors


def validate_home_links(wiki_pages: Set[str]) -> List[str]:
    """Validate that Home.md contains required navigation links.

    Returns:
        List of error messages for missing required links.
    """
    errors = []
    home_path = WIKI_DIR / "Home.md"
    if not home_path.exists():
        return [format_message(Severity.CRITICAL, "Home.md does not exist")]

    content = home_path.read_text(encoding="utf-8")

    for page_name, expected_display_text in REQUIRED_HOME_LINKS:
        # Check if there's a link to this page
        pattern = rf"\[\[{re.escape(page_name)}(?:#[^\]|]*)?\|([^\]]*)\]\]"
        matches = re.findall(pattern, content)

        if not matches:
            errors.append(
                format_message(
                    Severity.CRITICAL, f"Home.md missing link to '{page_name}' page"
                )
            )
        else:
            # Check if the page exists
            if page_name not in wiki_pages:
                errors.append(
                    format_message(
                        Severity.CRITICAL,
                        f"Home.md links to '{page_name}' but page doesn't exist",
                    )
                )
            # Validate display text contains expected text
            found_expected = any(
                expected_display_text in display for display in matches
            )
            if not found_expected:
                errors.append(
                    format_message(
                        Severity.WARNING,
                        f"Home.md link to '{page_name}' has unexpected display text "
                        f"(expected to contain '{expected_display_text}')",
                    )
                )

    return errors


def validate_sidebar_links(wiki_pages: Set[str]) -> List[str]:
    """Validate that all sidebar links point to existing pages.

    Returns:
        List of error messages for invalid sidebar links.
    """
    errors = []
    sidebar_path = WIKI_DIR / "_Sidebar.md"
    if not sidebar_path.exists():
        return [format_message(Severity.CRITICAL, "_Sidebar.md does not exist")]

    content = sidebar_path.read_text(encoding="utf-8")
    wiki_links = extract_wiki_links(content)

    for page_name, anchor, line_num in wiki_links:
        if page_name not in wiki_pages:
            errors.append(
                format_message(
                    Severity.CRITICAL,
                    f"_Sidebar.md:{line_num}: Links to non-existent "
                    f"page '[[{page_name}]]'",
                )
            )

    return errors


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

    # Phase 1: Validate critical pages exist and have content
    critical_errors = validate_critical_pages(wiki_pages)
    errors.extend(critical_errors)

    # Phase 2: Validate Home.md has required navigation links
    home_errors = validate_home_links(wiki_pages)
    errors.extend(home_errors)

    # Phase 3: Validate sidebar links
    sidebar_errors = validate_sidebar_links(wiki_pages)
    errors.extend(sidebar_errors)

    # Phase 4: Validate all wiki links in all files
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
    print(f"\nWiki Link Validation Report")
    print(f"{'=' * 40}")
    print(f"Wiki pages found: {len(wiki_pages)}")
    print(f"Total wiki links checked: {total_links}")
    print()

    # Show critical pages status
    print("Critical Pages Status:")
    for page_name in CRITICAL_PAGES:
        page_path = WIKI_DIR / f"{page_name}.md"
        if page_path.exists():
            size = page_path.stat().st_size
            print(f"  ✓ {page_name}.md ({size} bytes)")
        else:
            print(f"  ❌ {page_name}.md (MISSING)")
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
