# Design Document: Configurable Markdown-to-PDF Engine

## 1. Introduction

This document outlines the design for a Python-based PDF Generation Engine. The primary goal is to create a system capable of converting standard Markdown documents into visually appealing, well-structured, and highly customizable PDF files. The "Magic_Kingdom_Itinerary_2025.pdf" serves as a key inspiration and benchmark for the types of elements, layouts, and overall aesthetic quality the engine should aim to achieve.

This document details the proposed architecture, the choice of Python libraries, a Markdown extension syntax for custom components, a comprehensive style configuration system, a strategy for handling assets like images and fonts, and illustrative examples of the Markdown-to-PDF generation process.

## 2. Core Architecture and Library Choices

**1. Core Architecture**

The proposed PDF generation engine will follow a three-stage pipeline:

   1.  **Markdown Parsing:** The input Markdown file (`.md`) is first parsed into an intermediate structural representation. This stage identifies standard Markdown elements and custom-defined components.
   2.  **HTML Generation & Templating:** The parsed structure is then converted into an HTML document. A templating engine will be used to map Markdown elements and custom components to specific HTML tags, classes, and attributes. This HTML will also link to the necessary CSS for styling and include references to assets like images and fonts.
   3.  **PDF Rendering:** The generated HTML document, along with its associated CSS, is then processed by a PDF rendering engine to produce the final PDF output.

This pipeline offers significant advantages:
    *   **Leverages Existing Technologies:** HTML and CSS are mature, well-understood standards for document structuring and styling.
    *   **Flexibility:** Separating parsing, templating, and rendering allows for modularity and easier customization at each stage.
    *   **Powerful Styling:** CSS provides a rich set of features for controlling layout, typography, colors, and more, enabling the creation of visually appealing documents.
    *   **Developer Familiarity:** Many developers are already familiar with HTML and CSS, simplifying the creation of new themes and styles.

**2. Recommended Python Libraries**

The following Python libraries are recommended for implementing the engine:

   *   **Markdown Parsing: `python-markdown`**
      *   **Reasoning:** `python-markdown` is a well-established and highly extensible library. Its robust extension API is crucial for parsing custom components (e.g., `::: tip_box :::`) and transforming them into a structured format suitable for the HTML templating stage. It supports a wide range of standard Markdown features.
      *   **Website:** [https://python-markdown.github.io/](https://python-markdown.github.io/)

   *   **HTML Templating: `Jinja2`**
      *   **Reasoning:** `Jinja2` is a powerful, fast, and widely-used templating engine in the Python ecosystem. It will be used to convert the parsed Markdown structure (including custom components) into the final HTML document. Jinja2's features, such as template inheritance, macros, and conditional rendering, will be invaluable for creating flexible and maintainable templates that can adapt to different styling configurations and custom component types.
      *   **Website:** [https://jinja.palletsprojects.com/](https://jinja.palletsprojects.com/)

   *   **PDF Rendering: `WeasyPrint`**
      *   **Reasoning:** `WeasyPrint` is an excellent choice for converting HTML and CSS into high-quality PDFs. It aims to support web standards for printing, including CSS Paged Media Module, which is essential for features like page headers/footers, page numbering, and precise layout control. Its strong CSS support is key to achieving the "beautiful" and highly customizable output required by the project, mirroring the sophistication of the "Magic_Kingdom_Itinerary_2025.pdf" example. It also handles font embedding effectively.
      *   **Website:** [https://weasyprint.org/](https://weasyprint.org/)

   *   **Style Configuration Parsing: `PyYAML`**
      *   **Reasoning:** YAML (`.yaml` or `.yml`) is a human-readable data serialization language that is well-suited for configuration files. `PyYAML` is the standard Python library for parsing YAML. It will be used to read and process the user-defined style configurations (e.g., `theme.yaml`), which will define how Markdown elements and custom components are styled, page dimensions, font choices, etc.
      *   **Website:** [https://pyyaml.org/](https://pyyaml.org/)

This combination of libraries provides a solid foundation for building a flexible, powerful, and high-quality Markdown-to-PDF generation engine.

## 3. Markdown Extension Syntax for Custom Components

To accommodate elements beyond standard Markdown, such as the stylized boxes and callouts found in "Magic_Kingdom_Itinerary_2025.pdf," we will implement a Markdown extension strategy. This allows users to embed custom components directly within their `.md` files in a way that is both expressive and relatively easy to parse.

**3.1. Proposed Syntax: Fenced Divs with Attributes**

We will adopt a syntax similar to Pandoc's fenced divs or other common Markdown extensions (like `markdown-it-attrs` or Python-Markdown's `attr_list` for block elements, but more explicitly for custom named blocks). This involves using triple colons (`:::`) to demarcate a block, followed by a component name and optional attributes.

**General Syntax:**

```markdown
::: component_name attribute1="value1" attribute2="value2"
Content for the component goes here.
It can span multiple lines and include other
Markdown elements (like **bold text** or lists).
:::
```

*   `component_name`:  A unique identifier for the custom component (e.g., `tip_box`, `magic_secret`, `attention_box`). This name will be used to link the component to its styling rules in the configuration.
*   `attributeN="valueN"`: Optional key-value pairs that provide parameters to the component. These can be used for things like titles, icon names, colors, or other data needed for rendering. Values should be enclosed in quotes if they contain spaces.
*   `Content`: The Markdown content within the block will be processed and passed to the component's template.

**3.2. Translation to HTML**

The `python-markdown` extension developed for this engine will parse these custom blocks and transform them into specific HTML structures. Generally, they will be converted into `<div>` elements with classes that identify the component type and any specified attributes translated into `data-*` attributes.

**General HTML Transformation:**

```html
<div class="custom-block component_name" data-attribute1="value1" data-attribute2="value2">
  <!-- Processed Markdown content from the block -->
  <p>Content for the component goes here.</p>
  <p>It can span multiple lines and include other
  Markdown elements (like <strong>bold text</strong> or lists).</p>
</div>
```

The `custom-block` class can be used for global styling of all custom components, while `component_name` (e.g., `class="tip-box"`) will be used for specific styling of that component type.

**3.3. Examples Inspired by "Magic_Kingdom_Itinerary_2025.pdf"**

Let's illustrate with examples based on the elements described in the issue:

**Example 1: "DICA MÁGICA" (Magic Tip Box)**

*   **Markdown:**
    ```markdown
    ::: tip_box icon="lightbulb" title="DICA MÁGICA"
    Chegue pelo menos 1 hora antes da abertura oficial do parque. Isso permite que você passe pelos processos de segurança e entrada com calma e esteja entre os primeiros a entrar, aproveitando as atrações mais populares com menos fila.
    :::
    ```

*   **Conceptual HTML Output:**
    ```html
    <div class="custom-block tip-box" data-icon="lightbulb" data-title="DICA MÁGICA">
      <div class="block-title">
        <span class="icon icon-lightbulb"></span> <!-- Icon would be handled by CSS/JS or templating -->
        DICA MÁGICA
      </div>
      <div class="block-content">
        <p>Chegue pelo menos 1 hora antes da abertura oficial do parque. Isso permite que você passe pelos processos de segurança e entrada com calma e esteja entre os primeiros a entrar, aproveitando as atrações mais populares com menos fila.</p>
      </div>
    </div>
    ```
    *(Note: The exact HTML structure, especially for internal parts like title and icon, will be defined by the Jinja2 template for the `tip_box` component and can be made more sophisticated.)*

**Example 2: "SEGREDINHO MÁGICO" (Magic Secret Box)**

*   **Markdown:**
    ```markdown
    ::: magic_secret icon="wand" title="SEGREDINHO MÁGICO"
    Alguns personagens aparecem em locais não listados no mapa, especialmente no início da manhã ou final da tarde. Fique de olho perto da Town Square ou nas laterais do castelo!
    :::
    ```

*   **Conceptual HTML Output:**
    ```html
    <div class="custom-block magic-secret" data-icon="wand" data-title="SEGREDINHO MÁGICO">
      <div class="block-title">
        <span class="icon icon-wand"></span>
        SEGREDINHO MÁGICO
      </div>
      <div class="block-content">
        <p>Alguns personagens aparecem em locais não listados no mapa, especialmente no início da manhã ou final da tarde. Fique de olho perto da Town Square ou nas laterais do castelo!</p>
      </div>
    </div>
    ```

**Example 3: "ATENÇÃO - TRON" (Attention Box for TRON)**

*   **Markdown:**
    ```markdown
    ::: attention_box icon="alert-triangle" title="ATENÇÃO - TRON Lightcycle / Run" color_theme="tron_blue"
    Esta atração utiliza fila virtual! Certifique-se de entrar na fila pelo aplicativo My Disney Experience exatamente às 7h ou 13h. As vagas são limitadas e se esgotam rapidamente.
    :::
    ```

*   **Conceptual HTML Output:**
    ```html
    <div class="custom-block attention-box tron-attention" data-icon="alert-triangle" data-title="ATENÇÃO - TRON Lightcycle / Run" data-color-theme="tron_blue">
      <div class="block-title">
        <span class="icon icon-alert-triangle"></span>
        ATENÇÃO - TRON Lightcycle / Run
      </div>
      <div class="block-content">
        <p>Esta atração utiliza fila virtual! Certifique-se de entrar na fila pelo aplicativo My Disney Experience exatamente às 7h ou 13h. As vagas são limitadas e se esgotam rapidamente.</p>
      </div>
    </div>
    ```
    *(Here, `data-color-theme="tron_blue"` could be used by CSS to apply a specific color scheme to this instance of the attention box).*

This fenced div approach provides a clean way to embed semantic information for custom components directly in Markdown, which can then be precisely targeted for styling and layout in the subsequent HTML and CSS stages. The `python-markdown` extension will be responsible for the parsing of these blocks.

## 4. Style Configuration System

The engine's flexibility hinges on a comprehensive yet user-friendly style configuration system. This system will primarily rely on a YAML configuration file (e.g., `theme.yaml`) that works in conjunction with user-provided CSS files. This approach combines the readability of YAML for structural definitions with the power of CSS for detailed styling.

**4.1. Main Configuration File: `theme.yaml`**

Users will define the overall look and feel of their PDF through a `theme.yaml` file. This file will be structured to manage global settings, font definitions, element styling, and custom component configurations.

**Example `theme.yaml` Structure:**

```yaml
# theme.yaml

# 1. Global Page Settings
page_setup:
  size: "A4" # e.g., A4, Letter, Legal
  orientation: "portrait" # portrait or landscape
  margin:
    top: "2cm"
    bottom: "2cm"
    left: "1.5cm"
    right: "1.5cm"
  # Default font settings for the document
  default_font:
    family: ["Open Sans", "Arial", "sans-serif"] # List of font families (fallback)
    size: "11pt"
    color: "#333333"

# 2. Font Definitions (for embedding custom fonts)
fonts:
  - name: "Roboto"
    normal: "path/to/fonts/Roboto-Regular.ttf"
    bold: "path/to/fonts/Roboto-Bold.ttf"
    italic: "path/to/fonts/Roboto-Italic.ttf"
    bold_italic: "path/to/fonts/Roboto-BoldItalic.ttf"
  - name: "AwesomeFont" # For icons
    normal: "path/to/fonts/fontawesome-webfont.ttf"

# 3. CSS Files
# List of CSS files to be included. Paths are relative to the theme.yaml or an assets directory.
stylesheets:
  - "css/base.css"
  - "css/pygments-style.css" # For code block syntax highlighting
  - "css/custom-components.css"
  - "css/typography.css"

# 4. Styling for Standard Markdown Elements
# These typically map to CSS selectors. Users can define basic properties here
# or rely more heavily on the external CSS files for complex styling.
styles:
  h1:
    font_family: ["Roboto", "Helvetica Neue", "sans-serif"]
    font_size: "28pt"
    font_weight: "bold"
    color: "#1a5276"
    margin_top: "20px"
    margin_bottom: "10px"
    # Special properties like 'page_break_before: always' could be supported
  h2:
    font_family: ["Roboto", "sans-serif"]
    font_size: "22pt"
    # ... more styles
  p:
    line_height: "1.6"
    margin_bottom: "12px"
  ul:
    list_style_type: "disc" # Or custom image via CSS
  a:
    color: "#2980b9"
    text_decoration: "none"
  code_block: # For fenced code blocks
    background_color: "#f0f0f0"
    padding: "10px"
    border_radius: "4px"
    font_family: ["Courier New", "monospace"]
    # Syntax highlighting theme would be controlled by a CSS file (e.g., pygments)

# 5. Custom Component Configuration
# Defines how custom blocks from Markdown are templated and styled.
custom_components:
  tip_box:
    template: "templates/tip_box.html" # Path to a Jinja2 template for this component
    # Default parameters (can be overridden in Markdown)
    default_icon: "lightbulb"
    # Styles can be primarily handled by CSS targeting '.custom-block.tip-box'
    # but some direct parameters could be supported if simple.
  magic_secret:
    template: "templates/magic_secret.html"
    default_icon: "wand"
  attention_box:
    template: "templates/attention_box.html"
    default_icon: "alert-triangle"
  # Example of a component that might not need a complex template,
  # relying purely on CSS via its generated class.
  stylized_title:
    # No specific template, will be a div with class="custom-block stylized-title"
    # All styling done via CSS.
    # Attributes from Markdown (e.g., title="text") will be data-* attributes.

# 6. Page Headers and Footers
# Configuration for content in page margins (using CSS Paged Media)
page_headers:
  # Default for all pages, can be overridden by named pages
  default:
    left: "{page_number} | {section_title}" # Variables to be interpolated
    center: ""
    right: "My Document Title"
    font_family: ["Open Sans", "sans-serif"]
    font_size: "9pt"
    color: "#777777"
    line_separator: "true" # Draw a line below header

page_footers:
  default:
    left: "© My Company {year}"
    center: ""
    right: "Page {page_number} of {total_pages}"
    font_family: ["Open Sans", "sans-serif"]
    font_size: "9pt"
    color: "#777777"
    line_separator: "true" # Draw a line above footer

# (Future) Named pages for different header/footer styles, e.g., first page, chapter start
# named_pages:
#   first_page:
#     header: null # No header on first page
#     footer: ...
```

**4.2. Page-Level Attributes**

As shown in the `page_setup` section of `theme.yaml`, users can define:
*   **Page Size:** Standard (A4, Letter) or custom dimensions.
*   **Orientation:** Portrait or Landscape.
*   **Margins:** Top, bottom, left, right margins.
These will be translated into CSS `@page` rules.

**4.3. Styling Standard Markdown Elements**

The `styles` section in `theme.yaml` allows for defining basic properties for standard HTML tags generated from Markdown (e.g., `h1`, `p`, `ul`, `blockquote`).
*   The engine will convert these definitions into CSS rules. For instance, `h1: { color: "blue" }` becomes `h1 { color: blue; }`.
*   For more complex styling (pseudo-classes, advanced selectors), users should use the external CSS files referenced in the `stylesheets` array. The YAML definitions provide a quick way to override common properties.

**4.4. Custom Component Styling**

Custom components, defined in Markdown (e.g., `::: tip_box :::`), are handled as follows:
1.  **Mapping to HTML:** The Markdown parser (with extensions) converts the custom block into an HTML element, typically a `div` with a base class (e.g., `custom-block`) and a component-specific class (e.g., `tip-box`). Attributes from the Markdown (e.g., `icon="lightbulb"`, `title="My Tip"`) are passed as `data-*` attributes to the HTML element (e.g., `data-icon="lightbulb"`).
2.  **Jinja2 Templating:** The `custom_components` section in `theme.yaml` can specify a Jinja2 template for each component type (e.g., `tip_box.html`). This template receives the `data-*` attributes and the inner content of the block. The template is responsible for the HTML structure of the component (e.g., creating a title bar, an icon placeholder).
    ```html
    <!-- Example: templates/tip_box.html -->
    <div class="block-title">
      {% if icon %}<span class="icon icon-{{ icon }}"></span>{% endif %}
      {{ title }}
    </div>
    <div class="block-content">
      {{ content | markdown_to_html }} {# Assuming content is passed as Markdown string #}
    </div>
    ```
3.  **CSS Styling:** Styling is primarily done through CSS. Users will write CSS rules in their custom stylesheets (e.g., `custom-components.css`) to target the classes and attributes of the generated HTML.
    ```css
    /* Example: custom-components.css */
    .custom-block.tip-box {
      background-color: #eef7ff;
      border-left: 5px solid #2980b9;
      padding: 15px;
      margin-bottom: 20px;
    }
    .custom-block.tip-box .block-title {
      font-weight: bold;
      color: #2980b9;
      margin-bottom: 10px;
    }
    .custom-block.tip-box .icon-lightbulb::before {
      content: "\f0eb"; /* Example using FontAwesome unicode */
      font-family: "AwesomeFont";
      margin-right: 8px;
    }
    ```

**4.5. External CSS Files (`stylesheets`)**

The `stylesheets` key in `theme.yaml` lists CSS files to be included.
*   These files allow users to write any CSS they need, providing fine-grained control over appearance.
*   This is where most of the detailed styling for both standard elements and custom components will reside.
*   WeasyPrint will use these CSS files when rendering the PDF.
*   CSS features like variables, flexbox, grid, and Paged Media rules (for headers/footers, page breaks) can be used.

**4.6. Headers and Footers**

The `page_headers` and `page_footers` sections in `theme.yaml` allow defining content for the top and bottom margins of pages.
*   This will be implemented using CSS Paged Media (e.g., `@top-left`, `@bottom-right`).
*   The configuration allows specifying content for left, center, and right slots.
*   Special variables like `{page_number}`, `{total_pages}`, `{section_title}`, `{date}` can be made available for dynamic content.
*   Basic styling (font, size, color, line separator) can be defined in YAML, which translates to CSS.

This layered approach—YAML for structure and high-level settings, CSS for detailed presentation—offers a good balance of simplicity and power, enabling users to create highly customized PDF documents.

## 5. Asset Handling Strategy

Effective asset management is crucial for producing rich PDF documents that include images and custom typography. The engine needs a clear strategy for locating, processing, and embedding these assets. Assets primarily include images and fonts.

**5.1. Image Handling**

Images are typically included in Markdown using the `![alt text](path/to/image.jpg)` syntax.

*   **Path Resolution:**
    1.  **Relative Paths:** Image paths relative to the input Markdown file's location will be prioritized. For example, if the Markdown file is `/docs/document.md` and uses `![example](./images/example.png)`, the engine will look for `/docs/images/example.png`.
    2.  **Asset Directory:** The `theme.yaml` configuration may specify one or more asset directories (e.g., `asset_dirs: ["assets/", "_shared_images/"]`). If an image is not found relative to the Markdown file, these directories will be searched.
    3.  **Absolute Paths:** Absolute paths in Markdown will be used as-is, but their use is generally discouraged for portability.
    4.  **URLS:** Images referenced via URLs (e.g. `![alt text](http://example.com/image.png)`) will be downloaded by WeasyPrint during PDF generation. Internet access will be required at the time of PDF generation for this to work.

*   **Processing:**
    *   During the HTML generation phase, image paths will be resolved to be accessible to WeasyPrint. This might involve:
        *   Ensuring paths are correct for WeasyPrint's context (e.g., if running in a temporary directory).
        *   Converting paths to absolute paths or paths relative to the HTML file's location if it's generated in a temporary location.
    *   No server-side image manipulation (resizing, format conversion) is planned for the initial version, but this could be a future extension. Image sizing and styling should be controlled via CSS.

*   **Embedding:** WeasyPrint handles the embedding of images into the PDF based on the `<img>` tags in the HTML.

**5.2. Font Management**

Custom typography is a key requirement, necessitating robust font management.

*   **Font Declaration (`theme.yaml`):**
    *   Users will declare custom fonts in the `theme.yaml` file, as shown in the `Style Configuration System` section. This involves providing a font family name and paths to the font files (TTF, OTF, WOFF, WOFF2).
    ```yaml
    # Example from theme.yaml
    fonts:
      - name: "Roboto"
        normal: "path/to/fonts/Roboto-Regular.ttf"
        bold: "path/to/fonts/Roboto-Bold.ttf"
        italic: "path/to/fonts/Roboto-Italic.ttf"
        bold_italic: "path/to/fonts/Roboto-BoldItalic.ttf"
      - name: "MyIconFont"
        normal: "path/to/fonts/MyIconFont.ttf"
    ```
*   **Path Resolution for Fonts:**
    *   Paths to font files specified in `theme.yaml` can be:
        *   Absolute.
        *   Relative to the `theme.yaml` file's location.
        *   Relative to a designated global font directory (if such a feature is added).
*   **CSS `@font-face` Generation:**
    *   The engine will dynamically generate the necessary CSS `@font-face` rules based on the font declarations in `theme.yaml`. These rules will be included in the CSS fed to WeasyPrint.
    *   Example generated CSS:
      ```css
      @font-face {
        font-family: "Roboto";
        src: url("path/to/fonts/Roboto-Regular.ttf") format("truetype");
        font-weight: normal;
        font-style: normal;
      }
      @font-face {
        font-family: "Roboto";
        src: url("path/to/fonts/Roboto-Bold.ttf") format("truetype");
        font-weight: bold;
        font-style: normal;
      }
      /* ... and so on for italic, bold-italic */
      ```
*   **Font Usage in CSS:**
    *   Users will then reference these fonts in their `theme.yaml` style definitions or custom CSS files using the `font-family` property.
    ```css
    /* In a user's custom CSS file or generated from theme.yaml styles */
    h1 {
      font-family: "Roboto", sans-serif;
    }
    .icon {
      font-family: "MyIconFont";
    }
    ```
*   **Embedding:** WeasyPrint handles the embedding of the required fonts (or their subsets) into the final PDF document, ensuring that the PDF looks the same on systems where the fonts are not installed. This is a standard feature of WeasyPrint when fonts are correctly referenced via `@font-face`.

*   **Fallback Fonts:** The `default_font` in `theme.yaml` and individual font family declarations should encourage specifying fallback fonts (e.g., `font-family: ["CustomFont", "Arial", "sans-serif"]`) to gracefully handle cases where a custom font might fail to load or doesn't contain required glyphs.

**5.3. Other Assets**

*   **CSS Files:** As detailed in the Style Configuration System, paths to CSS files are specified in `theme.yaml`. These are resolved relative to the `theme.yaml` location or an assets directory.
*   **Jinja2 Templates:** Paths to custom component templates (`.html`) are specified in `theme.yaml` and resolved relative to the `theme.yaml` or a designated templates directory.

By clearly defining how assets are declared and located, the engine can reliably incorporate them into the PDF generation process, ensuring that the final documents are self-contained and visually consistent.

## 6. Example Mappings: Markdown to PDF

This section provides concrete examples of how Markdown input, combined with style configurations from `theme.yaml` and custom CSS, would translate into specific visual elements in the final PDF, drawing inspiration from "Magic_Kingdom_Itinerary_2025.pdf".

**Example 1: "DICA MÁGICA" Box (Custom Component)**

This example aims to replicate a styled callout box with an icon and title.

*   **A. Markdown Input (`document.md`):**
    ```markdown
    ::: tip_box icon="lightbulb" title="DICA MÁGICA"
    Aproveite o Rider Switch (Troca de Criança) se estiver com crianças pequenas que não atingem a altura mínima para certas atrações. Um adulto pode esperar com a criança enquanto o outro vai na atração, e depois eles trocam sem precisar pegar a fila novamente!
    :::
    ```

*   **B. Relevant `theme.yaml` Configuration:**
    ```yaml
    # theme.yaml (partial)

    fonts:
      - name: "AwesomeFontIcons"
        normal: "assets/fonts/awesomefonticons.ttf" # Path to an icon font
      - name: "Poppins"
        normal: "assets/fonts/Poppins-Regular.ttf"
        bold: "assets/fonts/Poppins-Bold.ttf"

    stylesheets:
      - "css/custom-styles.css"

    custom_components:
      tip_box:
        template: "templates/blocks/tip_box.html" # Jinja2 template for this component
        default_icon: "info-circle" # Default if no icon is specified
    ```

*   **C. Jinja2 Template (`templates/blocks/tip_box.html`):**
    ```html+jinja
    {# templates/blocks/tip_box.html #}
    <div class="block-title">
      {% if icon %}
      <span class="icon icon-font icon-{{ icon }}" aria-hidden="true"></span>
      {% endif %}
      {{ title }}
    </div>
    <div class="block-content">
      {{ content | markdown_to_html }} {# Assumes 'content' is raw Markdown passed to template #}
    </div>
    ```
    *(Note: `markdown_to_html` would be a custom filter or function available in Jinja to process the inner Markdown content of the block).*

*   **D. CSS Snippet (`css/custom-styles.css`):**
    ```css
    /* css/custom-styles.css */
    @font-face {
      font-family: 'AwesomeFontIcons';
      src: url('../assets/fonts/awesomefonticons.ttf') format('truetype');
    }
    @font-face {
      font-family: 'Poppins';
      src: url('../assets/fonts/Poppins-Regular.ttf') format('truetype');
      font-weight: normal;
    }
    @font-face {
      font-family: 'Poppins';
      src: url('../assets/fonts/Poppins-Bold.ttf') format('truetype');
      font-weight: bold;
    }

    .custom-block.tip-box {
      background-color: #E0F7FA; /* Light cyan background */
      border-left: 6px solid #00BCD4; /* Cyan border */
      padding: 15px 20px;
      margin: 20px 0;
      border-radius: 4px;
    }

    .custom-block.tip-box .block-title {
      font-family: "Poppins", sans-serif;
      font-weight: bold;
      font-size: 1.2em;
      color: #00796B; /* Darker cyan text */
      margin-bottom: 10px;
    }

    .custom-block.tip_box .block-title .icon-font {
      font-family: "AwesomeFontIcons"; /* Using the icon font */
      margin-right: 10px;
      color: #0097A7; /* Icon color */
    }
    /* Assuming icon-lightbulb class in the font provides the lightbulb icon */
    .icon-lightbulb::before { content: "\f0eb"; } /* Example Unicode for FontAwesome lightbulb */

    .custom-block.tip-box .block-content {
      font-family: "Poppins", sans-serif;
      font-size: 0.95em;
      line-height: 1.6;
      color: #004D40; /* Dark teal text */
    }
    ```

*   **E. Resulting PDF Appearance:**
    The PDF would display a rectangular box with a light cyan background and a distinct solid cyan left border.
    The title "DICA MÁGICA" would appear at the top, in a bold, slightly larger "Poppins" font, colored dark cyan, preceded by a lightbulb icon (rendered via the icon font).
    The content text below the title would be in a regular "Poppins" font, with good line spacing, in a dark teal color. The overall look would be clean, informative, and visually distinct, similar to the callout boxes in the reference PDF.

**Example 2: Numbered List Item with Custom Visual Marker**

This example aims to replicate the large, styled numbers next to list items, as seen in parts of the "Magic_Kingdom_Itinerary_2025.pdf".

*   **A. Markdown Input (`document.md`):**
    ```markdown
    1.  **Chegue Cedinho!** Planeje estar no portão do Magic Kingdom pelo menos 45 minutos antes da abertura oficial.
    2.  **Primeira Parada: Fantasyland.** Vá direto para Peter Pan's Flight ou Seven Dwarfs Mine Train, que são as filas que crescem mais rápido.
    ```
    *(Standard Markdown ordered list)*

*   **B. Relevant `theme.yaml` Configuration:**
    ```yaml
    # theme.yaml (partial)
    stylesheets:
      - "css/custom-styles.css"

    styles:
      ol:
        list_style_type: "none" # Disable default browser numbering
        padding_left: "0" # Reset padding
      li:
        margin_bottom: "15px"
    ```

*   **C. CSS Snippet (`css/custom-styles.css`):**
    ```css
    /* css/custom-styles.css */
    ol {
      counter-reset: styled-list-counter; /* Initialize a custom counter */
      list-style-type: none;
      padding-left: 0;
    }

    ol > li {
      position: relative; /* For positioning the custom number */
      padding-left: 60px; /* Space for the custom number */
      margin-bottom: 15px; /* Space between list items */
      font-family: "Poppins", sans-serif; /* Assuming Poppins from previous example */
      line-height: 1.5;
    }

    ol > li::before {
      counter-increment: styled-list-counter; /* Increment the counter */
      content: counter(styled-list-counter); /* Display the counter value */
      position: absolute;
      left: 0;
      top: -5px; /* Adjust vertical alignment */
      font-family: "Poppins", sans-serif; /* Or a different display font */
      font-size: 3em; /* Large number size */
      font-weight: bold;
      color: #FF6F00; /* Orange color for the number, like in the example */
      line-height: 1;
      /* Optional: Add a circle or other background shape */
      /* background-color: #FFF; */
      /* border: 2px solid #FF9800; */
      /* border-radius: 50%; */
      /* width: 45px; */
      /* height: 45px; */
      /* text-align: center; */
      /* display: inline-block; */
    }

    ol > li strong { /* Styling for bold text within the list item, like "Chegue Cedinho!" */
      font-weight: bold;
      color: #333; /* Or another thematic color */
    }
    ```

*   **D. Resulting PDF Appearance:**
    Each list item would *not* have the standard "1.", "2." numbering. Instead, to the left of the text, there would be a large, orange, bold number (e.g., "1", "2"). The text of the list item ("Chegue Cedinho!...") would be aligned next to this large custom number. The strong text within the list item would be bold. This styling provides a much more visually engaging list than standard Markdown output.

**Example 3: Page Header**

This example shows how a page header, like "4 | DIA 1 | Magic Kingdom", could be achieved.

*   **A. Markdown Input (`document.md`):**
    *(No direct Markdown input for headers/footers; this is defined globally or per section via configuration).*
    Assume the document has a way to define `section_title` metadata, perhaps from the frontmatter of the Markdown file or based on the current H1.

*   **B. Relevant `theme.yaml` Configuration:**
    ```yaml
    # theme.yaml (partial)
    page_setup:
      default_font:
        family: ["Open Sans", "Arial", "sans-serif"]
      # ... other page setup ...

    page_headers:
      default: # Applies to most pages
        left_content: "" # Example: "{current_date}"
        center_content: "{page_number} | {document_title} | {section_title}"
        right_content: "" # Example: "Version 1.0"
        font_family: ["Open Sans", "sans-serif"]
        font_size: "9pt"
        color: "#555555"
        line_separator: "true" # Draw a line below header
        line_color: "#aaaaaa"
    ```
    *(The engine would need to make `document_title` (e.g., from metadata) and `section_title` (e.g., current H1) available as variables for header/footer content).*

*   **C. CSS Snippet (Generated by Engine based on `theme.yaml`):**
    ```css
    /* CSS Generated by the engine for WeasyPrint */
    @page {
      /* ... other @page rules like margin, size ... */

      @top-center {
        content: counter(page) " | " string(document_title) " | " string(section_title_var);
        font-family: "Open Sans", sans-serif;
        font-size: 9pt;
        color: #555555;
        border-bottom: 1px solid #aaaaaa; /* For line_separator */
        padding-bottom: 5px; /* Space between text and line */
        vertical-align: bottom; /* Align text to the bottom of the header box */
      }
    }

    /* To get section titles into the header, a running element might be used. */
    /* The engine would convert H1s (or other designated section titles) to also use this: */
    h1 {
      string-set: section_title_var content(text); /* Capture H1 text into section_title_var */
      /* ... other h1 styles ... */
    }
    ```
    *(Note: `string(section_title_var)` is a CSS Paged Media feature. The engine would need to intelligently capture the current section title, perhaps from the most recent H1 heading, and make it available.)*

*   **D. Resulting PDF Appearance:**
    At the top center of each page (or as configured), the PDF would display text like "4 | My Itinerary | Magic Kingdom". This text would be in a 9pt "Open Sans" font, colored grey. A thin grey line would appear below this header text, separating it from the main page content. The page number would update automatically. The "My Itinerary" (document title) and "Magic Kingdom" (section title) would be dynamically inserted based on document metadata and content.

These examples illustrate how the combination of Markdown extensions, a flexible `theme.yaml`, Jinja2 templating (for custom components), and targeted CSS can achieve the sophisticated and customized document appearance seen in the "Magic_Kingdom_Itinerary_2025.pdf" benchmark.

## 7. Conclusion

This design document proposes a robust and flexible architecture for a Python-based Markdown-to-PDF engine. By leveraging the strengths of the `python-markdown` library for extensible parsing, `Jinja2` for powerful HTML templating, and `WeasyPrint` for high-fidelity HTML/CSS to PDF rendering, the engine is well-equipped to meet the project's core objectives.

The defined Markdown extension syntax for custom components, coupled with the detailed style configuration system (combining `theme.yaml` for structure and external CSS for intricate styling), provides the necessary tools for users to create PDFs that closely emulate the visual richness and custom elements found in the "Magic_Kingdom_Itinerary_2025.pdf" example. The strategies for asset handling ensure that images and custom fonts can be seamlessly integrated.

The example mappings illustrate the practical application of these systems, demonstrating a clear path from Markdown input to a polished PDF output.

Potential next steps include:
*   Developing a Proof-of-Concept (PoC) focusing on:
    *   A basic `python-markdown` extension for one custom component type.
    *   A minimal `theme.yaml` parser.
    *   Integration with WeasyPrint to generate a simple PDF with custom styling.
*   Refining the `theme.yaml` specification based on PoC experiences.
*   Developing a core set of Jinja2 templates for common custom components.

This design provides a solid foundation for building a configurable and powerful PDF generation engine that can transform simple Markdown into beautiful, professional-quality documents.
