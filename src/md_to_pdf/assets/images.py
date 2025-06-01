"""
Image asset handling and processing.

This module provides specialized functionality for handling image assets
including format detection, validation, and HTML reference updating.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from .exceptions import AssetValidationError
from .resolvers import AssetResolver


class ImageInfo:
    """Information about an image asset."""

    def __init__(self, path: Path):
        """Initialize image info.

        Args:
            path: Path to the image file
        """
        self.path = path
        self.format = self._detect_format()
        self.size_bytes = path.stat().st_size if path.exists() else 0
        self.dimensions = None  # Could be enhanced with PIL/Pillow

    def _detect_format(self) -> str:
        """Detect image format from file extension."""
        extension = self.path.suffix.lower()

        format_map = {
            ".png": "PNG",
            ".jpg": "JPEG",
            ".jpeg": "JPEG",
            ".gif": "GIF",
            ".bmp": "BMP",
            ".tiff": "TIFF",
            ".tif": "TIFF",
            ".webp": "WebP",
            ".svg": "SVG",
            ".ico": "ICO",
        }

        return format_map.get(extension, "Unknown")

    @property
    def is_vector(self) -> bool:
        """Check if image is vector format."""
        return self.format in ["SVG"]

    @property
    def is_raster(self) -> bool:
        """Check if image is raster format."""
        return self.format in ["PNG", "JPEG", "GIF", "BMP", "TIFF", "WebP", "ICO"]

    @property
    def is_web_compatible(self) -> bool:
        """Check if image format is web-compatible."""
        return self.format in ["PNG", "JPEG", "GIF", "SVG", "WebP"]


class ImageResolver:
    """Specialized image asset resolution and processing."""

    def __init__(self, asset_resolver: Optional[AssetResolver] = None):
        """Initialize image resolver.

        Args:
            asset_resolver: Base asset resolver to use
        """
        self.asset_resolver = asset_resolver or AssetResolver()
        self.supported_formats = {
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".bmp",
            ".tiff",
            ".tif",
            ".webp",
            ".svg",
            ".ico",
        }

    def resolve_image_path(
        self, image_path: str, context_path: Optional[Union[str, Path]] = None
    ) -> ImageInfo:
        """Resolve an image path and return image information.

        Args:
            image_path: Original image path from source
            context_path: Path to the file referencing this image

        Returns:
            ImageInfo object with resolved image details

        Raises:
            AssetValidationError: If image is not valid
        """
        # Resolve the basic path using the asset resolver
        resolved_path = self.asset_resolver.resolve_asset_path(
            image_path, context_path, asset_type="image"
        )

        # Validate it's actually an image
        if not self._is_image_file(resolved_path):
            raise AssetValidationError(
                str(resolved_path),
                f"File is not a supported image format. Extension: {resolved_path.suffix}",
            )

        return ImageInfo(resolved_path)

    def _is_image_file(self, file_path: Path) -> bool:
        """Check if file is a supported image format.

        Args:
            file_path: Path to check

        Returns:
            True if file is a supported image format
        """
        return file_path.suffix.lower() in self.supported_formats

    def extract_images_from_html(self, html_content: str) -> List[str]:
        """Extract image paths from HTML content.

        Args:
            html_content: HTML content to scan

        Returns:
            List of image paths found in the HTML
        """
        image_paths = []

        # Pattern to match img tags and extract src attribute
        img_pattern = r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>'

        for match in re.finditer(img_pattern, html_content, re.IGNORECASE):
            src = match.group(1).strip()

            # Skip data URLs and external URLs
            if not src.startswith(("http://", "https://", "data:", "//")):
                image_paths.append(src)

        return list(set(image_paths))  # Remove duplicates

    def extract_images_from_markdown(self, markdown_content: str) -> List[str]:
        """Extract image paths from Markdown content.

        Args:
            markdown_content: Markdown content to scan

        Returns:
            List of image paths found in the Markdown
        """
        image_paths = []

        # Pattern to match Markdown image syntax: ![alt](path)
        md_img_pattern = r"!\[[^\]]*\]\(([^)]+)\)"

        for match in re.finditer(md_img_pattern, markdown_content):
            src = match.group(1).strip()

            # Skip URLs and data URLs
            if not src.startswith(("http://", "https://", "data:", "//")):
                # Remove any title text after space
                src = src.split(" ")[0]
                image_paths.append(src)

        # Also check for reference-style images: ![alt][ref]
        # This would require tracking reference definitions, simplified for now

        return list(set(image_paths))  # Remove duplicates

    def update_html_image_refs(
        self, html_content: str, image_map: Dict[str, str]
    ) -> str:
        """Update image references in HTML content with new paths.

        Args:
            html_content: Original HTML content
            image_map: Mapping of original image paths to new paths

        Returns:
            Updated HTML content with new image paths
        """
        updated_html = html_content

        for original_path, new_path in image_map.items():
            # Convert path to file URI for HTML
            file_uri = Path(new_path).as_uri()

            # Update img src attributes with various quote styles
            patterns = [
                (f'src="{original_path}"', f'src="{file_uri}"'),
                (f"src='{original_path}'", f"src='{file_uri}'"),
                (f"src={original_path}", f'src="{file_uri}"'),  # No quotes
            ]

            for old_pattern, new_pattern in patterns:
                updated_html = updated_html.replace(old_pattern, new_pattern)

        return updated_html

    def validate_image_compatibility(self, image_info: ImageInfo) -> List[str]:
        """Validate image compatibility for PDF generation.

        Args:
            image_info: Image information to validate

        Returns:
            List of warning messages (empty if no issues)
        """
        warnings = []

        # Check format compatibility
        if not image_info.is_web_compatible:
            warnings.append(
                f"Image format '{image_info.format}' may not be fully supported in PDFs"
            )

        # Check file size
        if image_info.size_bytes > 10 * 1024 * 1024:  # 10MB
            warnings.append(
                f"Large image file ({image_info.size_bytes / 1024 / 1024:.1f}MB) may impact PDF size"
            )

        # Check if file exists and is readable
        if not image_info.path.exists():
            warnings.append("Image file does not exist")
        elif not image_info.path.is_file():
            warnings.append("Image path is not a file")

        return warnings

    def get_image_dimensions(self, image_path: Path) -> Optional[Tuple[int, int]]:
        """Get image dimensions if possible.

        Args:
            image_path: Path to the image file

        Returns:
            Tuple of (width, height) or None if not available

        Note:
            This is a placeholder. Full implementation would use PIL/Pillow
            or similar library to read image metadata.
        """
        # Placeholder implementation
        # In a full implementation, you would use PIL:
        # from PIL import Image
        # with Image.open(image_path) as img:
        #     return img.size
        return None

    def optimize_image_for_pdf(self, image_path: Path, output_path: Path) -> Path:
        """Optimize image for PDF embedding.

        Args:
            image_path: Source image path
            output_path: Output path for optimized image

        Returns:
            Path to optimized image

        Note:
            This is a placeholder. Full implementation would use PIL/Pillow
            for actual image optimization (resize, compress, etc.)
        """
        # Placeholder implementation - just copy the file
        import shutil

        shutil.copy2(image_path, output_path)
        return output_path

    def scan_for_images(
        self, directory: Union[str, Path], recursive: bool = True
    ) -> List[Path]:
        """Scan directory for image files.

        Args:
            directory: Directory to scan
            recursive: Whether to scan recursively

        Returns:
            List of found image file paths
        """
        directory = Path(directory)
        if not directory.exists() or not directory.is_dir():
            return []

        images = []
        pattern = "**/*" if recursive else "*"

        for file_path in directory.glob(pattern):
            if file_path.is_file() and self._is_image_file(file_path):
                images.append(file_path)

        return images
