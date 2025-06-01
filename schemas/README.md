# Theme Configuration Schema Documentation

This document describes the complete schema for `theme.yaml` files used by the Markdown-to-PDF engine.

## Overview

The `theme.yaml` file controls the visual appearance and layout of generated PDF documents. It provides a structured way to configure:

- Page layout (size, margins, orientation)
- Font loading and typography
- Styling for standard Markdown elements
- Custom component configurations
- Headers and footers
- CSS file integration

## Schema Structure

### `page_setup`

Controls the overall page layout and default typography.

```yaml
page_setup:
  size: "A4"                    # Page size: A4, A3, A5, Letter, Legal, Tabloid
  orientation: "portrait"       # Page orientation: portrait, landscape
  margin: "2cm"                 # Uniform margin OR object with top/bottom/left/right
  default_font:                 # Default font settings
    family: ["Open Sans", "Arial", "sans-serif"]
    size: "11pt"
    color: "#333333"
```

**Margin Options:**
```yaml
# Option 1: Uniform margin
margin: "2cm"

# Option 2: Individual margins
margin:
  top: "2cm"
  bottom: "2cm"
  left: "1.5cm"
  right: "1.5cm"
```

**Supported Units:** `cm`, `mm`, `in`, `pt`, `px`

### `fonts`

Declares custom fonts for embedding in the PDF.

```yaml
fonts:
  - name: "Inter"                    # Font family name used in CSS
    normal: "fonts/Inter-Regular.ttf"
    bold: "fonts/Inter-Bold.ttf"
    italic: "fonts/Inter-Italic.ttf"
    bold_italic: "fonts/Inter-BoldItalic.ttf"
  - name: "IconFont"
    normal: "fonts/icons.ttf"        # Only normal weight needed for icon fonts
```

**Requirements:**
- At least the `name` field is required
- Font file paths are relative to the theme.yaml location
- Generates CSS `@font-face` rules automatically

### `stylesheets`

Lists external CSS files to include.

```yaml
stylesheets:
  - "css/base.css"
  - "css/components.css"
  - "themes/custom.css"
```

**Notes:**
- Paths are relative to the theme.yaml location
- Files are included in the order specified
- Combined with generated CSS from theme configuration

### `styles`

Defines styling for standard Markdown elements using CSS-like properties.

```yaml
styles:
  h1:
    font_family: ["Inter", "sans-serif"]
    font_size: "28pt"
    font_weight: "bold"
    color: "#1a5276"
    margin_top: "24px"
    margin_bottom: "16px"
    text_align: "center"
    border_bottom: "3px solid #3498db"
  
  p:
    line_height: "1.6"
    margin_bottom: "12px"
    text_align: "justify"
  
  blockquote:
    color: "#666666"
    background_color: "#f8f9fa"
    border_left: "4px solid #3498db"
    padding: "15px 20px"
    margin: "20px 0"
```

**Supported Elements:**
- Headers: `h1`, `h2`, `h3`, `h4`, `h5`, `h6`
- Text: `p`, `strong`, `em`, `a`
- Lists: `ul`, `ol`, `li`
- Code: `code`, `code_block`, `pre`
- Other: `blockquote`, `table`, `th`, `td`, `img`, `hr`

**Supported Properties:**
- Typography: `font_family`, `font_size`, `font_weight`, `color`, `line_height`
- Spacing: `margin_top`, `margin_bottom`, `margin_left`, `margin_right`, `padding`
- Layout: `text_align`, `background_color`, `border`, `border_radius`
- Lists: `list_style_type`
- Links: `text_decoration`

### `custom_components`

Configures custom Markdown components (`::: component_name :::`).

```yaml
custom_components:
  tip_box:
    template: "templates/tip_box.html"    # Jinja2 template file
    default_icon: "lightbulb"            # Default icon
    default_attributes:                  # Default attributes
      theme: "blue"
      style: "modern"
  
  warning_box:
    template: "templates/warning.html"
    default_icon: "alert-triangle"
```

**Notes:**
- Template paths are relative to the theme.yaml location
- Default attributes can be overridden in Markdown
- Component names must be valid Python identifiers

### `page_headers` and `page_footers`

Configure page headers and footers with dynamic content.

```yaml
page_headers:
  default:                              # Named header configuration
    left: "{section_title}"             # Left position content
    center: "Document Title"            # Center position content
    right: "Confidential"               # Right position content
    font_family: ["Inter", "sans-serif"]
    font_size: "9pt"
    color: "#666666"
    line_separator: true                # Show separator line
    line_color: "#cccccc"

page_footers:
  default:
    left: "© 2025 Company"
    center: ""
    right: "Page {page_number} of {total_pages}"
    font_family: ["Inter", "sans-serif"]
    font_size: "8pt"
    color: "#777777"
    line_separator: true
```

**Dynamic Variables:**
- `{page_number}` - Current page number
- `{total_pages}` - Total number of pages
- `{section_title}` - Current section title (from H1)
- `{document_title}` - Document title (from metadata)
- `{date}` - Current date
- `{year}` - Current year

## Examples

### Minimal Configuration

```yaml
page_setup:
  size: "A4"
  margin: "2cm"

styles:
  h1:
    color: "#2c3e50"
    font_size: "24pt"

page_footers:
  default:
    center: "Page {page_number}"
```

### Corporate Theme

See [corporate.yaml](examples/corporate.yaml) for a comprehensive business document theme.

### Disney Magic Kingdom Theme

See [magic_kingdom.yaml](examples/magic_kingdom.yaml) for a themed itinerary example.

## Validation

The schema is validated using JSON Schema. Common validation errors:

- **Invalid units**: Use supported units (`cm`, `mm`, `in`, `pt`, `px`)
- **Invalid colors**: Use 6-digit hex colors (`#ffffff`)
- **Missing font files**: Ensure font paths are correct and files exist
- **Invalid element names**: Only standard Markdown elements are supported
- **Invalid page sizes**: Use standard sizes or define custom dimensions

## File Structure Recommendations

```
your-project/
├── theme.yaml
├── fonts/
│   ├── Inter-Regular.ttf
│   └── Inter-Bold.ttf
├── css/
│   ├── base.css
│   └── components.css
└── templates/
    ├── tip_box.html
    └── warning_box.html
```

## CSS Generation

The theme configuration generates CSS that is combined with your custom stylesheets:

1. **Font faces** - Generated from `fonts` section
2. **Page setup** - Generates `@page` rules
3. **Element styles** - Converts `styles` to CSS rules
4. **Headers/footers** - Generates CSS Paged Media rules

The final CSS order:
1. Generated CSS from theme.yaml
2. External stylesheets (in order specified)
3. Component-specific CSS

This ensures proper cascading and allows overrides in external CSS files. 