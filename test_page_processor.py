#!/usr/bin/env python3
"""Test script for PageProcessor advanced PDF features."""

import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from md_to_pdf.config import load_theme_config
from md_to_pdf.page_processor import PageProcessor, SectionTracker, VariableResolver


def test_variable_resolver():
    """Test variable resolution functionality."""
    print("🔍 Testing VariableResolver...")

    resolver = VariableResolver()

    # Test built-in variables
    context = {
        "page_number": 3,
        "total_pages": 25,
        "document_title": "My Test Document",
        "section_title": "Introduction",
    }

    # Test templates
    test_templates = [
        ("Page {page_number}", "Page 3"),
        ("{document_title} - {section_title}", "My Test Document - Introduction"),
        ("Page {page_number} of {total_pages}", "Page 3 of 25"),
        ("{date} - {year}", None),  # Date/year will be current values
    ]

    for template, expected in test_templates:
        result = resolver.resolve_variables(template, context)
        if expected:
            if result == expected:
                print(f"✅ Template '{template}' → '{result}'")
            else:
                print(f"❌ Template '{template}' → '{result}' (expected '{expected}')")
                return False
        else:
            print(f"✅ Template '{template}' → '{result}' (dynamic)")

    return True


def test_section_tracker():
    """Test section tracking functionality."""
    print("\n🔍 Testing SectionTracker...")

    tracker = SectionTracker()

    # Test HTML with headings
    html_content = """
    <html>
    <body>
        <h1>Chapter 1: Introduction</h1>
        <p>Some content...</p>
        <h2>1.1 Overview</h2>
        <p>More content...</p>
        <h2>1.2 Objectives</h2>
        <p>Even more content...</p>
        <h1>Chapter 2: Implementation</h1>
        <p>Implementation content...</p>
    </body>
    </html>
    """

    sections = tracker.extract_sections(html_content)

    print(f"Found {len(sections)} sections:")
    for section in sections:
        print(f"  {section}")

    # Test section context
    context = tracker.get_section_context(1)
    print(f"\nPage 1 context: {context}")

    if len(sections) >= 2:
        print("✅ Section extraction working")
        return True
    else:
        print("❌ Section extraction failed")
        return False


def test_page_processor():
    """Test PageProcessor integration."""
    print("\n🔍 Testing PageProcessor...")

    try:
        # Load minimal theme
        theme_config = load_theme_config(
            "schemas/examples/minimal.yaml", validate_files=False
        )

        processor = PageProcessor(theme_config)

        # Test HTML with title and sections
        html_content = """
        <html>
        <head>
            <title>Test Document</title>
            <meta name="author" content="Test Author">
        </head>
        <body>
            <h1>Test Document Title</h1>
            <p>This is a test document.</p>
            <h2>Section 1</h2>
            <p>Content for section 1.</p>
        </body>
        </html>
        """

        # Extract metadata
        metadata = processor.extract_document_metadata(html_content)
        print(f"Extracted metadata: {metadata}")

        # Process headers/footers
        processed_html = processor.process_headers_footers(html_content)
        print(f"Processed HTML length: {len(processed_html)} chars")

        # Generate paged media CSS
        paged_css = processor.generate_paged_media_css()
        print(f"Generated CSS length: {len(paged_css)} chars")

        if paged_css:
            print("✅ CSS Preview (first 300 chars):")
            print(paged_css[:300] + "..." if len(paged_css) > 300 else paged_css)

        return True

    except Exception as e:
        print(f"❌ PageProcessor test failed: {e}")
        return False


def main():
    """Run all PageProcessor tests."""
    print("🎯 Testing Advanced PDF Features (PageProcessor)\n")

    tests = [
        test_variable_resolver,
        test_section_tracker,
        test_page_processor,
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
        print("🎉 All PageProcessor tests passed!")
        return True
    else:
        print("💥 Some tests failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
