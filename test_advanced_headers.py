#!/usr/bin/env python3
"""Test script for advanced header/footer features."""

import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from md_to_pdf.config import load_theme_config
from md_to_pdf.css_generator import CSSGenerator
from md_to_pdf.page_processor import PageProcessor


def test_advanced_headers():
    """Test the advanced headers configuration."""
    print("🎯 Testing Advanced Headers and Footers\n")

    try:
        # Load advanced theme
        theme_config = load_theme_config(
            "schemas/examples/advanced_headers.yaml", validate_files=False
        )

        print("✅ Advanced theme loaded successfully")
        print(f"   Headers configured: {list(theme_config.page_headers.keys())}")
        print(f"   Footers configured: {list(theme_config.page_footers.keys())}")

        # Create PageProcessor
        processor = PageProcessor(theme_config)

        # Test document with multiple sections
        html_content = """
        <html>
        <head>
            <title>Advanced Features Demo</title>
            <meta name="author" content="Demo Author">
        </head>
        <body>
            <h1>Advanced Features Demo</h1>
            <p>This document demonstrates the advanced header and footer features with dynamic variable substitution.</p>
            
            <h2>Section 1: Introduction</h2>
            <p>This is the introduction section with detailed information about the features.</p>
            
            <h2>Section 2: Implementation</h2>
            <p>This section covers the implementation details.</p>
            
            <blockquote>
            This is an important note that should be highlighted in the document.
            </blockquote>
            
            <h1>Chapter 2: Advanced Topics</h1>
            <p>This chapter covers more advanced topics.</p>
            
            <h2>Section 2.1: Performance</h2>
            <p>Performance considerations and optimizations.</p>
        </body>
        </html>
        """

        # Extract metadata
        metadata = processor.extract_document_metadata(html_content)
        print("\n📋 Extracted metadata:")
        for key, value in metadata.items():
            print(f"   {key}: {value}")

        # Extract sections
        sections = processor.section_tracker.extract_sections(html_content)
        print(f"\n📑 Found {len(sections)} sections:")
        for section in sections:
            print(f"   {section}")

        # Generate CSS with advanced headers/footers
        css_generator = CSSGenerator(theme_config)
        generated_css = css_generator.generate_css()

        # Also generate paged media CSS from processor
        paged_css = processor.generate_paged_media_css()

        print("\n🎨 Generated CSS:")
        print(f"   Base CSS: {len(generated_css)} characters")
        print(f"   Paged Media CSS: {len(paged_css)} characters")

        print("\n📄 Paged Media CSS Preview:")
        print(paged_css[:500] + "..." if len(paged_css) > 500 else paged_css)

        # Test variable resolution with different contexts
        print("\n🔧 Variable Resolution Examples:")

        test_contexts = [
            {
                "page_number": 1,
                "total_pages": 10,
                "section_title": "Introduction",
                "document_title": "My Report",
            },
            {
                "page_number": 5,
                "total_pages": 10,
                "section_title": "Implementation",
                "document_title": "My Report",
            },
            {
                "page_number": 10,
                "total_pages": 10,
                "section_title": "Conclusion",
                "document_title": "My Report",
            },
        ]

        for i, context in enumerate(test_contexts, 1):
            print(f"\n   Page {context['page_number']} example:")

            # Test header template
            header_template = theme_config.page_headers["default"].left
            header_result = processor.variable_resolver.resolve_variables(
                header_template, context
            )
            print(f"     Header left: '{header_template}' → '{header_result}'")

            # Test footer template
            footer_template = theme_config.page_footers["default"].right
            footer_result = processor.variable_resolver.resolve_variables(
                footer_template, context
            )
            print(f"     Footer right: '{footer_template}' → '{footer_result}'")

        print("\n🎉 Advanced headers/footers test completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Advanced headers test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_advanced_headers()
    sys.exit(0 if success else 1)
