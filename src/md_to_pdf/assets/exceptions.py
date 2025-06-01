"""
Asset management exceptions.

This module defines custom exception classes for asset-related errors,
providing clear error messaging and categorization.
"""

from typing import List, Optional


class AssetError(Exception):
    """Base exception for asset-related errors."""

    def __init__(self, message: str, asset_path: Optional[str] = None):
        """Initialize asset error.

        Args:
            message: Error message
            asset_path: Path to the asset that caused the error
        """
        super().__init__(message)
        self.message = message
        self.asset_path = asset_path

    def __str__(self) -> str:
        """String representation of the error."""
        if self.asset_path:
            return f"{self.message} (asset: {self.asset_path})"
        return self.message


class AssetNotFoundError(AssetError):
    """Raised when an asset cannot be found."""

    def __init__(self, asset_path: str, searched_paths: Optional[List[str]] = None):
        """Initialize asset not found error.

        Args:
            asset_path: Original asset path that was searched for
            searched_paths: List of paths that were searched
        """
        message = f"Asset not found: {asset_path}"
        if searched_paths:
            message += f"\nSearched in: {', '.join(searched_paths)}"
        super().__init__(message, asset_path)
        self.searched_paths = searched_paths or []


class AssetResolutionError(AssetError):
    """Raised when asset path resolution fails."""

    def __init__(self, asset_path: str, reason: str):
        """Initialize asset resolution error.

        Args:
            asset_path: Asset path that failed to resolve
            reason: Reason for resolution failure
        """
        message = f"Failed to resolve asset path: {reason}"
        super().__init__(message, asset_path)
        self.reason = reason


class AssetCopyError(AssetError):
    """Raised when asset copying fails."""

    def __init__(self, source_path: str, dest_path: str, reason: str):
        """Initialize asset copy error.

        Args:
            source_path: Source asset path
            dest_path: Destination path
            reason: Reason for copy failure
        """
        message = f"Failed to copy asset from {source_path} to {dest_path}: {reason}"
        super().__init__(message, source_path)
        self.source_path = source_path
        self.dest_path = dest_path
        self.reason = reason


class AssetValidationError(AssetError):
    """Raised when asset validation fails."""

    def __init__(self, asset_path: str, validation_error: str):
        """Initialize asset validation error.

        Args:
            asset_path: Path to the invalid asset
            validation_error: Description of validation failure
        """
        message = f"Asset validation failed: {validation_error}"
        super().__init__(message, asset_path)
        self.validation_error = validation_error
