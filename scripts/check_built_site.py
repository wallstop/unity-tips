#!/usr/bin/env python3
"""Validate links in a built MkDocs site.

This script validates the generated HTML site to ensure all internal links resolve.
Run this after `mkdocs build` to catch broken links before deployment.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Set, Tuple
from urllib.parse import unquote, urljoin, urlparse
from html.parser import HTMLParser


@dataclass
class LinkIssue:
    """Represents a broken link in the built site."""

    source_file: Path
    href: str
    issue_type: str
    message: str

    def __str__(self) -> str:
        return f"{self.source_file}: [{self.issue_type}] {self.message} ({self.href})"


class LinkExtractor(HTMLParser):
    """Extract links from HTML files."""

    def __init__(self) -> None:
        super().__init__()
        self.links: List[str] = []

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        if tag == "a":
            for name, value in attrs:
                if name == "href" and value:
                    self.links.append(value)


def extract_html_links(content: str) -> List[str]:
    """Extract all href links from HTML content."""
    parser = LinkExtractor()
    try:
        parser.feed(content)
    except Exception:
        pass
    return parser.links


def build_site_index(site_dir: Path) -> Set[str]:
    """Build an index of all available paths in the site.

    Returns a set of normalized paths that exist in the site.
    """
    index: Set[str] = set()

    for path in site_dir.rglob("*"):
        if path.is_file():
            # Get relative path from site root
            rel_path = path.relative_to(site_dir)
            path_str = "/" + str(rel_path).replace("\\", "/")
            index.add(path_str)

            # For index.html, also add the directory path
            if path.name == "index.html":
                dir_path = "/" + str(rel_path.parent).replace("\\", "/")
                if dir_path != "/.":
                    index.add(dir_path)
                    index.add(dir_path + "/")
                else:
                    index.add("/")

    return index


def normalize_path(href: str, source_path: str) -> str:
    """Normalize a relative path to an absolute site path."""
    # Remove anchor
    href = href.split("#")[0]
    if not href:
        return ""

    # Already absolute
    if href.startswith("/"):
        return href

    # Relative path - resolve against source
    source_dir = "/".join(source_path.split("/")[:-1])
    if source_dir:
        combined = f"{source_dir}/{href}"
    else:
        combined = href

    # Normalize path (handle ../ and ./)
    parts: List[str] = []
    for part in combined.split("/"):
        if part == "..":
            if parts:
                parts.pop()
        elif part and part != ".":
            parts.append(part)

    return "/" + "/".join(parts)


def check_internal_link(
    href: str, source_path: str, site_index: Set[str], site_url_path: str = ""
) -> Optional[str]:
    """Check if an internal link resolves.

    Returns error message if broken, None if OK.

    Args:
        href: The href attribute from the link
        source_path: Path to the source HTML file
        site_index: Set of all available paths in the site
        site_url_path: The site URL path prefix (e.g., "/unity-tips")
    """
    # Skip external links and special protocols
    if href.startswith(("http://", "https://", "mailto:", "tel:", "javascript:")):
        return None

    # Skip pure anchors
    if href.startswith("#"):
        return None

    # Handle site_url prefix in links (e.g., /unity-tips/path -> /path)
    if site_url_path and href.startswith(site_url_path):
        href = href[len(site_url_path) :]
        if not href:
            href = "/"
        elif not href.startswith("/"):
            href = "/" + href

    # Normalize the path
    target = normalize_path(href, source_path)
    if not target:
        return None

    # Check if target exists
    target_decoded = unquote(target)

    # Try exact match
    if target_decoded in site_index:
        return None

    # Try with trailing slash
    if f"{target_decoded}/" in site_index:
        return None

    # Try with /index.html
    if f"{target_decoded}/index.html" in site_index:
        return None

    # Try removing trailing slash
    if target_decoded.endswith("/") and target_decoded[:-1] in site_index:
        return None

    # Handle .md extension - MkDocs converts foo.md to foo/index.html
    if target_decoded.endswith(".md"):
        base_path = target_decoded[:-3]
        if f"{base_path}/index.html" in site_index:
            return None
        if f"{base_path}/" in site_index:
            return None

    return f"Target not found: {target_decoded}"


def validate_html_file(
    file_path: Path,
    site_dir: Path,
    site_index: Set[str],
    site_url_path: str = "",
) -> List[LinkIssue]:
    """Validate all links in an HTML file."""
    issues: List[LinkIssue] = []

    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        issues.append(
            LinkIssue(
                source_file=file_path,
                href="",
                issue_type="read-error",
                message=f"Failed to read file: {e}",
            )
        )
        return issues

    links = extract_html_links(content)
    source_path = "/" + str(file_path.relative_to(site_dir)).replace("\\", "/")

    for href in links:
        error = check_internal_link(href, source_path, site_index, site_url_path)
        if error:
            issues.append(
                LinkIssue(
                    source_file=file_path,
                    href=href,
                    issue_type="broken-link",
                    message=error,
                )
            )

    return issues


def validate_site(
    site_dir: Path,
    site_url_path: str = "",
    ignore_files: Optional[Set[str]] = None,
) -> List[LinkIssue]:
    """Validate all links in the built site.

    Args:
        site_dir: Path to the built site directory
        site_url_path: The site URL path prefix (e.g., "/unity-tips")
        ignore_files: Set of filenames to skip validation (e.g., {"404.html"})
    """
    all_issues: List[LinkIssue] = []

    if ignore_files is None:
        ignore_files = {"404.html"}  # 404 pages have special navigation

    if not site_dir.exists():
        print(f"Error: Site directory not found: {site_dir}", file=sys.stderr)
        return [
            LinkIssue(
                source_file=site_dir,
                href="",
                issue_type="missing-site",
                message="Site directory does not exist",
            )
        ]

    # Build index of all available paths
    site_index = build_site_index(site_dir)

    # Check all HTML files
    for html_file in site_dir.rglob("*.html"):
        if html_file.name in ignore_files:
            continue
        issues = validate_html_file(html_file, site_dir, site_index, site_url_path)
        all_issues.extend(issues)

    return all_issues


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Validate links in a built MkDocs site"
    )
    parser.add_argument(
        "site_dir",
        type=Path,
        nargs="?",
        default=Path("_site"),
        help="Path to the built site directory (default: _site)",
    )
    parser.add_argument(
        "--site-url-path",
        type=str,
        default="",
        help="Site URL path prefix to strip from absolute links (e.g., /unity-tips)",
    )
    parser.add_argument(
        "--ignore-pattern",
        action="append",
        default=[],
        help="Regex patterns for links to ignore",
    )
    parser.add_argument(
        "--ignore-file",
        action="append",
        default=[],
        help="Filenames to skip validation (default: 404.html)",
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Main entry point."""
    args = parse_args(argv)

    ignore_files = set(args.ignore_file) if args.ignore_file else None
    issues = validate_site(args.site_dir, args.site_url_path, ignore_files)

    # Filter ignored patterns
    if args.ignore_pattern:
        patterns = [re.compile(p) for p in args.ignore_pattern]
        issues = [
            issue for issue in issues if not any(p.search(issue.href) for p in patterns)
        ]

    if issues:
        for issue in issues:
            print(str(issue), file=sys.stderr)

        print(f"\nFound {len(issues)} broken link(s)", file=sys.stderr)
        return 1

    print("All links validated successfully!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
