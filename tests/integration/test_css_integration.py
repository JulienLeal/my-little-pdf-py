#!/usr/bin/env python3
"""
Test CSS integration with the templating system.
"""

from pathlib import Path

from src.md_to_pdf.core import MarkdownToPDFConverter


def test_css_integration():
    """Test that CSS is properly integrated into generated HTML."""

    converter = MarkdownToPDFConverter()

    # Test markdown with various components
    markdown_content = """
# CSS Integration Test

:::tip_box color="blue"
This should have blue styling with a lightbulb icon.
:::

:::magic_secret reveal_text="Test"
This should have magical dark blue styling with stars.
:::

:::attention_box type="warning"
This should have warning styling with proper colors.
:::

:::unknown_component test="fallback"
This should have fallback dashed border styling.
:::
"""

    # Convert to HTML content only
    html_content = converter.markdown_processor.convert(markdown_content)

    # Create full HTML document with CSS
    full_html = converter.pdf_generator._create_html_document(
        html_content, "CSS Integration Test"
    )

    # Verify CSS is included
    assert ".custom-block" in full_html
    assert ".tip-box" in full_html
    assert ".magic-secret" in full_html
    assert ".attention-box" in full_html
    assert "linear-gradient" in full_html
    assert "box-shadow" in full_html

    # Verify HTML structure
    assert "template-wrapper" in full_html
    assert "color-blue" in full_html
    assert 'data-type="warning"' in full_html

    print("✅ CSS integration test passed!")
    print(f"📏 Full HTML document size: {len(full_html)} characters")

    # Save for manual inspection
    test_output = Path("test_css_output.html")
    with open(test_output, "w", encoding="utf-8") as f:
        f.write(full_html)

    print(f"🔗 Test output saved to: {test_output.absolute()}")
    return True


def test_css_loading():
    """Test that component CSS file is loaded correctly."""

    converter = MarkdownToPDFConverter()

    # Get component CSS
    component_css = converter.pdf_generator._get_component_css()

    # Verify CSS content
    assert len(component_css) > 1000  # Should be a substantial CSS file
    assert ".custom-block" in component_css
    assert ".tip-box" in component_css
    assert ".magic-secret" in component_css
    assert ".attention-box" in component_css

    print("✅ CSS loading test passed!")
    print(f"📏 Component CSS size: {len(component_css)} characters")
    return True


def test_pdf_generator_options():
    """Test PDF generator CSS options."""

    # Test with component CSS enabled (default)
    converter = MarkdownToPDFConverter()
    html_with_css = converter.pdf_generator._create_html_document("<p>Test</p>", "Test")
    assert ".custom-block" in html_with_css

    # Test with component CSS disabled
    from src.md_to_pdf.core import PDFGenerator

    pdf_gen_no_css = PDFGenerator(include_component_css=False)
    html_without_css = pdf_gen_no_css._create_html_document("<p>Test</p>", "Test")
    assert ".custom-block" not in html_without_css

    print("✅ PDF generator options test passed!")
    return True


if __name__ == "__main__":
    test_css_loading()
    test_css_integration()
    test_pdf_generator_options()
    print("\n🎉 All CSS integration tests passed!")
