#!/usr/bin/env python3
"""Generate index.md for MkDocs site.

This script generates the index.md landing page for the documentation site.
Used by both docs.yml (deployment) and pr-checks.yml (validation) workflows
to ensure the index page content is consistent.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional, Sequence

INDEX_CONTENT = """\
---
title: Unity Tips & Tools
description: Battle-tested practices and tools to build better Unity games faster
---

# Unity Tips & Tools

> Battle-tested practices and tools to build better Unity games faster. From beginner to expert.

Welcome to the Unity Tips & Tools documentation! This site contains comprehensive guides
for Unity best practices, recommended tools, and architectural patterns.

## Quick Navigation

<div class="grid cards" markdown>

- :material-rocket-launch: **[Best Practices](best-practices/README.md)**

    ---

    Prevent 80% of Unity bugs with lifecycle methods, null checks, physics patterns, and more.

- :material-tools: **[Development Tooling](tooling/README.md)**

    ---

    Auto-format code, catch allocations, and streamline your workflow.

- :material-animation: **[Animation & Polish](animancer/README.md)**

    ---

    Code-driven animation with Animancer, tweens with PrimeTween, and game juice with Feel.

- :material-speedometer: **[Performance](graphy/README.md)**

    ---

    Monitor FPS/memory, find asset usage, and optimize your builds.

</div>

## Getting Started

**New to Unity?** Start with [Best Practices](best-practices/README.md) to avoid common pitfalls.

**Setting up a project?** Check out [Development Tooling](tooling/README.md) for essential automation.

**Need specific help?** Use the search bar above or browse the sidebar navigation.

---

[:octicons-mark-github-16: View on GitHub](https://github.com/wallstop/unity-tips){ .md-button }
"""


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate index.md for MkDocs site"
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output file path (default: stdout)",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Don't print status messages to stderr",
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Main entry point."""
    args = parse_args(argv)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(INDEX_CONTENT, encoding="utf-8")
        if not args.quiet:
            print(f"Created {args.output}", file=sys.stderr)
    else:
        print(INDEX_CONTENT, end="")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
