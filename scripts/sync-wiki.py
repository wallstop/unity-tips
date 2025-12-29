#!/usr/bin/env python3
"""
Sync documentation from docs/ to GitHub Wiki format.

This script:
1. Copies markdown files from docs/ to wiki/
2. Converts internal links to wiki format
3. Generates a _Sidebar.md for navigation
4. Creates a Home.md landing page
"""

from __future__ import annotations

import shutil
from pathlib import Path, PurePosixPath

# Import shared link utilities for proper code block handling
from link_utils import (
    CRITICAL_PAGES,
    extract_links,
    find_code_fence_ranges,
    find_inline_code_ranges,
    in_ranges,
    split_anchor,
)

DOCS_DIR = Path("docs")
WIKI_DIR = Path("wiki")

# Mapping of source paths to wiki page names (always use forward slashes)
WIKI_STRUCTURE = {
    # Best Practices
    "best-practices/README.md": "Best-Practices",
    "best-practices/01-lifecycle-methods.md": "Lifecycle-Methods",
    "best-practices/02-null-checks.md": "Null-Checks",
    "best-practices/03-component-access.md": "Component-Access",
    "best-practices/04-serialization.md": "Serialization",
    "best-practices/05-coroutines.md": "Coroutines",
    "best-practices/06-physics.md": "Physics",
    "best-practices/07-performance-memory.md": "Performance-and-Memory",
    "best-practices/08-scriptable-objects.md": "ScriptableObjects",
    "best-practices/09-object-pooling.md": "Object-Pooling",
    "best-practices/10-event-systems.md": "Event-Systems",
    "best-practices/11-addressables.md": "Addressables",
    "best-practices/12-scene-loading.md": "Scene-Loading",
    "best-practices/13-jobs-burst.md": "Jobs-and-Burst",
    "best-practices/14-async-await.md": "Async-Await",
    "best-practices/15-profiling.md": "Profiling",
    "best-practices/16-automated-testing-ci.md": "Testing-and-CI",
    "best-practices/17-input-architecture.md": "Input-Architecture",
    "best-practices/18-save-load.md": "Save-Load",
    # Animancer
    "animancer/README.md": "Animancer",
    "animancer/01-getting-started.md": "Animancer-Getting-Started",
    "animancer/02-core-concepts.md": "Animancer-Core-Concepts",
    "animancer/03-advanced-techniques.md": "Animancer-Advanced",
    "animancer/04-best-practices.md": "Animancer-Best-Practices",
    "animancer/05-code-examples.md": "Animancer-Code-Examples",
    # PrimeTween
    "primetween/README.md": "PrimeTween",
    "primetween/01-getting-started.md": "PrimeTween-Getting-Started",
    "primetween/02-why-primetween.md": "PrimeTween-Why",
    "primetween/03-api-reference.md": "PrimeTween-API",
    "primetween/04-common-patterns.md": "PrimeTween-Patterns",
    "primetween/05-anti-patterns.md": "PrimeTween-Anti-Patterns",
    # Feel
    "feel/README.md": "Feel",
    "feel/01-getting-started.md": "Feel-Getting-Started",
    "feel/02-why-feel.md": "Feel-Why",
    "feel/03-feedback-catalog.md": "Feel-Feedback-Catalog",
    "feel/04-advanced-techniques.md": "Feel-Advanced",
    "feel/05-troubleshooting.md": "Feel-Troubleshooting",
    # Hot Reload
    "hot-reload/README.md": "Hot-Reload",
    "hot-reload/01-getting-started.md": "Hot-Reload-Getting-Started",
    "hot-reload/02-why-hot-reload.md": "Hot-Reload-Why",
    "hot-reload/03-how-to-use.md": "Hot-Reload-Usage",
    "hot-reload/04-troubleshooting.md": "Hot-Reload-Troubleshooting",
    "hot-reload/05-best-practices.md": "Hot-Reload-Best-Practices",
    # Odin
    "odin/README.md": "Odin-Inspector",
    "odin/01-getting-started.md": "Odin-Getting-Started",
    "odin/02-core-features.md": "Odin-Core-Features",
    "odin/03-advanced-techniques.md": "Odin-Advanced",
    "odin/04-common-patterns.md": "Odin-Patterns",
    "odin/05-best-practices.md": "Odin-Best-Practices",
    # Assembly Definitions
    "assembly-definitions/README.md": "Assembly-Definitions",
    "assembly-definitions/01-getting-started.md": "Assembly-Definitions-Getting-Started",
    "assembly-definitions/02-core-concepts.md": "Assembly-Definitions-Core-Concepts",
    "assembly-definitions/03-advanced-techniques.md": "Assembly-Definitions-Advanced",
    "assembly-definitions/04-common-patterns.md": "Assembly-Definitions-Patterns",
    "assembly-definitions/05-best-practices.md": "Assembly-Definitions-Best-Practices",
    # Input System
    "input-system/README.md": "Input-System",
    "input-system/01-getting-started.md": "Input-System-Getting-Started",
    "input-system/02-core-concepts.md": "Input-System-Core-Concepts",
    "input-system/03-advanced-techniques.md": "Input-System-Advanced",
    "input-system/04-common-patterns.md": "Input-System-Patterns",
    "input-system/05-troubleshooting.md": "Input-System-Troubleshooting",
    # Tooling
    "tooling/README.md": "Development-Tooling",
    "tooling/01-csharpier.md": "CSharpier",
    "tooling/02-editorconfig.md": "EditorConfig",
    "tooling/03-nuget-for-unity.md": "NuGet-for-Unity",
    "tooling/04-heap-allocation-viewer.md": "Heap-Allocation-Viewer",
    # Single-page tools
    "dxmessaging/README.md": "DxMessaging",
    "graphy/README.md": "Graphy",
    "better-build-info/README.md": "Better-Build-Info",
    "asset-usage-finder/README.md": "Asset-Usage-Finder",
    "unity-helpers/README.md": "Unity-Helpers",
}

# Root files that get special handling
ROOT_WIKI_NAMES = {
    "README": "Home",
    "CONTRIBUTING": "Contributing",
    "CHANGELOG": "Changelog",
}

# Track warnings for unmapped links
_unmapped_links: list[tuple[str, str, str]] = []


def normalize_path(path: str) -> str:
    """Normalize a path to use forward slashes (POSIX style) for consistent matching."""
    return str(PurePosixPath(Path(path)))


def remove_md_suffix(path: str) -> str:
    """Remove .md extension from path if present, only at the end."""
    return path.removesuffix(".md")


def resolve_relative_path(source_file: str, link: str) -> str | None:
    """
    Resolve a relative link path from a source file location.

    Returns None if the path escapes the documentation root (too many ..).
    """
    source_dir = PurePosixPath(source_file).parent
    if str(source_dir) == ".":
        resolved = PurePosixPath(link)
    else:
        resolved = source_dir / link

    # Normalize to handle .. and .
    parts: list[str] = []
    escape_count = 0

    for part in resolved.parts:
        if part == "..":
            if parts:
                parts.pop()
            else:
                # Trying to escape root
                escape_count += 1
        elif part != ".":
            parts.append(part)

    # If we ever tried to escape the root, the path is invalid
    if escape_count > 0:
        return None

    return str(PurePosixPath(*parts)) if parts else "."


def is_in_table_row(content: str, position: int) -> bool:
    """Check if a position in the content is inside a Markdown table row.

    A table row starts with | and contains | as column separators.
    We detect this by finding the start of the current line and checking
    if it begins with |.
    """
    # Find the start of the line containing this position
    line_start = content.rfind("\n", 0, position) + 1

    # Find the end of the line
    line_end = content.find("\n", position)
    if line_end == -1:
        line_end = len(content)

    line = content[line_start:line_end]

    # A table row starts with | (possibly with leading whitespace)
    # and is not a separator row (those contain only |, -, :, and spaces)
    stripped = line.strip()
    if not stripped.startswith("|"):
        return False

    # Check it's not a separator row like | --- | --- |
    separator_chars = set("|-: ")
    if all(c in separator_chars for c in stripped):
        return False

    return True


def convert_links(content: str, source_file: str) -> str:
    """Convert relative markdown links to wiki links, skipping code blocks."""
    # Get code ranges to skip
    code_ranges = find_code_fence_ranges(content)
    inline_code_ranges = find_inline_code_ranges(content)
    skip_ranges = code_ranges + inline_code_ranges

    # Use link_utils to extract links properly (handles nested brackets, escaping, etc.)
    links = extract_links(content)

    # Process links in reverse order to maintain correct positions during replacement
    result = content
    for link_match in reversed(links):
        # Skip links inside code blocks
        if in_ranges(link_match.start, skip_ranges):
            continue

        # Only process inline links (not autolinks or bare URLs)
        if link_match.kind != "inline":
            continue

        href = link_match.href
        link_text = link_match.text

        # Skip external links and anchors
        if href.startswith(("http://", "https://", "#", "mailto:")):
            continue

        # Handle anchors in links using split_anchor (handles URL decoding)
        link_path, anchor_text = split_anchor(href)

        # Format anchor for wiki link
        anchor = f"#{anchor_text}" if anchor_text else ""

        # Skip if it's just an anchor
        if not link_path:
            continue

        # Resolve relative path using POSIX-style paths
        resolved = resolve_relative_path(normalize_path(source_file), link_path)

        # Handle invalid paths (escaping root)
        if resolved is None:
            _unmapped_links.append(
                (source_file, href, "path escapes documentation root")
            )
            continue

        # Remove .md extension for matching
        resolved_without_ext = remove_md_suffix(resolved)

        # Strip docs/ prefix if present (for links from root files like README.md)
        # WIKI_STRUCTURE uses paths relative to docs/, not the repo root
        if resolved_without_ext.startswith("docs/"):
            resolved_without_ext = resolved_without_ext[5:]  # Remove "docs/" prefix

        # Handle trailing slashes (e.g., "./directory/" -> "directory/README")
        if resolved_without_ext.endswith("/"):
            resolved_without_ext = resolved_without_ext.rstrip("/") + "/README"

        # Look up wiki page name with exact matching
        wiki_name = None
        for src_path, name in WIKI_STRUCTURE.items():
            src_without_ext = remove_md_suffix(src_path)
            # Exact match only - no endswith to avoid false positives
            if resolved_without_ext == src_without_ext:
                wiki_name = name
                break

        # Handle root files
        if wiki_name is None and resolved_without_ext in ROOT_WIKI_NAMES:
            wiki_name = ROOT_WIKI_NAMES[resolved_without_ext]

        if wiki_name is not None:
            # Use wiki page name as fallback if link text is empty
            display_text = link_text if link_text.strip() else wiki_name

            # Check if this link is inside a table row
            # If so, we need to escape the pipe character to prevent it from
            # being interpreted as a table column separator
            # Note: Use original content for position check since link_match.start
            # refers to positions in the original content, not the modified result
            in_table = is_in_table_row(content, link_match.start)

            if in_table:
                # In tables, use escaped pipe: [[Display\|Page]]
                # GitHub Wiki interprets \| correctly inside tables
                separator = "\\|"
            else:
                separator = "|"

            # Replace with wiki link format:
            # - Normal context: [[DisplayText|PageName]]
            # - Table context:  [[DisplayText\|PageName]] (escaped pipe)
            # Note: GitHub Wiki format is opposite of MediaWiki
            new_link = f"[[{display_text}{separator}{wiki_name}{anchor}]]"
            result = result[: link_match.start] + new_link + result[link_match.end :]
        else:
            # Track unmapped internal links for warning
            _unmapped_links.append((source_file, href, "no mapping found"))

    return result


def read_file_safe(path: Path) -> str | None:
    """Safely read a file, returning None on error."""
    try:
        return path.read_text(encoding="utf-8")
    except OSError as e:
        print(f"  Error reading {path}: {e}")
        return None
    except UnicodeDecodeError as e:
        print(f"  Error decoding {path}: {e}")
        return None


def write_file_safe(path: Path, content: str) -> bool:
    """Safely write a file, returning False on error."""
    try:
        path.write_text(content, encoding="utf-8")
        return True
    except OSError as e:
        print(f"  Error writing {path}: {e}")
        return False


def process_file(src_path: Path, wiki_name: str) -> bool:
    """Process a markdown file and copy to wiki directory."""
    content = read_file_safe(src_path)
    if content is None:
        return False

    # Convert links using normalized path
    try:
        relative_path = str(src_path.relative_to(DOCS_DIR))
    except ValueError:
        relative_path = str(src_path)

    # Normalize to forward slashes for consistent link resolution
    relative_path = normalize_path(relative_path)
    content = convert_links(content, relative_path)

    # Write to wiki
    dest_path = WIKI_DIR / f"{wiki_name}.md"
    if write_file_safe(dest_path, content):
        print(f"  {src_path} -> {dest_path}")
        return True
    return False


def generate_sidebar() -> str:
    """Generate the wiki sidebar navigation.

    Note: GitHub Wiki link format is [[DisplayText|PageName]], which is
    the opposite of MediaWiki's [[PageName|DisplayText]] format.
    """
    return """# Unity Tips & Tools

**[[Home]]**

## Getting Started
- [[Overview|Home]]
- [[Contributing]]
- [[Changelog]]

## Best Practices
- [[Overview|Best-Practices]]
- [[Lifecycle-Methods]]
- [[Null-Checks]]
- [[Component-Access]]
- [[Serialization]]
- [[Coroutines]]
- [[Physics]]
- [[Performance-and-Memory]]
- [[ScriptableObjects]]
- [[Object-Pooling]]
- [[Event-Systems]]
- [[Addressables]]
- [[Scene-Loading]]
- [[Jobs-and-Burst]]
- [[Async-Await]]
- [[Profiling]]
- [[Testing-and-CI]]
- [[Input-Architecture]]
- [[Save-Load]]

## Animation & Polish
- [[Animancer]]
- [[PrimeTween]]
- [[Feel]]

## Editor & Workflow
- [[Hot-Reload]]
- [[Odin-Inspector]]

## Architecture
- [[Assembly-Definitions]]
- [[Input-System]]
- [[DxMessaging]]

## Development Tooling
- [[Overview|Development-Tooling]]
- [[CSharpier]]
- [[EditorConfig]]
- [[NuGet-for-Unity]]
- [[Heap-Allocation-Viewer]]

## Debugging & Performance
- [[Graphy]]
- [[Better-Build-Info]]
- [[Asset-Usage-Finder]]

## Utilities
- [[Unity-Helpers]]
"""


def generate_home() -> str:
    """Generate the Home.md landing page."""
    readme_path = Path("README.md")
    content = read_file_safe(readme_path)
    if content is not None:
        return convert_links(content, "README.md")

    return """# Unity Tips & Tools

> Battle-tested practices and tools to build better Unity games faster.

Welcome to the Unity Tips & Tools wiki!

## Quick Navigation

- [[Best Practices|Best-Practices]] - Prevent 80% of Unity bugs
- [[Development Tooling|Development-Tooling]] - Auto-format code, catch allocations
- [[Animancer]] - Code-driven animation
- [[Graphy]] - Monitor FPS/memory

## Documentation

This wiki is automatically synced from the [main repository](https://github.com/wallstop/unity-tips).

For the best reading experience with search and navigation, visit the
[GitHub Pages documentation site](https://wallstop.github.io/unity-tips).
"""


def validate_wiki_structure() -> list[str]:
    """Validate that all source files in WIKI_STRUCTURE exist.

    Returns:
        List of error messages for missing source files.
    """
    errors = []
    for src_rel, wiki_name in WIKI_STRUCTURE.items():
        src_path = DOCS_DIR / src_rel
        if not src_path.exists():
            errors.append(f"Missing source file: {src_path} (mapped to {wiki_name})")
    return errors


def main() -> int:
    """Main entry point. Returns 0 on success, 1 on failure."""
    print("Syncing documentation to GitHub Wiki...")
    errors = 0

    # Clear unmapped links tracking
    _unmapped_links.clear()

    # Pre-validate WIKI_STRUCTURE
    print("\nValidating WIKI_STRUCTURE mappings...")
    structure_errors = validate_wiki_structure()
    if structure_errors:
        print("  ERRORS found in WIKI_STRUCTURE:")
        for err in structure_errors:
            print(f"    ❌ {err}")
        errors += len(structure_errors)
    else:
        print(f"  ✓ All {len(WIKI_STRUCTURE)} source files exist")

    # Ensure wiki directory exists
    WIKI_DIR.mkdir(parents=True, exist_ok=True)

    # Clean wiki directory (except .git)
    for item in WIKI_DIR.iterdir():
        if item.name != ".git":
            try:
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()
            except OSError as e:
                print(f"  Warning: Could not remove {item}: {e}")

    # Process all mapped files
    print("\nProcessing documentation files:")
    for src_rel, wiki_name in WIKI_STRUCTURE.items():
        src_path = DOCS_DIR / src_rel
        if src_path.exists():
            if not process_file(src_path, wiki_name):
                errors += 1
        else:
            print(f"  ❌ MISSING: {src_path} (would generate {wiki_name}.md)")

    # Process root files
    print("\nProcessing root files:")
    root_mapping = {
        "CONTRIBUTING.md": "Contributing",
        "CHANGELOG.md": "Changelog",
    }
    for filename, wiki_name in root_mapping.items():
        src_path = Path(filename)
        if src_path.exists():
            if not process_file(src_path, wiki_name):
                errors += 1

    # Generate Home page
    print("\nGenerating Home page...")
    home_content = generate_home()
    if not write_file_safe(WIKI_DIR / "Home.md", home_content):
        errors += 1

    # Generate sidebar
    print("Generating sidebar...")
    sidebar_content = generate_sidebar()
    if not write_file_safe(WIKI_DIR / "_Sidebar.md", sidebar_content):
        errors += 1

    # Report unmapped links
    if _unmapped_links:
        print(f"\nWarning: {len(_unmapped_links)} unmapped link(s) found:")
        for source, link, reason in _unmapped_links:
            print(f"  {source}: [{link}] - {reason}")
        print(
            "  These links will not work in the wiki and may need to be added to WIKI_STRUCTURE."
        )

    # Final verification: Check critical pages were generated
    print("\nVerifying critical pages...")
    for page_name in CRITICAL_PAGES:
        page_path = WIKI_DIR / f"{page_name}.md"
        if page_path.exists():
            size = page_path.stat().st_size
            print(f"  ✓ {page_name}.md generated ({size} bytes)")
        else:
            print(f"  ❌ {page_name}.md NOT GENERATED")
            errors += 1

    if errors > 0:
        print(f"\nWiki sync completed with {errors} error(s)!")
        return 1

    print("\nWiki sync complete!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
