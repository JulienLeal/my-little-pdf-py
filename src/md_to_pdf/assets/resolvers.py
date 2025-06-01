"""
Asset path resolution utilities.

This module provides path resolution strategies for different types of assets
and context scenarios (Markdown files, theme configs, templates, etc.).
"""

import os
from pathlib import Path
from typing import List, Optional, Union

from .exceptions import AssetNotFoundError, AssetResolutionError


class AssetResolver:
    """Handles asset path resolution with multiple fallback strategies."""

    def __init__(self, base_paths: Optional[List[Union[str, Path]]] = None):
        """Initialize asset resolver.

        Args:
            base_paths: List of base directories to search for assets
        """
        self.base_paths = [Path(p) for p in (base_paths or [])]
        self.common_asset_dirs = ["assets", "images", "fonts", "static", "media"]

    def resolve_asset_path(
        self,
        asset_path: str,
        context_path: Optional[Union[str, Path]] = None,
        asset_type: Optional[str] = None,
    ) -> Path:
        """Resolve an asset path using multiple strategies.

        Args:
            asset_path: Original asset path from source
            context_path: Path to the file referencing this asset (for relative resolution)
            asset_type: Type of asset (image, font, etc.) for type-specific search

        Returns:
            Resolved absolute path to the asset

        Raises:
            AssetNotFoundError: If asset cannot be found
            AssetResolutionError: If path resolution fails
        """
        if not asset_path:
            raise AssetResolutionError(asset_path, "Empty asset path")

        asset_path = asset_path.strip()
        searched_paths = []

        # Strategy 1: Absolute path
        if os.path.isabs(asset_path):
            abs_path = Path(asset_path)
            searched_paths.append(str(abs_path))
            if abs_path.exists() and abs_path.is_file():
                return abs_path.resolve()

        # Strategy 2: Relative to context file
        if context_path:
            context_dir = (
                Path(context_path).parent
                if Path(context_path).is_file()
                else Path(context_path)
            )
            relative_path = context_dir / asset_path
            searched_paths.append(str(relative_path))
            if relative_path.exists() and relative_path.is_file():
                return relative_path.resolve()

        # Strategy 3: Relative to base paths
        for base_path in self.base_paths:
            base_asset_path = base_path / asset_path
            searched_paths.append(str(base_asset_path))
            if base_asset_path.exists() and base_asset_path.is_file():
                return base_asset_path.resolve()

        # Strategy 4: Search in common asset directories
        search_dirs = []

        # Add context-relative common directories
        if context_path:
            context_dir = (
                Path(context_path).parent
                if Path(context_path).is_file()
                else Path(context_path)
            )
            for common_dir in self.common_asset_dirs:
                search_dirs.append(context_dir / common_dir)

        # Add base path common directories
        for base_path in self.base_paths:
            for common_dir in self.common_asset_dirs:
                search_dirs.append(base_path / common_dir)

        # Search in common asset directories
        for search_dir in search_dirs:
            if search_dir.exists() and search_dir.is_dir():
                # Direct path in asset directory
                direct_path = search_dir / asset_path
                searched_paths.append(str(direct_path))
                if direct_path.exists() and direct_path.is_file():
                    return direct_path.resolve()

                # Search recursively for the filename
                filename = Path(asset_path).name
                for found_file in search_dir.rglob(filename):
                    searched_paths.append(str(found_file))
                    if found_file.is_file():
                        return found_file.resolve()

        # Strategy 5: Current working directory
        cwd_path = Path.cwd() / asset_path
        searched_paths.append(str(cwd_path))
        if cwd_path.exists() and cwd_path.is_file():
            return cwd_path.resolve()

        # Asset not found
        raise AssetNotFoundError(asset_path, searched_paths)

    def validate_asset_path(self, asset_path: Union[str, Path]) -> bool:
        """Validate that an asset path exists and is readable.

        Args:
            asset_path: Path to validate

        Returns:
            True if path is valid and readable
        """
        try:
            path = Path(asset_path)
            return path.exists() and path.is_file() and os.access(path, os.R_OK)
        except (OSError, PermissionError):
            return False

    def get_asset_type(self, asset_path: Union[str, Path]) -> str:
        """Determine asset type from file extension.

        Args:
            asset_path: Path to the asset

        Returns:
            Asset type string (image, font, css, etc.)
        """
        path = Path(asset_path)
        extension = path.suffix.lower()

        # Image types
        if extension in [
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".bmp",
            ".tiff",
            ".webp",
            ".svg",
        ]:
            return "image"

        # Font types
        if extension in [".ttf", ".otf", ".woff", ".woff2", ".eot"]:
            return "font"

        # Stylesheet types
        if extension in [".css", ".scss", ".sass", ".less"]:
            return "stylesheet"

        # Template types
        if extension in [".html", ".htm", ".jinja2", ".j2"]:
            return "template"

        # Default
        return "unknown"

    def add_base_path(self, base_path: Union[str, Path]) -> None:
        """Add a base path for asset resolution.

        Args:
            base_path: Directory to add to base paths
        """
        path = Path(base_path)
        if path not in self.base_paths:
            self.base_paths.append(path)

    def remove_base_path(self, base_path: Union[str, Path]) -> None:
        """Remove a base path from asset resolution.

        Args:
            base_path: Directory to remove from base paths
        """
        path = Path(base_path)
        if path in self.base_paths:
            self.base_paths.remove(path)

    def clear_base_paths(self) -> None:
        """Clear all base paths."""
        self.base_paths.clear()

    def scan_assets_in_directory(
        self,
        directory: Union[str, Path],
        recursive: bool = True,
        asset_types: Optional[List[str]] = None,
    ) -> List[Path]:
        """Scan a directory for assets.

        Args:
            directory: Directory to scan
            recursive: Whether to scan recursively
            asset_types: List of asset types to include (None for all)

        Returns:
            List of found asset paths
        """
        directory = Path(directory)
        if not directory.exists() or not directory.is_dir():
            return []

        assets = []

        if recursive:
            pattern = "**/*"
        else:
            pattern = "*"

        for item in directory.glob(pattern):
            if item.is_file():
                asset_type = self.get_asset_type(item)
                if asset_types is None or asset_type in asset_types:
                    assets.append(item)

        return assets
