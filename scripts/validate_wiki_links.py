#!/usr/bin/env python3
"""Wrapper script to sync wiki and validate links.

This script runs sync-wiki.py followed by check_wiki_links.py.
Used by pre-commit to validate wiki links in a single hook.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    """Run wiki sync and validation."""
    scripts_dir = Path(__file__).parent

    # Run sync-wiki.py
    result = subprocess.run(
        [sys.executable, scripts_dir / "sync-wiki.py"],
        env={"PYTHONPATH": str(scripts_dir)},
    )
    if result.returncode != 0:
        print("Wiki sync failed", file=sys.stderr)
        return result.returncode

    # Run check_wiki_links.py
    result = subprocess.run(
        [sys.executable, scripts_dir / "check_wiki_links.py"],
        env={"PYTHONPATH": str(scripts_dir)},
    )
    if result.returncode != 0:
        print("Wiki link validation failed", file=sys.stderr)
        return result.returncode

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
