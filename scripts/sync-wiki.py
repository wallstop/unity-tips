#!/usr/bin/env python3
"""
Sync documentation from docs/ to GitHub Wiki format.

This script:
1. Copies markdown files from docs/ to wiki/
2. Converts internal links to wiki format
3. Generates a _Sidebar.md for navigation
4. Creates a Home.md landing page
"""

import os
import re
import shutil
from pathlib import Path

DOCS_DIR = Path("docs")
WIKI_DIR = Path("wiki")
ROOT_FILES = ["README.md", "CONTRIBUTING.md", "CHANGELOG.md"]

# Mapping of source paths to wiki page names
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


def convert_links(content: str, source_file: str) -> str:
    """Convert relative markdown links to wiki links."""

    def replace_link(match: re.Match) -> str:
        text = match.group(1)
        link = match.group(2)

        # Skip external links and anchors
        if link.startswith(("http://", "https://", "#", "mailto:")):
            return match.group(0)

        # Resolve relative path
        source_dir = str(Path(source_file).parent)
        if source_dir == ".":
            resolved = link
        else:
            resolved = os.path.normpath(os.path.join(source_dir, link))

        # Remove .md extension and handle anchors
        anchor = ""
        if "#" in resolved:
            resolved, anchor = resolved.split("#", 1)
            anchor = "#" + anchor

        resolved = resolved.replace(".md", "")

        # Look up wiki page name
        for src_path, wiki_name in WIKI_STRUCTURE.items():
            src_without_ext = src_path.replace(".md", "")
            if resolved == src_without_ext or resolved.endswith(src_without_ext):
                return f"[[{wiki_name}{anchor}|{text}]]"

        # Handle root files
        if resolved in ["README", "CONTRIBUTING", "CHANGELOG"]:
            wiki_names = {"README": "Home", "CONTRIBUTING": "Contributing", "CHANGELOG": "Changelog"}
            return f"[[{wiki_names.get(resolved, resolved)}{anchor}|{text}]]"

        # Fallback: keep original link
        return match.group(0)

    # Match markdown links [text](link)
    pattern = r"\[([^\]]+)\]\(([^)]+)\)"
    return re.sub(pattern, replace_link, content)


def process_file(src_path: Path, wiki_name: str) -> None:
    """Process a markdown file and copy to wiki directory."""
    content = src_path.read_text(encoding="utf-8")

    # Convert links
    relative_path = str(src_path.relative_to(DOCS_DIR)) if str(src_path).startswith(str(DOCS_DIR)) else str(src_path)
    content = convert_links(content, relative_path)

    # Write to wiki
    dest_path = WIKI_DIR / f"{wiki_name}.md"
    dest_path.write_text(content, encoding="utf-8")
    print(f"  {src_path} -> {dest_path}")


def generate_sidebar() -> str:
    """Generate the wiki sidebar navigation."""
    return """# Unity Tips & Tools

**[[Home]]**

## Getting Started
- [[Home|Overview]]
- [[Contributing]]
- [[Changelog]]

## Best Practices
- [[Best-Practices|Overview]]
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
- [[Development-Tooling|Overview]]
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
    if readme_path.exists():
        content = readme_path.read_text(encoding="utf-8")
        content = convert_links(content, "README.md")
        return content
    return """# Unity Tips & Tools

> Battle-tested practices and tools to build better Unity games faster.

Welcome to the Unity Tips & Tools wiki!

## Quick Navigation

- [[Best-Practices|Best Practices]] - Prevent 80% of Unity bugs
- [[Development-Tooling|Development Tooling]] - Auto-format code, catch allocations
- [[Animancer]] - Code-driven animation
- [[Graphy]] - Monitor FPS/memory

## Documentation

This wiki is automatically synced from the [main repository](https://github.com/wallstop/unity-tips).

For the best reading experience with search and navigation, visit the
[GitHub Pages documentation site](https://wallstop.github.io/unity-tips).
"""


def main() -> None:
    """Main entry point."""
    print("Syncing documentation to GitHub Wiki...")

    # Clean wiki directory (except .git)
    if WIKI_DIR.exists():
        for item in WIKI_DIR.iterdir():
            if item.name != ".git":
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()

    # Process all mapped files
    print("\nProcessing documentation files:")
    for src_rel, wiki_name in WIKI_STRUCTURE.items():
        src_path = DOCS_DIR / src_rel
        if src_path.exists():
            process_file(src_path, wiki_name)
        else:
            print(f"  Warning: {src_path} not found")

    # Process root files
    print("\nProcessing root files:")
    root_mapping = {
        "CONTRIBUTING.md": "Contributing",
        "CHANGELOG.md": "Changelog",
    }
    for filename, wiki_name in root_mapping.items():
        src_path = Path(filename)
        if src_path.exists():
            process_file(src_path, wiki_name)

    # Generate Home page
    print("\nGenerating Home page...")
    home_content = generate_home()
    (WIKI_DIR / "Home.md").write_text(home_content, encoding="utf-8")

    # Generate sidebar
    print("Generating sidebar...")
    sidebar_content = generate_sidebar()
    (WIKI_DIR / "_Sidebar.md").write_text(sidebar_content, encoding="utf-8")

    print("\nWiki sync complete!")


if __name__ == "__main__":
    main()
