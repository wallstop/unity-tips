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


def transform_links(content: str) -> str:
    """Transform docs/ prefixed links to work on GitHub Pages."""
    # Pattern to match markdown links with docs/ prefix
    # Matches: [text](./docs/path) or [text](docs/path)
    pattern = r'(\[[^\]]*\]\()(\./)?docs/([^)]+\))'

    def replacer(match: re.Match[str]) -> str:
        prefix = match.group(1)  # [text](
        dot_slash = match.group(2) or ""  # ./ or empty
        path = match.group(3)  # path)
        return f"{prefix}{dot_slash}{path}"

    return re.sub(pattern, replacer, content)


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
