#!/usr/bin/env python3
"""Test script to verify error handling in the Markdown to PDF converter."""

import sys
from pathlib import Path

# Add src to path so we can import our modules
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from md_to_pdf.core import MarkdownProcessingError, MarkdownToPDFConverter


def test_file_not_found():
    """Test handling of missing input files."""
    print("🧪 Testing file not found error...")

    converter = MarkdownToPDFConverter()
    non_existent_file = Path("non_existent_file.md")
    output_file = Path("test_output.pdf")

    try:
        converter.convert_file(non_existent_file, output_file)
        print("❌ Expected FileNotFoundError but conversion succeeded")
        return False
    except FileNotFoundError as e:
        print(f"✅ Correctly caught FileNotFoundError: {e}")
        return True
    except Exception as e:
        print(f"❌ Unexpected error type: {type(e).__name__}: {e}")
        return False


def test_empty_markdown():
    """Test handling of empty markdown content."""
    print("\n🧪 Testing empty markdown content...")

    converter = MarkdownToPDFConverter()
    output_file = Path("test_empty_output.pdf")

    try:
        converter.convert_string("", output_file, "Empty Test")
        print("❌ Expected MarkdownProcessingError but conversion succeeded")
        return False
    except MarkdownProcessingError as e:
        print(f"✅ Correctly caught MarkdownProcessingError: {e}")
        return True
    except Exception as e:
        print(f"❌ Unexpected error type: {type(e).__name__}: {e}")
        return False


def test_whitespace_only_markdown():
    """Test handling of whitespace-only markdown content."""
    print("\n🧪 Testing whitespace-only markdown content...")

    converter = MarkdownToPDFConverter()
    output_file = Path("test_whitespace_output.pdf")

    try:
        converter.convert_string("   \n\n   \t   \n   ", output_file, "Whitespace Test")
        print("❌ Expected MarkdownProcessingError but conversion succeeded")
        return False
    except MarkdownProcessingError as e:
        print(f"✅ Correctly caught MarkdownProcessingError: {e}")
        return True
    except Exception as e:
        print(f"❌ Unexpected error type: {type(e).__name__}: {e}")
        return False


def test_invalid_file_extension():
    """Test handling of files with non-markdown extensions."""
    print("\n🧪 Testing invalid file extension...")

    # Create a test file with non-markdown extension
    test_file = Path("test_file.txt")
    test_file.write_text("# This is markdown but has wrong extension")

    converter = MarkdownToPDFConverter()
    output_file = Path("test_extension_output.pdf")

    try:
        converter.convert_file(test_file, output_file)
        print("❌ Expected MarkdownProcessingError but conversion succeeded")
        test_file.unlink()  # Clean up
        return False
    except MarkdownProcessingError as e:
        print(f"✅ Correctly caught MarkdownProcessingError: {e}")
        test_file.unlink()  # Clean up
        return True
    except Exception as e:
        print(f"❌ Unexpected error type: {type(e).__name__}: {e}")
        test_file.unlink()  # Clean up
        return False


def test_directory_instead_of_file():
    """Test handling when a directory is passed instead of a file."""
    print("\n🧪 Testing directory instead of file...")

    converter = MarkdownToPDFConverter()
    directory_path = Path("examples")  # This is a directory
    output_file = Path("test_dir_output.pdf")

    try:
        converter.convert_file(directory_path, output_file)
        print("❌ Expected FileNotFoundError but conversion succeeded")
        return False
    except FileNotFoundError as e:
        print(f"✅ Correctly caught FileNotFoundError: {e}")
        return True
    except Exception as e:
        print(f"❌ Unexpected error type: {type(e).__name__}: {e}")
        return False


def test_successful_conversion():
    """Test that normal conversions still work after error handling improvements."""
    print("\n🧪 Testing successful conversion still works...")

    converter = MarkdownToPDFConverter()
    markdown_content = "# Test\n\nThis should work fine."
    output_file = Path("examples/test_success.pdf")

    try:
        converter.convert_string(markdown_content, output_file, "Success Test")
        if output_file.exists():
            file_size = output_file.stat().st_size
            print(f"✅ Successful conversion: PDF created ({file_size} bytes)")
            return True
        else:
            print("❌ PDF file was not created")
            return False
    except Exception as e:
        print(f"❌ Unexpected error in successful conversion: {e}")
        return False


def main():
    """Run all error handling tests."""
    print("🚀 Testing Enhanced Error Handling")
    print("=" * 50)

    tests = [
        test_file_not_found,
        test_empty_markdown,
        test_whitespace_only_markdown,
        test_invalid_file_extension,
        test_directory_instead_of_file,
        test_successful_conversion,
    ]

    results = []
    for test in tests:
        results.append(test())

    # Summary
    print("\n" + "=" * 50)
    print("📊 Error Handling Test Summary:")

    test_names = [
        "File not found",
        "Empty markdown",
        "Whitespace-only markdown",
        "Invalid file extension",
        "Directory instead of file",
        "Successful conversion",
    ]

    for name, result in zip(test_names, results):
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {name}: {status}")

    passed_count = sum(results)
    total_count = len(results)

    if passed_count == total_count:
        print(f"\n🎉 All {total_count} error handling tests passed!")
        return 0
    else:
        print(f"\n💥 {total_count - passed_count}/{total_count} tests failed.")
        return 1


if __name__ == "__main__":
    exit(main())
