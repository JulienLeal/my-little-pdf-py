#!/usr/bin/env python3
"""
Demo script to test the templating system integration with the example markdown file.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.md_to_pdf.core import MarkdownToPDFConverter


def main():
    """Test the example markdown file with templating integration."""

    # Initialize converter with default template manager
    converter = MarkdownToPDFConverter()

    # Read the example markdown file (from project root)
    example_file = Path(__file__).parent.parent / "example_templated_markdown.md"

    if not example_file.exists():
        print("❌ Example file not found!")
        print(f"Looking for: {example_file}")
        return

    # Convert to HTML
    html_content = converter.markdown_processor.convert_file(example_file)

    # Create a complete HTML document with CSS styling
    full_html_document = converter.pdf_generator._create_html_document(
        html_content, "Templating System Integration Demo"
    )

    # Save complete HTML output for inspection (in examples directory)
    output_file = Path(__file__).parent / "demo_output.html"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(full_html_document)

    print("✅ Converted example markdown to styled HTML")
    print(f"📄 Output saved to: {output_file}")
    print(
        f"🔧 Template manager found {len(converter.template_manager.get_registered_components())} components"
    )
    print(
        f"📋 Registered components: {converter.template_manager.get_registered_components()}"
    )

    # Show info about the styling
    component_css = converter.pdf_generator._get_component_css()
    if component_css:
        print("🎨 Component CSS loaded successfully!")
        print(f"📏 CSS size: {len(component_css)} characters")
    else:
        print("⚠️  No component CSS found")

    print("\n🌐 Open the HTML file in your browser to see the beautiful styling!")
    print(f"🔗 file://{output_file.absolute()}")


if __name__ == "__main__":
    main()
