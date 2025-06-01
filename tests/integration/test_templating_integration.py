"""
Integration tests for the templating system with custom block extension.

Tests the complete pipeline from markdown with custom blocks to HTML output
using the templating system.
"""

import tempfile
from pathlib import Path

from src.md_to_pdf.core import MarkdownToPDFConverter
from src.md_to_pdf.templating import TemplateManager


def test_custom_block_with_template_integration():
    """Test that custom blocks are rendered using templates when available."""

    # Initialize converter with template manager
    converter = MarkdownToPDFConverter()

    # Test markdown with a tip_box component (should have template)
    markdown_content = """
# Test Document

This is a regular paragraph.

:::tip_box color="blue"
This is a helpful tip that should be rendered using the tip_box template.
:::

Another regular paragraph.
"""

    # Convert to HTML
    html_output = converter.markdown_processor.convert(markdown_content)

    # Check that the template was used (should contain template-specific content)
    assert "custom-block" in html_output
    assert "tip-box" in html_output or "tip_box" in html_output
    assert "This is a helpful tip" in html_output

    # Should contain template-wrapper div from our integration
    assert "template-wrapper" in html_output

    print("✅ Custom block with template integration test passed")
    print(f"Generated HTML: {html_output}")


def test_custom_block_fallback_for_missing_template():
    """Test that custom blocks fall back to simple div when template not available."""

    # Initialize converter with template manager
    converter = MarkdownToPDFConverter()

    # Test markdown with a component that doesn't have a template
    markdown_content = """
# Test Document

:::unknown_component attribute="value"
This component should fall back to a simple div.
:::
"""

    # Convert to HTML
    html_output = converter.markdown_processor.convert(markdown_content)

    # Check that fallback was used
    assert "custom-block unknown_component" in html_output
    assert 'data-attribute="value"' in html_output
    assert "This component should fall back" in html_output

    # Should NOT contain template-wrapper for fallback
    assert "template-wrapper" not in html_output

    print("✅ Custom block fallback test passed")
    print(f"Generated HTML: {html_output}")


def test_end_to_end_with_custom_template_directory():
    """Test end-to-end with custom template directory."""

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create a custom template
        template_content = """
<div class="my-custom-component {{ css_classes }}">
    <h3>{{ title | default('Custom Component') }}</h3>
    <div class="content">{{ content }}</div>
    <p>Style: {{ style | default('default') }}</p>
</div>
"""
        template_file = temp_path / "my_component.html"
        template_file.write_text(template_content)

        # Initialize converter with custom template directory
        converter = MarkdownToPDFConverter(template_dirs=[str(temp_path)])

        # Test markdown with the custom component
        markdown_content = """
:::my_component title="Test Title" style="fancy"
This is the component content.
:::
"""

        # Convert to HTML
        html_output = converter.markdown_processor.convert(markdown_content)

        # Check that custom template was used
        assert "my-custom-component" in html_output
        assert "Test Title" in html_output
        assert "This is the component content" in html_output
        assert "Style: fancy" in html_output
        assert "template-wrapper" in html_output

        print("✅ End-to-end custom template test passed")
        print(f"Generated HTML: {html_output}")


def test_core_converter_template_manager_property():
    """Test that the converter properly exposes the template manager."""

    converter = MarkdownToPDFConverter()

    # Should have template manager
    assert converter.template_manager is not None
    assert isinstance(converter.template_manager, TemplateManager)

    # Should have discovered some components from default templates
    registered_components = converter.template_manager.get_registered_components()
    assert len(registered_components) > 0

    # Should include our default templates
    assert "tip_box" in registered_components

    print("✅ Template manager property test passed")
    print(f"Registered components: {registered_components}")


if __name__ == "__main__":
    test_custom_block_with_template_integration()
    test_custom_block_fallback_for_missing_template()
    test_end_to_end_with_custom_template_directory()
    test_core_converter_template_manager_property()
    print("\n🎉 All integration tests passed!")
