#!/usr/bin/env python3
"""Fix ordered list numbering in Markdown files.

This keeps list numbering sequential per indentation level and ignores code fences.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

LIST_ITEM_PATTERN = re.compile(r"^(\s*)(\d+)([\.).])(.*)$")
FENCE_PATTERN = re.compile(r"^\s*(```|~~~)")


def renumber_markdown_lists(text: str) -> tuple[str, bool]:
    lines = text.splitlines()
    expected_by_indent: dict[int, int] = {}
    in_fence = False
    fence_delimiter: str | None = None
    changed = False

    for idx, original_line in enumerate(lines):
        line = original_line

        stripped = line.lstrip()
        leading_spaces = len(line) - len(stripped)

        if FENCE_PATTERN.match(stripped):
            fence_token = stripped[:3]
            if not in_fence:
                in_fence = True
                fence_delimiter = fence_token
            elif fence_token == fence_delimiter:
                in_fence = False
                fence_delimiter = None
            expected_by_indent.clear()
            continue

        if in_fence:
            continue

        match = LIST_ITEM_PATTERN.match(line)
        if match:
            indent_str, number_text, delimiter, rest = match.groups()
            indent = len(indent_str)

            # Remove expectations for deeper indentation levels.
            for depth in list(expected_by_indent):
                if depth > indent:
                    expected_by_indent.pop(depth)

            expected = expected_by_indent.get(indent, 1)
            if int(number_text) != expected:
                lines[idx] = f"{indent_str}{expected}{delimiter}{rest}"
                changed = True
            expected_by_indent[indent] = expected + 1
        else:
            if not stripped:
                continue
            if leading_spaces > 0:
                # Continuation of the previous list item; keep counters intact.
                continue
            expected_by_indent.clear()

    return "\n".join(lines) + ("\n" if text.endswith("\n") else ""), changed


def process_file(path: Path) -> bool:
    original_text = path.read_text(encoding="utf-8")
    new_text, changed = renumber_markdown_lists(original_text)
    if changed:
        path.write_text(new_text, encoding="utf-8")
    return changed


def main(argv: list[str]) -> int:
    any_changed = False
    for filename in argv[1:]:
        path = Path(filename)
        if path.suffix.lower() not in {".md", ".markdown", ".mdx"}:
            continue
        if process_file(path):
            any_changed = True
    return 0 if not any_changed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
