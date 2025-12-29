#!/usr/bin/env python3
"""Fix markdown links that are incorrectly placed inside code blocks.

When markdown links like [text](https://...) are inside code fences (```...```),
they are rendered as plain text instead of clickable HTML links.

This script identifies code blocks that contain markdown-style HTTP links and
converts them to regular markdown content by removing the code fences.

Note: This only fixes code blocks without a language specifier (``` not ```python).
Code blocks with language specifiers are assumed to be intentional code samples.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Optional, Sequence


def find_code_blocks_with_links(content: str) -> list[tuple[int, int, str]]:
    """Find code blocks WITHOUT language specifiers that contain markdown links.

    Only matches code blocks that start with ``` followed by optional whitespace
    and a newline (no language identifier). Blocks with language specifiers like
    ```python or ```csharp are intentional code samples and are skipped.

    Returns:
        List of (start, end, block_content) tuples for blocks that need fixing.
    """
    # Pattern for code blocks WITHOUT language specifier only
    # Matches: ``` followed by optional whitespace, then newline, content, closing ```
    # Does NOT match ```python, ```csharp, etc.
    # Note: Uses custom regex instead of shared find_code_fence_ranges() because
    # we specifically need to identify blocks WITHOUT language specifiers.
    pattern = re.compile(r"^```\s*\n(.*?)^```\s*$", re.MULTILINE | re.DOTALL)

    # Pattern for markdown links with HTTP URLs
    link_pattern = re.compile(r"\[([^\]]+)\]\((https?://[^)]+)\)")

    blocks_to_fix = []
    for match in pattern.finditer(content):
        block_content = match.group(1)
        # Check if this block contains HTTP links in markdown format
        if link_pattern.search(block_content):
            blocks_to_fix.append((match.start(), match.end(), block_content))

    return blocks_to_fix


def fix_code_blocks(content: str, verbose: bool = False) -> tuple[str, int]:
    """Fix code blocks that contain markdown links.

    Returns:
        Tuple of (fixed_content, number_of_fixes).
    """
    blocks = find_code_blocks_with_links(content)

    if not blocks:
        return content, 0

    # Process in reverse order to preserve string positions
    result = content
    fixes = 0

    for start, end, block_content in reversed(blocks):
        # Remove the code fence markers, keep the content
        # The content already has proper line breaks
        fixed_block = block_content.rstrip()

        if verbose:
            # Show first line of block for context
            first_line = block_content.strip().split("\n")[0]
            if len(first_line) > 60:
                first_line = first_line[:60] + "..."
            print(f"  Fixing code block: {first_line}")

        result = result[:start] + fixed_block + result[end:]
        fixes += 1

    return result, fixes


def process_file(
    file_path: Path, in_place: bool = False, verbose: bool = False
) -> tuple[bool, int]:
    """Process a single file.

    Returns:
        Tuple of (changed, fixes_count).
    """
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"Error reading {file_path}: {e}", file=sys.stderr)
        return False, 0

    fixed_content, fixes = fix_code_blocks(content, verbose)

    if fixes == 0:
        return False, 0

    if in_place:
        try:
            file_path.write_text(fixed_content, encoding="utf-8")
        except Exception as e:
            print(f"Error writing {file_path}: {e}", file=sys.stderr)
            return False, 0
        if verbose:
            print(f"  Fixed {fixes} code block(s) in {file_path}")
    else:
        print(f"Would fix {fixes} code block(s) in {file_path}")

    return True, fixes


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Fix markdown links inside code blocks"
    )
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        default=[Path("docs")],
        help="Files or directories to process (default: docs/)",
    )
    parser.add_argument(
        "-i", "--in-place", action="store_true", help="Modify files in-place"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Show detailed output"
    )
    args = parser.parse_args(argv)

    total_files = 0
    total_fixes = 0

    for path in args.paths:
        if path.is_file():
            files = [path]
        elif path.is_dir():
            files = list(path.rglob("*.md"))
        else:
            print(f"Warning: {path} not found", file=sys.stderr)
            continue

        for file_path in sorted(files):
            changed, fixes = process_file(file_path, args.in_place, args.verbose)
            if changed:
                total_files += 1
                total_fixes += fixes

    if total_fixes > 0:
        action = "Fixed" if args.in_place else "Would fix"
        print(f"\n{action} {total_fixes} code block(s) in {total_files} file(s)")
    else:
        print("No code blocks with links found")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
