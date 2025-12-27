#!/usr/bin/env python3
"""Validate MkDocs configuration and GitHub Pages link compatibility.

This script validates:
1. All nav entries in mkdocs.yml point to existing files
2. Links in markdown files are compatible with MkDocs/GitHub Pages
3. No broken internal references in the documentation structure
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, List, Optional, Sequence, Set

import yaml

from link_utils import LinkMatch, extract_links


class SafeLineLoader(yaml.SafeLoader):
    """YAML loader that handles MkDocs-specific Python tags safely."""

    pass


def _construct_python_name(loader: yaml.Loader, node: yaml.Node) -> str:
    """Handle !!python/name tags by returning placeholder string."""
    return f"<python:{node.value}>"


# Register handlers for MkDocs-specific Python tags
SafeLineLoader.add_constructor(
    "tag:yaml.org,2002:python/name:material.extensions.emoji.twemoji",
    _construct_python_name,
)
SafeLineLoader.add_constructor(
    "tag:yaml.org,2002:python/name:material.extensions.emoji.to_svg",
    _construct_python_name,
)
SafeLineLoader.add_constructor(
    "tag:yaml.org,2002:python/name:pymdownx.superfences.fence_code_format",
    _construct_python_name,
)
# Generic handler for any python/name tag
SafeLineLoader.add_multi_constructor(
    "tag:yaml.org,2002:python/name:",
    lambda loader, suffix, node: f"<python:{suffix}>",
)


@dataclass
class ValidationIssue:
    """Represents a validation problem found during checking."""

    file_path: Path
    line: int
    column: int
    issue_type: str
    message: str
    href: str = ""

    def __str__(self) -> str:
        loc = f"{self.file_path}:{self.line}:{self.column}"
        return f"{loc}: [{self.issue_type}] {self.message}"


@dataclass
class MkDocsConfig:
    """Parsed MkDocs configuration."""

    docs_dir: str = "docs"
    site_url: str = ""
    nav: List[Any] = field(default_factory=list)
    config_path: Path = field(default_factory=lambda: Path("mkdocs.yml"))


def load_mkdocs_config(config_path: Path) -> MkDocsConfig:
    """Load and parse mkdocs.yml configuration."""
    if not config_path.exists():
        raise FileNotFoundError(f"MkDocs config not found: {config_path}")

    with open(config_path, encoding="utf-8") as f:
        data = yaml.load(f, Loader=SafeLineLoader)

    return MkDocsConfig(
        docs_dir=data.get("docs_dir", "docs"),
        site_url=data.get("site_url", ""),
        nav=data.get("nav", []),
        config_path=config_path,
    )


def extract_nav_files(nav: List[Any], files: Optional[Set[str]] = None) -> Set[str]:
    """Recursively extract all file paths from nav structure."""
    if files is None:
        files = set()

    for item in nav:
        if isinstance(item, str):
            files.add(item)
        elif isinstance(item, dict):
            for value in item.values():
                if isinstance(value, str):
                    files.add(value)
                elif isinstance(value, list):
                    extract_nav_files(value, files)

    return files


def validate_nav_files(config: MkDocsConfig, base_dir: Path) -> List[ValidationIssue]:
    """Validate that all files referenced in nav exist.

    Handles the case where docs_dir is dynamically created (like site-docs)
    by checking multiple possible locations:
    - docs_dir if it exists
    - docs/ folder (source documentation)
    - root level (for README.md, CONTRIBUTING.md, etc.)
    """
    issues: List[ValidationIssue] = []
    docs_path = base_dir / config.docs_dir
    fallback_docs_path = base_dir / "docs"
    nav_files = extract_nav_files(config.nav)

    # Root-level files that are typically at repo root
    # overview.md is generated from README.md during build
    root_files = {
        "README.md",
        "CONTRIBUTING.md",
        "CHANGELOG.md",
        "index.md",
        "overview.md",
    }

    for file_ref in nav_files:
        found = False

        # Check docs_dir first
        if docs_path.exists():
            if (docs_path / file_ref).exists():
                found = True

        # Check fallback docs folder
        if not found and fallback_docs_path.exists():
            if (fallback_docs_path / file_ref).exists():
                found = True

        # Check root for specific files
        if not found and file_ref in root_files:
            if (base_dir / file_ref).exists():
                found = True

        # These files are generated during build, always consider them valid
        # index.md is generated from template, overview.md is generated from README.md
        if not found and file_ref in {"index.md", "overview.md"}:
            found = True

        if not found:
            issues.append(
                ValidationIssue(
                    file_path=config.config_path,
                    line=1,
                    column=1,
                    issue_type="missing-nav-file",
                    message=f"Nav references non-existent file: {file_ref}",
                    href=file_ref,
                )
            )

    return issues


def check_github_pages_compatibility(
    file_path: Path,
    link: LinkMatch,
    docs_dir: str,
    is_in_docs: bool,
    transformed_files: Optional[Set[str]] = None,
) -> Optional[ValidationIssue]:
    """Check if a link is compatible with GitHub Pages deployment.

    Issues detected:
    - Links with 'docs/' prefix that will break on GitHub Pages
    - Absolute paths that won't work on GitHub Pages

    Args:
        file_path: Path to the file being checked
        link: The link being validated
        docs_dir: The configured docs directory
        is_in_docs: Whether the file is in the docs directory
        transformed_files: Set of filenames that are transformed during build
                          (skip docs-prefix check for these)
    """
    href = link.href.strip()

    # Skip external URLs, anchors, and special protocols
    if href.startswith(("http://", "https://", "mailto:", "tel:", "#")):
        return None

    # Files that are transformed during build have their docs/ prefix fixed
    if transformed_files is None:
        transformed_files = {"README.md", "CHANGELOG.md"}

    # Skip docs-prefix check for files that will be transformed
    if file_path.name in transformed_files:
        return None

    # Check for docs/ prefix in links (breaks on GitHub Pages)
    # This applies to files that will be copied to site-docs
    if is_in_docs:
        # Check for ./docs/ or docs/ prefix
        docs_prefix_pattern = r"^\.?/?docs/"
        if re.match(docs_prefix_pattern, href):
            return ValidationIssue(
                file_path=file_path,
                line=link.line,
                column=link.column,
                issue_type="docs-prefix",
                message=(
                    f"Link has 'docs/' prefix which breaks on GitHub Pages. "
                    f"Use relative path without 'docs/' prefix."
                ),
                href=href,
            )

    return None


def check_mkdocs_link_format(
    file_path: Path,
    link: LinkMatch,
) -> Optional[ValidationIssue]:
    """Check that links follow MkDocs conventions."""
    href = link.href.strip()

    # Skip external URLs and special protocols
    if href.startswith(("http://", "https://", "mailto:", "tel:", "#")):
        return None

    # Warn about absolute paths starting with / (may not work as expected)
    if href.startswith("/") and not href.startswith("//"):
        return ValidationIssue(
            file_path=file_path,
            line=link.line,
            column=link.column,
            issue_type="absolute-path",
            message=(
                "Absolute paths may not work correctly on GitHub Pages. "
                "Consider using relative paths instead."
            ),
            href=href,
        )

    return None


def validate_markdown_file(
    file_path: Path,
    docs_dir: str,
    base_dir: Path,
    check_pages_compat: bool = True,
) -> List[ValidationIssue]:
    """Validate all links in a markdown file."""
    issues: List[ValidationIssue] = []

    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        issues.append(
            ValidationIssue(
                file_path=file_path,
                line=1,
                column=1,
                issue_type="read-error",
                message=f"Failed to read file: {e}",
            )
        )
        return issues

    links = extract_links(content)
    docs_path = base_dir / docs_dir

    # Determine if file is inside docs directory
    try:
        file_path.relative_to(docs_path)
        is_in_docs = True
    except ValueError:
        is_in_docs = False

    for link in links:
        # Check GitHub Pages compatibility
        if check_pages_compat:
            issue = check_github_pages_compatibility(
                file_path, link, docs_dir, is_in_docs
            )
            if issue:
                issues.append(issue)

        # Check MkDocs link format
        issue = check_mkdocs_link_format(file_path, link)
        if issue:
            issues.append(issue)

    return issues


def find_markdown_files(base_dir: Path, docs_dir: str) -> List[Path]:
    """Find all markdown files that will be part of the site."""
    files: List[Path] = []

    # Root level markdown files
    for name in ["README.md", "CONTRIBUTING.md", "CHANGELOG.md"]:
        path = base_dir / name
        if path.exists():
            files.append(path)

    # Docs directory
    docs_path = base_dir / docs_dir
    if docs_path.exists():
        files.extend(docs_path.rglob("*.md"))

    return files


def run_validation(
    base_dir: Path,
    config_path: Optional[Path] = None,
    check_nav: bool = True,
    check_pages_compat: bool = True,
    files: Optional[List[Path]] = None,
) -> List[ValidationIssue]:
    """Run all validation checks."""
    all_issues: List[ValidationIssue] = []

    # Load config
    if config_path is None:
        config_path = base_dir / "mkdocs.yml"

    try:
        config = load_mkdocs_config(config_path)
    except FileNotFoundError:
        # No mkdocs.yml - skip nav validation but continue with file checks
        config = MkDocsConfig(docs_dir="docs")
        check_nav = False

    # Validate nav entries
    if check_nav:
        all_issues.extend(validate_nav_files(config, base_dir))

    # Validate markdown files
    if files:
        md_files = files
    else:
        md_files = find_markdown_files(base_dir, config.docs_dir)

    for file_path in md_files:
        issues = validate_markdown_file(
            file_path,
            config.docs_dir,
            base_dir,
            check_pages_compat=check_pages_compat,
        )
        all_issues.extend(issues)

    return all_issues


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Validate MkDocs configuration and GitHub Pages link compatibility"
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help="Specific files to check (default: all markdown files)",
    )
    parser.add_argument(
        "--base-dir",
        type=Path,
        default=Path.cwd(),
        help="Base directory of the project",
    )
    parser.add_argument(
        "--config",
        type=Path,
        help="Path to mkdocs.yml (default: auto-detect)",
    )
    parser.add_argument(
        "--skip-nav",
        action="store_true",
        help="Skip nav file validation",
    )
    parser.add_argument(
        "--skip-pages-compat",
        action="store_true",
        help="Skip GitHub Pages compatibility checks",
    )
    parser.add_argument(
        "--warn-only",
        action="store_true",
        help="Exit with 0 even if issues found (warn only)",
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Main entry point."""
    args = parse_args(argv)

    files = [Path(p) for p in args.paths] if args.paths else None

    issues = run_validation(
        base_dir=args.base_dir,
        config_path=args.config,
        check_nav=not args.skip_nav,
        check_pages_compat=not args.skip_pages_compat,
        files=files,
    )

    if issues:
        for issue in issues:
            print(str(issue), file=sys.stderr)

        print(f"\nFound {len(issues)} issue(s)", file=sys.stderr)

        if args.warn_only:
            return 0
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
