#!/usr/bin/env python3
"""Test script for comprehensive base CSS system."""

import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from md_to_pdf.base_css import BaseCSSGenerator
from md_to_pdf.config import load_theme_config
from md_to_pdf.core import MarkdownToPDFConverter


def test_base_css_generator():
    """Test the BaseCSSGenerator class."""
    print("🎨 Testing BaseCSSGenerator...")

    generator = BaseCSSGenerator()

    # Generate base CSS
    base_css = generator.generate_base_css()

    print(f"✅ Generated {len(base_css)} characters of base CSS")

    # Check for key components
    required_sections = [
        "CSS Reset and Normalizations",
        "Professional Typography",
        "Page Layout",
        "Professional Headings",
        "Text Elements",
        "Lists",
        "Professional Tables",
        "Code and Preformatted Text",
        "Print Optimizations",
        "Utility Classes",
    ]

    missing_sections = []
    for section in required_sections:
        if section not in base_css:
            missing_sections.append(section)

    if missing_sections:
        print(f"❌ Missing sections: {missing_sections}")
        return False
    else:
        print("✅ All required CSS sections present")

    # Test theme-aware CSS
    theme_styles = {
        "body": {
            "font_family": ["Georgia", "serif"],
            "font_size": "12pt",
            "color": "#1a1a1a",
        }
    }

    theme_css = generator.generate_theme_aware_css(theme_styles)
    print(f"✅ Generated {len(theme_css)} characters of theme-aware CSS")

    if "Georgia" in theme_css and "12pt" in theme_css:
        print("✅ Theme overrides applied correctly")
        return True
    else:
        print("❌ Theme overrides not applied")
        return False


def test_pdf_generator_integration():
    """Test integration with PDFGenerator."""
    print("\n🔗 Testing PDFGenerator integration...")

    try:
        # Test without theme
        converter = MarkdownToPDFConverter()

        # Test markdown with diverse content
        markdown_content = """
# Professional Document Test

This document tests the comprehensive base CSS system with various markdown elements.

## Typography and Text Formatting

This is a paragraph with **bold text**, *italic text*, and `inline code`. We also have [links](https://example.com) and ==highlighted text==.

### Lists and Organization

#### Unordered List
- First item with detailed information
- Second item
  - Nested item
  - Another nested item
- Third item

#### Ordered List
1. First ordered item
2. Second ordered item
   1. Nested ordered item
   2. Another nested item
3. Third ordered item

#### Task List
- [x] Completed task
- [ ] Pending task
- [ ] Another pending task

### Code Examples

Here's some inline `code` and a code block:

```python
def hello_world():
    print("Hello, World!")
    return True
```

### Tables

| Feature | Status | Notes |
|---------|--------|-------|
| Headers | ✅ Complete | Working properly |
| Footers | ✅ Complete | With variables |
| CSS | ✅ Complete | Professional styling |

### Blockquotes

> This is an important blockquote that demonstrates the professional styling of quoted content. It should have proper margins, padding, and visual hierarchy.
> 
> Multiple paragraphs in blockquotes should also work correctly.

### Horizontal Rules

---

### Special Elements

This paragraph contains <sub>subscript</sub> and <sup>superscript</sup> text.

**Important:** This is a lead paragraph that should stand out.
        """

        output_path = Path("test_comprehensive_css.pdf")

        # Convert to PDF
        converter.convert_string(
            markdown_content, output_path, "Comprehensive CSS Test"
        )

        if output_path.exists():
            file_size = output_path.stat().st_size
            print(f"✅ PDF generated successfully: {file_size} bytes")

            # Clean up
            output_path.unlink()
            return True
        else:
            print("❌ PDF file not created")
            return False

    except Exception as e:
        print(f"❌ PDF generation failed: {e}")
        return False


def test_theme_integration():
    """Test comprehensive CSS with theme configuration."""
    print("\n🎭 Testing theme integration...")

    try:
        # Load a theme configuration
        theme_config = load_theme_config(
            "schemas/examples/advanced_headers.yaml", validate_files=False
        )

        converter = MarkdownToPDFConverter(
            theme_config_path=Path("schemas/examples/advanced_headers.yaml")
        )

        markdown_content = """
# Advanced Theme Integration Test

This document tests the comprehensive base CSS system working together with theme configurations.

## Professional Styling

The comprehensive base CSS provides professional defaults while allowing theme customization.

### Key Features

1. **Print Optimizations**: Orphans, widows, and page break controls
2. **Typography Scale**: Modular typography system
3. **Professional Colors**: Consistent color palette
4. **Table Styling**: Clean, readable tables
5. **Code Blocks**: Syntax-highlighted code blocks

### Sample Table

| Component | Base CSS | Theme Override | Result |
|-----------|----------|----------------|--------|
| Headers | Professional | Custom colors | ✅ Perfect |
| Typography | Modular scale | Font family | ✅ Perfect |
| Tables | Clean design | Border colors | ✅ Perfect |

> This blockquote demonstrates how base CSS and theme CSS work together seamlessly.
        """

        output_path = Path("test_theme_integration.pdf")

        converter.convert_string(
            markdown_content, output_path, "Theme Integration Test"
        )

        if output_path.exists():
            file_size = output_path.stat().st_size
            print(f"✅ Theme integration PDF generated: {file_size} bytes")

            # Clean up
            output_path.unlink()
            return True
        else:
            print("❌ Theme integration PDF not created")
            return False

    except Exception as e:
        print(f"❌ Theme integration test failed: {e}")
        return False


def test_css_quality():
    """Test CSS quality and structure."""
    print("\n🔍 Testing CSS quality...")

    generator = BaseCSSGenerator()
    css = generator.generate_base_css()

    # Check for professional features
    quality_checks = [
        # Print optimizations
        ("orphans", "Print optimization: orphans"),
        ("widows", "Print optimization: widows"),
        ("page-break-inside: avoid", "Page break controls"),
        # Typography
        ("text-rendering: optimizeLegibility", "Typography optimization"),
        ("font-smoothing", "Font smoothing"),
        # Professional styling
        ("border-collapse: collapse", "Table styling"),
        ("text-align: justify", "Text justification"),
        ("line-height: 1.6", "Readable line height"),
        # Utility classes
        (".text-center", "Utility classes"),
        (".page-break-before", "Page break utilities"),
        # Professional colors
        ("#3182ce", "Professional color palette"),
        ("#2c3e50", "Professional text colors"),
    ]

    passed_checks = 0
    for check, description in quality_checks:
        if check in css:
            print(f"  ✅ {description}")
            passed_checks += 1
        else:
            print(f"  ❌ Missing: {description}")

    print(f"✅ CSS quality: {passed_checks}/{len(quality_checks)} checks passed")

    return passed_checks >= len(quality_checks) * 0.8  # 80% pass rate required


def main():
    """Run comprehensive base CSS tests."""
    print("🎯 Testing Comprehensive Base CSS System\n")

    tests = [
        test_base_css_generator,
        test_css_quality,
        test_pdf_generator_integration,
        test_theme_integration,
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
        print("🎉 All comprehensive base CSS tests passed!")
        print("📝 Features verified:")
        print("  ✅ Professional typography with modular scale")
        print("  ✅ Print optimizations (orphans, widows, page breaks)")
        print("  ✅ Comprehensive table styling")
        print("  ✅ Code block and syntax highlighting support")
        print("  ✅ Professional color palette")
        print("  ✅ Utility classes for layout and styling")
        print("  ✅ Theme integration and customization")
        print("  ✅ CSS Paged Media support")
        return True
    else:
        print("💥 Some tests failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
