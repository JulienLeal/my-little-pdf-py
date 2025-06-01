"""
Configuration schema dataclasses for theme.yaml files.

This module defines type-safe dataclasses that represent the complete
theme configuration structure with sensible defaults.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


@dataclass
class Margin:
    """Page margin configuration.

    Can be specified as uniform margin or individual sides.
    """

    top: str = "2cm"
    bottom: str = "2cm"
    left: str = "2cm"
    right: str = "2cm"

    @classmethod
    def from_uniform(cls, margin: str) -> "Margin":
        """Create margin with uniform spacing on all sides."""
        return cls(top=margin, bottom=margin, left=margin, right=margin)


@dataclass
class Font:
    """Default font configuration."""

    family: List[str] = field(
        default_factory=lambda: ["Open Sans", "Arial", "sans-serif"]
    )
    size: str = "11pt"
    color: str = "#333333"


@dataclass
class PageSetup:
    """Page layout and default font settings."""

    size: str = "A4"
    orientation: str = "portrait"
    margin: Margin = field(default_factory=Margin)
    default_font: Font = field(default_factory=Font)


@dataclass
class FontDeclaration:
    """Custom font declaration for embedding."""

    name: str
    normal: Optional[str] = None
    bold: Optional[str] = None
    italic: Optional[str] = None
    bold_italic: Optional[str] = None

    def __post_init__(self):
        """Validate that at least normal font is provided."""
        if not self.normal and not any([self.bold, self.italic, self.bold_italic]):
            raise ValueError(
                f"Font '{self.name}' must have at least one font file specified"
            )


@dataclass
class ComponentConfig:
    """Configuration for custom Markdown components."""

    template: Optional[str] = None
    default_icon: Optional[str] = None
    default_attributes: Dict[str, str] = field(default_factory=dict)


@dataclass
class HeaderFooterConfig:
    """Configuration for page headers and footers."""

    left: str = ""
    center: str = ""
    right: str = ""
    font_family: List[str] = field(default_factory=lambda: ["Open Sans", "sans-serif"])
    font_size: str = "9pt"
    color: str = "#666666"
    line_separator: bool = False
    line_color: str = "#cccccc"


@dataclass
class ThemeConfig:
    """Complete theme configuration.

    This is the root configuration object that contains all theme settings
    loaded from a theme.yaml file.
    """

    page_setup: PageSetup = field(default_factory=PageSetup)
    fonts: List[FontDeclaration] = field(default_factory=list)
    stylesheets: List[str] = field(default_factory=list)
    styles: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    custom_components: Dict[str, ComponentConfig] = field(default_factory=dict)
    page_headers: Dict[str, HeaderFooterConfig] = field(default_factory=dict)
    page_footers: Dict[str, HeaderFooterConfig] = field(default_factory=dict)

    def __post_init__(self):
        """Post-initialization validation and setup."""
        # Ensure default header/footer configurations exist
        if "default" not in self.page_headers:
            self.page_headers["default"] = HeaderFooterConfig()
        if "default" not in self.page_footers:
            self.page_footers["default"] = HeaderFooterConfig()

    @property
    def has_custom_fonts(self) -> bool:
        """Check if any custom fonts are declared."""
        return len(self.fonts) > 0

    @property
    def has_custom_stylesheets(self) -> bool:
        """Check if any external stylesheets are specified."""
        return len(self.stylesheets) > 0

    @property
    def has_custom_components(self) -> bool:
        """Check if any custom components are configured."""
        return len(self.custom_components) > 0

    def get_component_config(self, component_name: str) -> Optional[ComponentConfig]:
        """Get configuration for a specific component."""
        return self.custom_components.get(component_name)

    def get_element_styles(self, element: str) -> Dict[str, Any]:
        """Get style configuration for a specific Markdown element."""
        return self.styles.get(element, {})

    def resolve_font_paths(self, base_path: Path) -> None:
        """Resolve relative font paths to absolute paths.

        Args:
            base_path: Base directory for resolving relative paths (usually theme.yaml location)
        """
        for font in self.fonts:
            if font.normal:
                font.normal = str((base_path / font.normal).resolve())
            if font.bold:
                font.bold = str((base_path / font.bold).resolve())
            if font.italic:
                font.italic = str((base_path / font.italic).resolve())
            if font.bold_italic:
                font.bold_italic = str((base_path / font.bold_italic).resolve())

    def resolve_stylesheet_paths(self, base_path: Path) -> None:
        """Resolve relative stylesheet paths to absolute paths.

        Args:
            base_path: Base directory for resolving relative paths (usually theme.yaml location)
        """
        self.stylesheets = [
            str((base_path / stylesheet).resolve()) for stylesheet in self.stylesheets
        ]

    def resolve_template_paths(self, base_path: Path) -> None:
        """Resolve relative template paths to absolute paths.

        Args:
            base_path: Base directory for resolving relative paths (usually theme.yaml location)
        """
        for component_config in self.custom_components.values():
            if component_config.template:
                component_config.template = str(
                    (base_path / component_config.template).resolve()
                )


# Type aliases for convenience
MarginSpec = Union[
    str, Dict[str, str]
]  # Can be "2cm" or {"top": "1cm", "bottom": "2cm"}
StyleDict = Dict[str, Any]  # Style properties dictionary
