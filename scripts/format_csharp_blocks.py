#!/usr/bin/env python3
"""Format C# code blocks in markdown files using CSharpier-style formatting.

This script extracts C# code blocks from markdown files and applies CSharpier-like
formatting rules:
- Allman-style braces (opening brace on its own line)
- 4 spaces indentation
- Spaces around operators
- Space after keywords (if, for, while, etc.)
- Space after commas
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Sequence, Tuple


@dataclass
class CodeBlock:
    file: Path
    line_start: int
    line_end: int
    content: str
    language: str


def extract_csharp_blocks(file: Path) -> List[CodeBlock]:
    """Extract C# code blocks from a markdown file."""
    content = file.read_text(encoding="utf-8")
    blocks: List[CodeBlock] = []
    lines = content.split("\n")

    in_block = False
    block_start = 0
    block_lines: List[str] = []

    for i, line in enumerate(lines, 1):
        if re.match(r"^```(?:csharp|cs)\s*$", line):
            in_block = True
            block_start = i
            block_lines = []
        elif in_block and line.startswith("```"):
            in_block = False
            blocks.append(
                CodeBlock(
                    file=file,
                    line_start=block_start,
                    line_end=i,
                    content="\n".join(block_lines),
                    language="csharp",
                )
            )
        elif in_block:
            block_lines.append(line)

    return blocks


class CSharpFormatter:
    """A simplified CSharpier-like formatter for C# code."""

    # Keywords that should have space after them before (
    # Note: nameof, typeof, sizeof, default do NOT get spaces in C#
    KEYWORDS_WITH_SPACE = {
        "if", "for", "foreach", "while", "do", "switch",
        "catch", "using", "lock", "fixed", "checked", "unchecked",
    }

    def __init__(self):
        self.indent_size = 4

    def format_code(self, code: str) -> str:
        """Format C# code using CSharpier-like rules."""
        if not code.strip():
            return code

        # Skip formatting for blocks that should remain unchanged
        if self._should_skip_block(code):
            return code

        # Normalize line endings
        code = code.replace("\r\n", "\n").replace("\r", "\n")

        # Apply formatting passes - each line independently
        lines = code.split("\n")
        result_lines = []

        for line in lines:
            formatted_line = self._format_line(line)
            result_lines.append(formatted_line)

        # Join and apply multi-line formatting
        code = "\n".join(result_lines)
        code = self._format_braces_allman(code)
        code = self._ensure_blank_lines_between_members(code)

        return code

    def _should_skip_block(self, code: str) -> bool:
        """Check if this code block should be skipped."""
        # Skip if it's a shell command or config
        lines = [l.strip() for l in code.strip().split("\n") if l.strip()]
        if not lines:
            return True

        first_line = lines[0]
        shell_prefixes = ["dotnet ", "git ", "mkdir ", "cat ", "pip ", "npm "]
        if any(first_line.startswith(p) for p in shell_prefixes):
            return True

        # Skip very short code blocks (usually fragments)
        if len(lines) <= 1 and len(code.strip()) < 40:
            return True

        return False

    def _format_line(self, line: str) -> str:
        """Format a single line of C# code."""
        if not line.strip():
            return line

        # Preserve original indentation
        original_indent = len(line) - len(line.lstrip())
        indent_str = line[:original_indent]
        content = line.strip()

        # Skip comment lines entirely
        if content.startswith("//") or content.startswith("/*") or content.startswith("*"):
            return line

        # Apply formatting transformations
        content = self._format_keywords_in_line(content)
        content = self._format_operators_in_line(content)
        content = self._format_commas_in_line(content)
        content = self._format_inheritance_colon(content)
        content = self._remove_space_before_semicolon(content)

        return indent_str + content

    def _format_keywords_in_line(self, content: str) -> str:
        """Add space after keywords before parentheses."""
        for keyword in self.KEYWORDS_WITH_SPACE:
            # Pattern: keyword immediately followed by (
            pattern = rf"\b({keyword})\("
            replacement = rf"\1 ("
            content = re.sub(pattern, replacement, content)
        return content

    def _format_operators_in_line(self, content: str) -> str:
        """Add spaces around assignment and comparison operators."""
        # Skip if line contains strings (simple heuristic)
        if '"' in content:
            return content

        # Add spaces around these operators if they don't have them
        operators = [
            ("==", r"(\S)==(\S)", r"\1 == \2"),
            ("!=", r"(\S)!=(\S)", r"\1 != \2"),
            ("<=", r"(\S)<=(\S)", r"\1 <= \2"),
            (">=", r"(\S)>=(\S)", r"\1 >= \2"),
            ("+=", r"(\S)\+=(\S)", r"\1 += \2"),
            ("-=", r"(\S)-=(\S)", r"\1 -= \2"),
            ("*=", r"(\S)\*=(\S)", r"\1 *= \2"),
            ("/=", r"(\S)/=(\S)", r"\1 /= \2"),
            ("&&", r"(\S)&&(\S)", r"\1 && \2"),
            ("||", r"(\S)\|\|(\S)", r"\1 || \2"),
            ("??", r"(\S)\?\?(\S)", r"\1 ?? \2"),
            ("=>", r"(\S)=>(\S)", r"\1 => \2"),
        ]

        for _, pattern, replacement in operators:
            content = re.sub(pattern, replacement, content)

        # Handle single = but not ==, !=, <=, >=, +=, etc.
        # Only if it's clearly an assignment (not in generics, attributes, etc.)
        if "=" in content and not any(op in content for op in ["==", "!=", "<=", ">=", "+=", "-=", "*=", "/=", "=>"]):
            # Simple assignment spacing
            content = re.sub(r"(\w)=(\w)", r"\1 = \2", content)

        return content

    def _format_commas_in_line(self, content: str) -> str:
        """Ensure space after commas."""
        # Add space after comma if not followed by space
        content = re.sub(r",(\S)", r", \1", content)
        # Remove space before comma
        content = re.sub(r"\s+,", ",", content)
        return content

    def _format_inheritance_colon(self, content: str) -> str:
        """Format colons in class inheritance."""
        # class Foo:Bar -> class Foo : Bar
        if any(kw in content for kw in ["class ", "interface ", "struct "]):
            # Match word:word pattern after class/interface/struct name
            content = re.sub(r"(\w):(\w)", r"\1 : \2", content)
        return content

    def _remove_space_before_semicolon(self, content: str) -> str:
        """Remove space before semicolon."""
        return re.sub(r"\s+;", ";", content)

    def _format_braces_allman(self, code: str) -> str:
        """Convert K&R braces to Allman style."""
        lines = code.split("\n")
        result = []

        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            indent = len(line) - len(line.lstrip())
            indent_str = " " * indent

            # Check for K&R style: something { at end of line (not just "{")
            if stripped.endswith(" {") and stripped != "{" and not stripped.endswith("= {"):
                # Skip inline initializers like `new List<int> {` or lambda `=> {`
                if " = new " in stripped or "=> {" in stripped or "= new(" in stripped:
                    result.append(line)
                    i += 1
                    continue

                # Skip attribute syntax
                if stripped.startswith("["):
                    result.append(line)
                    i += 1
                    continue

                # Move brace to next line
                content = stripped[:-2].rstrip()  # Remove " {"
                if content:
                    result.append(indent_str + content)
                    result.append(indent_str + "{")
                else:
                    result.append(line)
            else:
                result.append(line)

            i += 1

        return "\n".join(result)

    def _ensure_blank_lines_between_members(self, code: str) -> str:
        """Ensure blank lines between class members."""
        lines = code.split("\n")
        if len(lines) < 3:
            return code

        result = [lines[0]]

        for i in range(1, len(lines)):
            prev_line = lines[i - 1].strip()
            curr_line = lines[i].strip()

            # Add blank line after } if next line is a member declaration
            if prev_line == "}" and curr_line:
                member_keywords = ["public ", "private ", "protected ", "internal ", "static ", "void ", "async "]
                if any(curr_line.startswith(kw) for kw in member_keywords):
                    # Check if there's already a blank line
                    if result and result[-1].strip() != "":
                        result.append("")

            result.append(lines[i])

        return "\n".join(result)


def format_markdown_file(file: Path, dry_run: bool = False) -> Tuple[bool, int]:
    """Format all C# code blocks in a markdown file.

    Returns (was_modified, number_of_blocks_formatted).
    """
    content = file.read_text(encoding="utf-8")
    original_content = content
    blocks = extract_csharp_blocks(file)

    if not blocks:
        return False, 0

    formatter = CSharpFormatter()
    formatted_count = 0

    # Process blocks in reverse order to maintain line numbers
    for block in reversed(blocks):
        formatted = formatter.format_code(block.content)

        if formatted != block.content:
            formatted_count += 1

            # Replace in content
            lines = content.split("\n")
            # block.line_start is 1-indexed, points to the ```csharp line
            # block.line_end is 1-indexed, points to the closing ``` line

            new_lines = (
                lines[: block.line_start]  # Up to and including opening ```csharp
                + [formatted]
                + lines[block.line_end - 1 :]  # From closing ``` onwards
            )
            content = "\n".join(new_lines)

    if content != original_content:
        if not dry_run:
            file.write_text(content, encoding="utf-8")
        return True, formatted_count

    return False, formatted_count


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Format C# code blocks in markdown files"
    )
    parser.add_argument(
        "paths",
        nargs="*",
        default=["."],
        help="Markdown files or directories to format",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without modifying files",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show detailed output"
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    files_modified = 0
    blocks_formatted = 0

    paths_to_process: List[Path] = []

    for path_str in args.paths:
        path = Path(path_str)
        if path.is_file():
            if path.suffix.lower() in {".md", ".markdown", ".mdx"}:
                paths_to_process.append(path)
        elif path.is_dir():
            paths_to_process.extend(path.rglob("*.md"))
            paths_to_process.extend(path.rglob("*.markdown"))
            paths_to_process.extend(path.rglob("*.mdx"))

    for file in sorted(set(paths_to_process)):
        try:
            modified, count = format_markdown_file(file, dry_run=args.dry_run)
            if modified:
                files_modified += 1
                blocks_formatted += count
                if args.verbose:
                    action = "Would format" if args.dry_run else "Formatted"
                    print(f"{action}: {file} ({count} blocks)")
        except Exception as e:
            print(f"Error processing {file}: {e}")

    action = "Would modify" if args.dry_run else "Modified"
    print(f"\n{action} {files_modified} files ({blocks_formatted} code blocks)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
