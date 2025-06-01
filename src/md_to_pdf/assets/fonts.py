"""
Font asset handling and management.

This module provides specialized functionality for handling font assets
including validation, CSS generation, and font loading.
"""

from pathlib import Path
from typing import Dict, List, Optional, Union

from .exceptions import AssetValidationError
from .resolvers import AssetResolver

# Import theme config if available
try:
    from ..config import FontDeclaration, ThemeConfig

    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False


class FontInfo:
    """Information about a font asset."""

    def __init__(self, path: Path):
        """Initialize font info.

        Args:
            path: Path to the font file
        """
        self.path = path
        self.format = self._detect_format()
        self.size_bytes = path.stat().st_size if path.exists() else 0
        self.family_name = self._extract_family_name()

    def _detect_format(self) -> str:
        """Detect font format from file extension."""
        extension = self.path.suffix.lower()

        format_map = {
            ".ttf": "truetype",
            ".otf": "opentype",
            ".woff": "woff",
            ".woff2": "woff2",
            ".eot": "embedded-opentype",
        }

        return format_map.get(extension, "unknown")

    def _extract_family_name(self) -> str:
        """Extract font family name from filename.

        This is a simple implementation. Full implementation would
        parse the font file to extract the actual family name.
        """
        # Remove extension and common suffixes
        name = self.path.stem

        # Remove common weight/style suffixes
        suffixes_to_remove = [
            "Regular",
            "Bold",
            "Italic",
            "BoldItalic",
            "Light",
            "Medium",
            "SemiBold",
            "ExtraBold",
            "Black",
            "Thin",
            "UltraLight",
        ]

        for suffix in suffixes_to_remove:
            if name.endswith(suffix):
                name = name[: -len(suffix)]
                break

        # Remove hyphens and underscores at the end
        return name.rstrip("-_")

    @property
    def is_web_font(self) -> bool:
        """Check if font is a web font format."""
        return self.format in ["woff", "woff2"]

    @property
    def is_desktop_font(self) -> bool:
        """Check if font is a desktop font format."""
        return self.format in ["truetype", "opentype"]


class FontManager:
    """Specialized font asset management."""

    def __init__(self, asset_resolver: Optional[AssetResolver] = None):
        """Initialize font manager.

        Args:
            asset_resolver: Base asset resolver to use
        """
        self.asset_resolver = asset_resolver or AssetResolver()
        self.supported_formats = {".ttf", ".otf", ".woff", ".woff2", ".eot"}
        self.font_cache: Dict[str, FontInfo] = {}

    def validate_font_file(self, font_path: Union[str, Path]) -> FontInfo:
        """Validate a font file and return font information.

        Args:
            font_path: Path to the font file

        Returns:
            FontInfo object with font details

        Raises:
            AssetValidationError: If font is not valid
        """
        font_path = Path(font_path)

        # Check if file exists
        if not font_path.exists():
            raise AssetValidationError(str(font_path), "Font file does not exist")

        # Check if it's a file
        if not font_path.is_file():
            raise AssetValidationError(str(font_path), "Font path is not a file")

        # Check format
        if not self._is_font_file(font_path):
            raise AssetValidationError(
                str(font_path),
                f"File is not a supported font format. Extension: {font_path.suffix}",
            )

        # Check file size (basic validation)
        if font_path.stat().st_size == 0:
            raise AssetValidationError(str(font_path), "Font file is empty")

        return FontInfo(font_path)

    def _is_font_file(self, file_path: Path) -> bool:
        """Check if file is a supported font format.

        Args:
            file_path: Path to check

        Returns:
            True if file is a supported font format
        """
        return file_path.suffix.lower() in self.supported_formats

    def load_fonts_from_theme(self, theme_config) -> List[FontInfo]:
        """Load fonts from theme configuration.

        Args:
            theme_config: Theme configuration object

        Returns:
            List of FontInfo objects for valid fonts

        Note:
            This requires the theme config to be available
        """
        if not CONFIG_AVAILABLE:
            return []

        fonts = []

        for font_decl in theme_config.fonts:
            # Validate each font variant
            font_files = {
                "normal": font_decl.normal,
                "bold": font_decl.bold,
                "italic": font_decl.italic,
                "bold_italic": font_decl.bold_italic,
            }

            for variant, font_path in font_files.items():
                if font_path:
                    try:
                        # Resolve the font path relative to theme config
                        resolved_path = self.asset_resolver.resolve_asset_path(
                            font_path,
                            context_path=getattr(theme_config, "_config_path", None),
                        )
                        font_info = self.validate_font_file(resolved_path)
                        fonts.append(font_info)
                    except Exception as e:
                        # Log warning but continue with other fonts
                        print(f"Warning: Failed to load font {font_path}: {e}")

        return fonts

    def generate_font_face_css(self, font_declarations: List) -> str:
        """Generate @font-face CSS rules from font declarations.

        Args:
            font_declarations: List of FontDeclaration objects

        Returns:
            CSS string with @font-face rules
        """
        if not CONFIG_AVAILABLE:
            return ""

        css_rules = []

        for font_decl in font_declarations:
            # Generate @font-face for each font variant
            variants = [
                ("normal", "normal", font_decl.normal),
                ("bold", "normal", font_decl.bold),
                ("normal", "italic", font_decl.italic),
                ("bold", "italic", font_decl.bold_italic),
            ]

            for weight, style, font_path in variants:
                if font_path:
                    try:
                        # Resolve font path
                        resolved_path = self.asset_resolver.resolve_asset_path(
                            font_path,
                            context_path=getattr(font_decl, "_context_path", None),
                        )

                        # Generate CSS rule
                        css_rule = self._create_font_face_rule(
                            font_decl.name, resolved_path, weight, style
                        )
                        css_rules.append(css_rule)

                    except Exception as e:
                        # Log warning but continue
                        print(f"Warning: Failed to process font {font_path}: {e}")

        return "\n\n".join(css_rules)

    def _create_font_face_rule(
        self, family_name: str, font_path: Path, weight: str, style: str
    ) -> str:
        """Create a single @font-face CSS rule.

        Args:
            family_name: Font family name
            font_path: Path to font file
            weight: Font weight (normal, bold)
            style: Font style (normal, italic)

        Returns:
            @font-face CSS rule string
        """
        # Convert path to URI
        font_uri = font_path.as_uri()

        # Detect format
        font_info = FontInfo(font_path)

        return f'''@font-face {{
    font-family: "{family_name}";
    src: url("{font_uri}") format("{font_info.format}");
    font-weight: {weight};
    font-style: {style};
}}'''

    def get_font_fallbacks(self, primary_fonts: List[str]) -> List[str]:
        """Get appropriate font fallbacks for a font stack.

        Args:
            primary_fonts: List of primary font names

        Returns:
            Complete font stack with fallbacks
        """
        # Common system font fallbacks
        sans_serif_fallbacks = ["Arial", "Helvetica", "sans-serif"]

        serif_fallbacks = ["Times New Roman", "Times", "serif"]

        monospace_fallbacks = ["Courier New", "Courier", "monospace"]

        # Analyze primary fonts to determine appropriate fallbacks
        font_stack = list(primary_fonts)

        # Determine font category from primary fonts
        has_serif = any("serif" in font.lower() for font in primary_fonts)
        has_monospace = any(
            any(
                mono in font.lower() for mono in ["mono", "courier", "consolas", "code"]
            )
            for font in primary_fonts
        )

        # Add appropriate fallbacks
        if has_monospace:
            font_stack.extend(monospace_fallbacks)
        elif has_serif:
            font_stack.extend(serif_fallbacks)
        else:
            font_stack.extend(sans_serif_fallbacks)

        # Remove duplicates while preserving order
        seen = set()
        unique_fonts = []
        for font in font_stack:
            if font not in seen:
                seen.add(font)
                unique_fonts.append(font)

        return unique_fonts

    def scan_for_fonts(
        self, directory: Union[str, Path], recursive: bool = True
    ) -> List[Path]:
        """Scan directory for font files.

        Args:
            directory: Directory to scan
            recursive: Whether to scan recursively

        Returns:
            List of found font file paths
        """
        directory = Path(directory)
        if not directory.exists() or not directory.is_dir():
            return []

        fonts = []
        pattern = "**/*" if recursive else "*"

        for file_path in directory.glob(pattern):
            if file_path.is_file() and self._is_font_file(file_path):
                fonts.append(file_path)

        return fonts

    def validate_font_stack(
        self, font_stack: List[str]
    ) -> Dict[str, Union[bool, List[str]]]:
        """Validate a font stack for potential issues.

        Args:
            font_stack: List of font names in priority order

        Returns:
            Dictionary with validation results
        """
        results = {
            "has_fallback": False,
            "has_web_safe": False,
            "has_generic": False,
            "warnings": [],
        }

        # Check for generic fallbacks
        generic_families = {"serif", "sans-serif", "monospace", "cursive", "fantasy"}
        results["has_generic"] = any(font in generic_families for font in font_stack)

        # Check for web-safe fonts
        web_safe_fonts = {
            "Arial",
            "Helvetica",
            "Times New Roman",
            "Times",
            "Courier New",
            "Courier",
            "Verdana",
            "Georgia",
        }
        results["has_web_safe"] = any(font in web_safe_fonts for font in font_stack)

        # Check for fallbacks
        results["has_fallback"] = len(font_stack) > 1

        # Generate warnings
        if not results["has_generic"]:
            results["warnings"].append("Font stack should end with a generic family")

        if not results["has_fallback"]:
            results["warnings"].append("Font stack should include fallback fonts")

        if len(font_stack) == 1 and font_stack[0] not in web_safe_fonts:
            results["warnings"].append(
                "Single custom font without fallbacks may not display correctly"
            )

        return results
