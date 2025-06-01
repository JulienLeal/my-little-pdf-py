"""
Asset management core functionality.

This module provides the main AssetManager class that coordinates all asset
handling operations including resolution, copying, and caching.
"""

import shutil
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union

from .exceptions import AssetCopyError
from .resolvers import AssetResolver


@dataclass
class AssetInfo:
    """Information about a resolved asset."""

    original_path: str
    resolved_path: Path
    asset_type: str
    size: int
    last_modified: datetime
    context_path: Optional[Path] = None

    @property
    def exists(self) -> bool:
        """Check if the resolved asset still exists."""
        return self.resolved_path.exists()

    @property
    def is_valid(self) -> bool:
        """Check if asset is valid (exists and readable)."""
        try:
            return (
                self.resolved_path.exists()
                and self.resolved_path.is_file()
                and self.resolved_path.stat().st_size > 0
            )
        except (OSError, PermissionError):
            return False

    def refresh_info(self) -> None:
        """Refresh asset information from file system."""
        if self.resolved_path.exists():
            stat = self.resolved_path.stat()
            self.size = stat.st_size
            self.last_modified = datetime.fromtimestamp(stat.st_mtime)


class AssetManager:
    """Central asset management system."""

    def __init__(self, base_paths: Optional[List[Union[str, Path]]] = None):
        """Initialize asset manager.

        Args:
            base_paths: List of base directories to search for assets
        """
        self.resolver = AssetResolver(base_paths)
        self.asset_cache: Dict[str, AssetInfo] = {}
        self._temp_dirs: List[Path] = []

    def resolve_asset(
        self,
        asset_path: str,
        context_path: Optional[Union[str, Path]] = None,
        use_cache: bool = True,
    ) -> AssetInfo:
        """Resolve an asset and return detailed information.

        Args:
            asset_path: Original asset path from source
            context_path: Path to the file referencing this asset
            use_cache: Whether to use cached resolution results

        Returns:
            AssetInfo object with resolved asset details

        Raises:
            AssetError: If asset resolution fails
        """
        # Create cache key
        cache_key = f"{asset_path}:{context_path}" if context_path else asset_path

        # Check cache if enabled
        if use_cache and cache_key in self.asset_cache:
            cached_asset = self.asset_cache[cache_key]
            # Verify cached asset is still valid
            if cached_asset.is_valid:
                return cached_asset
            else:
                # Remove invalid cached entry
                del self.asset_cache[cache_key]

        # Resolve asset path
        resolved_path = self.resolver.resolve_asset_path(asset_path, context_path)

        # Get asset information
        asset_type = self.resolver.get_asset_type(resolved_path)
        stat = resolved_path.stat()

        asset_info = AssetInfo(
            original_path=asset_path,
            resolved_path=resolved_path,
            asset_type=asset_type,
            size=stat.st_size,
            last_modified=datetime.fromtimestamp(stat.st_mtime),
            context_path=Path(context_path) if context_path else None,
        )

        # Cache the result
        if use_cache:
            self.asset_cache[cache_key] = asset_info

        return asset_info

    def copy_assets_to_temp(
        self,
        asset_paths: List[str],
        context_path: Optional[Union[str, Path]] = None,
        temp_dir: Optional[Path] = None,
    ) -> Dict[str, str]:
        """Copy assets to a temporary directory for PDF generation.

        Args:
            asset_paths: List of asset paths to copy
            context_path: Context path for asset resolution
            temp_dir: Temporary directory to use (creates one if None)

        Returns:
            Dictionary mapping original paths to temporary paths

        Raises:
            AssetCopyError: If asset copying fails
        """
        if temp_dir is None:
            temp_dir = Path(tempfile.mkdtemp(prefix="md_to_pdf_assets_"))
            self._temp_dirs.append(temp_dir)

        asset_map = {}

        for asset_path in asset_paths:
            try:
                # Resolve the asset
                asset_info = self.resolve_asset(asset_path, context_path)

                # Create destination path (preserve relative structure)
                if Path(asset_path).is_absolute():
                    # For absolute paths, use just the filename
                    dest_name = asset_info.resolved_path.name
                else:
                    # For relative paths, preserve the path structure
                    dest_name = asset_path.replace("\\", "/").replace("/", "_")
                    # Ensure we keep the original extension
                    if not dest_name.endswith(asset_info.resolved_path.suffix):
                        dest_name += asset_info.resolved_path.suffix

                dest_path = temp_dir / dest_name

                # Ensure destination directory exists
                dest_path.parent.mkdir(parents=True, exist_ok=True)

                # Copy the file
                shutil.copy2(asset_info.resolved_path, dest_path)

                # Map original path to temp path
                asset_map[asset_path] = str(dest_path)

            except Exception as e:
                raise AssetCopyError(
                    asset_path, str(temp_dir / asset_path), str(e)
                ) from e

        return asset_map

    def cleanup_temp_assets(self, temp_dir: Optional[Path] = None) -> None:
        """Clean up temporary asset directories.

        Args:
            temp_dir: Specific temp directory to clean (cleans all if None)
        """
        if temp_dir:
            # Clean specific directory
            if temp_dir.exists():
                try:
                    shutil.rmtree(temp_dir)
                except Exception:
                    pass  # Ignore cleanup errors
            # Remove from tracked directories
            if temp_dir in self._temp_dirs:
                self._temp_dirs.remove(temp_dir)
        else:
            # Clean all tracked temp directories
            for temp_dir in self._temp_dirs[
                :
            ]:  # Copy list to avoid modification during iteration
                if temp_dir.exists():
                    try:
                        shutil.rmtree(temp_dir)
                    except Exception:
                        pass  # Ignore cleanup errors
                self._temp_dirs.remove(temp_dir)

    def get_asset_dependencies(
        self, html_content: str, context_path: Optional[Union[str, Path]] = None
    ) -> List[str]:
        """Extract asset dependencies from HTML content.

        Args:
            html_content: HTML content to scan for assets
            context_path: Context path for relative asset resolution

        Returns:
            List of asset paths found in the HTML
        """
        import re

        asset_paths = []

        # Find image sources
        img_pattern = r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>'
        for match in re.finditer(img_pattern, html_content, re.IGNORECASE):
            src = match.group(1)
            if not src.startswith(("http://", "https://", "data:")):
                asset_paths.append(src)

        # Find CSS links
        css_pattern = r'<link[^>]+href=["\']([^"\']+\.css)["\'][^>]*>'
        for match in re.finditer(css_pattern, html_content, re.IGNORECASE):
            href = match.group(1)
            if not href.startswith(("http://", "https://")):
                asset_paths.append(href)

        # Find other asset references (e.g., fonts in CSS)
        # This is a basic implementation - could be enhanced

        return list(set(asset_paths))  # Remove duplicates

    def update_html_asset_refs(
        self, html_content: str, asset_map: Dict[str, str]
    ) -> str:
        """Update asset references in HTML content with new paths.

        Args:
            html_content: Original HTML content
            asset_map: Mapping of original paths to new paths

        Returns:
            Updated HTML content with new asset paths
        """
        updated_html = html_content

        for original_path, new_path in asset_map.items():
            # Convert to file URI for HTML
            file_uri = Path(new_path).as_uri()

            # Replace in img src attributes
            updated_html = updated_html.replace(
                f'src="{original_path}"', f'src="{file_uri}"'
            )
            updated_html = updated_html.replace(
                f"src='{original_path}'", f"src='{file_uri}'"
            )

            # Replace in link href attributes
            updated_html = updated_html.replace(
                f'href="{original_path}"', f'href="{file_uri}"'
            )
            updated_html = updated_html.replace(
                f"href='{original_path}'", f"href='{file_uri}'"
            )

        return updated_html

    def add_base_path(self, base_path: Union[str, Path]) -> None:
        """Add a base path for asset resolution.

        Args:
            base_path: Directory to add to base paths
        """
        self.resolver.add_base_path(base_path)

    def clear_cache(self) -> None:
        """Clear the asset cache."""
        self.asset_cache.clear()

    def get_cache_stats(self) -> Dict[str, int]:
        """Get asset cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        valid_assets = sum(1 for asset in self.asset_cache.values() if asset.is_valid)
        invalid_assets = len(self.asset_cache) - valid_assets

        return {
            "total_cached": len(self.asset_cache),
            "valid_assets": valid_assets,
            "invalid_assets": invalid_assets,
            "temp_directories": len(self._temp_dirs),
        }

    def __del__(self):
        """Cleanup when manager is destroyed."""
        self.cleanup_temp_assets()
