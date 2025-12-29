#!/usr/bin/env python3
"""Tests for sync-wiki.py functionality."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

# Import sync-wiki.py (hyphenated module name requires special handling)
spec = importlib.util.spec_from_file_location(
    "sync_wiki", Path(__file__).parent / "sync-wiki.py"
)
assert spec is not None and spec.loader is not None
sync_wiki = importlib.util.module_from_spec(spec)
sys.modules["sync_wiki"] = sync_wiki
spec.loader.exec_module(sync_wiki)

is_in_table_row = sync_wiki.is_in_table_row


class TestIsInTableRow:
    """Tests for the is_in_table_row function."""

    def test_normal_table_row(self) -> None:
        """Links in normal table rows should be detected."""
        content = "| Link | Description |\n| --- | --- |\n| [[Page]] | text |"
        # Position of [[Page]] is at the third line
        position = content.find("[[Page]]")
        assert is_in_table_row(content, position) is True

    def test_header_row(self) -> None:
        """Links in table header rows should be detected."""
        content = "| [[Link]] | Description |\n| --- | --- |"
        position = content.find("[[Link]]")
        assert is_in_table_row(content, position) is True

    def test_separator_row_excluded(self) -> None:
        """Separator rows (| --- | --- |) should not be detected as table content."""
        content = "| Header |\n| --- |\n| Cell |"
        # Position in the separator row
        position = content.find("| --- |")
        assert is_in_table_row(content, position) is False

    def test_non_table_content(self) -> None:
        """Content not in tables should not be detected."""
        content = "This is [[Page]] not in a table."
        position = content.find("[[Page]]")
        assert is_in_table_row(content, position) is False

    def test_bullet_list(self) -> None:
        """Bullet lists should not be detected as tables."""
        content = "- [[Page]] in a list"
        position = content.find("[[Page]]")
        assert is_in_table_row(content, position) is False

    def test_numbered_list(self) -> None:
        """Numbered lists should not be detected as tables."""
        content = "1. [[Page]] in a numbered list"
        position = content.find("[[Page]]")
        assert is_in_table_row(content, position) is False

    def test_indented_table(self) -> None:
        """Indented tables should still be detected."""
        content = "  | [[Page]] | Description |"
        position = content.find("[[Page]]")
        assert is_in_table_row(content, position) is True

    def test_multiline_document(self) -> None:
        """Test correct detection in multiline documents."""
        content = """# Header

Some text with [[Link1]] not in table.

| Tool | Description |
| --- | --- |
| [[Link2]] | Some text |

More text with [[Link3]] not in table.
"""
        # Link1 - not in table
        pos1 = content.find("[[Link1]]")
        assert is_in_table_row(content, pos1) is False

        # Link2 - in table
        pos2 = content.find("[[Link2]]")
        assert is_in_table_row(content, pos2) is True

        # Link3 - not in table
        pos3 = content.find("[[Link3]]")
        assert is_in_table_row(content, pos3) is False

    def test_table_without_leading_pipe(self) -> None:
        """Tables without leading pipe (non-standard) should not be detected."""
        # Note: GFM standard requires leading |, but some parsers are lenient
        content = "Cell1 | Cell2 |"
        position = 0
        assert is_in_table_row(content, position) is False

    def test_separator_row_with_alignment(self) -> None:
        """Separator rows with alignment markers should be excluded."""
        content = "| Header |\n| :---: |\n| Cell |"
        position = content.find("| :---: |")
        assert is_in_table_row(content, position) is False

    def test_empty_line(self) -> None:
        """Empty lines should not be detected as table rows."""
        content = "| Header |\n\n| Cell |"
        # Position at the empty line
        position = content.find("\n\n") + 1
        assert is_in_table_row(content, position) is False


def run_tests() -> int:
    """Run all tests and return exit code."""
    test_instance = TestIsInTableRow()
    tests = [
        (test_instance.test_normal_table_row, "normal_table_row"),
        (test_instance.test_header_row, "header_row"),
        (test_instance.test_separator_row_excluded, "separator_row_excluded"),
        (test_instance.test_non_table_content, "non_table_content"),
        (test_instance.test_bullet_list, "bullet_list"),
        (test_instance.test_numbered_list, "numbered_list"),
        (test_instance.test_indented_table, "indented_table"),
        (test_instance.test_multiline_document, "multiline_document"),
        (test_instance.test_table_without_leading_pipe, "table_without_leading_pipe"),
        (
            test_instance.test_separator_row_with_alignment,
            "separator_row_with_alignment",
        ),
        (test_instance.test_empty_line, "empty_line"),
    ]

    passed = 0
    failed = 0

    for test_func, name in tests:
        try:
            test_func()
            print(f"  ✓ {name}")
            passed += 1
        except AssertionError as e:
            print(f"  ✗ {name}: {e}")
            failed += 1
        except Exception as e:
            print(f"  ✗ {name}: unexpected error: {e}")
            failed += 1

    print(f"\n{passed} passed, {failed} failed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    print("Running sync-wiki tests...")
    raise SystemExit(run_tests())
