#!/usr/bin/env python3
"""Format C# code blocks in markdown files using CSharpier-style formatting.

This script extracts C# code blocks from markdown files and applies CSharpier-like
formatting rules:
- Allman-style braces (opening brace on its own line)
- 4 spaces indentation
- Spaces around operators (outside of string literals)
- Space after keywords (if, for, while, etc.)
- Space after commas (outside of string literals)
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


class StringLiteralMasker:
    """Masks string literals to prevent formatting inside them."""

    def __init__(self):
        self.literals: List[str] = []
        # Use a unique placeholder that won't appear in real C# code
        self.placeholder_prefix = "\x00\x01STRLIT"
        self.placeholder_suffix = "\x01\x00"

    def mask(self, content: str) -> str:
        """Replace string literals with placeholders."""
        self.literals = []
        result = []
        i = 0

        while i < len(content):
            # Check for verbatim interpolated string $@"..." or @$"..."
            if i < len(content) - 2 and (
                (content[i] == "$" and content[i + 1] == "@" and content[i + 2] == '"')
                or (
                    content[i] == "@"
                    and content[i + 1] == "$"
                    and content[i + 2] == '"'
                )
            ):
                start = i
                i += 3  # Skip $@" or @$"
                brace_depth = 0
                while i < len(content):
                    if content[i] == "{":
                        if i + 1 < len(content) and content[i + 1] == "{":
                            i += 2  # Escaped brace
                            continue
                        brace_depth += 1
                    elif content[i] == "}":
                        if i + 1 < len(content) and content[i + 1] == "}":
                            i += 2  # Escaped brace
                            continue
                        brace_depth -= 1
                    elif content[i] == '"' and brace_depth == 0:
                        # Check for escaped quote "" in verbatim string
                        if i + 1 < len(content) and content[i + 1] == '"':
                            i += 2
                            continue
                        i += 1  # Include closing quote
                        break
                    i += 1
                literal = content[start:i]
                placeholder = f"{self.placeholder_prefix}{len(self.literals)}{self.placeholder_suffix}"
                self.literals.append(literal)
                result.append(placeholder)
                continue

            # Check for verbatim string @"..."
            if i < len(content) - 1 and content[i] == "@" and content[i + 1] == '"':
                start = i
                i += 2  # Skip @"
                while i < len(content):
                    if content[i] == '"':
                        # Check for escaped quote ""
                        if i + 1 < len(content) and content[i + 1] == '"':
                            i += 2
                            continue
                        i += 1  # Include closing quote
                        break
                    i += 1
                literal = content[start:i]
                placeholder = f"{self.placeholder_prefix}{len(self.literals)}{self.placeholder_suffix}"
                self.literals.append(literal)
                result.append(placeholder)
                continue

            # Check for interpolated string $"..."
            if i < len(content) - 1 and content[i] == "$" and content[i + 1] == '"':
                start = i
                i += 2  # Skip $"
                brace_depth = 0
                while i < len(content):
                    if content[i] == "{":
                        if i + 1 < len(content) and content[i + 1] == "{":
                            i += 2  # Escaped brace
                            continue
                        brace_depth += 1
                    elif content[i] == "}":
                        if i + 1 < len(content) and content[i + 1] == "}":
                            i += 2  # Escaped brace
                            continue
                        brace_depth -= 1
                    elif content[i] == '"' and brace_depth == 0:
                        i += 1  # Include closing quote
                        break
                    elif content[i] == "\\" and i + 1 < len(content):
                        i += 2  # Skip escaped char
                        continue
                    i += 1
                literal = content[start:i]
                placeholder = f"{self.placeholder_prefix}{len(self.literals)}{self.placeholder_suffix}"
                self.literals.append(literal)
                result.append(placeholder)
                continue

            # Check for regular string "..."
            if content[i] == '"':
                start = i
                i += 1  # Skip opening quote
                while i < len(content):
                    if content[i] == '"':
                        i += 1  # Include closing quote
                        break
                    elif content[i] == "\\" and i + 1 < len(content):
                        i += 2  # Skip escaped char
                        continue
                    i += 1
                literal = content[start:i]
                placeholder = f"{self.placeholder_prefix}{len(self.literals)}{self.placeholder_suffix}"
                self.literals.append(literal)
                result.append(placeholder)
                continue

            # Check for character literal '.'
            if content[i] == "'":
                start = i
                i += 1
                if i < len(content) and content[i] == "\\":
                    i += 2  # Skip escaped char
                elif i < len(content):
                    i += 1  # Skip char
                if i < len(content) and content[i] == "'":
                    i += 1  # Include closing quote
                literal = content[start:i]
                placeholder = f"{self.placeholder_prefix}{len(self.literals)}{self.placeholder_suffix}"
                self.literals.append(literal)
                result.append(placeholder)
                continue

            result.append(content[i])
            i += 1

        return "".join(result)

    def unmask(self, content: str) -> str:
        """Restore string literals from placeholders."""
        for idx, literal in enumerate(self.literals):
            placeholder = f"{self.placeholder_prefix}{idx}{self.placeholder_suffix}"
            content = content.replace(placeholder, literal)
        return content


class CSharpFormatter:
    """A simplified CSharpier-like formatter for C# code."""

    # Keywords that should have space after them before (
    # Note: nameof, typeof, sizeof, default do NOT get spaces in C#
    KEYWORDS_WITH_SPACE = {
        "if",
        "for",
        "foreach",
        "while",
        "do",
        "switch",
        "catch",
        "using",
        "lock",
        "fixed",
        "checked",
        "unchecked",
    }

    def __init__(self):
        self.indent_size = 4
        self.masker = StringLiteralMasker()

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
        if (
            content.startswith("//")
            or content.startswith("/*")
            or content.startswith("*")
        ):
            return line

        # Mask string literals before formatting
        self.masker = StringLiteralMasker()
        masked_content = self.masker.mask(content)

        # Apply formatting transformations on masked content
        masked_content = self._format_keywords_in_line(masked_content)
        masked_content = self._format_operators_in_line(masked_content)
        masked_content = self._format_commas_in_line(masked_content)
        masked_content = self._format_inheritance_colon(masked_content)
        masked_content = self._remove_space_before_semicolon(masked_content)

        # Restore string literals
        content = self.masker.unmask(masked_content)

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
        """Add spaces around assignment, comparison, and arithmetic operators."""
        # Add spaces around compound and comparison operators first (before single-char ops)
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
        if "=" in content and not any(
            op in content
            for op in ["==", "!=", "<=", ">=", "+=", "-=", "*=", "/=", "=>"]
        ):
            # Simple assignment spacing - word followed by = followed by non-space
            # This handles both `x=5` and `s="hello"` (masked as `s=\x00STR0\x00`)
            content = re.sub(r"(\w)=([^\s=])", r"\1 = \2", content)

        # Handle binary arithmetic operators (+, -, *, /)
        # Only when surrounded by word characters to avoid unary operators
        # e.g., "a+b" -> "a + b" but "-5" stays as "-5"
        content = re.sub(r"(\w)\+(\w)", r"\1 + \2", content)
        content = re.sub(r"(\w)-(\w)", r"\1 - \2", content)
        content = re.sub(r"(\w)\*(\w)", r"\1 * \2", content)
        content = re.sub(r"(\w)/(\w)", r"\1 / \2", content)
        content = re.sub(r"(\w)%(\w)", r"\1 % \2", content)

        return content

    def _format_commas_in_line(self, content: str) -> str:
        """Ensure space after commas in code (not in strings - those are masked)."""
        # Add space after comma if not followed by space
        content = re.sub(r",(\S)", r", \1", content)
        # Remove space before comma
        content = re.sub(r"\s+,", ",", content)
        return content

    def _split_code_and_comment(self, content: str) -> Tuple[str, str]:
        """Split a line into code and comment parts.

        Returns (code_part, comment_part) where comment_part includes the //.
        """
        # Find // that's not inside a string (strings are already masked)
        idx = content.find("//")
        if idx == -1:
            return content, ""
        return content[:idx], content[idx:]

    def _format_inheritance_colon(self, content: str) -> str:
        """Format colons in class/interface/struct inheritance declarations only.

        This is intentionally conservative to avoid breaking:
        - Case labels (case 1:)
        - Ternary operators (a ? b : c)
        - Dictionary initializers (["key"]: value)
        - Generic constraints (where T : class)
        - Comments (// Step 1: Do something)
        """
        # Split into code and comment parts - don't format comments
        code_part, comment_part = self._split_code_and_comment(content)

        # Only format if line contains a type declaration keyword
        # Match patterns like: class Foo:Bar, class Foo<T>:Bar<T>, struct Foo:IFoo
        if re.match(
            r"^\s*(public\s+|private\s+|internal\s+|protected\s+|abstract\s+|"
            r"sealed\s+|static\s+|partial\s+|readonly\s+)*"
            r"(class|interface|struct|record)\s+\w+",
            code_part,
        ):
            # Match TypeName:BaseType or TypeName<T>:BaseType<T> pattern
            # Handle generic types in both the class name and base type
            code_part = re.sub(
                r"(\w+(?:<[^>]+>)?)\s*:\s*(\w+)",
                r"\1 : \2",
                code_part,
            )
        return code_part + comment_part

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

            # Skip comment lines entirely
            if stripped.startswith("//") or stripped.startswith("/*"):
                result.append(line)
                i += 1
                continue

            # Check for } else or } else if patterns FIRST (before general { check)
            # This handles: } else {, } else if (x) {, } else, etc.
            if re.match(r"^\}\s*(else|else\s+if)", stripped):
                # Split into } and else/else if parts
                match = re.match(
                    r"^(\})\s*(else\s+if\s*\(.*\)|else\s+if.*|else)\s*(\{)?$", stripped
                )
                if match:
                    result.append(indent_str + "}")
                    else_part = match.group(2)
                    has_brace = match.group(3) == "{"
                    result.append(indent_str + else_part)
                    if has_brace:
                        result.append(indent_str + "{")
                else:
                    # Fallback: just append as-is if regex doesn't match expected pattern
                    result.append(line)
                i += 1
                continue

            # Check for K&R style: something { at end of line (not just "{")
            if (
                stripped.endswith(" {")
                and stripped != "{"
                and not stripped.endswith("= {")
            ):
                # Skip inline initializers and collection expressions
                skip_patterns = [
                    " = new ",  # Object initializer: var x = new Foo {
                    "=> {",  # Lambda with block body
                    "= new(",  # Target-typed new
                    "new[] {",  # Array initializer
                    "new[",  # Array initializer
                    "new {",  # Anonymous type
                    "new() {",  # Target-typed new with initializer
                    "with {",  # With expressions (C# 9+)
                    "] {",  # After indexer
                    "return new ",  # Return new object
                ]
                if any(pattern in stripped for pattern in skip_patterns):
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
                member_keywords = [
                    "public ",
                    "private ",
                    "protected ",
                    "internal ",
                    "static ",
                    "void ",
                    "async ",
                ]
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
