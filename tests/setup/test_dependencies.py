#!/usr/bin/env python3
"""Test script to verify all core dependencies are working."""


def test_markdown():
    """Test python-markdown installation and basic usage."""
    print("Testing python-markdown...")
    try:
        import markdown

        print(f"✅ Markdown version: {markdown.__version__}")

        md = markdown.Markdown()
        result = md.convert("# Hello **World**")
        expected = "<h1>Hello <strong>World</strong></h1>"
        assert result == expected, f"Expected: {expected}, Got: {result}"
        print("✅ Basic markdown conversion works")
        return True
    except Exception as e:
        print(f"❌ Markdown test failed: {e}")
        return False


def test_jinja2():
    """Test Jinja2 installation and basic templating."""
    print("\nTesting Jinja2...")
    try:
        from jinja2 import Template

        print("✅ Jinja2 imported successfully")

        template = Template("Hello {{ name }}!")
        result = template.render(name="World")
        expected = "Hello World!"
        assert result == expected, f"Expected: {expected}, Got: {result}"
        print("✅ Basic template rendering works")
        return True
    except Exception as e:
        print(f"❌ Jinja2 test failed: {e}")
        return False


def test_weasyprint():
    """Test WeasyPrint installation and basic HTML to PDF conversion."""
    print("\nTesting WeasyPrint...")
    try:
        import weasyprint

        print("✅ WeasyPrint imported successfully")

        # Test basic HTML to PDF (without actually creating a file)
        html_content = "<html><body><h1>Test</h1></body></html>"
        doc = weasyprint.HTML(string=html_content)
        print("✅ Basic HTML parsing works")

        # Try to render to bytes (memory) to test PDF generation
        # This might fail on Windows due to missing system dependencies
        try:
            pdf_bytes = doc.write_pdf()
            assert len(pdf_bytes) > 0, "PDF generation failed - no content"
            print(f"✅ PDF generation works (generated {len(pdf_bytes)} bytes)")
        except Exception as pdf_error:
            print(
                f"⚠️ PDF generation failed (likely missing system dependencies): {pdf_error}"
            )
            print("ℹ️ This is expected on Windows without GTK+ libraries")
            print("ℹ️ WeasyPrint import works, so we can proceed with development")

        return True
    except Exception as e:
        print(f"❌ WeasyPrint test failed: {e}")
        return False


def test_pyyaml():
    """Test PyYAML installation and basic parsing."""
    print("\nTesting PyYAML...")
    try:
        import yaml

        print("✅ PyYAML imported successfully")

        yaml_content = """
        name: test
        settings:
          debug: true
          version: 1.0
        """
        data = yaml.safe_load(yaml_content)
        assert data["name"] == "test", f"Expected name='test', got {data['name']}"
        assert data["settings"]["debug"] is True, "Expected debug=True"
        print("✅ Basic YAML parsing works")
        return True
    except Exception as e:
        print(f"❌ PyYAML test failed: {e}")
        return False


def test_click():
    """Test Click installation for CLI functionality."""
    print("\nTesting Click...")
    try:
        import click

        print("✅ Click imported successfully")

        @click.command()
        @click.option("--name", default="World")
        def hello(name):
            return f"Hello {name}!"

        # Test that the command was created successfully
        assert hasattr(hello, "params"), "Click command not properly decorated"
        print("✅ Basic Click command creation works")
        return True
    except Exception as e:
        print(f"❌ Click test failed: {e}")
        return False


def test_weasyprint_windows_fix():
    """Test WeasyPrint with Windows system dependencies."""
    print("\nTesting WeasyPrint Windows setup...")

    import os
    import platform

    # Only run detailed Windows tests on Windows
    if platform.system() != "Windows":
        print("ℹ️ Not on Windows, skipping Windows-specific tests")
        return True

    # Check if WEASYPRINT_DLL_DIRECTORIES is set
    dll_dirs = os.environ.get("WEASYPRINT_DLL_DIRECTORIES")
    if dll_dirs:
        print(f"✅ WEASYPRINT_DLL_DIRECTORIES set: {dll_dirs}")
    else:
        print("⚠️ WEASYPRINT_DLL_DIRECTORIES not set")
        print("ℹ️ See WEASYPRINT_WINDOWS_SETUP.md for setup instructions")

    # Check if MSYS2 libraries exist
    expected_path = "C:\\msys64\\mingw64\\bin"
    if os.path.exists(expected_path):
        print(f"✅ MSYS2 directory found: {expected_path}")

        # Check for key libraries
        key_dlls = ["libpango-1.0-0.dll", "libcairo-2.dll", "libgdk_pixbuf-2.0-0.dll"]
        found_dlls = 0
        for dll in key_dlls:
            dll_path = os.path.join(expected_path, dll)
            if os.path.exists(dll_path):
                print(f"✅ Found: {dll}")
                found_dlls += 1
            else:
                print(f"❌ Missing: {dll}")

        if found_dlls == 0:
            print("⚠️ No expected DLLs found. Run: pacman -S mingw-w64-x86_64-pango")
    else:
        print(f"❌ MSYS2 directory not found: {expected_path}")
        print("ℹ️ Install MSYS2 from https://www.msys2.org/")

    # Test WeasyPrint functionality with better error reporting
    try:
        import weasyprint

        html_content = "<html><body><h1>Windows Test</h1><p>Testing system dependencies...</p></body></html>"
        doc = weasyprint.HTML(string=html_content)
        pdf_bytes = doc.write_pdf()
        print(f"✅ PDF generation successful ({len(pdf_bytes)} bytes)")
        return True
    except Exception as e:
        print(f"❌ PDF generation failed: {e}")
        print("ℹ️ This likely means system dependencies are missing")
        print("ℹ️ Follow the steps in WEASYPRINT_WINDOWS_SETUP.md")
        return False


def main():
    """Run all dependency tests."""
    print("🔍 Testing all core dependencies...\n")

    tests = [
        test_markdown,
        test_jinja2,
        test_weasyprint,
        test_pyyaml,
        test_click,
        test_weasyprint_windows_fix,  # Add Windows-specific test
    ]

    results = []
    for test in tests:
        results.append(test())

    print(f"\n📊 Results: {sum(results)}/{len(results)} tests passed")

    if all(results):
        print("🎉 All dependencies are working correctly!")
        return True
    else:
        print("⚠️ Some dependencies have issues. Please check the output above.")

        # Special message for Windows users
        import platform

        if platform.system() == "Windows":
            print(
                "\n💡 Windows users: If WeasyPrint tests failed, check WEASYPRINT_WINDOWS_SETUP.md"
            )

        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
