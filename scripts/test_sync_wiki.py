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
_is_separator_row = sync_wiki._is_separator_row
convert_links = sync_wiki.convert_links
strip_markdown_formatting = sync_wiki.strip_markdown_formatting

# Import check_wiki_links functions for testing
import check_wiki_links

_split_wiki_link_on_pipe = check_wiki_links._split_wiki_link_on_pipe
extract_wiki_links = check_wiki_links.extract_wiki_links


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

    def test_table_row_with_separator_chars_as_content(self) -> None:
        """Table rows with separator chars as content should be detected as table rows.

        This tests the edge case where a cell contains only characters that could
        appear in a separator row (-, :, space) but is actually content.
        """
        # Row with single dash and colon as content - should be detected as table row
        content = "| Header | Type |\n| --- | --- |\n| - | : |"
        position = content.rfind("| - |")
        assert is_in_table_row(content, position) is True

        # Row with just dashes but less than 3 consecutive - should be table row
        content2 = "| A | B |\n| --- | --- |\n| -- | - |"
        position2 = content2.rfind("| -- |")
        assert is_in_table_row(content2, position2) is True

    def test_separator_row_requires_three_dashes_in_each_cell(self) -> None:
        """Per GFM spec, each cell in a separator row must have at least 3 consecutive dashes."""
        # Valid separator - all cells have 3+ dashes
        assert _is_separator_row("| --- | --- |") is True
        assert _is_separator_row("|---|---|") is True
        assert _is_separator_row("| :---: | :--- |") is True
        assert _is_separator_row("| ---- | ----- |") is True

        # Invalid - less than 3 consecutive dashes in any cell
        assert _is_separator_row("| -- | -- |") is False
        assert _is_separator_row("| - | - |") is False
        assert _is_separator_row("| : | : |") is False

        # Invalid - mixed cells where at least one cell has < 3 dashes
        # Per GFM spec, ALL cells must have 3+ dashes, not just one
        assert _is_separator_row("| --- | - |") is False
        assert _is_separator_row("| - | --- |") is False
        assert _is_separator_row("| --- | -- |") is False


class TestConvertLinksShortFormat:
    """Tests for short format optimization when display text matches page name."""

    def test_matching_display_text_uses_short_format(self) -> None:
        """When link text matches wiki page name, use short format [[PageName]]."""
        content = "[Coroutines](./05-coroutines.md) - Time-based operations"
        original_structure = sync_wiki.WIKI_STRUCTURE.copy()
        try:
            sync_wiki.WIKI_STRUCTURE["05-coroutines.md"] = "Coroutines"
            result = convert_links(content, "best-practices/README.md")
            # Should use short format since "Coroutines" == "Coroutines"
            assert "[[Coroutines]]" in result
            # Should NOT have redundant format
            assert "[[Coroutines|Coroutines]]" not in result
        finally:
            sync_wiki.WIKI_STRUCTURE.clear()
            sync_wiki.WIKI_STRUCTURE.update(original_structure)

    def test_different_display_text_uses_long_format(self) -> None:
        """When link text differs from wiki page name, use long format."""
        content = "[Performance & Memory](./07-performance-memory.md) - GC tips"
        original_structure = sync_wiki.WIKI_STRUCTURE.copy()
        try:
            sync_wiki.WIKI_STRUCTURE["07-performance-memory.md"] = (
                "Performance-and-Memory"
            )
            result = convert_links(content, "best-practices/README.md")
            # Should use long format since display text differs
            assert "[[Performance & Memory|Performance-and-Memory]]" in result
        finally:
            sync_wiki.WIKI_STRUCTURE.clear()
            sync_wiki.WIKI_STRUCTURE.update(original_structure)

    def test_short_format_with_anchor(self) -> None:
        """Short format should work correctly with anchors."""
        content = "[Coroutines](./05-coroutines.md#starting-coroutines) - Start tips"
        original_structure = sync_wiki.WIKI_STRUCTURE.copy()
        try:
            sync_wiki.WIKI_STRUCTURE["05-coroutines.md"] = "Coroutines"
            result = convert_links(content, "best-practices/README.md")
            # Should use short format with anchor
            assert "[[Coroutines#starting-coroutines]]" in result
            assert "[[Coroutines|Coroutines#" not in result
        finally:
            sync_wiki.WIKI_STRUCTURE.clear()
            sync_wiki.WIKI_STRUCTURE.update(original_structure)

    def test_table_context_matching_text_uses_short_format(self) -> None:
        """In tables, matching display text should still use short format (no pipe needed)."""
        content = "| [Coroutines](./05-coroutines.md) | Description |\n| --- | --- |"
        original_structure = sync_wiki.WIKI_STRUCTURE.copy()
        try:
            sync_wiki.WIKI_STRUCTURE["05-coroutines.md"] = "Coroutines"
            result = convert_links(content, "best-practices/README.md")
            # Should use short format even in tables since no pipe is needed
            assert "[[Coroutines]]" in result
            assert "[[Coroutines\\|Coroutines]]" not in result
        finally:
            sync_wiki.WIKI_STRUCTURE.clear()
            sync_wiki.WIKI_STRUCTURE.update(original_structure)


class TestConvertLinksTableIntegration:
    """Integration tests for convert_links with table detection."""

    def test_link_in_table_gets_escaped_pipe(self) -> None:
        """Links inside tables should have escaped pipes in wiki format."""
        # Link from README.md to docs/tool.md resolves to "tool" after stripping docs/ prefix
        content = "| [Tool](./docs/tool.md) | Description |\n| --- | --- |"
        # Mock the WIKI_STRUCTURE for this test
        original_structure = sync_wiki.WIKI_STRUCTURE.copy()
        try:
            # Key is "tool.md" because path resolves to "docs/tool.md",
            # then docs/ is stripped, leaving "tool.md"
            sync_wiki.WIKI_STRUCTURE["tool.md"] = "Tool-Page"
            result = convert_links(content, "README.md")
            # Should have escaped pipe in table
            assert "[[Tool\\|Tool-Page]]" in result
        finally:
            sync_wiki.WIKI_STRUCTURE.clear()
            sync_wiki.WIKI_STRUCTURE.update(original_structure)

    def test_link_outside_table_gets_normal_pipe(self) -> None:
        """Links outside tables should have normal pipes in wiki format."""
        content = "Check out [Tool](./docs/tool.md) for more info."
        original_structure = sync_wiki.WIKI_STRUCTURE.copy()
        try:
            sync_wiki.WIKI_STRUCTURE["tool.md"] = "Tool-Page"
            result = convert_links(content, "README.md")
            # Should have normal pipe outside table
            assert "[[Tool|Tool-Page]]" in result
            assert "\\|" not in result
        finally:
            sync_wiki.WIKI_STRUCTURE.clear()
            sync_wiki.WIKI_STRUCTURE.update(original_structure)

    def test_mixed_table_and_non_table_links(self) -> None:
        """Document with both table and non-table links should handle both correctly."""
        content = """# Guide

See [Overview](./docs/overview.md) for details.

| Tool | Link |
| --- | --- |
| First | [Tool1](./docs/tool1.md) |
| Second | [Tool2](./docs/tool2.md) |

More info at [Tool1](./docs/tool1.md).
"""
        original_structure = sync_wiki.WIKI_STRUCTURE.copy()
        try:
            sync_wiki.WIKI_STRUCTURE["overview.md"] = "Overview"
            sync_wiki.WIKI_STRUCTURE["tool1.md"] = "Tool1-Page"
            sync_wiki.WIKI_STRUCTURE["tool2.md"] = "Tool2-Page"
            result = convert_links(content, "README.md")

            # Non-table links with matching display text use short format
            assert "[[Overview]]" in result

            # Table links should have escaped pipes
            assert "[[Tool1\\|Tool1-Page]]" in result
            assert "[[Tool2\\|Tool2-Page]]" in result

            # The final non-table link to Tool1 should have normal pipe
            # Count occurrences - should be 1 escaped (in table) and 1 normal (outside)
            assert result.count("[[Tool1\\|Tool1-Page]]") == 1
            assert result.count("[[Tool1|Tool1-Page]]") == 1
        finally:
            sync_wiki.WIKI_STRUCTURE.clear()
            sync_wiki.WIKI_STRUCTURE.update(original_structure)


class TestStripMarkdownFormatting:
    """Tests for the strip_markdown_formatting function."""

    def test_bold_double_asterisk(self) -> None:
        """Bold text with ** should be stripped."""
        assert strip_markdown_formatting("**Coroutines**") == "Coroutines"

    def test_bold_double_underscore(self) -> None:
        """Bold text with __ should be stripped."""
        assert strip_markdown_formatting("__bold__") == "bold"

    def test_italic_single_asterisk(self) -> None:
        """Italic text with * should be stripped."""
        assert strip_markdown_formatting("*italic*") == "italic"

    def test_italic_single_underscore(self) -> None:
        """Italic text with _ should be stripped (word boundaries only)."""
        assert strip_markdown_formatting("_italic_") == "italic"

    def test_preserves_snake_case(self) -> None:
        """Underscores in snake_case should be preserved."""
        assert strip_markdown_formatting("snake_case_var") == "snake_case_var"

    def test_mixed_formatting(self) -> None:
        """Mixed bold and italic should all be stripped."""
        assert strip_markdown_formatting("**bold** and *italic*") == "bold and italic"

    def test_no_formatting(self) -> None:
        """Plain text should be unchanged."""
        assert strip_markdown_formatting("plain text") == "plain text"

    def test_nested_formatting(self) -> None:
        """Nested bold and italic should be fully stripped."""
        assert strip_markdown_formatting("**_bold italic_**") == "bold italic"
        assert strip_markdown_formatting("*__italic bold__*") == "italic bold"

    def test_multiple_occurrences(self) -> None:
        """Multiple formatted sections should all be stripped."""
        assert strip_markdown_formatting("**bold1** and **bold2**") == "bold1 and bold2"
        assert strip_markdown_formatting("*a* *b* *c*") == "a b c"


class TestConvertLinksStripsFormatting:
    """Tests for convert_links stripping markdown formatting from links."""

    def test_bold_link_text_stripped(self) -> None:
        """Bold formatting inside link text should be stripped."""
        content = "[**Coroutines**](./05-coroutines.md) - Time-based operations"
        original_structure = sync_wiki.WIKI_STRUCTURE.copy()
        try:
            sync_wiki.WIKI_STRUCTURE["05-coroutines.md"] = "Coroutines"
            result = convert_links(content, "best-practices/README.md")
            # Should use short format since stripped text matches
            assert "[[Coroutines]]" in result
            # Should NOT have bold markers inside the link
            assert "[[**Coroutines**" not in result
        finally:
            sync_wiki.WIKI_STRUCTURE.clear()
            sync_wiki.WIKI_STRUCTURE.update(original_structure)

    def test_bold_link_with_different_page_name(self) -> None:
        """Bold formatting stripped, but different display text preserved."""
        content = "[**Lifecycle Methods**](./01-lifecycle-methods.md)"
        original_structure = sync_wiki.WIKI_STRUCTURE.copy()
        try:
            sync_wiki.WIKI_STRUCTURE["01-lifecycle-methods.md"] = "Lifecycle-Methods"
            result = convert_links(content, "best-practices/README.md")
            # Should use long format with clean display text
            assert "[[Lifecycle Methods|Lifecycle-Methods]]" in result
            # Should NOT have bold markers
            assert "**" not in result
        finally:
            sync_wiki.WIKI_STRUCTURE.clear()
            sync_wiki.WIKI_STRUCTURE.update(original_structure)


class TestSplitWikiLinkOnPipe:
    """Tests for the _split_wiki_link_on_pipe helper function."""

    def test_no_pipe(self) -> None:
        """Links without pipe should return empty display text."""
        display, page = _split_wiki_link_on_pipe("PageName")
        assert display == ""
        assert page == "PageName"

    def test_simple_pipe(self) -> None:
        """Links with simple pipe should split correctly."""
        display, page = _split_wiki_link_on_pipe("Display Text|PageName")
        assert display == "Display Text"
        assert page == "PageName"

    def test_escaped_pipe(self) -> None:
        """Escaped pipes in table context should be handled correctly."""
        display, page = _split_wiki_link_on_pipe("Display Text\\|PageName")
        assert display == "Display Text"
        assert page == "PageName"

    def test_escaped_pipe_with_anchor(self) -> None:
        """Escaped pipes with anchors should work correctly."""
        display, page = _split_wiki_link_on_pipe("Display\\|PageName#anchor")
        assert display == "Display"
        assert page == "PageName#anchor"

    def test_multiple_pipes_uses_last(self) -> None:
        """Multiple pipes should split on the last one."""
        display, page = _split_wiki_link_on_pipe("Text|With|Pipes|PageName")
        assert display == "Text|With|Pipes"
        assert page == "PageName"

    def test_page_name_only_with_anchor(self) -> None:
        """Page name with anchor but no display text."""
        display, page = _split_wiki_link_on_pipe("PageName#section")
        assert display == ""
        assert page == "PageName#section"


class TestExtractWikiLinksEscapedPipes:
    """Tests for extract_wiki_links handling of escaped pipes."""

    def test_normal_link_extraction(self) -> None:
        """Normal links should be extracted correctly."""
        content = "See [[PageName]] for details."
        links = extract_wiki_links(content)
        assert len(links) == 1
        assert links[0].page_name == "PageName"
        assert links[0].anchor == ""

    def test_link_with_display_text(self) -> None:
        """Links with display text should be extracted correctly."""
        content = "See [[Display Text|PageName]] for details."
        links = extract_wiki_links(content, include_display_text=True)
        assert len(links) == 1
        assert links[0].display_text == "Display Text"
        assert links[0].page_name == "PageName"

    def test_escaped_pipe_link(self) -> None:
        """Links with escaped pipes should be extracted correctly."""
        content = "| [[Display\\|PageName]] | Description |"
        links = extract_wiki_links(content, include_display_text=True)
        assert len(links) == 1
        assert links[0].display_text == "Display"
        assert links[0].page_name == "PageName"

    def test_link_with_anchor(self) -> None:
        """Links with anchors should be extracted correctly."""
        content = "See [[PageName#section]] for details."
        links = extract_wiki_links(content)
        assert len(links) == 1
        assert links[0].page_name == "PageName"
        assert links[0].anchor == "#section"

    def test_escaped_pipe_with_anchor(self) -> None:
        """Escaped pipe links with anchors should work correctly."""
        content = "| [[Display\\|PageName#anchor]] | Info |"
        links = extract_wiki_links(content, include_display_text=True)
        assert len(links) == 1
        assert links[0].display_text == "Display"
        assert links[0].page_name == "PageName"
        assert links[0].anchor == "#anchor"


def run_tests() -> int:
    """Run all tests and return exit code."""
    test_instance = TestIsInTableRow()
    short_format_instance = TestConvertLinksShortFormat()
    integration_instance = TestConvertLinksTableIntegration()
    strip_formatting_instance = TestStripMarkdownFormatting()
    convert_strips_instance = TestConvertLinksStripsFormatting()
    split_pipe_instance = TestSplitWikiLinkOnPipe()
    escaped_pipes_instance = TestExtractWikiLinksEscapedPipes()
    tests = [
        # TestIsInTableRow tests
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
        (
            test_instance.test_table_row_with_separator_chars_as_content,
            "table_row_with_separator_chars_as_content",
        ),
        (
            test_instance.test_separator_row_requires_three_dashes_in_each_cell,
            "separator_row_requires_three_dashes_in_each_cell",
        ),
        # TestConvertLinksShortFormat tests
        (
            short_format_instance.test_matching_display_text_uses_short_format,
            "short_format_matching_display_text",
        ),
        (
            short_format_instance.test_different_display_text_uses_long_format,
            "short_format_different_display_text",
        ),
        (
            short_format_instance.test_short_format_with_anchor,
            "short_format_with_anchor",
        ),
        (
            short_format_instance.test_table_context_matching_text_uses_short_format,
            "short_format_in_table_context",
        ),
        # TestConvertLinksTableIntegration tests
        (
            integration_instance.test_link_in_table_gets_escaped_pipe,
            "integration_link_in_table_escaped",
        ),
        (
            integration_instance.test_link_outside_table_gets_normal_pipe,
            "integration_link_outside_table_normal",
        ),
        (
            integration_instance.test_mixed_table_and_non_table_links,
            "integration_mixed_table_and_non_table",
        ),
        # TestStripMarkdownFormatting tests
        (
            strip_formatting_instance.test_bold_double_asterisk,
            "strip_formatting_bold_asterisk",
        ),
        (
            strip_formatting_instance.test_bold_double_underscore,
            "strip_formatting_bold_underscore",
        ),
        (
            strip_formatting_instance.test_italic_single_asterisk,
            "strip_formatting_italic_asterisk",
        ),
        (
            strip_formatting_instance.test_italic_single_underscore,
            "strip_formatting_italic_underscore",
        ),
        (
            strip_formatting_instance.test_preserves_snake_case,
            "strip_formatting_preserves_snake_case",
        ),
        (
            strip_formatting_instance.test_mixed_formatting,
            "strip_formatting_mixed",
        ),
        (
            strip_formatting_instance.test_no_formatting,
            "strip_formatting_plain_text",
        ),
        (
            strip_formatting_instance.test_nested_formatting,
            "strip_formatting_nested",
        ),
        (
            strip_formatting_instance.test_multiple_occurrences,
            "strip_formatting_multiple",
        ),
        # TestConvertLinksStripsFormatting tests
        (
            convert_strips_instance.test_bold_link_text_stripped,
            "convert_links_strips_bold",
        ),
        (
            convert_strips_instance.test_bold_link_with_different_page_name,
            "convert_links_strips_bold_different_page",
        ),
        # TestSplitWikiLinkOnPipe tests
        (split_pipe_instance.test_no_pipe, "split_pipe_no_pipe"),
        (split_pipe_instance.test_simple_pipe, "split_pipe_simple"),
        (split_pipe_instance.test_escaped_pipe, "split_pipe_escaped"),
        (
            split_pipe_instance.test_escaped_pipe_with_anchor,
            "split_pipe_escaped_anchor",
        ),
        (split_pipe_instance.test_multiple_pipes_uses_last, "split_pipe_multiple"),
        (split_pipe_instance.test_page_name_only_with_anchor, "split_pipe_anchor_only"),
        # TestExtractWikiLinksEscapedPipes tests
        (escaped_pipes_instance.test_normal_link_extraction, "escaped_pipes_normal"),
        (escaped_pipes_instance.test_link_with_display_text, "escaped_pipes_display"),
        (escaped_pipes_instance.test_escaped_pipe_link, "escaped_pipes_escaped"),
        (escaped_pipes_instance.test_link_with_anchor, "escaped_pipes_anchor"),
        (escaped_pipes_instance.test_escaped_pipe_with_anchor, "escaped_pipes_both"),
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
