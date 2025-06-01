"""
YAML configuration validation using JSON Schema.

This module provides comprehensive validation for theme.yaml files using
the JSON Schema specification and custom validation functions.
"""

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

try:
    import jsonschema
    from jsonschema import ValidationError as JsonSchemaValidationError

    JSONSCHEMA_AVAILABLE = True
except ImportError:
    jsonschema = None
    JsonSchemaValidationError = Exception
    JSONSCHEMA_AVAILABLE = False

from .exceptions import UnsupportedFeatureError, ValidationError

# Schema file path relative to this module
SCHEMA_FILE = (
    Path(__file__).parent.parent.parent.parent / "schemas" / "theme_schema.json"
)


def validate_theme_config(
    config_data: Dict[str, Any], config_path: Optional[str] = None
) -> None:
    """Validate theme configuration data against JSON Schema.

    Args:
        config_data: Parsed YAML configuration data
        config_path: Path to the config file for error context

    Raises:
        ValidationError: If validation fails
        UnsupportedFeatureError: If jsonschema is not available
    """
    if not JSONSCHEMA_AVAILABLE or jsonschema is None:
        raise UnsupportedFeatureError(
            "jsonschema library not available", "Install with: pip install jsonschema"
        )

    # Load JSON Schema
    try:
        with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
            schema = json.load(f)
    except FileNotFoundError:
        raise ValidationError(
            f"Schema file not found: {SCHEMA_FILE}", file_path=config_path
        )
    except json.JSONDecodeError as e:
        raise ValidationError(
            f"Invalid JSON schema file: {e}", file_path=str(SCHEMA_FILE)
        )

    # Validate against schema
    try:
        jsonschema.validate(instance=config_data, schema=schema)
    except JsonSchemaValidationError as e:
        # Convert JSON Schema error to our ValidationError with better messaging
        field_path = _format_validation_path(e)
        error_msg = _format_validation_message(e)

        raise ValidationError(error_msg, field_path=field_path, file_path=config_path)

    # Additional custom validations
    _validate_custom_rules(config_data, config_path)


def _format_validation_path(error: Any) -> str:
    """Format JSON Schema validation path for human readability.

    Args:
        error: JSON Schema validation error

    Returns:
        Formatted field path string
    """
    # Safely get path items, handling different jsonschema versions
    try:
        if hasattr(error, "absolute_path"):
            path_items = list(error.absolute_path)
        elif hasattr(error, "path"):
            path_items = list(error.path)
        else:
            return "root"
    except (AttributeError, TypeError):
        return "root"

    if not path_items:
        return "root"

    formatted_path = []
    for item in path_items:
        if isinstance(item, int):
            # Array index
            if formatted_path:
                formatted_path[-1] = f"{formatted_path[-1]}[{item}]"
            else:
                formatted_path.append(f"[{item}]")
        else:
            # Object property
            formatted_path.append(str(item))

    return ".".join(formatted_path)


def _format_validation_message(error: Any) -> str:
    """Format JSON Schema validation error message for clarity.

    Args:
        error: JSON Schema validation error

    Returns:
        Human-readable error message
    """
    try:
        message = str(getattr(error, "message", "Validation failed"))
        schema = getattr(error, "schema", {})
        instance = getattr(error, "instance", None)
    except (AttributeError, TypeError):
        return "Configuration validation failed"

    # Improve common error messages
    if "is not of type" in message:
        if "string" in message:
            message = "must be a text value"
        elif "array" in message:
            message = "must be a list"
        elif "object" in message:
            message = "must be a dictionary/object"
        elif "boolean" in message:
            message = "must be true or false"
        elif "number" in message or "integer" in message:
            message = "must be a number"

    elif "is not one of" in message:
        # Extract enum values for better error messages
        if schema and "enum" in schema:
            allowed_values = ", ".join(f"'{v}'" for v in schema["enum"])
            message = f"must be one of: {allowed_values}"

    elif "does not match" in message:
        # Pattern validation errors
        if schema and "pattern" in schema:
            pattern = schema["pattern"]
            if "cm|mm|in|pt|px" in pattern:
                message = "must be a valid CSS unit (e.g., '2cm', '10pt', '1in')"
            elif "#[0-9a-fA-F]{6}" in pattern:
                message = "must be a valid hex color (e.g., '#ffffff', '#333333')"
            elif "pt|px|em|rem" in pattern:
                message = "must be a valid font size (e.g., '12pt', '16px', '1.2em')"

    elif "Additional properties are not allowed" in message:
        # Extract the invalid property name
        if instance and isinstance(instance, dict) and schema:
            properties = schema.get("properties", {})
            extra_props = set(instance.keys()) - set(properties.keys())
            if extra_props:
                prop_list = ", ".join(f"'{p}'" for p in extra_props)
                message = f"unknown properties: {prop_list}"

    elif "is a required property" in message:
        message = "required field is missing"

    return message


def _validate_custom_rules(
    config_data: Dict[str, Any], config_path: Optional[str] = None
) -> None:
    """Apply custom validation rules beyond JSON Schema.

    Args:
        config_data: Configuration data to validate
        config_path: Path to the config file for error context

    Raises:
        ValidationError: If custom validation fails
    """
    # Validate page sizes
    if "page_setup" in config_data:
        _validate_page_setup(config_data["page_setup"], config_path)

    # Validate font declarations
    if "fonts" in config_data:
        _validate_fonts(config_data["fonts"], config_path)

    # Validate style properties
    if "styles" in config_data:
        _validate_styles(config_data["styles"], config_path)

    # Validate component names
    if "custom_components" in config_data:
        _validate_component_names(config_data["custom_components"], config_path)


def _validate_page_setup(
    page_setup: Dict[str, Any], config_path: Optional[str] = None
) -> None:
    """Validate page setup configuration.

    Args:
        page_setup: Page setup configuration
        config_path: Config file path for error context
    """
    # Validate page size
    size = page_setup.get("size", "A4")
    valid_sizes = ["A4", "A3", "A5", "Letter", "Legal", "Tabloid"]
    if size not in valid_sizes:
        raise ValidationError(
            f"Invalid page size '{size}'. Must be one of: {', '.join(valid_sizes)}",
            field_path="page_setup.size",
            file_path=config_path,
        )

    # Validate orientation
    orientation = page_setup.get("orientation", "portrait")
    if orientation not in ["portrait", "landscape"]:
        raise ValidationError(
            f"Invalid orientation '{orientation}'. Must be 'portrait' or 'landscape'",
            field_path="page_setup.orientation",
            file_path=config_path,
        )


def _validate_fonts(
    fonts: Union[List[Dict[str, Any]], Any], config_path: Optional[str] = None
) -> None:
    """Validate font declarations.

    Args:
        fonts: List of font declarations
        config_path: Config file path for error context
    """
    if not isinstance(fonts, list):
        return  # Schema validation will catch this

    font_names = set()

    for i, font in enumerate(fonts):
        if not isinstance(font, dict):
            continue  # Schema validation will catch this

        font_name = font.get("name")
        if not font_name:
            continue  # Schema validation will catch this

        # Check for duplicate font names
        if font_name in font_names:
            raise ValidationError(
                f"Duplicate font name '{font_name}'. Font names must be unique",
                field_path=f"fonts[{i}].name",
                file_path=config_path,
            )
        font_names.add(font_name)

        # Validate that at least one font file is specified
        font_files = [
            font.get("normal"),
            font.get("bold"),
            font.get("italic"),
            font.get("bold_italic"),
        ]
        if not any(font_files):
            raise ValidationError(
                f"Font '{font_name}' must specify at least one font file",
                field_path=f"fonts[{i}]",
                file_path=config_path,
            )


def _validate_styles(styles: Dict[str, Any], config_path: Optional[str] = None) -> None:
    """Validate style definitions.

    Args:
        styles: Style definitions dictionary
        config_path: Config file path for error context
    """
    if not isinstance(styles, dict):
        return  # Schema validation will catch this

    # Valid Markdown elements
    valid_elements = {
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "p",
        "ul",
        "ol",
        "li",
        "blockquote",
        "a",
        "strong",
        "em",
        "code",
        "pre",
        "table",
        "th",
        "td",
        "img",
        "hr",
        "code_block",
    }

    for element_name, element_styles in styles.items():
        # Check if element is valid
        if element_name not in valid_elements:
            raise ValidationError(
                f"Unknown Markdown element '{element_name}'. "
                f"Valid elements: {', '.join(sorted(valid_elements))}",
                field_path=f"styles.{element_name}",
                file_path=config_path,
            )

        # Validate individual style properties
        if isinstance(element_styles, dict):
            _validate_style_properties(
                element_styles, f"styles.{element_name}", config_path
            )


def _validate_style_properties(
    properties: Dict[str, Any], field_path: str, config_path: Optional[str] = None
) -> None:
    """Validate individual style properties.

    Args:
        properties: Style properties dictionary
        field_path: Current field path for error context
        config_path: Config file path for error context
    """
    # Validate color properties
    color_properties = ["color", "background_color", "line_color"]
    for prop in color_properties:
        if prop in properties:
            _validate_color_value(properties[prop], f"{field_path}.{prop}", config_path)

    # Validate unit properties
    unit_properties = [
        "font_size",
        "margin",
        "margin_top",
        "margin_bottom",
        "margin_left",
        "margin_right",
        "padding",
        "padding_top",
        "padding_bottom",
        "padding_left",
        "padding_right",
        "border_radius",
    ]
    for prop in unit_properties:
        if prop in properties:
            _validate_unit_value(properties[prop], f"{field_path}.{prop}", config_path)


def _validate_color_value(
    value: Any, field_path: str, config_path: Optional[str] = None
) -> None:
    """Validate color value format.

    Args:
        value: Color value to validate
        field_path: Field path for error context
        config_path: Config file path for error context
    """
    if not isinstance(value, str):
        raise ValidationError(
            "Color must be a string", field_path=field_path, file_path=config_path
        )

    # Check hex color pattern
    if not re.match(r"^#[0-9a-fA-F]{6}$", value):
        raise ValidationError(
            f"Invalid color format '{value}'. Must be a 6-digit hex color (e.g., '#ffffff')",
            field_path=field_path,
            file_path=config_path,
        )


def _validate_unit_value(
    value: Any, field_path: str, config_path: Optional[str] = None
) -> None:
    """Validate CSS unit value format.

    Args:
        value: Unit value to validate
        field_path: Field path for error context
        config_path: Config file path for error context
    """
    if not isinstance(value, str):
        raise ValidationError(
            "Unit value must be a string", field_path=field_path, file_path=config_path
        )

    # Check if this is a shorthand property (margin, padding)
    if any(prop in field_path for prop in ["margin", "padding"]) and not any(
        side in field_path for side in ["_top", "_bottom", "_left", "_right"]
    ):
        # For shorthand properties, allow multiple space-separated values
        parts = value.strip().split()
        if len(parts) > 4:
            raise ValidationError(
                f"Invalid shorthand format '{value}'. Maximum 4 values allowed",
                field_path=field_path,
                file_path=config_path,
            )

        # Validate each part
        for part in parts:
            if not (
                part == "0" or re.match(r"^\d+(\.\d+)?(cm|mm|in|pt|px|em|rem|%)$", part)
            ):
                raise ValidationError(
                    f"Invalid unit format '{part}' in '{value}'. Each value must be a number "
                    "followed by a valid unit (e.g., '2cm', '12pt', '1.5em') or '0'",
                    field_path=field_path,
                    file_path=config_path,
                )
    else:
        # For single unit properties, use the original validation
        if not (
            value == "0" or re.match(r"^\d+(\.\d+)?(cm|mm|in|pt|px|em|rem|%)$", value)
        ):
            raise ValidationError(
                f"Invalid unit format '{value}'. Must be a number followed by a valid unit "
                "(e.g., '2cm', '12pt', '1.5em') or '0'",
                field_path=field_path,
                file_path=config_path,
            )


def _validate_component_names(
    components: Dict[str, Any], config_path: Optional[str] = None
) -> None:
    """Validate custom component names.

    Args:
        components: Custom components dictionary
        config_path: Config file path for error context
    """
    if not isinstance(components, dict):
        return  # Schema validation will catch this

    for component_name in components.keys():
        # Check if name is a valid Python identifier
        if not component_name.isidentifier():
            raise ValidationError(
                f"Invalid component name '{component_name}'. Component names must be valid "
                "Python identifiers (letters, numbers, underscores; cannot start with number)",
                field_path=f"custom_components.{component_name}",
                file_path=config_path,
            )

        # Check for reserved names
        reserved_names = {"if", "for", "while", "class", "def", "import", "from", "as"}
        if component_name in reserved_names:
            raise ValidationError(
                f"Component name '{component_name}' is reserved. Please choose a different name",
                field_path=f"custom_components.{component_name}",
                file_path=config_path,
            )


def check_jsonschema_available() -> bool:
    """Check if jsonschema library is available.

    Returns:
        True if jsonschema is available, False otherwise
    """
    return JSONSCHEMA_AVAILABLE


def get_validation_summary(config_data: Dict[str, Any]) -> Dict[str, Any]:
    """Get a summary of configuration validation status.

    Args:
        config_data: Configuration data to analyze

    Returns:
        Dictionary with validation summary information
    """
    summary = {
        "jsonschema_available": check_jsonschema_available(),
        "sections_present": [],
        "font_count": 0,
        "stylesheet_count": 0,
        "component_count": 0,
        "styled_elements": 0,
    }

    # Check which sections are present
    sections = [
        "page_setup",
        "fonts",
        "stylesheets",
        "styles",
        "custom_components",
        "page_headers",
        "page_footers",
    ]
    for section in sections:
        if section in config_data and config_data[section]:
            summary["sections_present"].append(section)

    # Count various configuration items
    if "fonts" in config_data:
        summary["font_count"] = len(config_data["fonts"])

    if "stylesheets" in config_data:
        summary["stylesheet_count"] = len(config_data["stylesheets"])

    if "custom_components" in config_data:
        summary["component_count"] = len(config_data["custom_components"])

    if "styles" in config_data:
        summary["styled_elements"] = len(config_data["styles"])

    return summary
