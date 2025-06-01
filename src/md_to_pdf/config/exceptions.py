"""
Configuration-specific exceptions for the theme configuration system.
"""

from typing import Optional


class ConfigurationError(Exception):
    """Base exception for configuration-related errors."""

    def __init__(
        self,
        message: str,
        file_path: Optional[str] = None,
        line_number: Optional[int] = None,
    ):
        self.message = message
        self.file_path = file_path
        self.line_number = line_number

        # Build detailed error message
        error_parts = [message]
        if file_path:
            error_parts.append(f"File: {file_path}")
        if line_number:
            error_parts.append(f"Line: {line_number}")

        super().__init__(" | ".join(error_parts))


class ValidationError(ConfigurationError):
    """Raised when configuration validation fails."""

    def __init__(self, message: str, field_path: Optional[str] = None, **kwargs):
        self.field_path = field_path

        if field_path:
            message = f"Validation error in '{field_path}': {message}"
        else:
            message = f"Validation error: {message}"

        super().__init__(message, **kwargs)


class FileNotFoundError(ConfigurationError):
    """Raised when a required configuration file cannot be found."""

    def __init__(self, file_path: str, file_type: str = "file"):
        self.file_path = file_path
        self.file_type = file_type

        message = f"Required {file_type} not found: {file_path}"
        super().__init__(message, file_path=file_path)


class InvalidYAMLError(ConfigurationError):
    """Raised when YAML syntax is invalid."""

    def __init__(self, message: str, yaml_error: Optional[Exception] = None, **kwargs):
        self.yaml_error = yaml_error

        if yaml_error:
            message = f"Invalid YAML syntax: {message} (Original error: {yaml_error})"
        else:
            message = f"Invalid YAML syntax: {message}"

        super().__init__(message, **kwargs)


class FontNotFoundError(FileNotFoundError):
    """Raised when a declared font file cannot be found."""

    def __init__(self, font_name: str, font_path: str):
        self.font_name = font_name
        super().__init__(font_path, file_type=f"font file for '{font_name}'")


class StylesheetNotFoundError(FileNotFoundError):
    """Raised when a declared stylesheet cannot be found."""

    def __init__(self, stylesheet_path: str):
        super().__init__(stylesheet_path, file_type="stylesheet")


class TemplateNotFoundError(FileNotFoundError):
    """Raised when a component template cannot be found."""

    def __init__(self, component_name: str, template_path: str):
        self.component_name = component_name
        super().__init__(
            template_path, file_type=f"template for component '{component_name}'"
        )


class UnsupportedFeatureError(ConfigurationError):
    """Raised when a configuration uses an unsupported feature."""

    def __init__(self, feature: str, suggestion: Optional[str] = None):
        self.feature = feature
        self.suggestion = suggestion

        message = f"Unsupported feature: {feature}"
        if suggestion:
            message += f". Suggestion: {suggestion}"

        super().__init__(message)
