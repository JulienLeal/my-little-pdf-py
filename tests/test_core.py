"""Tests for the core MD to PDF converter functionality."""

import tempfile
from pathlib import Path

import pytest

from src.md_to_pdf.core import MarkdownProcessor, MarkdownToPDFConverter, PDFGenerator


def test_markdown_processor():
    """Test the MarkdownProcessor class."""
    processor = MarkdownProcessor()

    # Test basic conversion
    result = processor.convert("# Hello **World**")
    assert "<h1>" in result
    assert "<strong>" in result
    assert "Hello" in result
    assert "World" in result


def test_markdown_processor_file():
    """Test MarkdownProcessor with file input."""
    processor = MarkdownProcessor()

    # Create a temporary markdown file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("# Test\n\nThis is a **test**.")
        temp_path = Path(f.name)

    try:
        result = processor.convert_file(temp_path)
        assert "<h1>Test</h1>" in result
        assert "<strong>test</strong>" in result
    finally:
        temp_path.unlink()  # Clean up


def test_markdown_processor_file_not_found():
    """Test MarkdownProcessor with non-existent file."""
    processor = MarkdownProcessor()

    with pytest.raises(FileNotFoundError):
        processor.convert_file(Path("nonexistent.md"))


def test_converter_initialization():
    """Test MarkdownToPDFConverter initialization."""
    converter = MarkdownToPDFConverter()

    # Should have markdown processor
    assert hasattr(converter, "markdown_processor")
    assert isinstance(converter.markdown_processor, MarkdownProcessor)

    # Should have pdf generator
    assert hasattr(converter, "pdf_generator")
    assert isinstance(converter.pdf_generator, PDFGenerator)


def test_converter_availability():
    """Test converter availability check."""
    converter = MarkdownToPDFConverter()

    # Should return a boolean
    available = converter.is_available()
    assert isinstance(available, bool)


def test_converter_string_to_html():
    """Test converting markdown string to HTML (without PDF generation)."""
    converter = MarkdownToPDFConverter()

    markdown_content = """
# Test Document

This is a **test** document.

- Item 1
- Item 2
"""

    html_result = converter.markdown_processor.convert(markdown_content)
    assert "<h1>Test Document</h1>" in html_result
    assert "<strong>test</strong>" in html_result
    assert "<ul>" in html_result
    assert "<li>Item 1</li>" in html_result
