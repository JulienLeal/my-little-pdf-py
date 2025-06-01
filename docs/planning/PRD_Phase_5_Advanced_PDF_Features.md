# PRD: Phase 5.1 - Advanced PDF Features

**Document Version**: 1.0  
**Date**: January 2025  
**Phase**: 5.1 - Advanced PDF Features  
**Priority**: High  
**Dependencies**: Phase 3 (Configuration System) ✅, Phase 4 (Asset Management) ✅

---

## 1. Executive Summary

### 1.1 Project Overview
Phase 5.1 focuses on implementing advanced PDF features that make generated documents production-ready for professional use. This includes dynamic content in headers/footers, sophisticated page numbering systems, and CSS Paged Media variable support.

### 1.2 Business Objectives
- **Professional Output**: Enable generation of business-quality PDFs with dynamic headers/footers
- **Navigation Enhancement**: Implement comprehensive page numbering and section tracking
- **Content Awareness**: Support dynamic content that responds to document structure
- **Standards Compliance**: Full CSS Paged Media specification support

### 1.3 Success Criteria
- ✅ Dynamic headers/footers with variable substitution working
- ✅ Page numbering system with counters and total pages
- ✅ CSS Paged Media variables (string(), counter()) functional
- ✅ Multi-section documents with different header/footer styles
- ✅ Table of contents generation (stretch goal)

---

## 2. Requirements Specification

### 2.1 Functional Requirements

#### FR-5.1.1: Dynamic Header/Footer Content
- **Must Have**: Variable substitution in header/footer text
  - `{page_number}` - Current page number
  - `{total_pages}` - Total number of pages  
  - `{section_title}` - Current section title (from H1)
  - `{document_title}` - Document title (from metadata or first H1)
  - `{date}` - Current date in configurable format
  - `{year}` - Current year
- **Should Have**: Support for custom variables from document metadata
- **Could Have**: Conditional content based on page position (first/last page)

#### FR-5.1.2: CSS Paged Media Variable Support
- **Must Have**: Implementation of CSS `string()` function for running headers
- **Must Have**: Implementation of CSS `counter()` functions for page numbering
- **Should Have**: Support for named counters for different numbering schemes
- **Could Have**: Support for `target-counter()` for cross-references

#### FR-5.1.3: Page Numbering System
- **Must Have**: Automatic page counter with start/reset capabilities
- **Must Have**: Different numbering formats (decimal, roman, alpha)
- **Should Have**: Section-based numbering (restart on chapters)
- **Could Have**: Custom numbering schemes and calculations

#### FR-5.1.4: Multi-Section Document Support
- **Must Have**: Different header/footer styles for different document sections
- **Should Have**: Named page configurations in theme.yaml
- **Could Have**: Automatic section detection from heading hierarchy

#### FR-5.1.5: Table of Contents Generation (Stretch)
- **Could Have**: Automatic TOC generation from heading structure
- **Could Have**: Clickable links to sections (if WeasyPrint supports)
- **Could Have**: Custom TOC styling via theme configuration

### 2.2 Non-Functional Requirements

#### NFR-5.1.1: Performance
- Header/footer processing should add <100ms to PDF generation time
- Variable substitution should handle documents up to 1000 pages efficiently

#### NFR-5.1.2: Compatibility
- Must work with existing WeasyPrint CSS Paged Media support
- Should be backward compatible with existing theme configurations
- Must integrate seamlessly with current CSS generation pipeline

#### NFR-5.1.3: Maintainability
- Clear separation between variable processing and CSS generation
- Extensible architecture for adding new variables/functions
- Comprehensive test coverage for all variable scenarios

---

## 3. Technical Specification

### 3.1 Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Theme Config  │───▶│  PageProcessor   │───▶│  CSS Generator  │
│  (headers/      │    │  - Variables     │    │  (enhanced)     │
│   footers)      │    │  - Counters      │    │                 │
└─────────────────┘    │  - Sections      │    └─────────────────┘
                       └──────────────────┘              │
                                 │                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Document      │───▶│  Variable        │    │   Enhanced CSS  │
│   Metadata      │    │  Resolver        │    │   with Paged    │
│                 │    │                  │    │   Media Rules   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### 3.2 Core Components

#### 3.2.1 PageProcessor Class
**File**: `src/md_to_pdf/page_processor.py`

```python
class PageProcessor:
    """Handles advanced page processing for PDF generation."""
    
    def __init__(self, theme_config: ThemeConfig):
        self.theme_config = theme_config
        self.variable_resolver = VariableResolver()
        self.section_tracker = SectionTracker()
    
    def process_headers_footers(self, html_content: str) -> str:
        """Process headers/footers with dynamic content."""
        
    def extract_document_metadata(self, html_content: str) -> Dict[str, Any]:
        """Extract metadata from HTML content."""
        
    def generate_paged_media_css(self) -> str:
        """Generate CSS Paged Media rules with variables."""
```

#### 3.2.2 VariableResolver Class
**File**: `src/md_to_pdf/page_processor.py`

```python
class VariableResolver:
    """Resolves variables in header/footer content."""
    
    def resolve_variables(self, 
                         template: str, 
                         context: Dict[str, Any]) -> str:
        """Replace variables in template with actual values."""
        
    def register_variable(self, name: str, resolver_func: Callable):
        """Register custom variable resolver."""
```

#### 3.2.3 SectionTracker Class
**File**: `src/md_to_pdf/page_processor.py`

```python
class SectionTracker:
    """Tracks document sections for header/footer context."""
    
    def extract_sections(self, html_content: str) -> List[Section]:
        """Extract section information from HTML."""
        
    def get_section_context(self, page_number: int) -> Dict[str, str]:
        """Get section context for a specific page."""
```

### 3.3 CSS Paged Media Integration

#### 3.3.1 Enhanced CSS Generation
The existing `CSSGenerator` class will be enhanced to support:

```css
/* Example generated CSS with variables */
@page {
    @top-center {
        content: string(section-title);
        font-family: "Inter", sans-serif;
        font-size: 9pt;
    }
    @bottom-right {
        content: "Page " counter(page) " of " counter(pages);
    }
}

h1 {
    string-set: section-title content();
}

/* Named page support */
@page :first {
    @top-center { content: none; }
}

@page chapter {
    @top-left { content: "Chapter " counter(chapter); }
    counter-increment: chapter;
}
```

#### 3.3.2 Variable Processing Pipeline

1. **HTML Analysis**: Extract sections, titles, and metadata
2. **Variable Context**: Build context dictionary with all available variables
3. **Template Processing**: Replace variables in header/footer templates
4. **CSS Generation**: Convert processed templates to CSS Paged Media rules
5. **Integration**: Combine with existing CSS generation pipeline

### 3.4 Theme Configuration Extensions

#### 3.4.1 Enhanced Header/Footer Configuration

```yaml
page_headers:
  default:
    left: "{section_title}"
    center: "{document_title}"
    right: "Page {page_number} of {total_pages}"
    font_family: ["Inter", "sans-serif"]
    font_size: "9pt"
    color: "#666666"
    line_separator: true
    
  first_page:
    left: ""
    center: "{document_title}"
    right: "{date}"
    
  chapter:
    left: "Chapter {chapter_number}"
    center: ""
    right: "{page_number}"

page_variables:
  date_format: "%B %Y"  # January 2025
  chapter_numbering: "roman"  # I, II, III, etc.
  section_numbering: "decimal"  # 1, 2, 3, etc.
```

#### 3.4.2 Document Metadata Support

```yaml
document:
  title: "My Document Title"
  author: "Author Name"
  subject: "Document Subject"
  keywords: ["pdf", "generation", "markdown"]
  custom_variables:
    company: "My Company"
    department: "Engineering"
```

---

## 4. Implementation Plan

### 4.1 Development Phases

#### Phase A: Core Variable System (8 hours)
1. **Create PageProcessor module** (2h)
   - Basic class structure and interfaces
   - Integration points with existing system
   
2. **Implement VariableResolver** (3h)
   - Variable substitution engine
   - Built-in variable providers (page, date, etc.)
   
3. **Basic HTML metadata extraction** (3h)
   - Document title extraction
   - Section title tracking

#### Phase B: CSS Paged Media Enhancement (6 hours)
1. **Enhance CSSGenerator** (3h)
   - Add support for string() and counter() functions
   - Named page configurations
   
2. **Page numbering system** (3h)
   - Automatic counter generation
   - Different numbering formats

#### Phase C: Advanced Features (8 hours)
1. **Section tracking** (4h)
   - Multi-section document support
   - Section-based header/footer switching
   
2. **Named page support** (2h)
   - First page, chapter pages, etc.
   
3. **Table of contents** (2h) - *Stretch goal*
   - Automatic TOC generation

#### Phase D: Testing & Integration (6 hours)
1. **Unit tests** (3h)
   - All variable resolution scenarios
   - CSS generation edge cases
   
2. **Integration tests** (2h)
   - End-to-end PDF generation
   - Multi-theme compatibility
   
3. **Documentation** (1h)
   - Update theme schema and examples

### 4.2 Testing Strategy

#### 4.2.1 Unit Tests
- **Variable Resolution**: All built-in variables work correctly
- **Template Processing**: Complex template strings processed accurately
- **CSS Generation**: Valid CSS Paged Media rules generated
- **Metadata Extraction**: Document metadata extracted correctly

#### 4.2.2 Integration Tests  
- **Single Page**: Headers/footers work on single-page documents
- **Multi Page**: Page numbering accurate across multiple pages
- **Multi Section**: Different headers/footers for different sections
- **Theme Compatibility**: Works with existing minimal/corporate themes

#### 4.2.3 Visual Tests
- **PDF Output**: Generated PDFs have correct headers/footers
- **Variable Values**: All variables display expected values
- **Formatting**: Header/footer styling matches theme configuration

---

## 5. Examples and Use Cases

### 5.1 Corporate Report
```yaml
page_headers:
  default:
    left: "Quarterly Report Q4 2024"
    center: ""
    right: "{date}"
    
page_footers:
  default:
    left: "© {company} {year}"
    center: ""
    right: "Page {page_number} of {total_pages}"
    
  first_page:
    left: ""
    center: ""
    right: ""
```

**Expected Output**: 
- Header: "Quarterly Report Q4 2024" (left), "January 2025" (right)
- Footer: "© My Company 2025" (left), "Page 1 of 15" (right)
- First page has no footer

### 5.2 Academic Paper
```yaml
page_headers:
  default:
    left: "{section_title}"
    center: ""
    right: "{document_title}"
    
page_footers:
  default:
    center: "{page_number}"
```

**Expected Output**:
- Header: "Introduction" (left), "Machine Learning in Healthcare" (right)
- Footer: "1" (center)

### 5.3 Multi-Chapter Book
```yaml
page_headers:
  chapter:
    left: "Chapter {chapter_number}: {section_title}"
    right: "{page_number}"
    
  appendix:
    left: "Appendix {appendix_letter}: {section_title}"
    right: "{page_number}"
```

**Expected Output**:
- Chapter pages: "Chapter 1: Getting Started" (left), "23" (right)
- Appendix pages: "Appendix A: References" (left), "156" (right)

---

## 6. Success Metrics

### 6.1 Functional Metrics
- ✅ All 6 built-in variables work correctly
- ✅ Page numbering accurate for documents up to 100 pages
- ✅ Section tracking works with nested headings (H1-H6)
- ✅ Named page configurations functional
- ✅ Generated CSS passes W3C validation

### 6.2 Performance Metrics
- Variable processing adds <100ms to PDF generation
- Memory usage increase <10MB for large documents
- No performance degradation for simple documents without variables

### 6.3 Quality Metrics
- Unit test coverage >90%
- Integration test coverage for all use cases
- No regressions in existing functionality
- Clean, maintainable code architecture

---

## 7. Risks and Mitigation

### 7.1 Technical Risks

#### Risk: WeasyPrint CSS Paged Media Limitations
- **Likelihood**: Medium
- **Impact**: High
- **Mitigation**: Research WeasyPrint capabilities early, implement fallbacks for unsupported features

#### Risk: Complex Variable Resolution Performance
- **Likelihood**: Low  
- **Impact**: Medium
- **Mitigation**: Implement caching for expensive operations, profile performance

#### Risk: CSS Generation Complexity
- **Likelihood**: Medium
- **Impact**: Medium
- **Mitigation**: Modular CSS generation, comprehensive unit tests

### 7.2 Integration Risks

#### Risk: Breaking Existing Theme Configurations
- **Likelihood**: Low
- **Impact**: High
- **Mitigation**: Extensive backward compatibility testing, gradual feature introduction

#### Risk: Performance Impact on Simple Documents
- **Likelihood**: Low
- **Impact**: Medium
- **Mitigation**: Lazy evaluation, conditional processing only when features are used

---

## 8. Dependencies and Assumptions

### 8.1 Technical Dependencies
- ✅ **Phase 3**: Theme configuration system (Complete)
- ✅ **Phase 4**: Asset management system (Complete)
- ✅ **WeasyPrint**: CSS Paged Media support
- **Python**: HTML parsing libraries (BeautifulSoup, lxml)

### 8.2 Assumptions
- WeasyPrint supports CSS `string()` and `counter()` functions
- Performance impact will be acceptable for target document sizes
- Users will primarily need the 6 built-in variables
- Theme configuration backward compatibility can be maintained

---

## 9. Timeline and Milestones

### 9.1 Development Timeline
- **Week 1**: Phase A - Core Variable System (8h)
- **Week 2**: Phase B - CSS Paged Media Enhancement (6h)  
- **Week 3**: Phase C - Advanced Features (8h)
- **Week 4**: Phase D - Testing & Integration (6h)

**Total Effort**: 28 hours over 4 weeks

### 9.2 Key Milestones
- **M1**: Basic variable substitution working
- **M2**: Page numbering system functional
- **M3**: Multi-section documents supported
- **M4**: Full test suite passing and integration complete

---

## 10. Post-Implementation

### 10.1 Documentation Updates
- Update theme schema documentation
- Add examples for all variable types
- Create troubleshooting guide for header/footer issues

### 10.2 Future Enhancements
- Custom JavaScript-like expressions in variables
- Advanced TOC generation with styling
- Cross-reference support with `target-counter()`
- Conditional content based on page ranges 