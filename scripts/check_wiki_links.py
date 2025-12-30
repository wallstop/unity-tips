#!/usr/bin/env python3
"""Validate wiki links in generated wiki files.

This script checks that all wiki-style links ([[PageName|text]]) in the wiki/
directory point to existing wiki pages, and that no markdown-style links
remain outside of code blocks.

Additional validations:
- Validates that sidebar references only existing pages
- Validates that critical pages (Best-Practices, Development-Tooling) are present
- Validates that Home.md contains expected navigation links

Note: WIKI_STRUCTURE source file validation is handled by sync-wiki.py.
"""

from __future__ import annotations

import re
import sys
from enum import Enum
from pathlib import Path
from typing import Set, Tuple, List, overload, Literal, NamedTuple

# Import shared link utilities
from link_utils import (
    CRITICAL_PAGES,
    MIN_PAGE_CONTENT_LENGTH,
    find_code_fence_ranges,
    find_inline_code_ranges,
    in_ranges,
)

WIKI_DIR = Path("wiki")


class Severity(Enum):
    """Severity levels for validation messages."""

    CRITICAL = "CRITICAL"
    WARNING = "WARNING"


def format_message(severity: Severity, message: str) -> str:
    """Format a validation message with consistent severity prefix."""
    return f"{severity.value}: {message}"


# Required navigation links in Home.md (page_name, display_text_contains)
# Note: Links must use the format [[PageName|Display Text]] with explicit display text.
# Links without display text like [[PageName]] won't match and will be flagged as missing.
REQUIRED_HOME_LINKS = [
    ("Best-Practices", "Best Practices"),
    ("Development-Tooling", "Development Tooling"),
]


class WikiLink(NamedTuple):
    """A wiki link without display text information."""

    page_name: str
    anchor: str
    line_num: int


class WikiLinkWithDisplay(NamedTuple):
    """A wiki link with display text information."""

    display_text: str
    page_name: str
    anchor: str
    line_num: int


def _split_wiki_link_on_pipe(inner: str) -> Tuple[str, str]:
    """Split wiki link inner content on the last pipe, handling escaped pipes.

    In GitHub Wiki format [[DisplayText|PageName]], the pipe separates display
    text from page name. In table contexts, the pipe is escaped as \\| to prevent
    Markdown from treating it as a table cell separator.

    Both [[DisplayText|PageName]] and [[DisplayText\\|PageName]] should parse as:
    - display_text = "DisplayText"
    - page_part = "PageName"

    Args:
        inner: The inner content of a wiki link (between [[ and ]]).

    Returns:
        Tuple of (display_text, page_part). If no pipe is found,
        returns ("", inner).
    """
    # Find the last pipe character
    pipe_idx = inner.rfind("|")

    if pipe_idx < 0:
        # No pipe found - no display text
        return ("", inner)

    # Check if this pipe was escaped (\|) for table context
    # We check the original string to identify \| as a unit
    is_escaped_pipe = pipe_idx > 0 and inner[pipe_idx - 1] == "\\"

    if is_escaped_pipe:
        # Escaped pipe: exclude the backslash from display text
        display_text = inner[: pipe_idx - 1]
    else:
        display_text = inner[:pipe_idx]

    page_part = inner[pipe_idx + 1 :]

    return (display_text, page_part)


@overload
def extract_wiki_links(
    content: str, include_display_text: Literal[False] = False
) -> List[WikiLink]: ...


@overload
def extract_wiki_links(
    content: str, include_display_text: Literal[True]
) -> List[WikiLinkWithDisplay]: ...


class _ParsedWikiLink(NamedTuple):
    """Internal parsed wiki link with all components."""

    display_text: str
    page_name: str
    anchor: str
    line_num: int


def _parse_wiki_link(inner: str, line_num: int) -> _ParsedWikiLink:
    """Parse a wiki link's inner content into its components.

    Args:
        inner: The inner content of a wiki link (between [[ and ]]).
        line_num: The line number where the link was found.

    Returns:
        _ParsedWikiLink with all components extracted.
    """
    # Parse using helper that handles escaped pipes
    display_text, page_part = _split_wiki_link_on_pipe(inner)

    # Extract anchor if present
    if "#" in page_part:
        page_name, anchor = page_part.split("#", 1)
        anchor = "#" + anchor
    else:
        page_name = page_part
        anchor = ""

    return _ParsedWikiLink(display_text.strip(), page_name.strip(), anchor, line_num)


def extract_wiki_links(
    content: str, include_display_text: bool = False
) -> List[WikiLink] | List[WikiLinkWithDisplay]:
    """Extract wiki-style links from content, skipping code blocks.

    GitHub Wiki link format is [[DisplayText|PageName]] or [[PageName]].
    Note: This is opposite of MediaWiki's [[PageName|DisplayText]] format.

    Handles escaped pipes (\\|) in table contexts - these are NOT treated as
    separators between display text and page name.

    Args:
        content: The content to extract links from.
        include_display_text: If True, returns WikiLinkWithDisplay tuples.
                              If False (default), returns WikiLink tuples.

    Returns:
        List of WikiLink or WikiLinkWithDisplay named tuples.
    """
    # Get code ranges to skip
    code_ranges = find_code_fence_ranges(content)
    inline_code_ranges = find_inline_code_ranges(content)
    skip_ranges = code_ranges + inline_code_ranges

    # Match [[...]] content
    pattern = re.compile(r"\[\[([^\]]+)\]\]")

    # Parse all links once using the shared helper
    parsed_links: List[_ParsedWikiLink] = []
    for match in pattern.finditer(content):
        if in_ranges(match.start(), skip_ranges):
            continue

        inner = match.group(1).strip()
        line_num = content[: match.start()].count("\n") + 1
        parsed_links.append(_parse_wiki_link(inner, line_num))

    # Convert to the appropriate return type
    if include_display_text:
        return [
            WikiLinkWithDisplay(p.display_text, p.page_name, p.anchor, p.line_num)
            for p in parsed_links
        ]
    else:
        return [WikiLink(p.page_name, p.anchor, p.line_num) for p in parsed_links]


def find_redundant_links(content: str) -> List[Tuple[str, int]]:
    """Find redundant wiki links where display text matches page name.

    Links like [[Coroutines|Coroutines]] are redundant and should be [[Coroutines]].
    This helps ensure the short format optimization is consistently applied.

    Returns:
        List of (page_name, line_number) tuples for redundant links.
    """
    # Get links with display text
    links = extract_wiki_links(content, include_display_text=True)

    redundant = []
    for link in links:
        # Use NamedTuple fields for clarity
        # If display text is non-empty and matches page name exactly, it's redundant
        if link.display_text and link.display_text == link.page_name:
            redundant.append((link.page_name, link.line_num))

    return redundant


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
            # Verify the file has content (page exists since it's in wiki_pages)
            page_path = WIKI_DIR / f"{page_name}.md"
            try:
                content = page_path.read_text(encoding="utf-8").strip()
            except OSError as e:
                errors.append(
                    format_message(
                        Severity.CRITICAL,
                        f"Failed to read '{page_name}.md': {e}",
                    )
                )
                continue
            if not content:
                errors.append(
                    format_message(
                        Severity.CRITICAL,
                        f"Page '{page_name}.md' exists but is empty",
                    )
                )
            elif len(content) < MIN_PAGE_CONTENT_LENGTH:
                errors.append(
                    format_message(
                        Severity.WARNING,
                        f"Page '{page_name}.md' has very little content "
                        f"({len(content)} chars, minimum {MIN_PAGE_CONTENT_LENGTH})",
                    )
                )
    return errors


def validate_home_links(wiki_pages: Set[str]) -> List[str]:
    """Validate that Home.md contains required navigation links.

    GitHub Wiki link format is [[DisplayText|PageName]] or [[PageName]].
    Note: This is opposite of MediaWiki's [[PageName|DisplayText]] format.

    Returns:
        List of error messages for missing required links.
    """
    errors = []
    home_path = WIKI_DIR / "Home.md"
    if not home_path.exists():
        return [format_message(Severity.CRITICAL, "Home.md does not exist")]

    try:
        content = home_path.read_text(encoding="utf-8")
    except OSError as e:
        return [format_message(Severity.CRITICAL, f"Failed to read Home.md: {e}")]

    for page_name, expected_display_text in REQUIRED_HOME_LINKS:
        # Check if there's a link to this page
        # GitHub Wiki format: [[DisplayText|PageName]] or [[DisplayText|PageName#anchor]]
        # We look for the page name after the pipe
        pattern = rf"\[\[([^\]|]+)\|{re.escape(page_name)}(?:#[^\]]+)?\]\]"
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

    try:
        content = sidebar_path.read_text(encoding="utf-8")
    except OSError as e:
        return [format_message(Severity.CRITICAL, f"Failed to read _Sidebar.md: {e}")]
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
        try:
            content = md_file.read_text(encoding="utf-8")
        except OSError as e:
            errors.append(
                format_message(
                    Severity.CRITICAL, f"{md_file.name}: Failed to read file: {e}"
                )
            )
            continue

        # Check wiki links
        wiki_links = extract_wiki_links(content)
        total_links += len(wiki_links)

        for page_name, anchor, line_num in wiki_links:
            if page_name not in wiki_pages:
                errors.append(
                    format_message(
                        Severity.CRITICAL,
                        f"{md_file.name}:{line_num}: Broken link to non-existent page "
                        f"'[[{page_name}]]'",
                    )
                )

        # Check for unconverted markdown links
        unconverted = find_unconverted_links(content, md_file)
        for href, line_num in unconverted:
            warnings.append(
                format_message(
                    Severity.WARNING,
                    f"{md_file.name}:{line_num}: Unconverted markdown link: [{href}]",
                )
            )

        # Check for redundant wiki links like [[X|X]] that should be [[X]]
        redundant = find_redundant_links(content)
        for page_name, line_num in redundant:
            warnings.append(
                format_message(
                    Severity.WARNING,
                    f"{md_file.name}:{line_num}: Redundant link format: "
                    f"[[{page_name}|{page_name}]] should be [[{page_name}]]",
                )
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
