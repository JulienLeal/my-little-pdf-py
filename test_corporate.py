#!/usr/bin/env python3
"""Simple test for corporate.yaml validation."""

import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from md_to_pdf.config import ValidationError, load_theme_config


def test_corporate_yaml():
    """Test loading corporate.yaml file."""
    try:
        config = load_theme_config(
            "schemas/examples/corporate.yaml",
            validate_files=False,
            validate_schema=True,
        )
        print("✅ corporate.yaml loads successfully")
        print(f"   - Page size: {config.page_setup.size}")
        print(f"   - Styled elements: {len(config.styles)}")
        print(f"   - Custom components: {len(config.custom_components)}")
        return True
    except ValidationError as e:
        print(f"❌ Validation error: {e.message}")
        if e.field_path:
            print(f"   Field: {e.field_path}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    test_corporate_yaml()
