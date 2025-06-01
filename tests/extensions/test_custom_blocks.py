#!/usr/bin/env python3
"""Unit tests for the custom blocks extension."""

import xml.etree.ElementTree as etree
from unittest.mock import Mock

import markdown
import pytest

from md_to_pdf.extensions.custom_blocks import (
    CustomBlockExtension,
    CustomBlockProcessor,
)
from md_to_pdf.templating import TemplateManager


class TestCustomBlockProcessor:
    """Test cases for the CustomBlockProcessor class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_template_manager = Mock(spec=TemplateManager)
        self.mock_template_manager.is_component_registered.return_value = True
        self.mock_template_manager.render_component.return_value = (
            "<div>Mock Template</div>"
        )

        # Create a mock markdown parser
        self.mock_parser = Mock()
        self.processor = CustomBlockProcessor(
            self.mock_parser, self.mock_template_manager
        )

        # Create a mock parent element
        self.mock_parent = Mock(spec=etree.Element)

    def test_test_method_detects_custom_blocks(self):
        """Test that the test method correctly identifies custom blocks."""
        # Test valid custom block syntax
        block = ':::tip_box color="blue"\n    Content here\n:::'
        assert self.processor.test(self.mock_parent, block) is True

        # Test with attributes
        block = ':::attention_box type="warning" important\n    Content\n:::'
        assert self.processor.test(self.mock_parent, block) is True

        # Test without attributes
        block = ":::magic_secret\n    Secret content\n:::"
        assert self.processor.test(self.mock_parent, block) is True

    def test_test_method_rejects_non_custom_blocks(self):
        """Test that the test method rejects non-custom block syntax."""
        # Regular markdown
        block = "This is just regular text"
        assert self.processor.test(self.mock_parent, block) is False

        # Code blocks
        block = "```python\ncode here\n```"
        assert self.processor.test(self.mock_parent, block) is False

        # Invalid syntax (not enough colons)
        block = "::tip_box\n    Content\n::"
        assert self.processor.test(self.mock_parent, block) is False

        # Empty block
        block = ""
        assert self.processor.test(self.mock_parent, block) is False

    def test_parse_attributes_with_quoted_values(self):
        """Test parsing attributes with quoted values."""
        attributes_str = 'color="blue" type="info" title="My Title"'
        attrs = self.processor._parse_attributes(attributes_str)

        expected = {"color": "blue", "type": "info", "title": "My Title"}
        assert attrs == expected

    def test_parse_attributes_with_single_quotes(self):
        """Test parsing attributes with single quotes."""
        attributes_str = "color='red' type='warning'"
        attrs = self.processor._parse_attributes(attributes_str)

        expected = {"color": "red", "type": "warning"}
        assert attrs == expected

    def test_parse_attributes_with_unquoted_values(self):
        """Test parsing attributes with unquoted values."""
        attributes_str = "color=blue important urgent level=5"
        attrs = self.processor._parse_attributes(attributes_str)

        # Check key-value pairs
        assert attrs["color"] == "blue"
        assert attrs["level"] == "5"

        # Check that flags are stored in _positional
        assert "_positional" in attrs
        assert "important" in attrs["_positional"]
        assert "urgent" in attrs["_positional"]

    def test_parse_attributes_mixed_quotes_and_flags(self):
        """Test parsing attributes with mixed quoted values and flags."""
        attributes_str = 'color="blue" important type=warning disabled'
        attrs = self.processor._parse_attributes(attributes_str)

        # Check the key-value pairs
        assert attrs["color"] == "blue"
        assert attrs["type"] == "warning"

        # Check that flags are in _positional
        assert "_positional" in attrs
        assert "important" in attrs["_positional"]
        assert "disabled" in attrs["_positional"]

    def test_parse_attributes_empty_string(self):
        """Test parsing empty attributes string."""
        attrs = self.processor._parse_attributes("")
        assert attrs == {}

    def test_parse_attributes_whitespace_only(self):
        """Test parsing whitespace-only attributes string."""
        attrs = self.processor._parse_attributes("   \t  ")
        assert attrs == {}

    def test_dedent_content_removes_indentation(self):
        """Test that content indentation is properly removed."""
        content = "    Line 1\n    Line 2\n        Indented more\n    Line 3"
        dedented = self.processor._dedent_content(content)

        expected = "Line 1\nLine 2\n    Indented more\nLine 3"
        assert dedented == expected

    def test_dedent_content_handles_mixed_indentation(self):
        """Test dedenting content with mixed indentation."""
        content = "\t\tLine 1\n\t\tLine 2\n\t\t\tExtra indent\n\t\tLine 3"
        dedented = self.processor._dedent_content(content)

        expected = "Line 1\nLine 2\n\tExtra indent\nLine 3"
        assert dedented == expected

    def test_dedent_content_handles_empty_lines(self):
        """Test dedenting content with empty lines."""
        content = "    Line 1\n\n    Line 2\n    \n    Line 3"
        dedented = self.processor._dedent_content(content)

        expected = "Line 1\n\nLine 2\n\nLine 3"
        assert dedented == expected


class TestCustomBlockExtension:
    """Test cases for the CustomBlockExtension class."""

    def test_extension_registers_processor(self):
        """Test that the extension properly registers the block processor."""
        mock_md = Mock()
        mock_md.parser = Mock()
        mock_md.parser.blockprocessors = Mock()

        extension = CustomBlockExtension()
        extension.extendMarkdown(mock_md)

        # Check that the processor was registered
        mock_md.parser.blockprocessors.register.assert_called_once()
        call_args = mock_md.parser.blockprocessors.register.call_args

        # Should be called with processor instance and name
        assert call_args[0][1] == "custom_blocks"  # name
        assert isinstance(call_args[0][0], CustomBlockProcessor)  # processor instance

    def test_extension_with_template_manager(self):
        """Test extension initialization with a template manager."""
        mock_template_manager = Mock(spec=TemplateManager)
        extension = CustomBlockExtension(template_manager=mock_template_manager)

        # The template manager should be stored as instance variable
        assert extension.template_manager == mock_template_manager


class TestCustomBlocksIntegration:
    """Integration tests for custom blocks with markdown processing."""

    def setup_method(self):
        """Set up test fixtures for integration tests."""
        self.mock_template_manager = Mock(spec=TemplateManager)
        self.mock_template_manager.is_component_registered.return_value = True

    def test_basic_custom_block_conversion(self):
        """Test basic custom block conversion to HTML."""
        self.mock_template_manager.render_component.return_value = (
            '<div class="tip-box">Rendered content</div>'
        )

        md = markdown.Markdown(
            extensions=[CustomBlockExtension(self.mock_template_manager)]
        )

        markdown_text = """
# Title

:::tip_box color="blue"
    This is a tip.
:::

Regular paragraph.
"""

        html = md.convert(markdown_text)

        # Check that template manager was called
        self.mock_template_manager.render_component.assert_called_once()
        call_args = self.mock_template_manager.render_component.call_args[0]

        assert call_args[0] == "tip_box"  # component name
        assert call_args[1]["color"] == "blue"  # attributes
        assert "This is a tip." in call_args[2]  # content

        # Check HTML output contains rendered template
        assert '<div class="tip-box">Rendered content</div>' in html
        assert "<h1>Title</h1>" in html
        assert "<p>Regular paragraph.</p>" in html

    def test_multiple_custom_blocks(self):
        """Test multiple custom blocks in the same document."""

        def mock_render(component_name, attributes, content):
            return f'<div class="{component_name}">Mock {component_name}</div>'

        self.mock_template_manager.render_component.side_effect = mock_render

        md = markdown.Markdown(
            extensions=[CustomBlockExtension(self.mock_template_manager)]
        )

        markdown_text = """
:::tip_box
    Tip content
:::

:::attention_box type="warning"
    Warning content
:::

:::magic_secret
    Secret content
:::
"""

        html = md.convert(markdown_text)

        # Check that all components were rendered
        assert self.mock_template_manager.render_component.call_count == 3
        assert '<div class="tip_box">Mock tip_box</div>' in html
        assert '<div class="attention_box">Mock attention_box</div>' in html
        assert '<div class="magic_secret">Mock magic_secret</div>' in html

    def test_custom_block_with_raw_content(self):
        """Test custom blocks containing raw content (not processed as markdown)."""

        def mock_render(component_name, attributes, content):
            return f'<div class="{component_name}">{content}</div>'

        self.mock_template_manager.render_component.side_effect = mock_render

        md = markdown.Markdown(
            extensions=[CustomBlockExtension(self.mock_template_manager)]
        )

        markdown_text = """
:::tip_box
    This has **bold** text and *italic* text.
    
    And a [link](http://example.com).
:::
"""

        html = md.convert(markdown_text)

        # Check that markdown within the block was NOT processed (raw content)
        call_args = self.mock_template_manager.render_component.call_args[0]
        content = call_args[2]

        assert "**bold**" in content  # Raw markdown, not processed
        assert "*italic*" in content  # Raw markdown, not processed
        assert "[link](http://example.com)" in content  # Raw markdown, not processed

    def test_unregistered_component_fallback(self):
        """Test fallback behavior for unregistered components."""
        self.mock_template_manager.is_component_registered.return_value = False

        md = markdown.Markdown(
            extensions=[CustomBlockExtension(self.mock_template_manager)]
        )

        markdown_text = """
:::unknown_component color="red"
    This component is not registered.
:::
"""

        html = md.convert(markdown_text)

        # Should create a fallback div
        assert 'class="custom-block unknown_component"' in html
        assert 'data-color="red"' in html
        assert "This component is not registered." in html

    def test_block_with_closing_fence(self):
        """Test custom blocks with explicit closing fence."""
        self.mock_template_manager.render_component.return_value = (
            "<div>Mock content</div>"
        )

        md = markdown.Markdown(
            extensions=[CustomBlockExtension(self.mock_template_manager)]
        )

        markdown_text = """
:::tip_box
    Content inside block.
    
    More content.
:::

This is outside the block.
"""

        html = md.convert(markdown_text)

        # Check content was properly separated
        call_args = self.mock_template_manager.render_component.call_args[0]
        content = call_args[2]

        assert "Content inside block." in content
        assert "More content." in content
        assert "This is outside the block." not in content

        # Check outside content was processed separately
        assert "<p>This is outside the block.</p>" in html


# Fixtures for pytest
@pytest.fixture
def sample_markdown():
    """Sample markdown content for testing."""
    return """
# Test Document

Regular paragraph before.

:::tip_box color="blue" important
    This is a tip with **bold** content.
    
    Multiple paragraphs are supported.
:::

:::attention_box type="warning"
    This is a warning message.
:::

Regular paragraph after.
"""


@pytest.fixture
def mock_template_manager():
    """Mock template manager for testing."""
    manager = Mock(spec=TemplateManager)
    manager.is_component_registered.return_value = True
    manager.render_component.return_value = "<div>Mock rendered content</div>"
    return manager


def test_make_extension_function():
    """Test the makeExtension function."""
    from md_to_pdf.extensions.custom_blocks import makeExtension

    ext = makeExtension()
    assert isinstance(ext, CustomBlockExtension)

    # Test with template manager
    mock_tm = Mock()
    ext = makeExtension(template_manager=mock_tm)
    assert ext.template_manager == mock_tm
