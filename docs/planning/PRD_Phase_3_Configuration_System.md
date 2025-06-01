# PRD: Phase 3.1 - YAML Configuration System

**Document Status**: Draft  
**Phase**: 3.1 - YAML Configuration Parser  
**Priority**: 🔴 High  
**Dependencies**: Phase 2 (Custom Component System) ✅ Complete  
**Estimated Duration**: 1-2 weeks  
**Total Estimated Hours**: 16 hours  

---

## 1. Executive Summary

### 1.1 Overview
Phase 3.1 implements a comprehensive YAML-based configuration system that allows users to control the visual appearance, layout, and styling of their PDF documents through a human-readable `theme.yaml` file. This system bridges the gap between the custom component framework (Phase 2) and the final PDF output by providing flexible, non-technical configuration options.

### 1.2 Goals
- **Primary**: Enable users to customize PDF appearance without writing CSS
- **Secondary**: Provide a structured, validated configuration schema
- **Tertiary**: Establish foundation for advanced styling features

### 1.3 Success Metrics
- ✅ Complete `theme.yaml` schema supports all design document requirements
- ✅ YAML validation prevents invalid configurations
- ✅ Default configurations provide good out-of-box experience
- ✅ Configuration system integrates seamlessly with existing components
- ✅ Sample themes demonstrate system capabilities

---

## 2. Requirements Analysis

### 2.1 Functional Requirements

#### FR-3.1.1: Core Schema Design
- **Must Have**: Define complete `theme.yaml` schema covering:
  - Page setup (size, orientation, margins)
  - Font declarations with multiple weights/styles
  - CSS file references
  - Standard Markdown element styling
  - Custom component configuration
  - Page headers/footers

#### FR-3.1.2: Configuration Parser
- **Must Have**: Python module to parse and validate YAML
- **Must Have**: Type-safe configuration classes with defaults
- **Should Have**: Helpful error messages for invalid configurations
- **Could Have**: Configuration inheritance/merging

#### FR-3.1.3: Validation System
- **Must Have**: Schema validation using JSON Schema or equivalent
- **Must Have**: File path validation (fonts, CSS, templates exist)
- **Should Have**: Warning system for deprecated options
- **Could Have**: Configuration linting with suggestions

#### FR-3.1.4: Default Configurations
- **Must Have**: Sensible defaults for all configuration options
- **Must Have**: Fallback fonts for cross-platform compatibility
- **Should Have**: Multiple preset themes (minimal, corporate, academic)

#### FR-3.1.5: Sample Configurations
- **Must Have**: Example `theme.yaml` files demonstrating features
- **Should Have**: Configuration for recreating Magic Kingdom itinerary style
- **Could Have**: Theme gallery with screenshots

### 2.2 Non-Functional Requirements

#### NFR-3.1.1: Performance
- Configuration parsing should complete in <100ms for typical files
- Memory usage should be minimal (configuration objects <1MB)

#### NFR-3.1.2: Usability
- YAML syntax should be intuitive for non-developers
- Error messages should be actionable and clear
- Documentation should include examples for all options

#### NFR-3.1.3: Reliability
- Invalid configurations should fail gracefully with clear errors
- Partial configurations should work with sensible defaults
- File path errors should be caught early

#### NFR-3.1.4: Maintainability
- Schema should be easy to extend for future features
- Configuration classes should be well-typed
- Test coverage should be >90%

---

## 3. Technical Specification

### 3.1 Schema Structure

Based on the design document, the `theme.yaml` schema includes:

```yaml
# Core structure from design document
page_setup:
  size: "A4"
  orientation: "portrait" 
  margin: { top: "2cm", bottom: "2cm", left: "1.5cm", right: "1.5cm" }
  default_font: { family: ["Open Sans", "Arial", "sans-serif"], size: "11pt", color: "#333333" }

fonts:
  - name: "Roboto"
    normal: "path/to/fonts/Roboto-Regular.ttf"
    bold: "path/to/fonts/Roboto-Bold.ttf"
    italic: "path/to/fonts/Roboto-Italic.ttf"
    bold_italic: "path/to/fonts/Roboto-BoldItalic.ttf"

stylesheets:
  - "css/base.css"
  - "css/custom-components.css"

styles:
  h1: { font_family: ["Roboto", "sans-serif"], font_size: "28pt", color: "#1a5276" }
  p: { line_height: "1.6", margin_bottom: "12px" }

custom_components:
  tip_box:
    template: "templates/tip_box.html"
    default_icon: "lightbulb"

page_headers:
  default:
    left: "{page_number} | {section_title}"
    center: ""
    right: "My Document Title"
    font_family: ["Open Sans", "sans-serif"]
    font_size: "9pt"
    color: "#777777"

page_footers:
  default:
    left: "© My Company {year}"
    center: ""
    right: "Page {page_number} of {total_pages}"
```

### 3.2 Implementation Architecture

```
src/md_to_pdf/config/
├── __init__.py
├── schema.py          # Configuration classes & types
├── parser.py          # YAML parsing & validation
├── defaults.py        # Default configuration values
├── validators.py      # Custom validation functions
└── exceptions.py      # Configuration-specific exceptions

schemas/
├── theme_schema.json  # JSON Schema for validation
└── examples/
    ├── minimal.yaml
    ├── corporate.yaml
    └── magic_kingdom.yaml
```

### 3.3 Key Classes

```python
@dataclass
class PageSetup:
    size: str = "A4"
    orientation: str = "portrait"
    margin: Margin = field(default_factory=Margin)
    default_font: Font = field(default_factory=Font)

@dataclass
class FontDeclaration:
    name: str
    normal: Optional[str] = None
    bold: Optional[str] = None
    italic: Optional[str] = None
    bold_italic: Optional[str] = None

@dataclass
class ThemeConfig:
    page_setup: PageSetup = field(default_factory=PageSetup)
    fonts: List[FontDeclaration] = field(default_factory=list)
    stylesheets: List[str] = field(default_factory=list)
    styles: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    custom_components: Dict[str, ComponentConfig] = field(default_factory=dict)
    page_headers: Dict[str, HeaderFooterConfig] = field(default_factory=dict)
    page_footers: Dict[str, HeaderFooterConfig] = field(default_factory=dict)
```

---

## 4. User Stories

### 4.1 Primary User Stories

**US-3.1.1: Basic Theme Configuration**
> As a **content creator**, I want to **configure basic page settings like size and margins in YAML** so that **I can control the layout without learning CSS**.

*Acceptance Criteria:*
- Can set page size (A4, Letter, Legal, custom)
- Can set orientation (portrait/landscape)
- Can set margins for all sides
- Configuration validates and provides helpful errors

**US-3.1.2: Custom Font Loading**
> As a **designer**, I want to **declare custom fonts in my theme** so that **my PDFs use my brand typography**.

*Acceptance Criteria:*
- Can specify font family name and file paths
- Supports multiple font weights (normal, bold, italic, bold-italic)
- Validates font files exist and are readable
- Generates appropriate CSS @font-face rules

**US-3.1.3: Element Styling**
> As a **document author**, I want to **style standard Markdown elements via YAML** so that **I can customize appearance without CSS knowledge**.

*Acceptance Criteria:*
- Can style h1-h6, p, ul, ol, blockquote, etc.
- Supports common properties (font, size, color, spacing)
- Provides intelligent defaults for unspecified elements
- Validates property values

**US-3.1.4: Component Configuration**
> As a **template user**, I want to **configure my custom components** so that **they match my document theme**.

*Acceptance Criteria:*
- Can specify template paths for custom components
- Can set default attributes (icons, colors, etc.)
- Configuration integrates with existing component system
- Validates template files exist

### 4.2 Secondary User Stories

**US-3.1.5: Header/Footer Setup**
> As a **professional document creator**, I want to **configure page headers and footers** so that **my PDFs include consistent branding and navigation**.

*Acceptance Criteria:*
- Can set content for left/center/right positions
- Supports dynamic variables ({page_number}, {total_pages}, etc.)
- Can style headers/footers independently
- Can enable/disable separator lines

**US-3.1.6: Configuration Validation**
> As a **developer**, I want **clear validation errors** so that **I can quickly fix configuration issues**.

*Acceptance Criteria:*
- Validates YAML syntax and structure
- Checks file paths exist for fonts/CSS/templates
- Provides line numbers and specific error descriptions
- Suggests corrections for common mistakes

---

## 5. Implementation Tasks

### 5.1 Sprint Breakdown

#### Task 3.1.1: Design `theme.yaml` schema ⏳ (4h)
**Current Status**: In Progress  
**Dependencies**: Phase 2 complete ✅  
**Deliverables**:
- Complete YAML schema definition
- JSON Schema file for validation
- Documentation of all configuration options

#### Task 3.1.2: Create `src/md_to_pdf/config.py` (3h)
**Dependencies**: Schema design complete  
**Deliverables**:
- Configuration dataclasses with type hints
- Parser function for YAML files
- Integration with existing core classes

#### Task 3.1.3: Implement YAML validation (4h)
**Dependencies**: Config classes created  
**Deliverables**:
- JSON Schema validation
- Custom validation functions
- Comprehensive error messages

#### Task 3.1.4: Add default configuration fallbacks (3h)
**Dependencies**: Validation implemented  
**Deliverables**:
- Sensible default values for all options
- Fallback font stacks
- Minimal working configuration

#### Task 3.1.5: Create sample theme.yaml files (2h)
**Dependencies**: Defaults working  
**Deliverables**:
- Minimal example configuration
- Corporate/professional theme
- Magic Kingdom itinerary recreation theme

### 5.2 Testing Requirements
- Unit tests for all configuration classes
- Validation tests for schema compliance
- Error handling tests for malformed YAML
- Integration tests with existing component system
- Sample configuration tests

---

## 6. Risk Assessment

### 6.1 Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Complex YAML syntax confuses users | Medium | Medium | Provide clear examples and error messages |
| JSON Schema validation too strict | Low | Medium | Iterative testing with real configurations |
| Font path resolution cross-platform issues | Medium | High | Robust path handling and testing |
| Performance impact from validation | Low | Low | Optimize validation for typical file sizes |

### 6.2 User Experience Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Too many configuration options overwhelm users | Medium | Medium | Good defaults and progressive disclosure |
| Configuration errors block PDF generation | High | High | Graceful fallbacks and helpful messages |
| YAML syntax errors frustrate non-technical users | Medium | Medium | Clear documentation and examples |

---

## 7. Success Criteria

### 7.1 Phase Completion Criteria
- [ ] Complete `theme.yaml` schema covers all design requirements
- [ ] YAML parser with comprehensive validation
- [ ] Default configurations enable immediate usage
- [ ] Sample configurations demonstrate all features
- [ ] Integration tests pass with existing components
- [ ] Documentation includes usage examples

### 7.2 Quality Gates
- [ ] >90% test coverage on configuration module
- [ ] All sample configurations validate successfully
- [ ] Performance: Configuration loads in <100ms
- [ ] Zero critical security vulnerabilities
- [ ] Documentation review completed

### 7.3 User Acceptance Criteria
- [ ] Non-technical users can modify basic settings
- [ ] Configuration errors provide actionable feedback
- [ ] Sample themes produce expected PDF output
- [ ] Font loading works on Windows, macOS, Linux

---

## 8. Next Phase Preview

### 8.1 Phase 3.2: Style System Implementation
Following Phase 3.1, we'll implement:
- YAML→CSS conversion engine
- Standard Markdown element styling
- Custom component CSS generation
- Integration with WeasyPrint CSS pipeline

### 8.2 Key Dependencies
- Theme configuration schema (this phase)
- Valid sample configurations (this phase)
- Component template system (Phase 2 ✅)

---

## 9. Appendix

### 9.1 Schema Examples

**Minimal Configuration:**
```yaml
page_setup:
  size: "A4"
  margin: "2cm"

styles:
  h1:
    color: "#2c3e50"
    font_size: "24pt"
```

**Corporate Theme:**
```yaml
page_setup:
  size: "Letter"
  margin:
    top: "1in"
    bottom: "1in"
    left: "0.75in"
    right: "0.75in"

fonts:
  - name: "Inter"
    normal: "fonts/Inter-Regular.ttf"
    bold: "fonts/Inter-Bold.ttf"

stylesheets:
  - "themes/corporate/base.css"
  - "themes/corporate/components.css"

page_headers:
  default:
    right: "Company Confidential"
    font_size: "8pt"
    color: "#666"

page_footers:
  default:
    center: "Page {page_number} of {total_pages}"
    font_size: "8pt"
```

### 9.2 Integration Points
- **Component System**: Custom components reference templates and defaults
- **CSS Generation**: Styles section generates CSS rules
- **Asset Management**: Font and CSS file paths are resolved
- **PDF Generation**: Page setup controls WeasyPrint @page rules

---

*This PRD will be updated as implementation progresses and requirements are refined.* 