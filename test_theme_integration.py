#!/usr/bin/env python3
"""Test script for theme configuration integration with PDF generation."""

import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from md_to_pdf.core import MarkdownToPDFConverter


def test_theme_integration():
    """Test theme configuration integration with PDF generation."""
    print("🔍 Testing theme configuration integration...")

    # Test with minimal theme
    minimal_theme_path = Path("schemas/examples/minimal.yaml")
    if not minimal_theme_path.exists():
        print(f"❌ Theme file not found: {minimal_theme_path}")
        return False

    try:
        # Create converter with theme configuration
        converter = MarkdownToPDFConverter(theme_config_path=minimal_theme_path)

        # Test Markdown content
        markdown_content = """
# Test Document

This is a test document to verify theme integration.

## Section 2

Some paragraph text with **bold** and *italic* formatting.

- List item 1
- List item 2
- List item 3

> This is a blockquote to test styling.

```python
# Code block
def hello_world():
    print("Hello, World!")
```
"""

        # Generate PDF
        output_path = Path("test_output_minimal.pdf")
        converter.convert_string(
            markdown_content, output_path, "Theme Integration Test"
        )

        if output_path.exists() and output_path.stat().st_size > 0:
            print(
                f"✅ PDF generated with minimal theme: {output_path.stat().st_size} bytes"
            )
            return True
        else:
            print("❌ PDF was not created or is empty")
            return False

    except Exception as e:
        print(f"❌ Theme integration test failed: {e}")
        return False


def test_css_generation():
    """Test CSS generation from theme configuration."""
    print("\n🔍 Testing CSS generation from theme...")

    try:
        from md_to_pdf.config import load_theme_config
        from md_to_pdf.css_generator import CSSGenerator

        # Load minimal theme
        theme_config = load_theme_config(
            "schemas/examples/minimal.yaml", validate_files=False
        )

        # Generate CSS
        css_generator = CSSGenerator(theme_config)
        generated_css = css_generator.generate_css()

        print("✅ CSS generated successfully")
        print(f"   CSS length: {len(generated_css)} characters")

        # Check for key CSS elements
        if "@page" in generated_css:
            print("✅ Page setup CSS found")
        else:
            print("❌ Page setup CSS missing")

        if "h1 {" in generated_css:
            print("✅ Element styles CSS found")
        else:
            print("❌ Element styles CSS missing")

        # Show a preview of generated CSS
        print("\n📄 CSS Preview (first 500 chars):")
        print(
            generated_css[:500] + "..." if len(generated_css) > 500 else generated_css
        )

        return True

    except Exception as e:
        print(f"❌ CSS generation test failed: {e}")
        return False


def test_corporate_theme():
    """Test with corporate theme configuration."""
    print("\n🔍 Testing corporate theme integration...")

    corporate_theme_path = Path("schemas/examples/corporate.yaml")
    if not corporate_theme_path.exists():
        print(f"❌ Corporate theme file not found: {corporate_theme_path}")
        return False

    try:
        # Create converter with corporate theme
        converter = MarkdownToPDFConverter(theme_config_path=corporate_theme_path)

        # Test Markdown content
        markdown_content = """
# Corporate Document

This document demonstrates corporate theme styling.

## Executive Summary

Professional business document with custom fonts and styling.

### Key Points

- Professional appearance
- Custom typography
- Branded colors

> Important note: This blockquote should have corporate styling.
"""

        # Generate PDF
        output_path = Path("test_output_corporate.pdf")
        converter.convert_string(markdown_content, output_path, "Corporate Theme Test")

        if output_path.exists() and output_path.stat().st_size > 0:
            print(
                f"✅ PDF generated with corporate theme: {output_path.stat().st_size} bytes"
            )
            return True
        else:
            print("❌ PDF was not created or is empty")
            return False

    except Exception as e:
        print(f"❌ Corporate theme test failed: {e}")
        return False


def main():
    """Run all theme integration tests."""
    print("🎨 Testing Theme Configuration Integration\n")

    tests = [
        test_css_generation,
        test_theme_integration,
        test_corporate_theme,
    ]

    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ {test_func.__name__} crashed: {e}")
            results.append(False)

    print(f"\n🎯 Test Results: {sum(results)}/{len(results)} tests passed")

    if all(results):
        print("🎉 All theme integration tests passed!")
        return True
    else:
        print("💥 Some tests failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
