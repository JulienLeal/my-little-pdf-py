"""
Asset management package for Markdown-to-PDF conversion.

This package provides comprehensive asset handling including images, fonts,
and other static resources used in PDF documents.
"""

from .exceptions import (
    AssetCopyError,
    AssetError,
    AssetNotFoundError,
    AssetResolutionError,
    AssetValidationError,
)
from .fonts import FontInfo, FontManager
from .images import ImageInfo, ImageResolver
from .manager import AssetInfo, AssetManager
from .resolvers import AssetResolver

__all__ = [
    "AssetManager",
    "AssetInfo",
    "AssetResolver",
    "ImageResolver",
    "ImageInfo",
    "FontManager",
    "FontInfo",
    "AssetError",
    "AssetNotFoundError",
    "AssetResolutionError",
    "AssetCopyError",
    "AssetValidationError",
]
