"""Shared helper utilities for Markdown link processing."""

from __future__ import annotations

import re
from bisect import bisect_right
from dataclasses import dataclass
from typing import Iterable, List, Sequence, Tuple
from urllib.parse import unquote

# =============================================================================
# Shared Constants
# =============================================================================

# Critical wiki pages that MUST exist (these have historically caused issues)
CRITICAL_PAGES = ["Best-Practices", "Development-Tooling", "Home", "_Sidebar"]

# Minimum content length for a page to be considered non-trivial (in characters)
MIN_PAGE_CONTENT_LENGTH = 100

# Maximum lengths for display truncation
MAX_DISPLAY_LINE_LENGTH = 60  # For verbose output of code block first lines
MAX_LINK_TEXT_LENGTH = 40  # For truncating link text in warnings
MAX_URL_LENGTH = 50  # For truncating URLs in warnings

# =============================================================================
# Data Classes
# =============================================================================


@dataclass
class LinkMatch:
    kind: str  # inline | autolink | bare
    start: int
    end: int
    text: str
    href: str
    line: int
    column: int
    segment: str
    separator: str = ""
    dest_content: str = ""


@dataclass
class InlineLink:
    start: int
    end: int
    text: str
    href: str
    separator: str
    dest_content: str
    segment: str


def extract_links(text: str) -> List[LinkMatch]:
    matches: List[LinkMatch] = []
    code_ranges = find_code_fence_ranges(text)
    inline_code_ranges = find_inline_code_ranges(text)
    html_tag_ranges = find_html_tag_ranges(text)
    # Skip code blocks, inline code, and HTML tags when detecting links
    skip_ranges = code_ranges + inline_code_ranges + html_tag_ranges
    line_offsets = build_line_offsets(text)

    for inline in find_inline_links(text):
        if in_ranges(inline.start, skip_ranges):
            continue
        line, column = index_to_line_column(line_offsets, inline.start)
        matches.append(
            LinkMatch(
                kind="inline",
                start=inline.start,
                end=inline.end,
                text=inline.text,
                href=inline.href,
                line=line,
                column=column,
                segment=inline.segment,
                separator=inline.separator,
                dest_content=inline.dest_content,
            )
        )

    used_ranges = [(m.start, m.end) for m in matches]

    for autolink_match in re.finditer(r"<(https?://[^>\s]+)>", text):
        start, end = autolink_match.span()
        if in_ranges(start, skip_ranges) or overlaps_any(start, end, used_ranges):
            continue
        href = autolink_match.group(1)
        line, column = index_to_line_column(line_offsets, start)
        matches.append(
            LinkMatch(
                kind="autolink",
                start=start,
                end=end,
                text=href,
                href=href,
                line=line,
                column=column,
                segment=text[start:end],
            )
        )
        used_ranges.append((start, end))

    bare_pattern = re.compile(r'https?://[^\s)<>"\']+')
    for bare in bare_pattern.finditer(text):
        start, end = bare.span()
        if in_ranges(start, skip_ranges) or overlaps_any(start, end, used_ranges):
            continue
        href = bare.group(0)
        trailing = ""
        while href and href[-1] in ".,;:!?":
            trailing = href[-1] + trailing
            href = href[:-1]
            end -= 1
        if not href:
            continue
        line, column = index_to_line_column(line_offsets, start)
        matches.append(
            LinkMatch(
                kind="bare",
                start=start,
                end=end,
                text=href,
                href=href,
                line=line,
                column=column,
                segment=text[start:end],
                separator=trailing,
            )
        )
        used_ranges.append((start, end))
    return sorted(matches, key=lambda m: m.start)


def find_inline_links(text: str) -> Iterable[InlineLink]:
    idx = 0
    length = len(text)
    while idx < length:
        char = text[idx]
        if char != "[":
            idx += 1
            continue
        if idx > 0 and text[idx - 1] == "!":
            idx += 1
            continue
        close = find_closing(text, idx, "[", "]")
        if close == -1:
            idx += 1
            continue
        j = close + 1
        sep_chars: List[str] = []
        while j < length and text[j].isspace():
            sep_chars.append(text[j])
            j += 1
        if j >= length or text[j] != "(":
            idx = close + 1
            continue
        dest_end = find_closing(text, j, "(", ")")
        if dest_end == -1:
            idx = close + 1
            continue
        dest_content = text[j + 1 : dest_end]
        href = extract_href(dest_content)
        if not href:
            idx = dest_end + 1
            continue
        segment = text[idx : dest_end + 1]
        link_text = text[idx + 1 : close]
        yield InlineLink(
            start=idx,
            end=dest_end + 1,
            text=link_text,
            href=href,
            separator="".join(sep_chars),
            dest_content=dest_content,
            segment=segment,
        )
        idx = dest_end + 1


def find_closing(text: str, start: int, opener: str, closer: str) -> int:
    depth = 0
    i = start
    while i < len(text):
        current = text[i]
        if current == "\\":
            i += 2
            continue
        if current == opener:
            depth += 1
        elif current == closer:
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return -1


def extract_href(dest_content: str) -> str:
    content = dest_content.strip()
    if not content:
        return ""
    if content.startswith("<") and ">" in content:
        closing = content.find(">")
        href = content[1:closing]
        return href.strip()
    parts = content.split()
    if not parts:
        return ""
    return parts[0]


def build_line_offsets(text: str) -> List[int]:
    offsets = [0]
    total = 0
    for line in text.splitlines(keepends=True):
        total += len(line)
        offsets.append(total)
    return offsets


def index_to_line_column(offsets: Sequence[int], index: int) -> Tuple[int, int]:
    line = bisect_right(offsets, index) - 1
    column = index - offsets[line] + 1
    return line + 1, column


def find_html_tag_ranges(text: str) -> List[Tuple[int, int]]:
    """Find ranges of HTML tags to skip when looking for bare URLs.

    This prevents URLs inside HTML attributes (like href="..." or src="...")
    from being treated as bare markdown links.
    """
    ranges: List[Tuple[int, int]] = []
    # Match HTML tags including their attributes
    # This handles <a href="...">...</a>, <img src="...">, etc.
    tag_pattern = re.compile(r"<[a-zA-Z][^>]*>")
    for match in tag_pattern.finditer(text):
        ranges.append((match.start(), match.end()))
    return ranges


def find_code_fence_ranges(text: str) -> List[Tuple[int, int]]:
    ranges: List[Tuple[int, int]] = []
    fence_pattern = re.compile(r"^\s*(```+|~~~+)")
    in_fence = False
    fence_char = ""
    fence_start = 0
    offset = 0

    for line in text.splitlines(keepends=True):
        if not in_fence:
            if fence_pattern.match(line):
                in_fence = True
                fence_char = line.strip()[0]
                fence_start = offset
        else:
            if line.strip().startswith(fence_char * 3):
                ranges.append((fence_start, offset + len(line)))
                in_fence = False
        offset += len(line)
    if in_fence:
        ranges.append((fence_start, len(text)))
    return ranges


def find_inline_code_ranges(text: str) -> List[Tuple[int, int]]:
    ranges: List[Tuple[int, int]] = []
    i = 0
    length = len(text)
    while i < length:
        if text[i] != "`":
            i += 1
            continue
        run = 1
        while i + run < length and text[i + run] == "`":
            run += 1
        # Treat runs of three or more as potential fences handled elsewhere.
        if run >= 3:
            i += run
            continue
        j = i + run
        while j < length:
            if text[j] != "`":
                j += 1
                continue
            close_run = 1
            while j + close_run < length and text[j + close_run] == "`":
                close_run += 1
            if close_run == run:
                ranges.append((i, j + close_run))
                i = j + close_run
                break
            j += close_run
        else:
            i += run
    return ranges


def in_ranges(index: int, ranges: Iterable[Tuple[int, int]]) -> bool:
    for start, end in ranges:
        if start <= index < end:
            return True
    return False


def overlaps_any(start: int, end: int, ranges: Iterable[Tuple[int, int]]) -> bool:
    for r_start, r_end in ranges:
        if start < r_end and end > r_start:
            return True
    return False


def split_anchor(href: str) -> Tuple[str, str | None]:
    """Split a URL into path and anchor parts, URL-decoding both.

    Args:
        href: The URL/path to split (e.g., "path/to/file.md#section")

    Returns:
        Tuple of (path, anchor) where anchor is None if not present.
        Both path and anchor are URL-decoded.
    """
    if "#" not in href:
        return unquote(href), None
    path, anchor = href.split("#", 1)
    return unquote(path), unquote(anchor)
