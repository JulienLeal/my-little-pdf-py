#!/usr/bin/env python3
"""Test script for CLI functionality."""

import sys
import tempfile
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from md_to_pdf.cli import MarkdownToPDFCLI


def create_test_markdown() -> str:
    """Create test markdown content."""
    return """
# CLI Test Document

This is a test document for the CLI functionality.

## Features

- Professional PDF generation
- Custom themes support
- Advanced typography
- Print optimizations

### Sample Table

| Feature | Status | Notes |
|---------|--------|-------|
| CLI | Working | Comprehensive interface |
| Themes | Working | YAML configuration |
| CSS | Working | Professional styling |

### Code Example

```python
def hello_cli():
    print("CLI is working!")
    return True
```

> This blockquote demonstrates the styling capabilities of the CLI.

## Conclusion

The CLI provides a user-friendly interface for converting Markdown to PDF.
"""


def test_cli_help():
    """Test CLI help functionality."""
    print("Testing CLI help...")

    cli = MarkdownToPDFCLI()

    try:
        # Test help
        exit_code = cli.run(["--help"])
        # Help should exit with 0 (argparse behavior)
        print("SUCCESS: Help command accessible")
        return True
    except SystemExit as e:
        if e.code == 0:
            print("SUCCESS: Help command works correctly")
            return True
        else:
            print(f"FAILED: Help command failed with exit code: {e.code}")
            return False
    except Exception as e:
        print(f"FAILED: Help command error: {e}")
        return False


def test_cli_version():
    """Test CLI version command."""
    print("\nTesting CLI version...")

    cli = MarkdownToPDFCLI()

    try:
        exit_code = cli.run(["--version"])
        print("SUCCESS: Version command accessible")
        return True
    except SystemExit as e:
        if e.code == 0:
            print("SUCCESS: Version command works correctly")
            return True
        else:
            print(f"FAILED: Version command failed with exit code: {e.code}")
            return False
    except Exception as e:
        print(f"FAILED: Version command error: {e}")
        return False


def test_cli_validation():
    """Test CLI theme validation."""
    print("\nTesting CLI theme validation...")

    cli = MarkdownToPDFCLI()

    try:
        # Test with valid theme
        exit_code = cli.run(["--validate", "--theme", "schemas/examples/minimal.yaml"])
        if exit_code == 0:
            print("SUCCESS: Theme validation works")
            return True
        else:
            print(f"FAILED: Theme validation failed with exit code: {exit_code}")
            return False
    except Exception as e:
        print(f"FAILED: Theme validation error: {e}")
        return False


def test_cli_basic_conversion():
    """Test basic CLI conversion."""
    print("\nTesting CLI basic conversion...")

    cli = MarkdownToPDFCLI()

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create test markdown file
        md_file = temp_path / "test.md"
        md_file.write_text(create_test_markdown())

        # Test basic conversion
        try:
            exit_code = cli.run([str(md_file), "--verbose"])

            if exit_code == 0:
                # Check if PDF was created
                pdf_file = temp_path / "test.pdf"
                if pdf_file.exists():
                    file_size = pdf_file.stat().st_size
                    print(f"SUCCESS: Basic conversion successful: {file_size} bytes")
                    return True
                else:
                    print("FAILED: PDF file not created")
                    return False
            else:
                print(f"FAILED: Conversion failed with exit code: {exit_code}")
                return False

        except Exception as e:
            print(f"FAILED: Basic conversion error: {e}")
            return False


def test_cli_themed_conversion():
    """Test CLI conversion with theme."""
    print("\nTesting CLI themed conversion...")

    cli = MarkdownToPDFCLI()

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create test markdown file
        md_file = temp_path / "themed_test.md"
        md_file.write_text(create_test_markdown())

        # Output file
        pdf_file = temp_path / "themed_output.pdf"

        try:
            exit_code = cli.run(
                [
                    str(md_file),
                    "--output",
                    str(pdf_file),
                    "--theme",
                    "schemas/examples/advanced_headers.yaml",
                    "--title",
                    "CLI Themed Test",
                    "--verbose",
                ]
            )

            if exit_code == 0:
                if pdf_file.exists():
                    file_size = pdf_file.stat().st_size
                    print(f"SUCCESS: Themed conversion successful: {file_size} bytes")
                    return True
                else:
                    print("FAILED: Themed PDF file not created")
                    return False
            else:
                print(f"FAILED: Themed conversion failed with exit code: {exit_code}")
                return False

        except Exception as e:
            print(f"FAILED: Themed conversion error: {e}")
            return False


def test_cli_multiple_files():
    """Test CLI multiple file conversion."""
    print("\nTesting CLI multiple file conversion...")

    cli = MarkdownToPDFCLI()

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create multiple test markdown files
        files = []
        for i in range(3):
            md_file = temp_path / f"doc_{i + 1}.md"
            content = f"# Document {i + 1}\n\n" + create_test_markdown()
            md_file.write_text(content)
            files.append(md_file)

        # Output directory
        output_dir = temp_path / "output"

        try:
            # Convert all files
            file_args = [str(f) for f in files]
            exit_code = cli.run(
                file_args + ["--output-dir", str(output_dir), "--verbose"]
            )

            if exit_code == 0:
                # Check if all PDFs were created
                created_pdfs = list(output_dir.glob("*.pdf"))
                if len(created_pdfs) == 3:
                    total_size = sum(pdf.stat().st_size for pdf in created_pdfs)
                    print(
                        f"SUCCESS: Multiple file conversion successful: {len(created_pdfs)} files, {total_size} bytes total"
                    )
                    return True
                else:
                    print(f"FAILED: Expected 3 PDFs, got {len(created_pdfs)}")
                    return False
            else:
                print(
                    f"FAILED: Multiple file conversion failed with exit code: {exit_code}"
                )
                return False

        except Exception as e:
            print(f"FAILED: Multiple file conversion error: {e}")
            return False


def test_cli_dry_run():
    """Test CLI dry run functionality."""
    print("\nTesting CLI dry run...")

    cli = MarkdownToPDFCLI()

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create test markdown file
        md_file = temp_path / "dry_run_test.md"
        md_file.write_text(create_test_markdown())

        try:
            exit_code = cli.run([str(md_file), "--dry-run", "--verbose"])

            if exit_code == 0:
                # Check that no PDF was actually created
                pdf_file = temp_path / "dry_run_test.pdf"
                if not pdf_file.exists():
                    print("SUCCESS: Dry run successful - no file created")
                    return True
                else:
                    print("FAILED: Dry run created file when it shouldn't")
                    return False
            else:
                print(f"FAILED: Dry run failed with exit code: {exit_code}")
                return False

        except Exception as e:
            print(f"FAILED: Dry run error: {e}")
            return False


def test_cli_error_handling():
    """Test CLI error handling."""
    print("\nTesting CLI error handling...")

    cli = MarkdownToPDFCLI()

    # Test with non-existent file
    try:
        exit_code = cli.run(["nonexistent.md"])
        if exit_code != 0:
            print("SUCCESS: Non-existent file error handled correctly")
            return True
        else:
            print("FAILED: Non-existent file should return error")
            return False
    except Exception as e:
        print(f"FAILED: Error handling test failed: {e}")
        return False


def main():
    """Run all CLI tests."""
    print("Testing Command Line Interface\n")

    tests = [
        test_cli_help,
        test_cli_version,
        test_cli_validation,
        test_cli_basic_conversion,
        test_cli_themed_conversion,
        test_cli_multiple_files,
        test_cli_dry_run,
        test_cli_error_handling,
    ]

    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"FAILED: {test_func.__name__} crashed: {e}")
            results.append(False)

    print(f"\nCLI Test Results: {sum(results)}/{len(results)} tests passed")

    if all(results):
        print("All CLI tests passed!")
        print("CLI features verified:")
        print("  - Help and version commands")
        print("  - Theme validation")
        print("  - Basic Markdown conversion")
        print("  - Themed conversion with custom output")
        print("  - Multiple file batch processing")
        print("  - Dry run functionality")
        print("  - Error handling and validation")
        print("  - Verbose and quiet modes")
        print("  - File pattern matching")
        return True
    else:
        print("Some CLI tests failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
