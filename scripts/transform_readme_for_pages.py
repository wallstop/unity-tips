#!/usr/bin/env python3
"""Transform README.md links for GitHub Pages compatibility.

This script transforms links in README.md from the GitHub repository format
to the GitHub Pages format:
- ./docs/best-practices/README.md -> ./best-practices/README.md
- docs/tooling/01-csharpier.md -> tooling/01-csharpier.md

This is necessary because the docs/ folder contents are copied directly
to site-docs/ without the docs/ prefix.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Optional, Sequence

from link_utils import extract_links


def transform_links(content: str) -> str:
    """Transform docs/ prefixed links to work on GitHub Pages.

    Uses link_utils.extract_links for robust link extraction that properly
    handles escaped brackets, nested brackets, and other edge cases.
    """
    # Pattern to detect docs/ prefix in hrefs
    docs_prefix_pattern = re.compile(r"^(\./)?docs/(.+)$")

    # Extract all links using the robust link_utils parser
    links = extract_links(content)

    # Process links in reverse order to preserve string positions
    result = content
    for link in reversed(links):
        if link.kind != "inline":
            continue

        match = docs_prefix_pattern.match(link.href)
        if not match:
            continue

        # Transform the href by removing the docs/ prefix
        dot_slash = match.group(1) or ""
        path = match.group(2)
        new_href = f"{dot_slash}{path}"

        # Reconstruct the link with the new href
        # Original segment format: [text](href) or [text]( href "title" )
        old_segment = link.segment
        new_segment = old_segment.replace(link.href, new_href, 1)

        result = result[: link.start] + new_segment + result[link.end :]

    return result


def process_file(input_path: Path, output_path: Optional[Path] = None) -> bool:
    """Process a file and transform its links.

    Args:
        input_path: Path to the input file
        output_path: Path to write the output (None = stdout, same as input = in-place)

    Returns:
        True if changes were made, False otherwise
    """
    try:
        content = input_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"Error reading {input_path}: {e}", file=sys.stderr)
        return False

    transformed = transform_links(content)

    if content == transformed:
        # No changes needed
        if output_path and output_path != input_path:
            output_path.write_text(content, encoding="utf-8")
        return False

    if output_path is None:
        print(transformed, end="")
    else:
        output_path.write_text(transformed, encoding="utf-8")

    return True


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Transform README.md links for GitHub Pages"
    )
    parser.add_argument("input", type=Path, help="Input file to transform")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output file (default: stdout, use --in-place to modify in-place)",
    )
    parser.add_argument(
        "-i",
        "--in-place",
        action="store_true",
        help="Modify file in-place",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Don't print status messages",
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Main entry point."""
    args = parse_args(argv)

    if args.in_place:
        output = args.input
    else:
        output = args.output

    changed = process_file(args.input, output)

    if not args.quiet:
        if changed:
            print(f"Transformed links in {args.input}", file=sys.stderr)
        else:
            print(f"No changes needed in {args.input}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
