#!/usr/bin/env python3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from md_to_pdf.core import MarkdownToPDFConverter


def debug_html():
    converter = MarkdownToPDFConverter()
    html = converter.markdown_processor.convert_file(
        Path("examples/magic_kingdom_guide.md")
    )

    print("COMPONENT CLASSES FOUND:")
    print(f"magic-secret: {'magic-secret' in html}")
    print(f"tip-box: {'tip-box' in html}")
    print(f"attention-box: {'attention-box' in html}")

    print("\nFirst component HTML snippet:")
    if "magic-secret" in html:
        start = html.find("magic-secret")
        snippet = html[max(0, start - 50) : start + 200]
        print(snippet)

    # Save HTML for inspection
    with open("debug_output.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("\nFull HTML saved to debug_output.html")


if __name__ == "__main__":
    debug_html()
