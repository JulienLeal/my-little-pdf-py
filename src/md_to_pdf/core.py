"""Core functionality for Markdown to PDF conversion."""

import warnings
from pathlib import Path
from typing import List, Optional, Union

import markdown
from markdown.extensions import Extension

from .base_css import BaseCSSGenerator
from .templating import TemplateManager

# Import theme configuration and CSS generation
try:
    from .config import ThemeConfig, load_theme_config
    from .css_generator import CSSGenerator

    THEME_CONFIG_AVAILABLE = True
except ImportError:
    THEME_CONFIG_AVAILABLE = False

# WeasyPrint import with fallback for systems without GTK dependencies
try:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        import weasyprint
    WEASYPRINT_AVAILABLE = True
except ImportError as e:
    WEASYPRINT_AVAILABLE = False
    WEASYPRINT_ERROR = str(e)
except Exception as e:
    # Catch other errors like missing system libraries
    WEASYPRINT_AVAILABLE = False
    WEASYPRINT_ERROR = str(e)


class MarkdownProcessingError(Exception):
    """Raised when Markdown processing fails."""

    pass


class PDFGenerationError(Exception):
    """Raised when PDF generation fails."""

    pass


class ConverterNotAvailableError(Exception):
    """Raised when required dependencies are not available."""

    pass


class MarkdownProcessor:
    """Handles Markdown parsing and conversion to HTML."""

    def __init__(self, extensions: Optional[List[Union[str, Extension]]] = None):
        """Initialize the Markdown processor.

        Args:
            extensions: List of Markdown extensions to use (strings or extension objects)
        """
        self.extensions = extensions or []
        self.md_parser = markdown.Markdown(extensions=self.extensions)

    def convert(self, markdown_content: str) -> str:
        """Convert Markdown content to HTML.

        Args:
            markdown_content: The Markdown content to convert

        Returns:
            HTML string

        Raises:
            MarkdownProcessingError: If Markdown processing fails
        """
        if not markdown_content.strip():
            raise MarkdownProcessingError("Markdown content is empty")

        try:
            return self.md_parser.convert(markdown_content)
        except Exception as e:
            raise MarkdownProcessingError(f"Failed to process Markdown: {e}")

    def convert_file(self, input_path: Path) -> str:
        """Convert a Markdown file to HTML.

        Args:
            input_path: Path to the Markdown file

        Returns:
            HTML string

        Raises:
            FileNotFoundError: If the input file doesn't exist
            MarkdownProcessingError: If Markdown processing fails
        """
        if not input_path.exists():
            raise FileNotFoundError(f"Markdown file not found: {input_path}")

        if not input_path.is_file():
            raise FileNotFoundError(f"Path is not a file: {input_path}")

        if input_path.suffix.lower() not in [".md", ".markdown"]:
            raise MarkdownProcessingError(
                f"File does not appear to be a Markdown file: {input_path}"
            )

        try:
            with open(input_path, "r", encoding="utf-8") as f:
                markdown_content = f.read()
        except Exception as e:
            raise MarkdownProcessingError(f"Failed to read Markdown file: {e}")

        return self.convert(markdown_content)


class PDFGenerator:
    """Handles PDF generation from HTML content."""

    def __init__(
        self,
        base_css: Optional[str] = None,
        include_component_css: bool = True,
        theme_config: Optional["ThemeConfig"] = None,
    ):
        """Initialize PDF generator.

        Args:
            base_css: Custom base CSS (if None, uses comprehensive default)
            include_component_css: Whether to include component CSS
            theme_config: Theme configuration for enhanced styling
        """
        if base_css is None:
            # Use comprehensive base CSS system
            css_generator = BaseCSSGenerator()
            if theme_config and hasattr(theme_config, "styles"):
                self.base_css = css_generator.generate_theme_aware_css(
                    theme_config.styles
                )
            else:
                self.base_css = css_generator.generate_base_css()
        else:
            self.base_css = base_css

        self.include_component_css = include_component_css
        self.theme_config = theme_config
        self._weasyprint_checked = False

    def _get_default_css(self) -> str:
        """Get default CSS for PDF generation (deprecated - using BaseCSSGenerator now)."""
        # This method is kept for backwards compatibility but is no longer used
        # New comprehensive CSS is generated in __init__
        return """
        body {
            font-family: Arial, sans-serif;
            margin: 2cm;
            line-height: 1.6;
            color: #333;
        }
        
        h1, h2, h3, h4, h5, h6 {
            color: #2c3e50;
            margin-top: 20px;
            margin-bottom: 10px;
        }
        
        h1 { font-size: 2.5em; }
        h2 { font-size: 2em; }
        h3 { font-size: 1.5em; }
        
        p {
            margin-bottom: 12px;
        }
        
        ul, ol {
            padding-left: 30px;
            margin-bottom: 12px;
        }
        
        li {
            margin-bottom: 6px;
        }
        
        code {
            background-color: #f8f9fa;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: "Courier New", monospace;
        }
        
        pre {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            margin-bottom: 20px;
        }
        
        blockquote {
            border-left: 4px solid #3498db;
            padding-left: 20px;
            margin-left: 0;
            font-style: italic;
            color: #7f8c8d;
        }
        
        table {
            border-collapse: collapse;
            width: 100%;
            margin-bottom: 20px;
        }
        
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        
        th {
            background-color: #f8f9fa;
            font-weight: bold;
        }
        
        @page {
            margin: 2cm;
        }
        """

    def _get_component_css(self) -> str:
        """Get CSS for custom components."""
        # Try to read the component CSS file
        try:
            css_file = (
                Path(__file__).parent.parent.parent
                / "assets"
                / "css"
                / "components.css"
            )
            if css_file.exists():
                return css_file.read_text(encoding="utf-8")
        except Exception:
            pass

        # Return empty string if file not found or error reading
        return ""

    def _create_html_document(
        self, html_content: str, title: str = "Generated PDF"
    ) -> str:
        """Create a complete HTML document with CSS.

        Args:
            html_content: The HTML content for the body
            title: Document title

        Returns:
            Complete HTML document string
        """
        # Start with base CSS
        all_css = self.base_css

        # Add theme-generated CSS if theme configuration is available
        if self.theme_config and THEME_CONFIG_AVAILABLE:
            css_generator = CSSGenerator(self.theme_config)
            theme_css = css_generator.generate_css()

            # Load external stylesheets from theme
            external_css = css_generator.load_external_stylesheets()

            # Combine CSS in proper order: base -> theme -> external -> components
            all_css = f"{self.base_css}\n\n/* Theme CSS */\n{theme_css}"

            if external_css:
                all_css += f"\n\n/* External Stylesheets */\n{external_css}"

        # Add component CSS last to ensure it can override theme styles
        if self.include_component_css:
            component_css = self._get_component_css()
            if component_css:
                all_css += "\n\n/* Custom Components CSS */\n" + component_css

        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <style>
        {all_css}
    </style>
</head>
<body>
    {html_content}
</body>
</html>"""

    def _check_weasyprint(self):
        """Check if WeasyPrint is available and raise error if not."""
        if not self._weasyprint_checked:
            if not WEASYPRINT_AVAILABLE:
                raise ConverterNotAvailableError(
                    f"WeasyPrint is required but not available: {WEASYPRINT_ERROR}\n"
                    f"Please install WeasyPrint and its dependencies. "
                    f"On Windows, you may need to install MSYS2 first."
                )
            self._weasyprint_checked = True

    def generate_pdf(
        self, html_content: str, output_path: Path, title: str = "Generated PDF"
    ) -> None:
        """Generate PDF from HTML content.

        Args:
            html_content: HTML content to convert
            output_path: Path where PDF should be saved
            title: Document title

        Raises:
            PDFGenerationError: If PDF generation fails
            ConverterNotAvailableError: If WeasyPrint is not available
        """
        if not html_content.strip():
            raise PDFGenerationError("HTML content is empty")

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        full_html = self._create_html_document(html_content, title)

        try:
            self._check_weasyprint()
            weasyprint.HTML(string=full_html).write_pdf(str(output_path))
        except ConverterNotAvailableError:
            # Re-raise converter availability errors
            raise
        except Exception as e:
            raise PDFGenerationError(f"Failed to generate PDF: {e}")

    def generate_pdf_bytes(
        self, html_content: str, title: str = "Generated PDF"
    ) -> bytes:
        """Generate PDF from HTML content and return as bytes.

        Args:
            html_content: HTML content to convert
            title: Document title

        Returns:
            PDF content as bytes

        Raises:
            PDFGenerationError: If PDF generation fails
            ConverterNotAvailableError: If WeasyPrint is not available
        """
        if not html_content.strip():
            raise PDFGenerationError("HTML content is empty")

        full_html = self._create_html_document(html_content, title)

        try:
            self._check_weasyprint()
            pdf_bytes = weasyprint.HTML(string=full_html).write_pdf()
            if pdf_bytes is None:
                raise PDFGenerationError(
                    "WeasyPrint returned None instead of PDF bytes"
                )
            return pdf_bytes
        except ConverterNotAvailableError:
            # Re-raise converter availability errors
            raise
        except Exception as e:
            raise PDFGenerationError(f"Failed to generate PDF: {e}")


class MarkdownToPDFConverter:
    """Main converter class that combines Markdown processing and PDF generation."""

    def __init__(
        self,
        theme_config_path: Optional[Path] = None,
        extensions: Optional[List[Union[str, Extension]]] = None,
        base_css: Optional[str] = None,
        template_manager: Optional[TemplateManager] = None,
        template_dirs: Optional[List[str]] = None,
    ):
        """Initialize the converter.

        Args:
            theme_config_path: Path to theme configuration file
            extensions: Markdown extensions to use (strings or extension objects)
            base_css: Base CSS for PDF styling
            template_manager: Template manager for custom components
            template_dirs: Directories to search for templates (if template_manager not provided)
        """
        self.theme_config_path = theme_config_path
        self.theme_config = None

        # Load theme configuration if provided
        if theme_config_path and THEME_CONFIG_AVAILABLE:
            try:
                self.theme_config = load_theme_config(
                    theme_config_path,
                    validate_files=False,  # Don't validate file existence for now
                    validate_schema=True,
                )
                print(f"✅ Theme configuration loaded: {theme_config_path}")
            except Exception as e:
                print(f"⚠️ Failed to load theme configuration: {e}")
                print("   Continuing with default styling...")

        # Initialize template manager if not provided
        if template_manager is None and template_dirs is not None:
            template_manager = TemplateManager(template_dirs)
        elif template_manager is None:
            # Use default template manager
            template_manager = TemplateManager()

        self.template_manager = template_manager

        # Setup extensions with template manager integration
        processed_extensions = self._setup_extensions(extensions, template_manager)

        self.markdown_processor = MarkdownProcessor(extensions=processed_extensions)
        self.pdf_generator = PDFGenerator(
            base_css=base_css, theme_config=self.theme_config
        )

    def _setup_extensions(
        self,
        extensions: Optional[List[Union[str, Extension]]],
        template_manager: TemplateManager,
    ) -> List[Union[str, Extension]]:
        """Setup extensions with template manager integration."""
        if extensions is None:
            extensions = []

        # Convert to list if not already
        processed_extensions = list(extensions)

        # Check if custom_blocks extension is already included
        has_custom_blocks = any(
            (isinstance(ext, str) and "custom_blocks" in ext)
            or (hasattr(ext, "__class__") and "CustomBlock" in ext.__class__.__name__)
            for ext in processed_extensions
        )

        if not has_custom_blocks:
            # Import and add the custom blocks extension with template manager
            from .extensions.custom_blocks import CustomBlockExtension

            custom_blocks_ext = CustomBlockExtension(template_manager=template_manager)
            processed_extensions.append(custom_blocks_ext)

        return processed_extensions

    def convert_file(self, input_path: Path, output_path: Path) -> None:
        """Convert a Markdown file to PDF.

        Args:
            input_path: Path to input Markdown file
            output_path: Path where PDF should be saved

        Raises:
            FileNotFoundError: If input file doesn't exist
            MarkdownProcessingError: If Markdown processing fails
            PDFGenerationError: If PDF generation fails
            ConverterNotAvailableError: If required dependencies are not available
        """
        try:
            # Convert Markdown to HTML
            html_content = self.markdown_processor.convert_file(input_path)

            # Generate title from filename
            title = input_path.stem.replace("_", " ").replace("-", " ").title()

            # Generate PDF
            self.pdf_generator.generate_pdf(html_content, output_path, title)

            print(f"✅ PDF generated: {output_path}")

        except (
            FileNotFoundError,
            MarkdownProcessingError,
            PDFGenerationError,
            ConverterNotAvailableError,
        ):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Catch any unexpected errors
            raise PDFGenerationError(f"Unexpected error during conversion: {e}")

    def convert_string(
        self, markdown_content: str, output_path: Path, title: str = "Generated PDF"
    ) -> None:
        """Convert Markdown string to PDF.

        Args:
            markdown_content: Markdown content as string
            output_path: Path where PDF should be saved
            title: Document title

        Raises:
            MarkdownProcessingError: If Markdown processing fails
            PDFGenerationError: If PDF generation fails
            ConverterNotAvailableError: If required dependencies are not available
        """
        try:
            # Convert Markdown to HTML
            html_content = self.markdown_processor.convert(markdown_content)

            # Generate PDF
            self.pdf_generator.generate_pdf(html_content, output_path, title)

            print(f"✅ PDF generated: {output_path}")

        except (
            MarkdownProcessingError,
            PDFGenerationError,
            ConverterNotAvailableError,
        ):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Catch any unexpected errors
            raise PDFGenerationError(f"Unexpected error during conversion: {e}")

    def is_available(self) -> bool:
        """Check if the converter is available (all dependencies working).

        Returns:
            True if converter can be used, False otherwise
        """
        return WEASYPRINT_AVAILABLE
