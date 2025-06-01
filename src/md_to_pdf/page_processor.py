"""
Advanced page processing for PDF generation.

This module handles dynamic content in headers/footers, variable substitution,
and document metadata extraction for professional PDF output.
"""

import re
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

try:
    from bs4 import BeautifulSoup

    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

from .config import ThemeConfig


class Section:
    """Represents a document section for header/footer context."""

    def __init__(self, level: int, title: str, start_page: int = 1):
        """Initialize section information.

        Args:
            level: Heading level (1-6 for H1-H6)
            title: Section title text
            start_page: Page number where section starts
        """
        self.level = level
        self.title = title
        self.start_page = start_page
        self.end_page: Optional[int] = None

    def __repr__(self) -> str:
        return f"Section(H{self.level}: '{self.title}', pages {self.start_page}-{self.end_page})"


class VariableResolver:
    """Resolves variables in header/footer content."""

    def __init__(self):
        """Initialize variable resolver with built-in variables."""
        self._resolvers: Dict[str, Callable[[Dict[str, Any]], str]] = {}
        self._register_builtin_variables()

    def _register_builtin_variables(self):
        """Register built-in variable resolvers."""

        def page_number_resolver(context: Dict[str, Any]) -> str:
            return str(context.get("page_number", 1))

        def total_pages_resolver(context: Dict[str, Any]) -> str:
            return str(context.get("total_pages", 1))

        def section_title_resolver(context: Dict[str, Any]) -> str:
            return str(context.get("section_title", ""))

        def document_title_resolver(context: Dict[str, Any]) -> str:
            return str(context.get("document_title", ""))

        def date_resolver(context: Dict[str, Any]) -> str:
            date_format = context.get("date_format", "%B %Y")
            return datetime.now().strftime(date_format)

        def year_resolver(context: Dict[str, Any]) -> str:
            return str(datetime.now().year)

        # Register built-in variables
        self._resolvers["page_number"] = page_number_resolver
        self._resolvers["total_pages"] = total_pages_resolver
        self._resolvers["section_title"] = section_title_resolver
        self._resolvers["document_title"] = document_title_resolver
        self._resolvers["date"] = date_resolver
        self._resolvers["year"] = year_resolver

    def register_variable(
        self, name: str, resolver_func: Callable[[Dict[str, Any]], str]
    ):
        """Register custom variable resolver.

        Args:
            name: Variable name (without braces)
            resolver_func: Function that takes context dict and returns string value
        """
        self._resolvers[name] = resolver_func

    def resolve_variables(self, template: str, context: Dict[str, Any]) -> str:
        """Replace variables in template with actual values.

        Args:
            template: Template string with {variable} placeholders
            context: Context dictionary with variable values

        Returns:
            Template with variables replaced by actual values
        """
        if not template:
            return template

        # Find all variable patterns like {variable_name}
        variable_pattern = r"\{([^}]+)\}"

        def replace_variable(match):
            var_name = match.group(1).strip()

            # Check if we have a resolver for this variable
            if var_name in self._resolvers:
                try:
                    return self._resolvers[var_name](context)
                except Exception as e:
                    # Log warning but don't break the processing
                    print(f"Warning: Failed to resolve variable '{var_name}': {e}")
                    return match.group(0)  # Return original text

            # Check if variable is directly in context
            if var_name in context:
                return str(context[var_name])

            # Check for nested context (e.g., custom_variables.company)
            if "." in var_name:
                parts = var_name.split(".")
                value = context
                try:
                    for part in parts:
                        value = value[part]
                    return str(value)
                except (KeyError, TypeError):
                    pass

            # Variable not found - return original text with warning
            print(f"Warning: Unknown variable '{var_name}' in template")
            return match.group(0)

        return re.sub(variable_pattern, replace_variable, template)


class SectionTracker:
    """Tracks document sections for header/footer context."""

    def __init__(self):
        """Initialize section tracker."""
        self.sections: List[Section] = []
        self._current_page = 1

    def extract_sections(self, html_content: str) -> List[Section]:
        """Extract section information from HTML content.

        Args:
            html_content: HTML content to analyze

        Returns:
            List of Section objects representing document structure
        """
        if not BS4_AVAILABLE:
            # Fallback: simple regex-based extraction
            return self._extract_sections_regex(html_content)

        # Use BeautifulSoup for robust HTML parsing
        soup = BeautifulSoup(html_content, "html.parser")
        sections = []

        # Find all heading elements H1-H6
        headings = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])

        for i, heading in enumerate(headings):
            # Extract heading level (1-6)
            level = int(heading.name[1])

            # Extract heading text, removing any HTML tags
            title = heading.get_text().strip()

            if title:  # Only add non-empty headings
                # Estimate page number (simplified - real implementation would need page break info)
                estimated_page = max(1, i // 3 + 1)  # Rough estimate

                section = Section(level, title, estimated_page)
                sections.append(section)

        # Set end pages for sections
        for i, section in enumerate(sections):
            if i + 1 < len(sections):
                section.end_page = sections[i + 1].start_page - 1
            else:
                section.end_page = None  # Last section goes to end of document

        self.sections = sections
        return sections

    def _extract_sections_regex(self, html_content: str) -> List[Section]:
        """Fallback section extraction using regex (when BeautifulSoup not available).

        Args:
            html_content: HTML content to analyze

        Returns:
            List of Section objects
        """
        sections = []

        # Regex to match heading tags
        heading_pattern = r"<h([1-6])[^>]*>(.*?)</h[1-6]>"

        for i, match in enumerate(
            re.finditer(heading_pattern, html_content, re.IGNORECASE | re.DOTALL)
        ):
            level = int(match.group(1))
            title_html = match.group(2)

            # Remove HTML tags from title
            title = re.sub(r"<[^>]+>", "", title_html).strip()

            if title:
                estimated_page = max(1, i // 3 + 1)
                section = Section(level, title, estimated_page)
                sections.append(section)

        # Set end pages
        for i, section in enumerate(sections):
            if i + 1 < len(sections):
                section.end_page = sections[i + 1].start_page - 1
            else:
                section.end_page = None

        self.sections = sections
        return sections

    def get_section_context(self, page_number: int) -> Dict[str, str]:
        """Get section context for a specific page.

        Args:
            page_number: Page number to get context for

        Returns:
            Dictionary with section context variables
        """
        context = {
            "section_title": "",
            "section_level": 0,
            "chapter_number": 0,
            "chapter_title": "",
        }

        # Find the section that contains this page
        current_section = None
        chapter_count = 0

        for section in self.sections:
            # Count H1 sections as chapters
            if section.level == 1:
                chapter_count += 1

            # Check if this page falls within this section
            if section.start_page <= page_number:
                if section.end_page is None or page_number <= section.end_page:
                    current_section = section
                    if section.level == 1:
                        context["chapter_number"] = chapter_count
                        context["chapter_title"] = section.title

        if current_section:
            context["section_title"] = current_section.title
            context["section_level"] = current_section.level

        return context


class PageProcessor:
    """Handles advanced page processing for PDF generation."""

    def __init__(self, theme_config: ThemeConfig):
        """Initialize page processor.

        Args:
            theme_config: Theme configuration for styling and variables
        """
        self.theme_config = theme_config
        self.variable_resolver = VariableResolver()
        self.section_tracker = SectionTracker()
        self._document_metadata: Dict[str, Any] = {}

    def extract_document_metadata(self, html_content: str) -> Dict[str, Any]:
        """Extract metadata from HTML content.

        Args:
            html_content: HTML content to analyze

        Returns:
            Dictionary with document metadata
        """
        metadata = {
            "title": "",
            "author": "",
            "total_pages": 1,  # Will be updated during PDF generation
        }

        if not BS4_AVAILABLE:
            # Fallback: simple regex-based extraction
            return self._extract_metadata_regex(html_content, metadata)

        # Use BeautifulSoup for robust parsing
        soup = BeautifulSoup(html_content, "html.parser")

        # Extract title from first H1 or title tag
        title_element = soup.find("h1") or soup.find("title")
        if title_element:
            metadata["title"] = title_element.get_text().strip()

        # Extract author from meta tag
        author_meta = soup.find("meta", attrs={"name": "author"})
        if (
            author_meta
            and hasattr(author_meta, "attrs")
            and author_meta.attrs.get("content")
        ):
            metadata["author"] = author_meta.attrs["content"].strip()

        # Extract other meta information
        for meta_name in ["description", "keywords", "subject"]:
            meta_tag = soup.find("meta", attrs={"name": meta_name})
            if (
                meta_tag
                and hasattr(meta_tag, "attrs")
                and meta_tag.attrs.get("content")
            ):
                metadata[meta_name] = meta_tag.attrs["content"].strip()

        self._document_metadata = metadata
        return metadata

    def _extract_metadata_regex(
        self, html_content: str, metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Fallback metadata extraction using regex.

        Args:
            html_content: HTML content to analyze
            metadata: Existing metadata dictionary to update

        Returns:
            Updated metadata dictionary
        """
        # Extract title from first H1
        h1_match = re.search(
            r"<h1[^>]*>(.*?)</h1>", html_content, re.IGNORECASE | re.DOTALL
        )
        if h1_match:
            title = re.sub(r"<[^>]+>", "", h1_match.group(1)).strip()
            if title:
                metadata["title"] = title

        # Extract author from meta tag
        author_match = re.search(
            r'<meta\s+name=["\']author["\']\s+content=["\']([^"\']+)',
            html_content,
            re.IGNORECASE,
        )
        if author_match:
            metadata["author"] = author_match.group(1).strip()

        return metadata

    def process_headers_footers(self, html_content: str) -> str:
        """Process headers/footers with dynamic content.

        Args:
            html_content: Original HTML content

        Returns:
            Enhanced HTML with processed headers/footers
        """
        # Extract document metadata and sections
        self.extract_document_metadata(html_content)
        self.section_tracker.extract_sections(html_content)

        # Build variable context
        context = self._build_variable_context()

        # Process headers and footers in theme configuration
        # This will be used by the CSS generator for @page rules
        # The actual processing happens in the CSS generation phase

        return html_content  # HTML content unchanged, CSS handles headers/footers

    def _build_variable_context(self, page_number: int = 1) -> Dict[str, Any]:
        """Build context dictionary for variable resolution.

        Args:
            page_number: Current page number (for page-specific context)

        Returns:
            Context dictionary with all available variables
        """
        context = {
            "page_number": page_number,
            "total_pages": self._document_metadata.get("total_pages", 1),
            "document_title": self._document_metadata.get("title", ""),
            "author": self._document_metadata.get("author", ""),
            "date_format": "%B %Y",  # Default format
        }

        # Add section context for current page
        section_context = self.section_tracker.get_section_context(page_number)
        context.update(section_context)

        # Add custom variables from theme config if available
        custom_vars = getattr(self.theme_config, "custom_variables", None)
        if custom_vars:
            context["custom_variables"] = custom_vars

        return context

    def generate_paged_media_css(self) -> str:
        """Generate CSS Paged Media rules with variables.

        Returns:
            CSS string with enhanced @page rules for headers/footers
        """
        css_parts = []

        # Process each header/footer configuration
        for name, header_config in self.theme_config.page_headers.items():
            if any([header_config.left, header_config.center, header_config.right]):
                css_parts.append(self._generate_header_css(name, header_config))

        for name, footer_config in self.theme_config.page_footers.items():
            if any([footer_config.left, footer_config.center, footer_config.right]):
                css_parts.append(self._generate_footer_css(name, footer_config))

        return "\n\n".join(filter(None, css_parts))

    def _generate_header_css(self, name: str, header_config) -> str:
        """Generate CSS for a specific header configuration with variables.

        Args:
            name: Header configuration name
            header_config: Header configuration object

        Returns:
            CSS string for header
        """
        # Build sample context for variable processing
        context = self._build_variable_context()

        css_rules = []
        page_selector = f"@page {name}" if name != "default" else "@page"

        # Process header content with variables
        if header_config.left:
            content = self.variable_resolver.resolve_variables(
                header_config.left, context
            )
            css_rules.append(f"""{page_selector} {{
    @top-left {{
        content: "{content}";
        font-family: {", ".join(f'"{f}"' for f in header_config.font_family)};
        font-size: {header_config.font_size};
        color: {header_config.color};
    }}
}}""")

        if header_config.center:
            content = self.variable_resolver.resolve_variables(
                header_config.center, context
            )
            css_rules.append(f"""{page_selector} {{
    @top-center {{
        content: "{content}";
        font-family: {", ".join(f'"{f}"' for f in header_config.font_family)};
        font-size: {header_config.font_size};
        color: {header_config.color};
    }}
}}""")

        if header_config.right:
            content = self.variable_resolver.resolve_variables(
                header_config.right, context
            )
            css_rules.append(f"""{page_selector} {{
    @top-right {{
        content: "{content}";
        font-family: {", ".join(f'"{f}"' for f in header_config.font_family)};
        font-size: {header_config.font_size};
        color: {header_config.color};
    }}
}}""")

        # Add line separator if configured
        if header_config.line_separator:
            css_rules.append(f"""{page_selector} {{
    @top-center {{
        border-bottom: 1px solid {header_config.line_color};
        padding-bottom: 5px;
    }}
}}""")

        return "\n\n".join(css_rules)

    def _generate_footer_css(self, name: str, footer_config) -> str:
        """Generate CSS for a specific footer configuration with variables.

        Args:
            name: Footer configuration name
            footer_config: Footer configuration object

        Returns:
            CSS string for footer
        """
        # Build sample context for variable processing
        context = self._build_variable_context()

        css_rules = []
        page_selector = f"@page {name}" if name != "default" else "@page"

        # Process footer content with variables
        if footer_config.left:
            content = self.variable_resolver.resolve_variables(
                footer_config.left, context
            )
            css_rules.append(f"""{page_selector} {{
    @bottom-left {{
        content: "{content}";
        font-family: {", ".join(f'"{f}"' for f in footer_config.font_family)};
        font-size: {footer_config.font_size};
        color: {footer_config.color};
    }}
}}""")

        if footer_config.center:
            content = self.variable_resolver.resolve_variables(
                footer_config.center, context
            )
            css_rules.append(f"""{page_selector} {{
    @bottom-center {{
        content: "{content}";
        font-family: {", ".join(f'"{f}"' for f in footer_config.font_family)};
        font-size: {footer_config.font_size};
        color: {footer_config.color};
    }}
}}""")

        if footer_config.right:
            content = self.variable_resolver.resolve_variables(
                footer_config.right, context
            )
            css_rules.append(f"""{page_selector} {{
    @bottom-right {{
        content: "{content}";
        font-family: {", ".join(f'"{f}"' for f in footer_config.font_family)};
        font-size: {footer_config.font_size};
        color: {footer_config.color};
    }}
}}""")

        # Add line separator if configured
        if footer_config.line_separator:
            css_rules.append(f"""{page_selector} {{
    @bottom-center {{
        border-top: 1px solid {footer_config.line_color};
        padding-top: 5px;
    }}
}}""")

        return "\n\n".join(css_rules)
