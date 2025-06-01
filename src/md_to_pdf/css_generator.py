"""
CSS generation from theme configuration.

This module converts theme.yaml configurations into CSS that can be used
by WeasyPrint for PDF generation.
"""

from pathlib import Path
from typing import Any

from .config import ThemeConfig


class CSSGenerator:
    """Generates CSS from theme configuration."""

    def __init__(self, theme_config: ThemeConfig):
        """Initialize CSS generator with theme configuration.

        Args:
            theme_config: Loaded theme configuration
        """
        self.theme_config = theme_config

    def generate_css(self) -> str:
        """Generate complete CSS from theme configuration.

        Returns:
            Complete CSS string ready for WeasyPrint
        """
        css_parts = []

        # Generate page setup CSS
        css_parts.append(self._generate_page_css())

        # Generate font declarations
        if self.theme_config.has_custom_fonts:
            css_parts.append(self._generate_font_css())

        # Generate element styles
        if self.theme_config.styles:
            css_parts.append(self._generate_element_styles())

        # Generate header/footer CSS
        css_parts.append(self._generate_header_footer_css())

        return "\n\n".join(filter(None, css_parts))

    def _generate_page_css(self) -> str:
        """Generate @page CSS rules from page setup configuration."""
        page_setup = self.theme_config.page_setup

        css_rules = []

        # Page size and orientation
        size_rule = f"size: {page_setup.size}"
        if page_setup.orientation == "landscape":
            size_rule += " landscape"
        css_rules.append(size_rule)

        # Page margins
        margin = page_setup.margin
        margin_rule = (
            f"margin: {margin.top} {margin.right} {margin.bottom} {margin.left}"
        )
        css_rules.append(margin_rule)

        page_css = "@page {\n"
        for rule in css_rules:
            page_css += f"    {rule};\n"
        page_css += "}"

        # Body default font
        body_css = "body {\n"
        font = page_setup.default_font
        body_css += f"    font-family: {', '.join(f'"{f}"' for f in font.family)};\n"
        body_css += f"    font-size: {font.size};\n"
        body_css += f"    color: {font.color};\n"
        body_css += "}"

        return f"{page_css}\n\n{body_css}"

    def _generate_font_css(self) -> str:
        """Generate @font-face declarations for custom fonts."""
        font_css = []

        for font_decl in self.theme_config.fonts:
            # Generate @font-face rules for each font variant
            if font_decl.normal:
                font_css.append(
                    self._create_font_face(
                        font_decl.name, font_decl.normal, "normal", "normal"
                    )
                )

            if font_decl.bold:
                font_css.append(
                    self._create_font_face(
                        font_decl.name, font_decl.bold, "bold", "normal"
                    )
                )

            if font_decl.italic:
                font_css.append(
                    self._create_font_face(
                        font_decl.name, font_decl.italic, "normal", "italic"
                    )
                )

            if font_decl.bold_italic:
                font_css.append(
                    self._create_font_face(
                        font_decl.name, font_decl.bold_italic, "bold", "italic"
                    )
                )

        return "\n\n".join(font_css)

    def _create_font_face(
        self, family_name: str, font_path: str, weight: str, style: str
    ) -> str:
        """Create a single @font-face rule.

        Args:
            family_name: Font family name
            font_path: Path to font file
            weight: Font weight (normal, bold, etc.)
            style: Font style (normal, italic)

        Returns:
            @font-face CSS rule
        """
        # Convert file path to URL format for CSS
        font_url = Path(font_path).as_uri()

        # Determine font format from file extension
        ext = Path(font_path).suffix.lower()
        format_map = {
            ".ttf": "truetype",
            ".otf": "opentype",
            ".woff": "woff",
            ".woff2": "woff2",
        }
        font_format = format_map.get(ext, "truetype")

        return f"""@font-face {{
    font-family: "{family_name}";
    src: url("{font_url}") format("{font_format}");
    font-weight: {weight};
    font-style: {style};
}}"""

    def _generate_element_styles(self) -> str:
        """Generate CSS for Markdown element styles."""
        element_css = []

        for element, styles in self.theme_config.styles.items():
            css_rule = f"{element} {{\n"

            for property_name, value in styles.items():
                css_property = self._convert_property_name(property_name)
                css_value = self._convert_property_value(property_name, value)
                css_rule += f"    {css_property}: {css_value};\n"

            css_rule += "}"
            element_css.append(css_rule)

        return "\n\n".join(element_css)

    def _convert_property_name(self, property_name: str) -> str:
        """Convert theme property name to CSS property name.

        Args:
            property_name: Property name from theme config

        Returns:
            CSS property name
        """
        # Convert underscore to hyphen for CSS
        return property_name.replace("_", "-")

    def _convert_property_value(self, property_name: str, value: Any) -> str:
        """Convert theme property value to CSS value.

        Args:
            property_name: Property name for context
            value: Property value from theme config

        Returns:
            CSS-formatted value
        """
        if isinstance(value, list):
            # Handle font family lists
            if property_name == "font_family":
                return ", ".join(f'"{font}"' for font in value)
            else:
                return ", ".join(str(v) for v in value)
        elif isinstance(value, (int, float)):
            # Handle numeric values (like font-weight)
            return str(value)
        else:
            # Handle string values
            return str(value)

    def _generate_header_footer_css(self) -> str:
        """Generate CSS for page headers and footers."""
        css_parts = []

        # Generate header CSS
        for name, header_config in self.theme_config.page_headers.items():
            if any([header_config.left, header_config.center, header_config.right]):
                css_parts.append(self._generate_header_css(name, header_config))

        # Generate footer CSS
        for name, footer_config in self.theme_config.page_footers.items():
            if any([footer_config.left, footer_config.center, footer_config.right]):
                css_parts.append(self._generate_footer_css(name, footer_config))

        return "\n\n".join(css_parts)

    def _generate_header_css(self, name: str, header_config) -> str:
        """Generate CSS for a specific header configuration."""
        css_rules = []

        # Header positioning and content
        if header_config.left:
            css_rules.append(f"""@page {{
    @top-left {{
        content: "{header_config.left}";
        font-family: {", ".join(f'"{f}"' for f in header_config.font_family)};
        font-size: {header_config.font_size};
        color: {header_config.color};
    }}
}}""")

        if header_config.center:
            css_rules.append(f"""@page {{
    @top-center {{
        content: "{header_config.center}";
        font-family: {", ".join(f'"{f}"' for f in header_config.font_family)};
        font-size: {header_config.font_size};
        color: {header_config.color};
    }}
}}""")

        if header_config.right:
            css_rules.append(f"""@page {{
    @top-right {{
        content: "{header_config.right}";
        font-family: {", ".join(f'"{f}"' for f in header_config.font_family)};
        font-size: {header_config.font_size};
        color: {header_config.color};
    }}
}}""")

        # Line separator
        if header_config.line_separator:
            css_rules.append(f"""@page {{
    @top-center {{
        border-bottom: 1px solid {header_config.line_color};
        padding-bottom: 5px;
    }}
}}""")

        return "\n\n".join(css_rules)

    def _generate_footer_css(self, name: str, footer_config) -> str:
        """Generate CSS for a specific footer configuration."""
        css_rules = []

        # Footer positioning and content
        if footer_config.left:
            css_rules.append(f"""@page {{
    @bottom-left {{
        content: "{footer_config.left}";
        font-family: {", ".join(f'"{f}"' for f in footer_config.font_family)};
        font-size: {footer_config.font_size};
        color: {footer_config.color};
    }}
}}""")

        if footer_config.center:
            css_rules.append(f"""@page {{
    @bottom-center {{
        content: "{footer_config.center}";
        font-family: {", ".join(f'"{f}"' for f in footer_config.font_family)};
        font-size: {footer_config.font_size};
        color: {footer_config.color};
    }}
}}""")

        if footer_config.right:
            css_rules.append(f"""@page {{
    @bottom-right {{
        content: "{footer_config.right}";
        font-family: {", ".join(f'"{f}"' for f in footer_config.font_family)};
        font-size: {footer_config.font_size};
        color: {footer_config.color};
    }}
}}""")

        # Line separator
        if footer_config.line_separator:
            css_rules.append(f"""@page {{
    @bottom-center {{
        border-top: 1px solid {footer_config.line_color};
        padding-top: 5px;
    }}
}}""")

        return "\n\n".join(css_rules)

    def load_external_stylesheets(self) -> str:
        """Load and combine external CSS files specified in theme.

        Returns:
            Combined CSS content from external files
        """
        if not self.theme_config.has_custom_stylesheets:
            return ""

        css_content = []

        for stylesheet_path in self.theme_config.stylesheets:
            try:
                with open(stylesheet_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    css_content.append(f"/* {stylesheet_path} */\n{content}")
            except Exception as e:
                # Log warning but continue with other stylesheets
                print(f"Warning: Could not load stylesheet {stylesheet_path}: {e}")

        return "\n\n".join(css_content)
