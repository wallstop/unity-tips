#!/usr/bin/env python3
"""Check for markdown links that are incorrectly placed inside code blocks.

When markdown links like [text](https://...) are inside code fences (```...```),
they are rendered as plain text instead of clickable HTML links.

This script identifies such issues and warns about them. All links inside code
blocks are flagged, as they will not be clickable in the rendered output.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Optional, Sequence

# Import shared link utilities for consistent code block detection
from link_utils import find_code_fence_ranges, in_ranges


def truncate_with_ellipsis(text: str, max_len: int) -> str:
    """Truncate text and add ellipsis only if it exceeds max_len."""
    if len(text) > max_len:
        return text[:max_len] + "..."
    return text


def check_file(file_path: Path, verbose: bool = False) -> list[str]:
    """Check a file for links inside code blocks.

    Returns:
        List of warning messages.
    """
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        return [f"Error reading {file_path}: {e}"]

    warnings = []
    code_ranges = find_code_fence_ranges(content)

    # Find markdown links with HTTP URLs
    link_pattern = re.compile(r"\[([^\]]+)\]\((https?://[^)]+)\)")

    for match in link_pattern.finditer(content):
        if in_ranges(match.start(), code_ranges):
            line_num = content[: match.start()].count("\n") + 1
            link_text = truncate_with_ellipsis(match.group(1), 40)
            url = truncate_with_ellipsis(match.group(2), 50)

            warnings.append(
                f"{file_path}:{line_num}: Link in code block won't be clickable: "
                f"[{link_text}]({url})"
            )

    return warnings


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Check for links inside code blocks that won't be clickable"
    )
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        default=[Path("docs")],
        help="Files or directories to check (default: docs/)",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Show verbose output"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with error code if any issues found",
    )
    args = parser.parse_args(argv)

    all_warnings = []

    for path in args.paths:
        if path.is_file():
            files = [path]
        elif path.is_dir():
            files = list(path.rglob("*.md"))
        else:
            print(f"Warning: {path} not found", file=sys.stderr)
            continue

        for file_path in sorted(files):
            warnings = check_file(file_path, args.verbose)
            all_warnings.extend(warnings)

    if all_warnings:
        print("Links found inside code blocks (won't be clickable in HTML):")
        for warning in all_warnings:
            print(f"  ⚠️  {warning}")
        print(f"\nTotal: {len(all_warnings)} link(s) in code blocks")
        print("\nTo fix: Remove the code fences (```) around content with links,")
        print("or use regular markdown formatting instead.")

        if args.strict:
            return 1
    else:
        if args.verbose:
            print("No links found inside code blocks")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
