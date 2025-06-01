# PRD: Phase 3.1.4 - PDF Engine Integration

## Overview
Integrate the YAML configuration system with the existing PDF generation engine to enable theme-based document styling.

## Objectives
- Connect theme configuration to WeasyPrint CSS generation
- Enable dynamic font loading from theme configuration
- Apply style configurations to Markdown elements
- Support custom stylesheets and components

## Technical Requirements

### 1. CSS Generation from Theme Configuration
- Convert theme styles to CSS rules
- Handle font family stacks and fallbacks
- Generate CSS for all supported Markdown elements
- Support shorthand properties (margin, padding)

### 2. Font Integration
- Load custom fonts declared in theme configuration
- Register fonts with WeasyPrint
- Handle font file path resolution
- Provide fallback fonts when custom fonts fail

### 3. Stylesheet Integration
- Load external CSS files specified in theme
- Merge theme-generated CSS with external stylesheets
- Maintain proper CSS cascade order

### 4. Page Setup Integration
- Apply page size and orientation from theme
- Set page margins from theme configuration
- Configure default font settings

### 5. Header/Footer Integration
- Generate CSS for page headers and footers
- Support variable substitution in header/footer content
- Apply header/footer styling from theme

## Implementation Plan

### Step 1: Update WeasyPrint Engine
- Modify `weasyprint_engine.py` to accept theme configuration
- Add CSS generation methods
- Integrate font loading

### Step 2: CSS Generation Module
- Create `css_generator.py` for converting theme to CSS
- Implement style property conversion
- Handle CSS specificity and inheritance

### Step 3: Font Management
- Add font loading utilities
- Handle font registration with WeasyPrint
- Implement font fallback mechanisms

### Step 4: Integration Testing
- Test with all example theme configurations
- Verify CSS output quality
- Ensure proper error handling

## Success Criteria
- Theme configurations successfully generate valid CSS
- Custom fonts load and display correctly
- All style properties apply to generated PDFs
- External stylesheets integrate properly
- Headers and footers render with theme styling

## Dependencies
- Existing WeasyPrint engine
- YAML configuration system (Phase 3.1.1-3.1.3)
- Theme example configurations

## Estimated Time
2 hours

## Deliverables
- Updated `weasyprint_engine.py` with theme integration
- New `css_generator.py` module
- Font loading utilities
- Integration tests
- Documentation updates 