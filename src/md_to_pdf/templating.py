"""
Templating system for custom components.

This module provides the TemplateManager class that handles:
- Jinja2 environment setup and configuration
- Component template registration and loading
- Template context building from component attributes
- HTML generation for custom components
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from markupsafe import Markup


class TemplateManager:
    """Manages Jinja2 templates for custom components."""

    def __init__(self, template_dirs: Optional[List[str]] = None):
        """
        Initialize the template manager.

        Args:
            template_dirs: List of directories to search for templates.
                          If None, uses default 'templates' directory.
        """
        if template_dirs is None:
            # Default to templates directory in project root
            project_root = Path(__file__).parent.parent.parent
            template_dirs = [str(project_root / "templates")]

        # Ensure all template directories exist
        for template_dir in template_dirs:
            Path(template_dir).mkdir(parents=True, exist_ok=True)

        # Set up Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(template_dirs),
            autoescape=True,  # Auto-escape HTML for security
            trim_blocks=True,  # Remove newlines after block tags
            lstrip_blocks=True,  # Remove leading whitespace before blocks
        )

        # Add custom filters
        self._setup_custom_filters()

        # Registry of available components
        self.component_registry: Dict[str, str] = {}

        # Discover and register available templates
        self._discover_templates()

    def _setup_custom_filters(self):
        """Set up custom Jinja2 filters for template processing."""

        def css_class_filter(value: str) -> str:
            """Convert a string to a valid CSS class name."""
            return value.lower().replace("_", "-").replace(" ", "-")

        def attr_string_filter(attrs: Dict[str, Any]) -> Markup:
            """Convert a dictionary of attributes to an HTML attribute string."""
            if not attrs:
                return Markup("")

            attr_parts = []
            for key, value in attrs.items():
                if value is True:
                    # Boolean attribute (e.g., disabled, checked)
                    attr_parts.append(key)
                elif value is not False and value is not None:
                    # Regular attribute with value
                    escaped_value = str(value).replace('"', "&quot;")
                    attr_parts.append(f'{key}="{escaped_value}"')

            return Markup(" " + " ".join(attr_parts) if attr_parts else "")

        # Register filters
        self.env.filters["css_class"] = css_class_filter
        self.env.filters["attr_string"] = attr_string_filter

    def _discover_templates(self):
        """Discover available component templates and register them."""
        # Only discover templates if we have a FileSystemLoader
        if isinstance(self.env.loader, FileSystemLoader):
            for template_dir in self.env.loader.searchpath:
                template_path = Path(template_dir)
                if template_path.exists():
                    # Look for .html files in the template directory
                    for template_file in template_path.glob("*.html"):
                        component_name = template_file.stem
                        template_name = template_file.name
                        self.register_component(component_name, template_name)

    def register_component(self, component_name: str, template_name: str):
        """
        Register a component with its template.

        Args:
            component_name: Name of the component (e.g., 'tip_box')
            template_name: Name of the template file (e.g., 'tip_box.html')
        """
        self.component_registry[component_name] = template_name

    def is_component_registered(self, component_name: str) -> bool:
        """Check if a component is registered."""
        return component_name in self.component_registry

    def get_registered_components(self) -> List[str]:
        """Get a list of all registered component names."""
        return list(self.component_registry.keys())

    def build_context(
        self, component_name: str, attributes: Dict[str, Any], content: str = ""
    ) -> Dict[str, Any]:
        """
        Build template context from component attributes and content.

        Args:
            component_name: Name of the component
            attributes: Dictionary of component attributes
            content: Inner content of the component

        Returns:
            Dictionary containing template context variables
        """
        # Start with basic context
        context = {
            "component_name": component_name,
            "content": content,
            "attributes": attributes,
        }

        # Add individual attributes as top-level variables for convenience
        context.update(attributes)

        # Add some computed values
        context["css_classes"] = self._build_css_classes(component_name, attributes)
        context["data_attributes"] = self._build_data_attributes(attributes)

        return context

    def _build_css_classes(
        self, component_name: str, attributes: Dict[str, Any]
    ) -> str:
        """Build CSS class string for the component."""
        classes = ["custom-block", component_name.replace("_", "-")]

        # Add classes based on attributes
        if "color" in attributes:
            classes.append(f"color-{attributes['color']}")

        if "size" in attributes:
            classes.append(f"size-{attributes['size']}")

        # Add any explicit class attributes
        if "class" in attributes:
            classes.append(str(attributes["class"]))

        return " ".join(classes)

    def _build_data_attributes(self, attributes: Dict[str, Any]) -> Dict[str, Any]:
        """Build data attributes for the component."""
        data_attrs = {}

        # Convert certain attributes to data attributes
        for key, value in attributes.items():
            if key not in ["class", "id", "style"]:  # Skip standard HTML attributes
                data_attrs[f"data-{key.replace('_', '-')}"] = value

        return data_attrs

    def render_component(
        self, component_name: str, attributes: Dict[str, Any], content: str = ""
    ) -> str:
        """
        Render a component to HTML.

        Args:
            component_name: Name of the component to render
            attributes: Dictionary of component attributes
            content: Inner content of the component

        Returns:
            Rendered HTML string

        Raises:
            TemplateNotFound: If the component template is not found
            ValueError: If the component is not registered
        """
        if not self.is_component_registered(component_name):
            raise ValueError(f"Component '{component_name}' is not registered")

        template_name = self.component_registry[component_name]

        try:
            template = self.env.get_template(template_name)
        except TemplateNotFound:
            raise TemplateNotFound(
                f"Template '{template_name}' not found for component '{component_name}'"
            )

        context = self.build_context(component_name, attributes, content)
        return template.render(**context)

    def render_from_string(self, template_string: str, context: Dict[str, Any]) -> str:
        """
        Render a template from a string.

        Args:
            template_string: Template content as string
            context: Template context variables

        Returns:
            Rendered HTML string
        """
        template = self.env.from_string(template_string)
        return template.render(**context)

    def add_template_directory(self, template_dir: str):
        """
        Add an additional template directory to the search path.

        Args:
            template_dir: Path to the template directory
        """
        # Create new loader with updated search path
        if isinstance(self.env.loader, FileSystemLoader):
            current_paths = list(self.env.loader.searchpath)
            if template_dir not in current_paths:
                current_paths.append(template_dir)
                self.env.loader = FileSystemLoader(current_paths)

                # Re-discover templates
                self._discover_templates()
