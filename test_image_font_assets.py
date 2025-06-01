#!/usr/bin/env python3
"""Test script for image and font asset handling."""

import re
import sys
import tempfile
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from md_to_pdf.assets import AssetValidationError, FontManager, ImageResolver


def test_image_resolver():
    """Test image resolution and processing functionality."""
    print("🔍 Testing ImageResolver...")

    # Create temporary image files for testing
    test_files = []
    try:
        # Create test files with different extensions
        image_extensions = [".png", ".jpg", ".gif", ".svg"]
        for ext in image_extensions:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=ext, delete=False
            ) as temp_file:
                temp_file.write("fake image content")
                test_files.append(Path(temp_file.name))

        resolver = ImageResolver()

        # Test image format detection
        for test_file in test_files:
            try:
                image_info = resolver.resolve_image_path(str(test_file))
                print(f"✅ {test_file.suffix} resolved as {image_info.format}")
                print(
                    f"   Vector: {image_info.is_vector}, Raster: {image_info.is_raster}"
                )
                print(f"   Web compatible: {image_info.is_web_compatible}")
            except Exception as e:
                print(f"❌ Failed to resolve {test_file.suffix}: {e}")
                return False

        # Test HTML image extraction
        html_content = """
        <img src="image1.png" alt="Test">
        <img src="path/to/image2.jpg" alt="Test 2">
        <img src="https://example.com/image3.png" alt="External">
        <img src="data:image/png;base64,..." alt="Data URL">
        """

        extracted_images = resolver.extract_images_from_html(html_content)
        expected_local_images = ["image1.png", "path/to/image2.jpg"]

        if set(extracted_images) == set(expected_local_images):
            print(
                f"✅ HTML image extraction found {len(extracted_images)} local images"
            )
        else:
            print(
                f"❌ HTML extraction failed. Found: {extracted_images}, Expected: {expected_local_images}"
            )
            return False

        # Test Markdown image extraction
        markdown_content = """
        ![Alt text](image1.png)
        ![Another image](folder/image2.jpg "Title")
        ![External](https://example.com/image.png)
        """

        extracted_md_images = resolver.extract_images_from_markdown(markdown_content)
        expected_md_images = ["image1.png", "folder/image2.jpg"]

        if set(extracted_md_images) == set(expected_md_images):
            print(
                f"✅ Markdown image extraction found {len(extracted_md_images)} local images"
            )
        else:
            print(
                f"❌ Markdown extraction failed. Found: {extracted_md_images}, Expected: {expected_md_images}"
            )
            return False

        return True

    finally:
        # Clean up test files
        for test_file in test_files:
            if test_file.exists():
                test_file.unlink()


def test_font_manager():
    """Test font management functionality."""
    print("\n🔍 Testing FontManager...")

    # Create temporary font files for testing
    test_files = []
    try:
        # Create test files with different font extensions
        font_extensions = [".ttf", ".otf", ".woff", ".woff2"]
        for ext in font_extensions:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=ext, delete=False
            ) as temp_file:
                temp_file.write("fake font content")
                test_files.append(Path(temp_file.name))

        manager = FontManager()

        # Test font format detection and validation
        for test_file in test_files:
            try:
                font_info = manager.validate_font_file(test_file)
                print(f"✅ {test_file.suffix} validated as {font_info.format}")
                print(f"   Family: {font_info.family_name}")
                print(
                    f"   Web font: {font_info.is_web_font}, Desktop: {font_info.is_desktop_font}"
                )
            except AssetValidationError as e:
                print(f"❌ Font validation failed for {test_file.suffix}: {e}")
                return False

        # Test font fallback generation
        test_stacks = [
            ["Roboto", "Arial"],
            ["Times New Roman"],
            ["Courier New", "monospace"],
            ["Custom Font"],
        ]

        for stack in test_stacks:
            fallbacks = manager.get_font_fallbacks(stack)
            if len(fallbacks) > len(stack):
                print(f"✅ Font stack {stack} expanded to {len(fallbacks)} fonts")
            else:
                print(f"❌ Font fallbacks not added for {stack}")
                return False

        # Test font stack validation
        test_validation_stacks = [
            ["Arial", "sans-serif"],  # Good stack
            ["Custom Font"],  # Missing fallbacks
        ]

        for stack in test_validation_stacks:
            validation = manager.validate_font_stack(stack)
            warnings = validation["warnings"]
            # Ensure warnings is a list before calling len()
            if isinstance(warnings, list):
                print(f"✅ Font stack {stack} validation: {len(warnings)} warnings")
            else:
                print(f"✅ Font stack {stack} validation: warnings type issue")
                return False

        return True

    finally:
        # Clean up test files
        for test_file in test_files:
            if test_file.exists():
                test_file.unlink()


def test_asset_scanning():
    """Test directory scanning for assets."""
    print("\n🔍 Testing asset scanning...")

    # Create a temporary directory structure with assets
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create subdirectories
        images_dir = temp_path / "images"
        fonts_dir = temp_path / "fonts"
        images_dir.mkdir()
        fonts_dir.mkdir()

        # Create test files
        test_assets = [
            images_dir / "test1.png",
            images_dir / "test2.jpg",
            fonts_dir / "font1.ttf",
            fonts_dir / "font2.woff",
            temp_path / "document.txt",  # Non-asset file
        ]

        for asset_path in test_assets:
            asset_path.write_text("test content")

        # Test image scanning
        image_resolver = ImageResolver()
        found_images = image_resolver.scan_for_images(temp_path)

        expected_images = 2
        if len(found_images) == expected_images:
            print(f"✅ Image scanning found {len(found_images)} images")
        else:
            print(
                f"❌ Image scanning failed. Found {len(found_images)}, expected {expected_images}"
            )
            return False

        # Test font scanning
        font_manager = FontManager()
        found_fonts = font_manager.scan_for_fonts(temp_path)

        expected_fonts = 2
        if len(found_fonts) == expected_fonts:
            print(f"✅ Font scanning found {len(found_fonts)} fonts")
        else:
            print(
                f"❌ Font scanning failed. Found {len(found_fonts)}, expected {expected_fonts}"
            )
            return False

    return True


def test_html_reference_updating():
    """Test HTML reference updating."""
    print("\n🔍 Testing HTML reference updating...")

    image_resolver = ImageResolver()

    # Test HTML content
    original_html = """
    <img src="image1.png" alt="Test">
    <img src='image2.jpg' alt="Test 2">
    <img src=image3.gif alt="Test 3">
    """

    # Test asset mapping - use Windows-compatible temp paths
    import tempfile

    temp_dir = Path(tempfile.gettempdir())
    asset_map = {
        "image1.png": str(temp_dir / "assets" / "image1.png"),
        "image2.jpg": str(temp_dir / "assets" / "image2.jpg"),
        "image3.gif": str(temp_dir / "assets" / "image3.gif"),
    }

    updated_html = image_resolver.update_html_image_refs(original_html, asset_map)

    # Check if the src attributes were properly updated (not just if the filename appears anywhere)
    for original_path in asset_map.keys():
        # Check if the original path still appears as a src attribute value
        src_pattern = rf'src=["\']?{re.escape(original_path)}["\']?'
        if re.search(src_pattern, updated_html):
            print(f"❌ Original src {original_path} still present in updated HTML")
            return False

    # Check if file URIs are present
    if "file://" in updated_html:
        print("✅ HTML references updated to file URIs")
    else:
        print("❌ File URIs not found in updated HTML")
        return False

    return True


def main():
    """Run all image and font asset tests."""
    print("🎨 Testing Image and Font Asset Management\n")

    tests = [
        test_image_resolver,
        test_font_manager,
        test_asset_scanning,
        test_html_reference_updating,
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
        print("🎉 All image and font asset tests passed!")
        return True
    else:
        print("💥 Some tests failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
