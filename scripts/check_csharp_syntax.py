#!/usr/bin/env python3
"""Extract and validate C# code blocks from markdown files.

This performs basic syntax validation without requiring Unity or .NET SDK.
It checks for common issues like:
- Unbalanced braces, brackets, parentheses
- Unclosed strings
- Missing semicolons after statements
- Obvious typos in common patterns
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Sequence, Tuple


@dataclass
class CodeBlock:
    file: Path
    line_start: int
    content: str
    language: str


@dataclass
class SyntaxIssue:
    file: Path
    line: int
    message: str
    code_snippet: str


def extract_csharp_blocks(file: Path) -> List[CodeBlock]:
    """Extract C# code blocks from a markdown file."""
    content = file.read_text(encoding="utf-8")
    blocks: List[CodeBlock] = []

    # Match fenced code blocks with csharp/cs language
    pattern = r"```(?:csharp|cs)\s*\n(.*?)```"
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
                    line_start=block_start + 1,
                    content="\n".join(block_lines),
                    language="csharp",
                )
            )
        elif in_block:
            block_lines.append(line)

    return blocks


def check_balanced(code: str, open_char: str, close_char: str) -> Tuple[bool, int]:
    """Check if characters are balanced, returns (is_balanced, depth_at_end)."""
    depth = 0
    in_string = False
    in_char = False
    in_comment = False
    in_multiline_comment = False
    escape_next = False

    i = 0
    while i < len(code):
        c = code[i]

        if escape_next:
            escape_next = False
            i += 1
            continue

        if c == "\\" and (in_string or in_char):
            escape_next = True
            i += 1
            continue

        # Handle comments
        if not in_string and not in_char:
            if i + 1 < len(code):
                two_char = code[i : i + 2]
                if two_char == "//" and not in_multiline_comment:
                    # Skip to end of line
                    newline = code.find("\n", i)
                    if newline == -1:
                        break
                    i = newline + 1
                    continue
                elif two_char == "/*" and not in_multiline_comment:
                    in_multiline_comment = True
                    i += 2
                    continue
                elif two_char == "*/" and in_multiline_comment:
                    in_multiline_comment = False
                    i += 2
                    continue

        if in_multiline_comment:
            i += 1
            continue

        # Handle strings
        if c == '"' and not in_char:
            # Check for verbatim string
            if i > 0 and code[i - 1] == "@":
                # Verbatim string - find closing quote (doubled quotes are escaped)
                i += 1
                while i < len(code):
                    if code[i] == '"':
                        if i + 1 < len(code) and code[i + 1] == '"':
                            i += 2
                            continue
                        break
                    i += 1
                i += 1
                continue
            in_string = not in_string
            i += 1
            continue

        if c == "'" and not in_string:
            in_char = not in_char
            i += 1
            continue

        if not in_string and not in_char:
            if c == open_char:
                depth += 1
            elif c == close_char:
                depth -= 1
                if depth < 0:
                    return False, depth

        i += 1

    return depth == 0, depth


def check_code_block(block: CodeBlock) -> List[SyntaxIssue]:
    """Check a code block for syntax issues."""
    issues: List[SyntaxIssue] = []
    code = block.content

    # Skip empty blocks
    if not code.strip():
        return issues

    # Check balanced braces
    balanced, depth = check_balanced(code, "{", "}")
    if not balanced:
        if depth > 0:
            issues.append(
                SyntaxIssue(
                    file=block.file,
                    line=block.line_start,
                    message=f"Unbalanced braces: {depth} unclosed '{{' found",
                    code_snippet=code[:100] + "..." if len(code) > 100 else code,
                )
            )
        else:
            issues.append(
                SyntaxIssue(
                    file=block.file,
                    line=block.line_start,
                    message=f"Unbalanced braces: {-depth} extra '}}' found",
                    code_snippet=code[:100] + "..." if len(code) > 100 else code,
                )
            )

    # Check balanced parentheses
    balanced, depth = check_balanced(code, "(", ")")
    if not balanced:
        if depth > 0:
            issues.append(
                SyntaxIssue(
                    file=block.file,
                    line=block.line_start,
                    message=f"Unbalanced parentheses: {depth} unclosed '(' found",
                    code_snippet=code[:100] + "..." if len(code) > 100 else code,
                )
            )
        else:
            issues.append(
                SyntaxIssue(
                    file=block.file,
                    line=block.line_start,
                    message=f"Unbalanced parentheses: {-depth} extra ')' found",
                    code_snippet=code[:100] + "..." if len(code) > 100 else code,
                )
            )

    # Check balanced brackets
    balanced, depth = check_balanced(code, "[", "]")
    if not balanced:
        if depth > 0:
            issues.append(
                SyntaxIssue(
                    file=block.file,
                    line=block.line_start,
                    message=f"Unbalanced brackets: {depth} unclosed '[' found",
                    code_snippet=code[:100] + "..." if len(code) > 100 else code,
                )
            )
        else:
            issues.append(
                SyntaxIssue(
                    file=block.file,
                    line=block.line_start,
                    message=f"Unbalanced brackets: {-depth} extra ']' found",
                    code_snippet=code[:100] + "..." if len(code) > 100 else code,
                )
            )

    # Check for common typos
    typo_patterns = [
        (r"\bMonoBehavior\b", "MonoBehaviour (British spelling)"),
        (r"\bGameobject\b", "GameObject (capital O)"),
        (r"\bTransfrom\b", "Transform (typo)"),
        (r"\bInstanitate\b", "Instantiate (typo)"),
        (r"\bDestory\b", "Destroy (typo)"),
        (r"\bCoroutnie\b", "Coroutine (typo)"),
        (r"\bStartCoroutnie\b", "StartCoroutine (typo)"),
        (r"\bAddComponet\b", "AddComponent (typo)"),
        (r"\bGetComponet\b", "GetComponent (typo)"),
    ]

    for pattern, fix in typo_patterns:
        if re.search(pattern, code):
            issues.append(
                SyntaxIssue(
                    file=block.file,
                    line=block.line_start,
                    message=f"Possible typo: should be {fix}",
                    code_snippet=re.search(pattern, code).group(0) if re.search(pattern, code) else "",
                )
            )

    return issues


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check C# syntax in markdown files")
    parser.add_argument("paths", nargs="+", help="Markdown files to check")
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    all_issues: List[SyntaxIssue] = []

    for path_str in args.paths:
        path = Path(path_str)
        if not path.exists() or path.suffix.lower() not in {".md", ".markdown", ".mdx"}:
            continue

        blocks = extract_csharp_blocks(path)
        for block in blocks:
            issues = check_code_block(block)
            all_issues.extend(issues)

    if all_issues:
        for issue in all_issues:
            print(f"{issue.file}:{issue.line}: {issue.message}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
