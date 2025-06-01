#!/usr/bin/env python3
"""
Test script for YAML configuration validation system.

This script tests the complete validation pipeline including JSON Schema
validation and custom validation rules.
"""

import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from md_to_pdf.config import (
    ValidationError,
    check_jsonschema_available,
    get_validation_summary,
    load_theme_config,
    validate_theme_config,
)


def test_validation_availability():
    """Test if validation dependencies are available."""
    print("=== Testing Validation Availability ===")

    available = check_jsonschema_available()
    print(f"JSON Schema validation available: {available}")

    if available:
        print("✅ Validation system ready")
        return True
    else:
        print("❌ jsonschema not available - install with: pip install jsonschema")
        return False


def test_valid_configurations():
    """Test validation with valid configurations."""
    print("\n=== Testing Valid Configurations ===")

    # Test minimal configuration
    minimal_config = {
        "page_setup": {"size": "A4", "orientation": "portrait", "margin": "2cm"}
    }

    try:
        validate_theme_config(minimal_config)
        print("✅ Minimal configuration validation passed")
    except ValidationError as e:
        print(f"❌ Minimal configuration failed: {e}")
        return False

    # Test complex configuration
    complex_config = {
        "page_setup": {
            "size": "A4",
            "orientation": "landscape",
            "margin": {"top": "2cm", "bottom": "2cm", "left": "3cm", "right": "3cm"},
            "default_font": {
                "family": ["Arial", "sans-serif"],
                "size": "12pt",
                "color": "#333333",
            },
        },
        "fonts": [
            {
                "name": "CustomFont",
                "normal": "fonts/custom-regular.ttf",
                "bold": "fonts/custom-bold.ttf",
            }
        ],
        "stylesheets": ["styles/custom.css"],
        "styles": {
            "h1": {"font_size": "24pt", "color": "#000000", "margin_bottom": "1cm"},
            "p": {"font_size": "11pt", "color": "#333333", "line_height": "1.5"},
        },
        "custom_components": {
            "note_box": {"template": "templates/note.html", "default_icon": "info"}
        },
        "page_headers": {"default": {"left": "{{title}}", "right": "Page {{page}}"}},
    }

    try:
        validate_theme_config(complex_config)
        print("✅ Complex configuration validation passed")
    except ValidationError as e:
        print(f"❌ Complex configuration failed: {e}")
        return False

    return True


def test_invalid_configurations():
    """Test validation with invalid configurations."""
    print("\n=== Testing Invalid Configurations ===")

    test_cases = [
        # Invalid page size
        {
            "config": {"page_setup": {"size": "INVALID"}},
            "description": "Invalid page size",
        },
        # Invalid orientation
        {
            "config": {"page_setup": {"orientation": "diagonal"}},
            "description": "Invalid orientation",
        },
        # Invalid color format
        {
            "config": {
                "styles": {
                    "h1": {"color": "red"}  # Should be hex
                }
            },
            "description": "Invalid color format",
        },
        # Invalid font size format
        {
            "config": {
                "styles": {
                    "p": {"font_size": "12"}  # Missing unit
                }
            },
            "description": "Invalid font size format",
        },
        # Duplicate font names
        {
            "config": {
                "fonts": [
                    {"name": "TestFont", "normal": "font1.ttf"},
                    {"name": "TestFont", "normal": "font2.ttf"},
                ]
            },
            "description": "Duplicate font names",
        },
        # Invalid component name
        {
            "config": {"custom_components": {"123invalid": {"template": "test.html"}}},
            "description": "Invalid component name",
        },
        # Unknown style element
        {
            "config": {"styles": {"unknown_element": {"color": "#000000"}}},
            "description": "Unknown style element",
        },
    ]

    passed = 0
    for i, test_case in enumerate(test_cases):
        try:
            validate_theme_config(test_case["config"])
            print(
                f"❌ Test {i + 1} ({test_case['description']}) should have failed but passed"
            )
        except ValidationError as e:
            print(
                f"✅ Test {i + 1} ({test_case['description']}) correctly failed: {e.message}"
            )
            passed += 1
        except Exception as e:
            print(
                f"❌ Test {i + 1} ({test_case['description']}) failed with unexpected error: {e}"
            )

    print(f"\nValidation tests passed: {passed}/{len(test_cases)}")
    return passed == len(test_cases)


def test_file_loading():
    """Test loading actual configuration files."""
    print("\n=== Testing File Loading ===")

    # Test loading example configurations
    schema_dir = Path("schemas/examples")
    if not schema_dir.exists():
        print("❌ Example configurations not found")
        return False

    example_files = ["minimal.yaml", "corporate.yaml", "magic_kingdom.yaml"]

    for filename in example_files:
        filepath = schema_dir / filename
        if not filepath.exists():
            print(f"❌ Example file not found: {filename}")
            continue

        try:
            config = load_theme_config(
                filepath, validate_files=False, validate_schema=True
            )

            # Create test data dictionary for validation summary
            test_data = {
                "page_setup": True,
                "fonts": config.fonts,
                "stylesheets": config.stylesheets,
                "styles": config.styles,
                "custom_components": config.custom_components,
                "page_headers": config.page_headers if config.page_headers else {},
                "page_footers": config.page_footers if config.page_footers else {},
            }
            summary = get_validation_summary(test_data)

            print(f"✅ {filename} loaded successfully")
            print(f"   - Sections: {', '.join(summary['sections_present'])}")
            print(f"   - Fonts: {summary['font_count']}")
            print(f"   - Components: {summary['component_count']}")
            print(f"   - Styled elements: {summary['styled_elements']}")
        except Exception as e:
            print(f"❌ Failed to load {filename}: {e}")
            return False

    return True


def test_validation_summary():
    """Test validation summary functionality."""
    print("\n=== Testing Validation Summary ===")

    test_config = {
        "page_setup": {"size": "A4"},
        "fonts": [
            {"name": "Font1", "normal": "font1.ttf"},
            {"name": "Font2", "normal": "font2.ttf"},
        ],
        "stylesheets": ["style1.css", "style2.css"],
        "styles": {"h1": {"color": "#000000"}, "p": {"color": "#333333"}},
        "custom_components": {"box": {"template": "box.html"}},
        "page_headers": {"default": {"center": "Title"}},
    }

    summary = get_validation_summary(test_config)

    expected = {
        "font_count": 2,
        "stylesheet_count": 2,
        "component_count": 1,
        "styled_elements": 2,
        "sections_present": [
            "page_setup",
            "fonts",
            "stylesheets",
            "styles",
            "custom_components",
            "page_headers",
        ],
    }

    success = True
    for key, expected_value in expected.items():
        if summary[key] != expected_value:
            print(f"❌ {key}: expected {expected_value}, got {summary[key]}")
            success = False
        else:
            print(f"✅ {key}: {summary[key]}")

    return success


def main():
    """Run all validation tests."""
    print("🔍 Testing YAML Configuration Validation System\n")

    # Check if validation is available
    if not test_validation_availability():
        print("\n❌ Cannot run validation tests without jsonschema")
        return False

    # Run test suites
    tests = [
        test_valid_configurations,
        test_invalid_configurations,
        test_file_loading,
        test_validation_summary,
    ]

    passed = 0
    for test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_func.__name__} failed")
        except Exception as e:
            print(f"❌ {test_func.__name__} crashed: {e}")

    print(f"\n🎯 Test Results: {passed}/{len(tests)} test suites passed")

    if passed == len(tests):
        print("🎉 All validation tests passed!")
        return True
    else:
        print("💥 Some tests failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
