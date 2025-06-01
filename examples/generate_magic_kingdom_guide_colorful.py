#!/usr/bin/env python3
"""
Magic Kingdom Guide PDF Generator - Colorful Version

This script demonstrates the complete PDF generation pipeline by creating
a beautiful Magic Kingdom travel guide using our markdown-to-pdf engine
with vibrant Disney-inspired colors and styling.
"""

import sys
import time
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from md_to_pdf.cli import MarkdownToPDFCLI


def main():
    """Generate both minimal and colorful versions of the Magic Kingdom guide PDF."""
    print("🏰 ✨ Magic Kingdom Guide PDF Generator - Colorful Edition ✨ 🏰\n")

    # Paths
    current_dir = Path(__file__).parent
    input_file = current_dir / "magic_kingdom_guide.md"

    # Theme files
    minimal_theme = current_dir.parent / "schemas" / "examples" / "minimal.yaml"
    colorful_theme = current_dir / "magic_kingdom_colorful.yaml"

    # Output files
    minimal_output = current_dir / "magic_kingdom_guide.pdf"
    colorful_output = current_dir / "magic_kingdom_guide_colorful.pdf"

    # Check if input files exist
    if not input_file.exists():
        print(f"❌ Input file not found: {input_file}")
        return 1

    if not minimal_theme.exists():
        print(f"❌ Minimal theme file not found: {minimal_theme}")
        return 1

    if not colorful_theme.exists():
        print(f"❌ Colorful theme file not found: {colorful_theme}")
        return 1

    print(f"📝 Input:  {input_file.name}")
    print(
        f"🎨 Themes: {minimal_theme.name} (minimal) & {colorful_theme.name} (colorful)"
    )
    print(f"📄 Outputs: {minimal_output.name} & {colorful_output.name}")
    print()

    # Create CLI instance
    cli = MarkdownToPDFCLI()

    results = []

    # Generate both versions
    for theme_name, theme_file, output_file, title_suffix in [
        ("Minimal", minimal_theme, minimal_output, "Clean"),
        ("Colorful", colorful_theme, colorful_output, "Colorido"),
    ]:
        print(f"🔄 Generating {theme_name} PDF...")
        start_time = time.time()

        try:
            exit_code = cli.run(
                [
                    str(input_file),
                    "--output",
                    str(output_file),
                    "--theme",
                    str(theme_file),
                    "--title",
                    f"Magic Kingdom - Guia {title_suffix}",
                    "--verbose",
                ]
            )

            end_time = time.time()
            generation_time = end_time - start_time

            if exit_code == 0 and output_file.exists():
                file_size = output_file.stat().st_size
                file_size_kb = file_size / 1024

                results.append(
                    {
                        "name": theme_name,
                        "file": output_file.name,
                        "size": file_size,
                        "size_kb": file_size_kb,
                        "time": generation_time,
                        "success": True,
                    }
                )

                print(f"✅ {theme_name} PDF generated successfully!")
                print(f"   📊 Size: {file_size:,} bytes ({file_size_kb:.1f} KB)")
                print(f"   ⏱️ Time: {generation_time:.2f} seconds")
            else:
                results.append(
                    {"name": theme_name, "success": False, "exit_code": exit_code}
                )
                print(
                    f"❌ {theme_name} PDF generation failed with exit code: {exit_code}"
                )

        except Exception as e:
            results.append({"name": theme_name, "success": False, "error": str(e)})
            print(f"❌ {theme_name} PDF generation failed: {e}")

        print()

    # Summary
    print("🎉 Generation Complete! Summary:")
    print("=" * 50)

    successful = [r for r in results if r.get("success", False)]
    failed = [r for r in results if not r.get("success", False)]

    if successful:
        print(f"✅ Successfully generated {len(successful)} PDF(s):")
        for result in successful:
            print(
                f"   • {result['name']}: {result['file']} ({result['size_kb']:.1f} KB)"
            )

    if failed:
        print(f"❌ Failed to generate {len(failed)} PDF(s):")
        for result in failed:
            error_msg = result.get(
                "error", f"Exit code {result.get('exit_code', 'unknown')}"
            )
            print(f"   • {result['name']}: {error_msg}")

    if successful:
        print("\n📖 Content Statistics:")
        content = input_file.read_text(encoding="utf-8")
        lines = len(content.split("\n"))
        words = len(content.split())
        chars = len(content)

        print(f"   • Lines: {lines:,}")
        print(f"   • Words: {words:,}")
        print(f"   • Characters: {chars:,}")

        print("\n🎪 Comparison:")
        if len(successful) == 2:
            size_diff = successful[1]["size"] - successful[0]["size"]
            size_diff_kb = size_diff / 1024
            percentage = (size_diff / successful[0]["size"]) * 100
            print(
                f"   • Colorful version is {size_diff:,} bytes ({size_diff_kb:.1f} KB) larger"
            )
            print(f"   • That's {percentage:.1f}% more styling and visual richness!")

        print("\n✨ Your magical PDF guides are ready! ✨")
        for result in successful:
            print(f"🎪 Open {result['file']} to see the magic!")

    return 0 if len(failed) == 0 else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
