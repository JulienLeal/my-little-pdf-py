"""
Comprehensive base CSS for professional PDF generation.

This module provides professional-grade CSS for all PDF outputs, including
typography, print optimizations, and visual hierarchy.
"""

from typing import Any, Dict


class BaseCSSGenerator:
    """Generates comprehensive base CSS for professional PDF output."""

    def __init__(self):
        """Initialize base CSS generator."""
        pass

    def generate_base_css(self) -> str:
        """Generate comprehensive base CSS for professional PDFs.

        Returns:
            Complete CSS string with professional styling
        """
        css_sections = [
            self._get_css_reset(),
            self._get_typography(),
            self._get_page_layout(),
            self._get_headings(),
            self._get_text_elements(),
            self._get_lists(),
            self._get_tables(),
            self._get_code_blocks(),
            self._get_forms(),
            self._get_print_optimizations(),
            self._get_utility_classes(),
        ]

        return "\n\n".join(css_sections)

    def _get_css_reset(self) -> str:
        """CSS reset and base normalizations."""
        return """/* CSS Reset and Normalizations */
* {
    box-sizing: border-box;
}

html {
    font-size: 16px; /* Base font size for rem calculations */
    line-height: 1.15; /* Improve line spacing */
    -webkit-text-size-adjust: 100%; /* Prevent font size adjustments */
}

body {
    margin: 0;
    padding: 0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    font-size: 11pt; /* Optimal for print */
    line-height: 1.6; /* Excellent readability */
    color: #2c3e50; /* Professional dark blue-gray */
    background-color: #ffffff;
    text-rendering: optimizeLegibility;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}"""

    def _get_typography(self) -> str:
        """Professional typography settings."""
        return """/* Professional Typography */
.serif {
    font-family: "Times New Roman", "Georgia", "DejaVu Serif", serif;
}

.sans-serif {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

.monospace {
    font-family: "SF Mono", "Monaco", "Inconsolata", "Roboto Mono", "Consolas", "Courier New", monospace;
}

/* Text sizes following a modular scale */
.text-xs { font-size: 0.75rem; line-height: 1.0; }
.text-sm { font-size: 0.875rem; line-height: 1.25; }
.text-base { font-size: 1rem; line-height: 1.5; }
.text-lg { font-size: 1.125rem; line-height: 1.75; }
.text-xl { font-size: 1.25rem; line-height: 1.75; }
.text-2xl { font-size: 1.5rem; line-height: 2; }
.text-3xl { font-size: 1.875rem; line-height: 2.25; }
.text-4xl { font-size: 2.25rem; line-height: 2.5; }

/* Font weights */
.font-thin { font-weight: 100; }
.font-light { font-weight: 300; }
.font-normal { font-weight: 400; }
.font-medium { font-weight: 500; }
.font-semibold { font-weight: 600; }
.font-bold { font-weight: 700; }
.font-extrabold { font-weight: 800; }
.font-black { font-weight: 900; }"""

    def _get_page_layout(self) -> str:
        """Page layout and margin settings."""
        return """/* Page Layout */
@page {
    size: A4;
    margin: 2.5cm 2cm 2cm 2cm; /* Top, Right, Bottom, Left */
    orphans: 3; /* Minimum lines at bottom of page */
    widows: 3; /* Minimum lines at top of page */
    
    /* Footer space */
    @bottom-center {
        content: counter(page);
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        font-size: 9pt;
        color: #6c757d;
    }
}

@page :first {
    margin-top: 3cm; /* Extra space for title */
}

@page :left {
    margin-left: 2.5cm;
    margin-right: 1.5cm;
}

@page :right {
    margin-left: 1.5cm;
    margin-right: 2.5cm;
}

/* Page break controls */
.page-break-before { page-break-before: always; }
.page-break-after { page-break-after: always; }
.page-break-inside-avoid { page-break-inside: avoid; }
.page-break-avoid { page-break-inside: avoid; }"""

    def _get_headings(self) -> str:
        """Professional heading styles."""
        return """/* Professional Headings */
h1, h2, h3, h4, h5, h6 {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    font-weight: 600;
    line-height: 1.25;
    color: #1a365d; /* Professional dark blue */
    margin-top: 2rem;
    margin-bottom: 1rem;
    page-break-after: avoid; /* Keep headings with following content */
    orphans: 3;
    widows: 3;
}

h1 {
    font-size: 2.25rem; /* 36px at 16px base */
    font-weight: 700;
    color: #1a365d;
    margin-top: 0;
    margin-bottom: 2rem;
    padding-bottom: 0.5rem;
    border-bottom: 3px solid #3182ce;
    page-break-before: auto;
}

h2 {
    font-size: 1.875rem; /* 30px */
    font-weight: 600;
    color: #2d3748;
    margin-top: 2.5rem;
    margin-bottom: 1.5rem;
    padding-bottom: 0.25rem;
    border-bottom: 1px solid #e2e8f0;
}

h3 {
    font-size: 1.5rem; /* 24px */
    font-weight: 600;
    color: #2d3748;
    margin-top: 2rem;
    margin-bottom: 1rem;
}

h4 {
    font-size: 1.25rem; /* 20px */
    font-weight: 600;
    color: #4a5568;
    margin-top: 1.5rem;
    margin-bottom: 0.75rem;
}

h5 {
    font-size: 1.125rem; /* 18px */
    font-weight: 600;
    color: #4a5568;
    margin-top: 1.25rem;
    margin-bottom: 0.5rem;
}

h6 {
    font-size: 1rem; /* 16px */
    font-weight: 600;
    color: #718096;
    margin-top: 1rem;
    margin-bottom: 0.5rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* Heading hierarchy indicators */
h1::before { content: ""; }
h2::before { content: ""; }
h3::before { content: ""; }

/* Chapter numbering support */
.chapter-number {
    color: #3182ce;
    font-weight: 300;
    margin-right: 0.5rem;
}"""

    def _get_text_elements(self) -> str:
        """Text elements and formatting."""
        return """/* Text Elements */
p {
    margin-bottom: 1rem;
    line-height: 1.6;
    text-align: justify;
    hyphens: auto;
    orphans: 2;
    widows: 2;
}

p:last-child {
    margin-bottom: 0;
}

/* Lead paragraph */
.lead {
    font-size: 1.125rem;
    font-weight: 300;
    line-height: 1.75;
    color: #4a5568;
    margin-bottom: 1.5rem;
}

/* Text formatting */
strong, b {
    font-weight: 600;
    color: #2d3748;
}

em, i {
    font-style: italic;
    color: #4a5568;
}

mark {
    background-color: #fef5e7;
    color: #744210;
    padding: 0.125rem 0.25rem;
    border-radius: 0.125rem;
}

del {
    text-decoration: line-through;
    color: #a0aec0;
}

ins {
    text-decoration: underline;
    color: #38a169;
    background-color: #f0fff4;
}

sub, sup {
    font-size: 0.75rem;
    line-height: 0;
    position: relative;
    vertical-align: baseline;
}

sub { bottom: -0.25rem; }
sup { top: -0.5rem; }

/* Links */
a {
    color: #3182ce;
    text-decoration: none;
    border-bottom: 1px solid transparent;
    transition: all 0.2s ease-in-out;
}

a:hover {
    color: #2c5282;
    border-bottom-color: #3182ce;
}

/* Print-specific link handling */
@media print {
    a[href^="http"]:after {
        content: " (" attr(href) ")";
        font-size: 0.8rem;
        color: #718096;
    }
}

/* Blockquotes */
blockquote {
    margin: 1.5rem 0;
    padding: 1rem 1.5rem;
    border-left: 4px solid #3182ce;
    background-color: #f7fafc;
    color: #4a5568;
    font-style: italic;
    position: relative;
    page-break-inside: avoid;
}

blockquote p {
    margin-bottom: 0.5rem;
}

blockquote p:last-child {
    margin-bottom: 0;
}

blockquote cite {
    display: block;
    margin-top: 0.5rem;
    font-size: 0.875rem;
    color: #718096;
    font-style: normal;
}

blockquote cite::before {
    content: "— ";
}

/* Horizontal rules */
hr {
    border: none;
    height: 1px;
    background: linear-gradient(to right, transparent, #e2e8f0, transparent);
    margin: 2rem 0;
    page-break-after: avoid;
}

hr.thick {
    height: 3px;
    background: #3182ce;
}"""

    def _get_lists(self) -> str:
        """List styling."""
        return """/* Lists */
ul, ol {
    margin: 1rem 0;
    padding-left: 2rem;
    page-break-inside: avoid;
}

ul {
    list-style-type: disc;
}

ol {
    list-style-type: decimal;
}

li {
    margin-bottom: 0.5rem;
    line-height: 1.6;
    page-break-inside: avoid;
}

li > p {
    margin-bottom: 0.5rem;
}

li > ul, li > ol {
    margin-top: 0.5rem;
    margin-bottom: 0.5rem;
}

/* Nested list styles */
ul ul { list-style-type: circle; }
ul ul ul { list-style-type: square; }
ol ol { list-style-type: lower-alpha; }
ol ol ol { list-style-type: lower-roman; }

/* Definition lists */
dl {
    margin: 1rem 0;
}

dt {
    font-weight: 600;
    color: #2d3748;
    margin-top: 1rem;
    margin-bottom: 0.25rem;
}

dd {
    margin-left: 1.5rem;
    margin-bottom: 0.75rem;
    color: #4a5568;
}

/* Task lists */
.task-list {
    list-style: none;
    padding-left: 0;
}

.task-list-item {
    position: relative;
    padding-left: 1.5rem;
}

.task-list-item input[type="checkbox"] {
    position: absolute;
    left: 0;
    top: 0.25rem;
    margin: 0;
}"""

    def _get_tables(self) -> str:
        """Professional table styling."""
        return """/* Professional Tables */
table {
    width: 100%;
    border-collapse: collapse;
    margin: 1.5rem 0;
    font-size: 0.9rem;
    page-break-inside: avoid;
    background-color: #ffffff;
}

/* Table headers */
thead {
    background-color: #f8f9fa;
}

th {
    background-color: #e9ecef;
    color: #2d3748;
    font-weight: 600;
    text-align: left;
    padding: 0.75rem;
    border: 1px solid #dee2e6;
    font-size: 0.875rem;
    text-transform: uppercase;
    letter-spacing: 0.025em;
}

/* Table cells */
td {
    padding: 0.75rem;
    border: 1px solid #dee2e6;
    color: #4a5568;
    vertical-align: top;
    line-height: 1.5;
}

/* Alternating row colors */
tbody tr:nth-child(even) {
    background-color: #f8f9fa;
}

tbody tr:hover {
    background-color: #e9ecef;
}

/* Table variants */
.table-striped tbody tr:nth-child(odd) {
    background-color: #ffffff;
}

.table-striped tbody tr:nth-child(even) {
    background-color: #f8f9fa;
}

.table-bordered {
    border: 2px solid #dee2e6;
}

.table-bordered th,
.table-bordered td {
    border: 1px solid #dee2e6;
}

/* Responsive table wrapper */
.table-responsive {
    overflow-x: auto;
    margin: 1rem 0;
}

/* Table captions */
caption {
    padding: 0.75rem;
    color: #6c757d;
    text-align: left;
    caption-side: bottom;
    font-size: 0.875rem;
}"""

    def _get_code_blocks(self) -> str:
        """Code and preformatted text styling."""
        return """/* Code and Preformatted Text */
code {
    font-family: "SF Mono", "Monaco", "Inconsolata", "Roboto Mono", "Consolas", "Courier New", monospace;
    font-size: 0.875rem;
    color: #e83e8c;
    background-color: #f8f9fa;
    padding: 0.125rem 0.375rem;
    border-radius: 0.25rem;
    border: 1px solid #e9ecef;
    white-space: nowrap;
}

/* Code blocks */
pre {
    font-family: "SF Mono", "Monaco", "Inconsolata", "Roboto Mono", "Consolas", "Courier New", monospace;
    font-size: 0.825rem;
    color: #2d3748;
    background-color: #f8f9fa;
    border: 1px solid #e2e8f0;
    border-radius: 0.375rem;
    padding: 1rem 1.25rem;
    margin: 1.5rem 0;
    overflow-x: auto;
    line-height: 1.6;
    page-break-inside: avoid;
}

pre code {
    color: inherit;
    background-color: transparent;
    padding: 0;
    border: none;
    border-radius: 0;
    white-space: pre;
    font-size: inherit;
}

/* Syntax highlighting support */
.highlight {
    background-color: #f8f9fa;
    border-radius: 0.375rem;
    margin: 1.5rem 0;
}

.highlight pre {
    margin: 0;
    border: none;
    background-color: transparent;
}

/* Language labels */
pre[data-lang]::before {
    content: attr(data-lang);
    display: block;
    font-size: 0.75rem;
    font-weight: 600;
    color: #718096;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.5rem;
    padding-bottom: 0.25rem;
    border-bottom: 1px solid #e2e8f0;
}"""

    def _get_forms(self) -> str:
        """Form element styling."""
        return """/* Form Elements */
input, select, textarea {
    font-family: inherit;
    font-size: 0.9rem;
    border: 1px solid #d2d6dc;
    border-radius: 0.25rem;
    padding: 0.5rem 0.75rem;
    background-color: #ffffff;
    color: #374151;
}

input:focus, select:focus, textarea:focus {
    outline: none;
    border-color: #3182ce;
    box-shadow: 0 0 0 3px rgba(49, 130, 206, 0.1);
}

label {
    display: block;
    font-weight: 500;
    color: #374151;
    margin-bottom: 0.25rem;
}

fieldset {
    border: 1px solid #d2d6dc;
    border-radius: 0.375rem;
    padding: 1rem;
    margin: 1rem 0;
}

legend {
    font-weight: 600;
    color: #2d3748;
    padding: 0 0.5rem;
}"""

    def _get_print_optimizations(self) -> str:
        """Print-specific optimizations."""
        return """/* Print Optimizations */
@media print {
    * {
        background: transparent !important;
        color: black !important;
        box-shadow: none !important;
        text-shadow: none !important;
    }
    
    body {
        font-size: 11pt;
        line-height: 1.5;
    }
    
    h1, h2, h3, h4, h5, h6 {
        page-break-after: avoid;
        orphans: 3;
        widows: 3;
    }
    
    h1 {
        font-size: 18pt;
    }
    
    h2 {
        font-size: 16pt;
    }
    
    h3 {
        font-size: 14pt;
    }
    
    h4, h5, h6 {
        font-size: 12pt;
    }
    
    p, li, blockquote {
        orphans: 3;
        widows: 3;
    }
    
    blockquote, pre, table {
        page-break-inside: avoid;
    }
    
    img {
        max-width: 100% !important;
        page-break-inside: avoid;
    }
    
    /* Hide unnecessary elements */
    .no-print {
        display: none !important;
    }
    
    /* Show print-only elements */
    .print-only {
        display: block !important;
    }
    
    /* Improve contrast for print */
    a {
        text-decoration: underline;
    }
    
    /* Page headers and footers */
    @page {
        margin: 2cm 1.5cm;
    }
    
    @page :first {
        margin-top: 3cm;
    }
}"""

    def _get_utility_classes(self) -> str:
        """Utility classes for common styling needs."""
        return """/* Utility Classes */

/* Spacing */
.mt-0 { margin-top: 0; }
.mt-1 { margin-top: 0.25rem; }
.mt-2 { margin-top: 0.5rem; }
.mt-3 { margin-top: 0.75rem; }
.mt-4 { margin-top: 1rem; }
.mt-5 { margin-top: 1.25rem; }
.mt-6 { margin-top: 1.5rem; }

.mb-0 { margin-bottom: 0; }
.mb-1 { margin-bottom: 0.25rem; }
.mb-2 { margin-bottom: 0.5rem; }
.mb-3 { margin-bottom: 0.75rem; }
.mb-4 { margin-bottom: 1rem; }
.mb-5 { margin-bottom: 1.25rem; }
.mb-6 { margin-bottom: 1.5rem; }

.ml-0 { margin-left: 0; }
.ml-1 { margin-left: 0.25rem; }
.ml-2 { margin-left: 0.5rem; }
.ml-3 { margin-left: 0.75rem; }
.ml-4 { margin-left: 1rem; }

.mr-0 { margin-right: 0; }
.mr-1 { margin-right: 0.25rem; }
.mr-2 { margin-right: 0.5rem; }
.mr-3 { margin-right: 0.75rem; }
.mr-4 { margin-right: 1rem; }

/* Text alignment */
.text-left { text-align: left; }
.text-center { text-align: center; }
.text-right { text-align: right; }
.text-justify { text-align: justify; }

/* Colors */
.text-primary { color: #3182ce; }
.text-secondary { color: #718096; }
.text-success { color: #38a169; }
.text-danger { color: #e53e3e; }
.text-warning { color: #d69e2e; }
.text-info { color: #0bc5ea; }
.text-muted { color: #a0aec0; }

.bg-primary { background-color: #3182ce; color: white; }
.bg-secondary { background-color: #718096; color: white; }
.bg-success { background-color: #38a169; color: white; }
.bg-danger { background-color: #e53e3e; color: white; }
.bg-warning { background-color: #d69e2e; color: white; }
.bg-info { background-color: #0bc5ea; color: white; }
.bg-light { background-color: #f7fafc; color: #2d3748; }
.bg-dark { background-color: #2d3748; color: white; }

/* Borders */
.border { border: 1px solid #e2e8f0; }
.border-top { border-top: 1px solid #e2e8f0; }
.border-bottom { border-bottom: 1px solid #e2e8f0; }
.border-left { border-left: 1px solid #e2e8f0; }
.border-right { border-right: 1px solid #e2e8f0; }

.rounded { border-radius: 0.25rem; }
.rounded-lg { border-radius: 0.5rem; }
.rounded-full { border-radius: 9999px; }

/* Shadows */
.shadow-sm { box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05); }
.shadow { box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06); }
.shadow-lg { box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05); }

/* Display */
.block { display: block; }
.inline-block { display: inline-block; }
.inline { display: inline; }
.hidden { display: none; }

/* Professional document sections */
.title-page {
    page-break-after: always;
    text-align: center;
    padding-top: 25%;
}

.executive-summary {
    page-break-before: always;
    border-left: 4px solid #3182ce;
    padding-left: 1rem;
    margin: 2rem 0;
}

.appendix {
    page-break-before: always;
}

.toc {
    page-break-after: always;
}

.toc ul {
    list-style: none;
    padding-left: 0;
}

.toc li {
    margin-bottom: 0.5rem;
    border-bottom: 1px dotted #e2e8f0;
    padding-bottom: 0.25rem;
}

.toc a {
    text-decoration: none;
    color: #4a5568;
}

.toc .page-number {
    float: right;
    color: #718096;
}"""

    def generate_theme_aware_css(self, theme_styles: Dict[str, Any]) -> str:
        """Generate base CSS that's aware of theme customizations.

        Args:
            theme_styles: Theme style overrides

        Returns:
            CSS that incorporates theme preferences
        """
        base_css = self.generate_base_css()

        # Add theme-specific overrides
        if not theme_styles:
            return base_css

        theme_overrides = []

        # Process common theme overrides
        if "body" in theme_styles:
            body_styles = theme_styles["body"]
            overrides = []

            if "font_family" in body_styles:
                font_family = ", ".join(
                    f'"{font}"' for font in body_styles["font_family"]
                )
                overrides.append(f"font-family: {font_family};")

            if "font_size" in body_styles:
                overrides.append(f"font-size: {body_styles['font_size']};")

            if "color" in body_styles:
                overrides.append(f"color: {body_styles['color']};")

            if overrides:
                theme_overrides.append(f"body {{ {' '.join(overrides)} }}")

        # Add theme overrides
        if theme_overrides:
            base_css += "\n\n/* Theme Overrides */\n" + "\n".join(theme_overrides)

        return base_css
