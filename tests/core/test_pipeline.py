#!/usr/bin/env python3
"""Test script for the complete Markdown to PDF pipeline."""

from pathlib import Path

from src.md_to_pdf.core import MarkdownToPDFConverter


def test_basic_pipeline():
    """Test the basic Markdown to PDF conversion pipeline."""
    print("🔍 Testing basic Markdown → PDF pipeline...")

    # Check if WeasyPrint is available
    converter = MarkdownToPDFConverter()
    if not converter.is_available():
        print("⚠️ WeasyPrint not available - testing Markdown → HTML only")

        # Test just the Markdown processing
        input_file = Path("examples/sample.md")
        if not input_file.exists():
            print(f"❌ Sample file not found: {input_file}")
            return False

        html_content = converter.markdown_processor.convert_file(input_file)
        print(f"✅ Markdown → HTML conversion successful ({len(html_content)} chars)")
        print("ℹ️ HTML preview (first 200 chars):")
        print(html_content[:200] + "..." if len(html_content) > 200 else html_content)
        return True

    # Full pipeline test
    input_file = Path("examples/sample.md")
    output_file = Path("examples/sample.pdf")

    if not input_file.exists():
        print(f"❌ Sample file not found: {input_file}")
        return False

    try:
        converter.convert_file(input_file, output_file)

        if output_file.exists() and output_file.stat().st_size > 0:
            print(
                f"✅ Complete pipeline successful! PDF size: {output_file.stat().st_size} bytes"
            )
            return True
        else:
            print("❌ PDF was not created or is empty")
            return False

    except Exception as e:
        print(f"❌ Pipeline failed: {e}")
        return False


def test_string_conversion():
    """Test converting a Markdown string directly."""
    print("\n🔍 Testing string conversion...")

    converter = MarkdownToPDFConverter()

    markdown_content = """
# Test Document

This is a **test** from a string.

- Item 1
- Item 2
- Item 3
"""

    if not converter.is_available():
        # Test just HTML conversion
        html_content = converter.markdown_processor.convert(markdown_content)
        print(f"✅ String → HTML conversion successful ({len(html_content)} chars)")
        return True

    output_file = Path("examples/string_test.pdf")

    try:
        converter.convert_string(markdown_content, output_file, "String Test")

        if output_file.exists() and output_file.stat().st_size > 0:
            print(
                f"✅ String → PDF conversion successful! PDF size: {output_file.stat().st_size} bytes"
            )
            return True
        else:
            print("❌ PDF was not created or is empty")
            return False

    except Exception as e:
        print(f"❌ String conversion failed: {e}")
        return False


def main():
    """Run all pipeline tests."""
    print("🚀 Testing Markdown-to-PDF Pipeline\n")

    tests = [test_basic_pipeline, test_string_conversion]

    results = []
    for test in tests:
        results.append(test())

    print(f"\n📊 Results: {sum(results)}/{len(results)} tests passed")

    if all(results):
        print("🎉 All pipeline tests successful!")
        return True
    else:
        print("⚠️ Some tests failed. Check output above.")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
