#!/usr/bin/env python3
"""Ensure Markdown links use human-readable link text."""

from __future__ import annotations

import argparse
import os
import re
from pathlib import Path
from typing import List, Optional, Sequence, Tuple
from urllib.parse import urlparse

from link_utils import LinkMatch, extract_links, split_anchor

COMMON_TLDS = {
    "com",
    "org",
    "net",
    "io",
    "dev",
    "app",
    "edu",
    "gov",
    "co",
    "uk",
    "au",
    "ca",
    "us",
}


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Markdown link text")
    parser.add_argument("paths", nargs="+", help="Markdown files to check")
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Automatically rewrite non-readable link text",
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    total_issues = 0

    for path_str in args.paths:
        path = Path(path_str)
        if not path.exists() or path.suffix.lower() not in {".md", ".markdown", ".mdx"}:
            continue
        text = path.read_text(encoding="utf-8")
        matches = extract_links(text)
        issues: List[LinkMatch] = []
        modifications: List[Tuple[int, int, str]] = []

        for match in matches:
            if not should_check(match.href):
                continue
            if is_human_readable(match.text, match.href):
                continue
            if args.fix:
                suggestion = suggest_text(path, match.href)
                if suggestion:
                    replacement = build_replacement(match, suggestion)
                    if replacement:
                        modifications.append((match.start, match.end, replacement))
                        continue
            issues.append(match)

        if args.fix and modifications:
            text = apply_modifications(text, modifications)
            path.write_text(text, encoding="utf-8")

        for issue in issues:
            print(
                f"{path}:{issue.line}:{issue.column}: Link text is not human-readable ({issue.href})"
            )
        total_issues += len(issues)

    return 1 if total_issues else 0


def should_check(href: str) -> bool:
    parsed = urlparse(href)
    if parsed.scheme in {"http", "https", ""}:
        return True
    if href.startswith("#"):
        return True
    return False


def is_human_readable(text: str, href: str) -> bool:
    stripped = text.strip()
    if not stripped:
        return False
    if stripped.lower().startswith("http://") or stripped.lower().startswith("https://"):
        return False
    if stripped.lower() == href.strip().lower():
        return False
    if not re.search(r"[a-zA-Z]", stripped):
        return False
    parsed = urlparse(href)
    domain = parsed.netloc.lower()
    if domain and stripped.lower() == domain:
        return False
    return True


def suggest_text(base_path: Path, href: str) -> Optional[str]:
    parsed = urlparse(href)
    if parsed.scheme in {"http", "https"}:
        return humanize_url(parsed)
    if href.startswith("#"):
        return humanize_anchor(href[1:])
    target_path, anchor = split_anchor(href)
    if not target_path:
        return humanize_anchor(anchor) if anchor else None
    candidate = (base_path.parent / target_path).resolve()
    if candidate.is_file():
        text = humanize_file_name(candidate.name)
    else:
        text = humanize_file_name(Path(target_path).name)
    if anchor:
        anchor_text = humanize_anchor(anchor)
        if anchor_text:
            text = f"{text} — {anchor_text}" if text else anchor_text
    return text


def humanize_url(parsed) -> str:
    domain_parts = [part for part in parsed.netloc.split(".") if part and part != "www"]
    if domain_parts and domain_parts[-1] in COMMON_TLDS:
        domain_parts = domain_parts[:-1]
    domain_label = " ".join(part.replace("-", " ").title() for part in domain_parts)
    path_segments = [seg for seg in parsed.path.strip("/").split("/") if seg]
    last_segment = path_segments[-1] if path_segments else ""
    last_segment = os.path.splitext(last_segment)[0]
    path_label = last_segment.replace("-", " ").replace("_", " ").title()
    parts = [value for value in (domain_label, path_label) if value]
    if not parts:
        parts.append(parsed.netloc)
    return " — ".join(dict.fromkeys(parts))


def humanize_anchor(anchor: str) -> str:
    cleaned = anchor.replace("-", " ").replace("_", " ")
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip().title()


def humanize_file_name(name: str) -> str:
    stem = os.path.splitext(name)[0]
    stem = re.sub(r"^\d+[-_]?", "", stem)
    stem = stem.replace("-", " ").replace("_", " ")
    return stem.strip().title()


def build_replacement(match: LinkMatch, new_text: str) -> Optional[str]:
    new_text = new_text.strip()
    if not new_text:
        return None
    if match.kind == "inline":
        return f"[{new_text}]{match.separator}({match.dest_content})"
    if match.kind in {"autolink", "bare"}:
        return f"[{new_text}]({match.href})"
    return None


def apply_modifications(text: str, modifications: Sequence[Tuple[int, int, str]]) -> str:
    chunks: List[str] = []
    last_index = 0
    for start, end, replacement in sorted(modifications, key=lambda m: m[0]):
        chunks.append(text[last_index:start])
        chunks.append(replacement)
        last_index = end
    chunks.append(text[last_index:])
    return "".join(chunks)


if __name__ == "__main__":
    raise SystemExit(main())
