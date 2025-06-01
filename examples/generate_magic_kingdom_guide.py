#!/usr/bin/env python3
"""
Magic Kingdom Guide PDF Generator

This script demonstrates the complete PDF generation pipeline by creating
a beautiful Magic Kingdom travel guide using our markdown-to-pdf engine.
"""

import sys
import time
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from md_to_pdf.cli import MarkdownToPDFCLI


def main():
    """Generate the Magic Kingdom guide PDF."""
    print("🏰 ✨ Magic Kingdom Guide PDF Generator ✨ 🏰\n")

    # Paths
    current_dir = Path(__file__).parent
    input_file = current_dir / "magic_kingdom_guide.md"
    theme_file = (
        current_dir.parent / "schemas" / "examples" / "minimal.yaml"
    )  # Use the working theme
    output_file = current_dir / "magic_kingdom_guide.pdf"

    # Check if input files exist
    if not input_file.exists():
        print(f"❌ Input file not found: {input_file}")
        return 1

    if not theme_file.exists():
        print(f"❌ Theme file not found: {theme_file}")
        return 1

    print(f"📝 Input:  {input_file.name}")
    print(f"🎨 Theme:  {theme_file.name}")
    print(f"📄 Output: {output_file.name}")
    print()

    # Create CLI instance
    cli = MarkdownToPDFCLI()

    # Measure generation time
    start_time = time.time()

    try:
        # Generate PDF
        print("🔄 Generating PDF...")
        exit_code = cli.run(
            [
                str(input_file),
                "--output",
                str(output_file),
                "--theme",
                str(theme_file),
                "--title",
                "Magic Kingdom - Guia Completo do Dia 1",
                "--verbose",
            ]
        )

        end_time = time.time()
        generation_time = end_time - start_time

        if exit_code == 0:
            # Check if file was created and get size
            if output_file.exists():
                file_size = output_file.stat().st_size
                file_size_kb = file_size / 1024

                print("\n🎉 Success! Magic Kingdom guide generated!")
                print("📊 Statistics:")
                print(f"   • File size: {file_size:,} bytes ({file_size_kb:.1f} KB)")
                print(f"   • Generation time: {generation_time:.2f} seconds")
                print(f"   • Output: {output_file}")

                # Count some basic stats from the markdown
                content = input_file.read_text(encoding="utf-8")
                lines = len(content.split("\n"))
                words = len(content.split())
                chars = len(content)

                print("\n📖 Content Statistics:")
                print(f"   • Lines: {lines:,}")
                print(f"   • Words: {words:,}")
                print(f"   • Characters: {chars:,}")

                print("\n✨ Your magical PDF guide is ready! ✨")
                print(f"🎪 Open {output_file.name} to see the magic!")

                return 0
            else:
                print("❌ PDF file was not created!")
                return 1
        else:
            print(f"❌ PDF generation failed with exit code: {exit_code}")
            return exit_code

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
