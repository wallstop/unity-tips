#!/usr/bin/env python3
"""Validate Markdown links for local and remote targets."""

from __future__ import annotations

import argparse
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple
from urllib.parse import urlparse

import os
import sys
import requests

from link_utils import LinkMatch, extract_links, split_anchor

CONNECT_TIMEOUT = float(os.getenv("LINK_CHECK_CONNECT_TIMEOUT", "5"))
READ_TIMEOUT = float(os.getenv("LINK_CHECK_READ_TIMEOUT", "20"))
REQUEST_TIMEOUT = (CONNECT_TIMEOUT, READ_TIMEOUT)
USER_AGENT = "unity-tips-link-checker/1.0"


@dataclass
class LinkIssue:
    path: Path
    line: int
    column: int
    href: str
    message: str


class LinkChecker:
    def __init__(self) -> None:
        self.remote_cache: Dict[str, Tuple[bool, str]] = {}
        self.heading_cache: Dict[Path, Optional[Dict[str, str]]] = {}

    def process_file(self, path: Path) -> List[LinkIssue]:
        text = path.read_text(encoding="utf-8")
        issues: List[LinkIssue] = []
        for match in extract_links(text):
            href = match.href.strip()
            parsed = urlparse(href)
            if parsed.scheme in {"mailto", "tel"}:
                continue
            if parsed.scheme in {"http", "https"}:
                ok, message = self._check_remote(href)
            elif href.startswith("#"):
                ok, message = self._check_local_anchor(path, path, href[1:])
            else:
                ok, message = self._check_local_path(path, href)
            if not ok:
                issues.append(
                    LinkIssue(
                        path=path,
                        line=match.line,
                        column=match.column,
                        href=href,
                        message=message,
                    )
                )
        return issues

    def _check_remote(self, url: str) -> Tuple[bool, str]:
        cached = self.remote_cache.get(url)
        if cached is not None:
            return cached
        headers = {"User-Agent": USER_AGENT}
        try:
            response = requests.head(
                url,
                allow_redirects=True,
                timeout=REQUEST_TIMEOUT,
                headers=headers,
            )
            status = response.status_code
            if status == 429:
                message = "Rate limited (HTTP 429); skipping validation"
                print(f"warning: {url}: {message}", file=sys.stderr)
                result = (True, message)
                self.remote_cache[url] = result
                return result
            if status >= 400 or status == 405:
                response = requests.get(
                    url,
                    allow_redirects=True,
                    timeout=REQUEST_TIMEOUT,
                    headers=headers,
                )
                status = response.status_code
                if status == 429:
                    message = "Rate limited (HTTP 429); skipping validation"
                    print(f"warning: {url}: {message}", file=sys.stderr)
                    result = (True, message)
                    self.remote_cache[url] = result
                    return result
            if 200 <= status < 400:
                result = (True, "")
            else:
                result = (False, f"HTTP status {status}")
        except requests.RequestException as exc:  # pragma: no cover - defensive
            result = (False, f"Request failed: {exc}")
        self.remote_cache[url] = result
        return result

    def _check_local_path(self, base_path: Path, href: str) -> Tuple[bool, str]:
        target_str, anchor = split_anchor(href)
        if target_str.startswith("/"):
            target = Path(target_str.lstrip("/")).resolve()
        else:
            target = (base_path.parent / target_str).resolve()
        if not target.exists():
            return False, f"Missing local target: {target_str or base_path.name}"
        if anchor:
            return self._check_local_anchor(base_path, target, anchor)
        return True, ""

    def _check_local_anchor(
        self, base_path: Path, target: Path, anchor: str
    ) -> Tuple[bool, str]:
        anchor = anchor.strip()
        if not anchor:
            return False, "Empty anchor reference"
        slugs = self._get_heading_slugs(target)
        if slugs is None:
            return True, ""
        if anchor in slugs:
            return True, ""
        return False, f"Missing anchor '#{anchor}'"

    def _get_heading_slugs(self, path: Path) -> Optional[Dict[str, str]]:
        if path.suffix.lower() not in {".md", ".markdown", ".mdx"}:
            return None
        cached = self.heading_cache.get(path)
        if cached is not None:
            return cached
        if not path.exists():
            self.heading_cache[path] = {}
            return {}
        counts: Dict[str, int] = defaultdict(int)
        slugs: Dict[str, str] = {}
        for line in path.read_text(encoding="utf-8").splitlines():
            stripped = line.lstrip()
            if not stripped.startswith("#"):
                continue
            heading_text = stripped.lstrip("#").strip()
            if not heading_text:
                continue
            base_slug = self._slugify(heading_text)
            occurrence = counts[base_slug]
            counts[base_slug] += 1
            slug = base_slug if occurrence == 0 else f"{base_slug}-{occurrence}"
            slugs[slug] = heading_text
        self.heading_cache[path] = slugs
        return slugs

    @staticmethod
    def _slugify(text: str) -> str:
        slug = text.strip().lower()
        slug = re.sub(r"[\s]+", "-", slug)
        slug = re.sub(r"[^a-z0-9\-]", "", slug)
        return slug.strip("-")


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check Markdown links")
    parser.add_argument("paths", nargs="+", help="Markdown files to verify")
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    checker = LinkChecker()
    all_issues: List[LinkIssue] = []

    for path_str in args.paths:
        path = Path(path_str)
        if not path.exists() or path.suffix.lower() not in {".md", ".markdown", ".mdx"}:
            continue
        all_issues.extend(checker.process_file(path))

    if all_issues:
        for issue in all_issues:
            print(
                f"{issue.path}:{issue.line}:{issue.column}: {issue.message} ({issue.href})"
            )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
