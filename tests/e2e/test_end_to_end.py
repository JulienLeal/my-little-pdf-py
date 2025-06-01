#!/usr/bin/env python3
"""End-to-end test for the Markdown to PDF conversion pipeline."""

import sys
from pathlib import Path

# Add src to path so we can import our modules
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from md_to_pdf.core import MarkdownToPDFConverter


def test_basic_conversion():
    """Test basic Markdown to PDF conversion with sample.md."""
    print("🧪 Starting end-to-end test...")

    # Define paths
    input_file = Path("examples/sample.md")
    output_file = Path("examples/sample_output.pdf")

    # Check if input file exists
    if not input_file.exists():
        print(f"❌ Input file not found: {input_file}")
        return False

    try:
        # Initialize converter
        print("📝 Initializing converter...")
        converter = MarkdownToPDFConverter()

        # Check if converter is available
        if not converter.is_available():
            print("❌ Converter dependencies not available")
            return False

        print("✅ Converter initialized successfully")

        # Convert file
        print(f"🔄 Converting {input_file} to {output_file}...")
        converter.convert_file(input_file, output_file)

        # Verify output file was created
        if output_file.exists():
            file_size = output_file.stat().st_size
            print(f"✅ End-to-end test passed! PDF created ({file_size} bytes)")
            return True
        else:
            print("❌ PDF file was not created")
            return False

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False


def test_string_conversion():
    """Test Markdown string to PDF conversion."""
    print("\n🧪 Testing string conversion...")

    markdown_content = """
# Test Document

This is a **test** of string conversion.

- Item 1
- Item 2
- Item 3

## Code Block

```python
print("Hello from string conversion!")
```
"""

    output_file = Path("examples/string_test_output.pdf")

    try:
        converter = MarkdownToPDFConverter()
        print("🔄 Converting markdown string to PDF...")
        converter.convert_string(markdown_content, output_file, "String Test Document")

        if output_file.exists():
            file_size = output_file.stat().st_size
            print(f"✅ String conversion test passed! PDF created ({file_size} bytes)")
            return True
        else:
            print("❌ PDF file was not created")
            return False

    except Exception as e:
        print(f"❌ String conversion test failed: {e}")
        return False


def main():
    """Run all end-to-end tests."""
    print("🚀 Running Markdown to PDF Pipeline Tests")
    print("=" * 50)

    # Test 1: File conversion
    test1_passed = test_basic_conversion()

    # Test 2: String conversion
    test2_passed = test_string_conversion()

    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print(f"   File conversion: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"   String conversion: {'✅ PASSED' if test2_passed else '❌ FAILED'}")

    if test1_passed and test2_passed:
        print("\n🎉 All tests passed! The basic pipeline is working!")
        return 0
    else:
        print("\n💥 Some tests failed. Check the output above for details.")
        return 1


if __name__ == "__main__":
    exit(main())
