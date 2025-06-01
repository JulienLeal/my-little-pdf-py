#!/usr/bin/env python3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from md_to_pdf.core import MarkdownToPDFConverter


def debug_css():
    # Load the colorful theme
    theme_path = Path("examples/magic_kingdom_colorful.yaml")
    converter = MarkdownToPDFConverter(theme_config_path=theme_path)

    # Get component CSS
    component_css = converter.pdf_generator._get_component_css()
    print(f"Component CSS length: {len(component_css)} characters")
    print(f"Component CSS loaded: {len(component_css) > 0}")

    if component_css:
        print("\nComponent CSS contains:")
        print(f"magic-secret: {'.magic-secret' in component_css}")
        print(f"tip-box: {'.tip-box' in component_css}")
        print(f"attention-box: {'.attention-box' in component_css}")
        print(f"gradients: {'gradient' in component_css}")
        print(f"background colors: {'background:' in component_css}")

        # Show first 500 chars of component CSS
        print("\nFirst 500 chars of component CSS:")
        print(component_css[:500])

    # Generate HTML and check if it includes component CSS
    html = converter.markdown_processor.convert_file(
        Path("examples/magic_kingdom_guide.md")
    )
    full_html = converter.pdf_generator._create_html_document(html, "Test")

    print(f"\nFull HTML document length: {len(full_html)} characters")
    print(f"Contains component CSS: {'Custom Components CSS' in full_html}")
    print(f"Contains magic-secret CSS: {'.magic-secret' in full_html}")

    # Save for inspection
    with open("debug_full_html.html", "w", encoding="utf-8") as f:
        f.write(full_html)
    print("\nFull HTML document saved to debug_full_html.html")


if __name__ == "__main__":
    debug_css()
