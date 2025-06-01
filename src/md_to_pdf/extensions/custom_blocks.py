"""
Custom Block Extension for Python-Markdown

This extension parses custom blocks with the syntax:
:::component_name attribute="value" flag
    Content here
:::

Based on research of python-markdown BlockProcessor API.
"""

import re
import xml.etree.ElementTree as etree
from typing import Any, Dict, Optional

from markdown.blockprocessors import BlockProcessor
from markdown.extensions import Extension

from ..templating import TemplateManager


class CustomBlockProcessor(BlockProcessor):
    """
    Block processor for custom component blocks.

    Parses blocks like:
    :::component_name attribute="value" flag
        Content here
    :::

    Or:
    :::component_name attribute="value" flag
        Content here (indented)
    """

    # Regex to match the start of a custom block - must be at the beginning of a line
    RE_FENCE_START = re.compile(r"^[ \t]*:::(\w+)(?:\s+(.*))?$", re.MULTILINE)
    RE_FENCE_END = re.compile(r"^[ \t]*:::[ \t]*$", re.MULTILINE)

    def __init__(self, parser, template_manager: Optional[TemplateManager] = None):
        """Initialize the processor with optional template manager."""
        super().__init__(parser)
        self.template_manager = template_manager

    def test(self, parent, block):
        """Test if this block should be processed by this processor."""
        # Check if the block starts with our custom block syntax
        lines = block.split("\n")
        for line in lines:
            if line.strip():  # First non-empty line
                return bool(re.match(r"^[ \t]*:::(\w+)(?:\s+.*)?$", line))
        return False

    def run(self, parent, blocks):
        """Process the custom block."""
        original_block = blocks[0]

        # Find the opening fence line
        lines = original_block.split("\n")
        opening_line = None
        opening_line_idx = -1

        for i, line in enumerate(lines):
            if line.strip():  # First non-empty line
                match = re.match(r"^[ \t]*:::(\w+)(?:\s+(.*))?$", line)
                if match:
                    opening_line = line
                    opening_line_idx = i
                    break
                else:
                    return False  # Not a custom block

        if opening_line is None:
            return False

        # Extract component name and attributes
        match = re.match(r"^[ \t]*:::(\w+)(?:\s+(.*))?$", opening_line)
        if not match:
            return False
        component_name = match.group(1)
        attributes_str = match.group(2) or ""

        # Look for content and closing fence
        content_lines = []
        closing_fence_found = False

        # First, check if there's a closing fence in the current block
        remaining_lines = lines[opening_line_idx + 1 :]
        for i, line in enumerate(remaining_lines):
            if re.match(r"^[ \t]*:::[ \t]*$", line):
                closing_fence_found = True
                # Put any content after the fence back into blocks
                if i + 1 < len(remaining_lines):
                    after_fence = "\n".join(remaining_lines[i + 1 :])
                    if after_fence.strip():
                        blocks[0] = after_fence
                    else:
                        blocks.pop(0)
                else:
                    blocks.pop(0)
                break
            else:
                content_lines.append(line)

        # If no closing fence in current block, look in subsequent blocks
        if not closing_fence_found:
            blocks.pop(0)  # Remove the processed first block

            blocks_consumed = 0
            for block_idx, block in enumerate(blocks):
                block_lines = block.split("\n")

                # Check for closing fence in this block
                fence_line_idx = -1
                for line_idx, line in enumerate(block_lines):
                    if re.match(r"^[ \t]*:::[ \t]*$", line):
                        fence_line_idx = line_idx
                        break

                if fence_line_idx >= 0:
                    # Found closing fence
                    closing_fence_found = True
                    # Add content before the fence
                    content_lines.extend(block_lines[:fence_line_idx])

                    # Put content after the fence back
                    if fence_line_idx + 1 < len(block_lines):
                        after_fence = "\n".join(block_lines[fence_line_idx + 1 :])
                        if after_fence.strip():
                            blocks[block_idx] = after_fence
                        else:
                            blocks_consumed = block_idx + 1
                    else:
                        blocks_consumed = block_idx + 1
                    break
                else:
                    # This entire block is content
                    content_lines.extend(block_lines)
                    blocks_consumed = block_idx + 1

            # Remove consumed blocks
            for _ in range(blocks_consumed):
                if blocks:
                    blocks.pop(0)

        # If still no closing fence found, use indentation-based detection
        if not closing_fence_found:
            # Use the original approach but simpler
            content_lines = []
            remaining_lines = lines[opening_line_idx + 1 :]

            for line in remaining_lines:
                # Empty lines are always included
                if not line.strip():
                    content_lines.append(line)
                # Indented lines are content
                elif line.startswith("    ") or line.startswith("\t"):
                    content_lines.append(line)
                else:
                    # Non-indented line - this is where the block ends
                    # Put this line and everything after back into blocks
                    remaining_idx = remaining_lines.index(line)
                    remaining_content = "\n".join(remaining_lines[remaining_idx:])
                    if remaining_content.strip():
                        blocks[0] = remaining_content
                    else:
                        blocks.pop(0)
                    break
            else:
                # Reached end of block without finding non-indented content
                blocks.pop(0)

        # Parse attributes from the header line
        attributes = self._parse_attributes(attributes_str)

        # Process content - remove indentation
        content = "\n".join(content_lines)
        content = self._dedent_content(content)

        # Generate the HTML element
        element = self._create_element(parent, component_name, attributes, content)

        return True

    def _parse_attributes(self, attributes_str: str) -> Dict[str, Any]:
        """Parse attributes from the header line."""
        attributes = {}
        if not attributes_str:
            return attributes

        # Simple regex to parse key="value" and standalone values
        # This is a simplified parser - could be made more robust
        token_pattern = re.compile(
            r"""
            (?:
                (\w+)=              # key=
                (?:
                    "([^"]*)"       # "quoted value"
                    |'([^']*)'      # 'quoted value'  
                    |(\S+)          # unquoted value
                )
            )
            |
            (\w+)                   # standalone flag/value
        """,
            re.VERBOSE,
        )

        positional_args = []

        for match in token_pattern.finditer(attributes_str):
            key, quoted_val, single_quoted_val, unquoted_val, standalone = (
                match.groups()
            )

            if key:
                # Key-value pair
                value = quoted_val or single_quoted_val or unquoted_val
                attributes[key] = value
            elif standalone:
                # Standalone value (could be a flag or positional argument)
                positional_args.append(standalone)

        # Store positional arguments
        if positional_args:
            attributes["_positional"] = positional_args

        return attributes

    def _dedent_content(self, content: str) -> str:
        """Remove consistent indentation from content."""
        if not content:
            return content

        lines = content.split("\n")

        # Find minimum indentation (ignoring empty lines)
        min_indent = float("inf")
        for line in lines:
            if line.strip():  # Skip empty lines
                indent = len(line) - len(line.lstrip())
                min_indent = min(min_indent, indent)

        if min_indent == float("inf"):
            min_indent = 0

        # Remove the minimum indentation from all lines
        dedented_lines = []
        for line in lines:
            if line.strip():  # Non-empty line
                dedented_lines.append(
                    line[min_indent:] if len(line) > min_indent else line
                )
            else:  # Empty line
                dedented_lines.append("")

        return "\n".join(dedented_lines).strip()

    def _create_element(
        self, parent, component_name: str, attributes: Dict[str, Any], content: str
    ) -> etree.Element:
        """Create the HTML element for the custom block."""
        # Try to use templating system if available
        if self.template_manager and self.template_manager.is_component_registered(
            component_name
        ):
            try:
                # Render using template
                rendered_html = self.template_manager.render_component(
                    component_name, attributes, content
                )

                # Parse the rendered HTML into an element
                try:
                    # Wrap in a div to ensure we have a single root element
                    wrapped_html = (
                        f"<div class='template-wrapper'>{rendered_html}</div>"
                    )
                    element = etree.fromstring(wrapped_html)

                    # Add the element to the parent
                    parent.append(element)
                    return element

                except etree.ParseError as e:
                    # If HTML parsing fails, fall back to simple div
                    print(
                        f"Warning: Failed to parse rendered HTML for {component_name}: {e}"
                    )
                    return self._create_fallback_element(
                        parent, component_name, attributes, content
                    )

            except Exception as e:
                # If template rendering fails, fall back to simple div
                print(f"Warning: Failed to render template for {component_name}: {e}")
                return self._create_fallback_element(
                    parent, component_name, attributes, content
                )
        else:
            # No template manager or component not registered - use fallback
            return self._create_fallback_element(
                parent, component_name, attributes, content
            )

    def _create_fallback_element(
        self, parent, component_name: str, attributes: Dict[str, Any], content: str
    ) -> etree.Element:
        """Create a fallback HTML element when templating is not available."""
        div = etree.SubElement(parent, "div")
        div.set("class", f"custom-block {component_name}")

        # Add attributes as data attributes
        for key, value in attributes.items():
            if key != "_positional":
                div.set(f"data-{key}", str(value))

        # Add positional arguments as data attribute
        if "_positional" in attributes:
            div.set("data-args", " ".join(attributes["_positional"]))

        # Process content as markdown
        if content:
            # Parse the content as markdown and add to the div
            self.parser.parseChunk(div, content)

        return div


class CustomBlockExtension(Extension):
    """Extension that adds custom block support to Markdown."""

    def __init__(self, template_manager: Optional[TemplateManager] = None, **kwargs):
        """Initialize the extension with optional template manager."""
        self.template_manager = template_manager
        super().__init__(**kwargs)

    def extendMarkdown(self, md):
        """Add the custom block processor to markdown."""
        processor = CustomBlockProcessor(md.parser, self.template_manager)
        # Register with a priority higher than most other block processors
        md.parser.blockprocessors.register(processor, "custom_blocks", 75)


# Convenience function for creating the extension
def makeExtension(template_manager: Optional[TemplateManager] = None, **kwargs):
    """Create and return the CustomBlockExtension."""
    return CustomBlockExtension(template_manager=template_manager, **kwargs)
