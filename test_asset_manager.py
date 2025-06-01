#!/usr/bin/env python3
"""Test script for asset management system."""

import sys
import tempfile
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from md_to_pdf.assets import AssetManager, AssetNotFoundError, AssetResolver


def test_asset_resolver():
    """Test basic asset resolution functionality."""
    print("🔍 Testing AssetResolver...")

    resolver = AssetResolver()

    # Test asset type detection
    test_files = {
        "image.png": "image",
        "font.ttf": "font",
        "styles.css": "stylesheet",
        "template.html": "template",
        "unknown.xyz": "unknown",
    }

    for filename, expected_type in test_files.items():
        detected_type = resolver.get_asset_type(filename)
        if detected_type == expected_type:
            print(f"✅ {filename} correctly detected as {detected_type}")
        else:
            print(
                f"❌ {filename} detected as {detected_type}, expected {expected_type}"
            )
            return False

    return True


def test_asset_manager():
    """Test basic asset manager functionality."""
    print("\n🔍 Testing AssetManager...")

    # Create a temporary test file
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False
    ) as temp_file:
        temp_file.write("Test asset content")
        temp_path = Path(temp_file.name)

    try:
        manager = AssetManager()

        # Test asset resolution with existing file
        try:
            asset_info = manager.resolve_asset(str(temp_path))
            print(f"✅ Asset resolved: {asset_info.original_path}")
            print(f"   Type: {asset_info.asset_type}")
            print(f"   Size: {asset_info.size} bytes")
            print(f"   Valid: {asset_info.is_valid}")
        except Exception as e:
            print(f"❌ Failed to resolve existing asset: {e}")
            return False

        # Test asset resolution with non-existing file
        try:
            manager.resolve_asset("non_existent_file.png")
            print("❌ Should have failed for non-existent file")
            return False
        except AssetNotFoundError:
            print("✅ Correctly failed for non-existent file")
        except Exception as e:
            print(f"❌ Unexpected error for non-existent file: {e}")
            return False

        # Test cache functionality
        cache_stats = manager.get_cache_stats()
        print(f"✅ Cache stats: {cache_stats}")

        return True

    finally:
        # Clean up temp file
        if temp_path.exists():
            temp_path.unlink()


def test_asset_copying():
    """Test asset copying functionality."""
    print("\n🔍 Testing asset copying...")

    # Create test files
    test_files = []
    try:
        for i in range(2):
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=f"_test_{i}.txt", delete=False
            ) as temp_file:
                temp_file.write(f"Test content {i}")
                test_files.append(Path(temp_file.name))

        manager = AssetManager()
        asset_paths = [str(f) for f in test_files]

        # Test copying assets
        try:
            asset_map = manager.copy_assets_to_temp(asset_paths)
            print(f"✅ Copied {len(asset_map)} assets to temp directory")

            # Verify copied files exist
            for original, copied in asset_map.items():
                if Path(copied).exists():
                    print(f"✅ Copied file exists: {Path(copied).name}")
                else:
                    print(f"❌ Copied file missing: {copied}")
                    return False

            # Test cleanup
            manager.cleanup_temp_assets()
            cache_stats = manager.get_cache_stats()
            print(f"✅ Cleanup completed. Temp dirs: {cache_stats['temp_directories']}")

            return True

        except Exception as e:
            print(f"❌ Asset copying failed: {e}")
            return False

    finally:
        # Clean up test files
        for test_file in test_files:
            if test_file.exists():
                test_file.unlink()


def main():
    """Run all asset manager tests."""
    print("🎯 Testing Asset Management System\n")

    tests = [
        test_asset_resolver,
        test_asset_manager,
        test_asset_copying,
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
        print("🎉 All asset management tests passed!")
        return True
    else:
        print("💥 Some tests failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
