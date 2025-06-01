"""
Configuration package for md-to-pdf.

This package provides YAML-based configuration management for PDF generation,
including theme configuration, validation, and typed configuration objects.
"""

from .exceptions import (
    ConfigurationError,
    FileNotFoundError,
    InvalidYAMLError,
    UnsupportedFeatureError,
    ValidationError,
)
from .parser import load_theme_config
from .schema import (
    ComponentConfig,
    Font,
    FontDeclaration,
    HeaderFooterConfig,
    Margin,
    PageSetup,
    ThemeConfig,
)
from .validators import (
    check_jsonschema_available,
    get_validation_summary,
    validate_theme_config,
)

__all__ = [
    # Configuration loading
    "load_theme_config",
    # Schema classes
    "ThemeConfig",
    "PageSetup",
    "Margin",
    "Font",
    "FontDeclaration",
    "ComponentConfig",
    "HeaderFooterConfig",
    # Validation
    "validate_theme_config",
    "check_jsonschema_available",
    "get_validation_summary",
    # Exceptions
    "ConfigurationError",
    "FileNotFoundError",
    "InvalidYAMLError",
    "ValidationError",
    "UnsupportedFeatureError",
]
