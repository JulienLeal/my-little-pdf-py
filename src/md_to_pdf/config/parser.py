"""
YAML configuration parser for theme.yaml files.

This module handles loading, parsing, and converting YAML configuration
files into typed dataclass instances with validation.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Union

import yaml

from .exceptions import (
    ConfigurationError,
    FileNotFoundError,
    InvalidYAMLError,
    ValidationError,
)
from .schema import (
    ComponentConfig,
    Font,
    FontDeclaration,
    HeaderFooterConfig,
    Margin,
    PageSetup,
    ThemeConfig,
)
from .validators import check_jsonschema_available, validate_theme_config


def load_theme_config(
    config_path: Union[str, Path],
    validate_files: bool = True,
    validate_schema: bool = True,
) -> ThemeConfig:
    """Load and parse a theme configuration file.

    Args:
        config_path: Path to the theme.yaml file
        validate_files: Whether to validate that referenced files exist
        validate_schema: Whether to run JSON Schema validation

    Returns:
        ThemeConfig instance with parsed configuration

    Raises:
        FileNotFoundError: If the config file doesn't exist
        InvalidYAMLError: If the YAML syntax is invalid
        ValidationError: If the configuration structure is invalid
        ConfigurationError: For other configuration-related errors
    """
    config_path = Path(config_path)

    # Check if config file exists
    if not config_path.exists():
        raise FileNotFoundError(str(config_path), "theme configuration file")

    # Load YAML content
    try:
        with open(config_path, "r", encoding="utf-8") as file:
            yaml_data = yaml.safe_load(file) or {}
    except yaml.YAMLError as e:
        raise InvalidYAMLError(
            "Failed to parse YAML content", yaml_error=e, file_path=str(config_path)
        )
    except Exception as e:
        raise ConfigurationError(
            f"Failed to read configuration file: {e}", file_path=str(config_path)
        )

    # Validate configuration using JSON Schema (if requested and available)
    if validate_schema:
        if check_jsonschema_available():
            try:
                validate_theme_config(yaml_data, str(config_path))
            except ValidationError as e:
                # Re-raise with additional context
                raise ValidationError(
                    e.message, field_path=e.field_path, file_path=str(config_path)
                ) from e
        else:
            # Log warning if validation was requested but jsonschema isn't available
            print("Warning: JSON Schema validation skipped (jsonschema not installed)")

    # Convert to ThemeConfig
    try:
        theme_config = _parse_theme_config(yaml_data, config_path)
    except Exception as e:
        if isinstance(e, (ValidationError, ConfigurationError)):
            # Re-raise our own exceptions with file context
            e.file_path = str(config_path)
            raise
        else:
            # Wrap unexpected exceptions
            raise ConfigurationError(
                f"Unexpected error while parsing configuration: {e}",
                file_path=str(config_path),
            )

    # Resolve relative paths
    base_path = config_path.parent
    theme_config.resolve_font_paths(base_path)
    theme_config.resolve_stylesheet_paths(base_path)
    theme_config.resolve_template_paths(base_path)

    # Validate file existence if requested
    if validate_files:
        _validate_file_references(theme_config)

    return theme_config


def _parse_theme_config(data: Dict[str, Any], config_path: Path) -> ThemeConfig:
    """Parse YAML data into ThemeConfig dataclass.

    Args:
        data: Parsed YAML data
        config_path: Path to the config file (for error context)

    Returns:
        ThemeConfig instance
    """
    try:
        # Parse page setup
        page_setup_data = data.get("page_setup", {})
        page_setup = _parse_page_setup(page_setup_data)

        # Parse fonts
        fonts_data = data.get("fonts", [])
        fonts = _parse_fonts(fonts_data)

        # Parse stylesheets
        stylesheets = data.get("stylesheets", [])
        if not isinstance(stylesheets, list):
            raise ValidationError("stylesheets must be a list")

        # Parse styles
        styles = data.get("styles", {})
        if not isinstance(styles, dict):
            raise ValidationError("styles must be a dictionary")

        # Parse custom components
        components_data = data.get("custom_components", {})
        custom_components = _parse_custom_components(components_data)

        # Parse headers
        headers_data = data.get("page_headers", {})
        page_headers = _parse_headers_footers(headers_data)

        # Parse footers
        footers_data = data.get("page_footers", {})
        page_footers = _parse_headers_footers(footers_data)

        return ThemeConfig(
            page_setup=page_setup,
            fonts=fonts,
            stylesheets=stylesheets,
            styles=styles,
            custom_components=custom_components,
            page_headers=page_headers,
            page_footers=page_footers,
        )

    except ValidationError:
        raise  # Re-raise validation errors as-is
    except Exception as e:
        raise ValidationError(f"Failed to parse theme configuration: {e}")


def _parse_page_setup(data: Dict[str, Any]) -> PageSetup:
    """Parse page setup configuration."""
    try:
        size = data.get("size", "A4")
        orientation = data.get("orientation", "portrait")

        # Parse margin (can be string or dict)
        margin_data = data.get("margin", "2cm")
        if isinstance(margin_data, str):
            margin = Margin.from_uniform(margin_data)
        elif isinstance(margin_data, dict):
            margin = Margin(
                top=margin_data.get("top", "2cm"),
                bottom=margin_data.get("bottom", "2cm"),
                left=margin_data.get("left", "2cm"),
                right=margin_data.get("right", "2cm"),
            )
        else:
            raise ValidationError(
                "margin must be a string or dictionary", "page_setup.margin"
            )

        # Parse default font
        font_data = data.get("default_font", {})
        default_font = Font(
            family=font_data.get("family", ["Open Sans", "Arial", "sans-serif"]),
            size=font_data.get("size", "11pt"),
            color=font_data.get("color", "#333333"),
        )

        return PageSetup(
            size=size,
            orientation=orientation,
            margin=margin,
            default_font=default_font,
        )

    except ValidationError:
        raise
    except Exception as e:
        raise ValidationError(f"Invalid page_setup configuration: {e}", "page_setup")


def _parse_fonts(data: List[Dict[str, Any]]) -> List[FontDeclaration]:
    """Parse font declarations."""
    fonts = []

    if not isinstance(data, list):
        raise ValidationError("fonts must be a list", "fonts")

    for i, font_data in enumerate(data):
        if not isinstance(font_data, dict):
            raise ValidationError(f"font entry {i} must be a dictionary", f"fonts[{i}]")

        if "name" not in font_data:
            raise ValidationError(
                f"font entry {i} must have a 'name' field", f"fonts[{i}].name"
            )

        try:
            font = FontDeclaration(
                name=font_data["name"],
                normal=font_data.get("normal"),
                bold=font_data.get("bold"),
                italic=font_data.get("italic"),
                bold_italic=font_data.get("bold_italic"),
            )
            fonts.append(font)
        except ValueError as e:
            raise ValidationError(str(e), f"fonts[{i}]")

    return fonts


def _parse_custom_components(data: Dict[str, Any]) -> Dict[str, ComponentConfig]:
    """Parse custom component configurations."""
    components = {}

    if not isinstance(data, dict):
        raise ValidationError(
            "custom_components must be a dictionary", "custom_components"
        )

    for name, config_data in data.items():
        if not isinstance(config_data, dict):
            raise ValidationError(
                f"component '{name}' configuration must be a dictionary",
                f"custom_components.{name}",
            )

        component_config = ComponentConfig(
            template=config_data.get("template"),
            default_icon=config_data.get("default_icon"),
            default_attributes=config_data.get("default_attributes", {}),
        )
        components[name] = component_config

    return components


def _parse_headers_footers(data: Dict[str, Any]) -> Dict[str, HeaderFooterConfig]:
    """Parse header or footer configurations."""
    configs = {}

    if not isinstance(data, dict):
        raise ValidationError("headers/footers configuration must be a dictionary")

    for name, config_data in data.items():
        if not isinstance(config_data, dict):
            raise ValidationError(f"'{name}' configuration must be a dictionary")

        config = HeaderFooterConfig(
            left=config_data.get("left", ""),
            center=config_data.get("center", ""),
            right=config_data.get("right", ""),
            font_family=config_data.get("font_family", ["Open Sans", "sans-serif"]),
            font_size=config_data.get("font_size", "9pt"),
            color=config_data.get("color", "#666666"),
            line_separator=config_data.get("line_separator", False),
            line_color=config_data.get("line_color", "#cccccc"),
        )
        configs[name] = config

    return configs


def _validate_file_references(config: ThemeConfig) -> None:
    """Validate that all referenced files exist.

    Args:
        config: Theme configuration to validate

    Raises:
        FileNotFoundError: If any referenced file is missing
    """
    # Validate font files
    for font in config.fonts:
        for weight, path in [
            ("normal", font.normal),
            ("bold", font.bold),
            ("italic", font.italic),
            ("bold_italic", font.bold_italic),
        ]:
            if path and not os.path.exists(path):
                raise FileNotFoundError(
                    f"Font file for '{font.name}' ({weight}): {path}"
                )

    # Validate stylesheets
    for stylesheet in config.stylesheets:
        if not os.path.exists(stylesheet):
            raise FileNotFoundError(f"Stylesheet: {stylesheet}")

    # Validate component templates
    for name, component in config.custom_components.items():
        if component.template and not os.path.exists(component.template):
            raise FileNotFoundError(
                f"Template for component '{name}': {component.template}"
            )
