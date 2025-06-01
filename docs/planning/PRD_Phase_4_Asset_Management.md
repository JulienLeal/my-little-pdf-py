# PRD: Phase 4 - Asset Management System

**Document Status**: Draft  
**Phase**: 4 - Asset Management  
**Priority**: 🔴 High  
**Dependencies**: Phase 3 (YAML Configuration System) ✅ Complete  
**Estimated Duration**: 2-3 weeks  
**Total Estimated Hours**: 24 hours  

---

## 1. Executive Summary

### 1.1 Overview
Phase 4 implements a comprehensive asset management system that handles images, fonts, and other static resources used in PDF documents. This system ensures proper path resolution, asset copying, and integration with the existing theme configuration and component systems.

### 1.2 Goals
- **Primary**: Enable robust handling of images and fonts in PDF documents
- **Secondary**: Provide asset path resolution and copying mechanisms
- **Tertiary**: Integrate assets seamlessly with the theme and component systems

### 1.3 Success Metrics
- ✅ Images display correctly in generated PDFs regardless of source location
- ✅ Custom fonts load reliably from theme configurations
- ✅ Asset path resolution works across different directory structures
- ✅ Asset copying mechanism handles large files efficiently
- ✅ Integration with existing component and theme systems

---

## 2. Requirements Analysis

### 2.1 Functional Requirements

#### FR-4.1.1: Image Handling
- **Must Have**: Support common image formats (PNG, JPEG, GIF, SVG)
- **Must Have**: Resolve relative and absolute image paths
- **Must Have**: Handle image references in Markdown and components
- **Should Have**: Image optimization for PDF embedding
- **Could Have**: Image caching mechanism

#### FR-4.1.2: Font Management
- **Must Have**: Load custom fonts from theme configuration
- **Must Have**: Support multiple font formats (TTF, OTF, WOFF, WOFF2)
- **Must Have**: Generate @font-face CSS declarations
- **Should Have**: Font fallback mechanisms
- **Could Have**: Font subsetting for smaller PDFs

#### FR-4.1.3: Asset Path Resolution
- **Must Have**: Resolve paths relative to Markdown source file
- **Must Have**: Resolve paths relative to theme configuration file
- **Must Have**: Support absolute paths and URLs
- **Should Have**: Asset directory scanning and indexing
- **Could Have**: Asset validation and integrity checking

#### FR-4.1.4: Asset Pipeline Integration
- **Must Have**: Integrate with template system for component assets
- **Must Have**: Copy assets to temporary directory for PDF generation
- **Should Have**: Asset cleanup after PDF generation
- **Could Have**: Asset preprocessing and optimization

### 2.2 Non-Functional Requirements

#### NFR-4.1.1: Performance
- Asset resolution should complete in <50ms per asset
- Asset copying should handle files up to 50MB
- Memory usage should be optimized for large numbers of assets

#### NFR-4.1.2: Reliability
- Missing assets should fail gracefully with clear error messages
- Asset copying should be atomic (all or nothing)
- Path resolution should be platform-independent

#### NFR-4.1.3: Usability
- Asset paths should work intuitively (relative to source files)
- Error messages should indicate which assets are missing
- Asset directory structure should be flexible

#### NFR-4.1.4: Maintainability
- Asset management should be modular and extensible
- Support for new asset types should be easy to add
- Code should be well-tested with >90% coverage

---

## 3. Technical Specification

### 3.1 Asset Management Architecture

```
src/md_to_pdf/assets/
├── __init__.py
├── manager.py         # Main asset manager class
├── resolvers.py       # Path resolution utilities
├── processors.py      # Asset processing and optimization
├── fonts.py          # Font-specific handling
├── images.py         # Image-specific handling
└── exceptions.py     # Asset-specific exceptions
```

### 3.2 Key Classes

```python
@dataclass
class AssetInfo:
    """Information about a resolved asset."""
    original_path: str
    resolved_path: Path
    asset_type: str
    size: int
    last_modified: datetime

class AssetManager:
    """Central asset management system."""
    
    def __init__(self, base_paths: List[Path] = None):
        self.base_paths = base_paths or []
        self.asset_cache: Dict[str, AssetInfo] = {}
    
    def resolve_asset(self, asset_path: str, context_path: Path = None) -> AssetInfo
    def copy_assets_to_temp(self, temp_dir: Path) -> Dict[str, str]
    def cleanup_temp_assets(self, temp_dir: Path) -> None

class FontManager:
    """Specialized font asset management."""
    
    def load_fonts_from_theme(self, theme_config: ThemeConfig) -> List[FontAsset]
    def generate_font_face_css(self, fonts: List[FontAsset]) -> str
    def validate_font_files(self, fonts: List[FontAsset]) -> List[str]

class ImageResolver:
    """Image path resolution and processing."""
    
    def resolve_image_path(self, image_path: str, context_path: Path) -> Path
    def process_image_for_pdf(self, image_path: Path) -> ProcessedImage
    def update_html_image_refs(self, html: str, asset_map: Dict[str, str]) -> str
```

### 3.3 Asset Resolution Strategy

1. **Markdown Context**: Resolve relative to Markdown file location
2. **Theme Context**: Resolve relative to theme configuration file
3. **Template Context**: Resolve relative to template file
4. **Absolute Paths**: Use as-is if they exist
5. **Asset Directories**: Search in configured asset directories
6. **Fallback**: Try common locations (assets/, images/, fonts/)

---

## 4. User Stories

### 4.1 Primary User Stories

**US-4.1.1: Image Embedding**
> As a **content creator**, I want to **include images in my Markdown documents** so that **they appear correctly in the generated PDF**.

*Acceptance Criteria:*
- Can reference images with relative paths (`![alt](images/photo.jpg)`)
- Can reference images with absolute paths
- Images display correctly regardless of where PDF is generated
- Error messages when images are missing

**US-4.1.2: Custom Font Usage**
> As a **designer**, I want to **use custom fonts from my theme configuration** so that **my PDFs have the correct typography**.

*Acceptance Criteria:*
- Custom fonts declared in theme.yaml load correctly
- Font files can be in different directories
- Fallback fonts work when custom fonts fail
- Font loading errors are reported clearly

**US-4.1.3: Component Assets**
> As a **template creator**, I want to **include assets in my custom components** so that **components can have icons, images, and styling**.

*Acceptance Criteria:*
- Component templates can reference images and fonts
- Asset paths resolve relative to template location
- Components work when used in different documents
- Asset conflicts between components are avoided

### 4.2 Secondary User Stories

**US-4.1.4: Asset Organization**
> As a **project maintainer**, I want to **organize assets in logical directories** so that **projects remain maintainable**.

*Acceptance Criteria:*
- Can organize assets in subdirectories
- Asset resolution searches multiple directories
- Directory structure is flexible and configurable
- Asset discovery works automatically

**US-4.1.5: Error Handling**
> As a **developer**, I want **clear error messages for missing assets** so that **I can quickly fix asset issues**.

*Acceptance Criteria:*
- Missing images report exact file paths searched
- Missing fonts indicate which declaration failed
- Asset errors don't crash PDF generation
- Suggestions provided for common mistakes

---

## 5. Implementation Tasks

### 5.1 Sprint Breakdown

#### Task 4.1.1: Create Asset Management Foundation (6h)
**Dependencies**: Phase 3 complete ✅  
**Deliverables**:
- `src/md_to_pdf/assets/` package structure
- `AssetManager` class with basic functionality
- Asset resolution algorithms
- Unit tests for core functionality

#### Task 4.1.2: Image Handling Implementation (6h)
**Dependencies**: Task 4.1.1 complete  
**Deliverables**:
- `ImageResolver` class for image path resolution
- Image format detection and validation
- HTML image reference updating
- Image embedding tests

#### Task 4.1.3: Font Management Enhancement (6h)
**Dependencies**: Task 4.1.2 complete  
**Deliverables**:
- Enhanced `FontManager` class
- Font file validation
- Improved @font-face CSS generation
- Font fallback mechanisms

#### Task 4.1.4: Asset Pipeline Integration (6h)
**Dependencies**: Task 4.1.3 complete  
**Deliverables**:
- Integration with existing PDF generation pipeline
- Asset copying to temporary directories
- Component asset handling
- Cleanup mechanisms

### 5.2 Testing Requirements
- Unit tests for all asset classes
- Integration tests with PDF generation
- Error handling tests for missing assets
- Performance tests with large numbers of assets
- Cross-platform path resolution tests

---

## 6. Risk Assessment

### 6.1 Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Large asset files impact performance | Medium | Medium | Implement asset size limits and streaming |
| Path resolution fails on different platforms | Low | High | Comprehensive cross-platform testing |
| Font loading issues with WeasyPrint | Medium | Medium | Robust fallback mechanisms |
| Asset copying failures | Low | High | Atomic copying with rollback |

### 6.2 User Experience Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Complex asset directory structures confuse users | Medium | Medium | Clear documentation and examples |
| Asset errors block PDF generation | High | High | Graceful fallbacks and helpful errors |
| Asset organization becomes unwieldy | Medium | Low | Best practices guide |

---

## 7. Success Criteria

### 7.1 Phase Completion Criteria
- [ ] Complete asset management system handles images and fonts
- [ ] Asset path resolution works reliably across platforms
- [ ] Integration with existing theme and component systems
- [ ] Comprehensive error handling and user feedback
- [ ] Performance meets requirements for typical use cases
- [ ] Documentation includes usage examples

### 7.2 Quality Gates
- [ ] >90% test coverage on asset management modules
- [ ] All asset types (images, fonts) work in PDF generation
- [ ] Performance: Asset resolution <50ms per asset
- [ ] Zero critical security vulnerabilities
- [ ] Documentation review completed

### 7.3 User Acceptance Criteria
- [ ] Users can include images in documents intuitively
- [ ] Custom fonts work reliably from theme configurations
- [ ] Asset errors provide actionable feedback
- [ ] Asset management works on Windows, macOS, Linux

---

## 8. Next Phase Preview

### 8.1 Phase 5: PDF Generation Enhancement
Following Phase 4, we'll implement:
- Advanced PDF features (TOC, bookmarks, metadata)
- Enhanced styling and layout options
- Performance optimizations
- Print-specific optimizations

### 8.2 Key Dependencies
- Asset management system (this phase)
- Theme configuration system (Phase 3 ✅)
- Component system (Phase 2 ✅)

---

## 9. Appendix

### 9.1 Asset Types Supported

**Images:**
- PNG, JPEG, GIF (raster formats)
- SVG (vector format)
- WebP (modern format)

**Fonts:**
- TTF (TrueType)
- OTF (OpenType)
- WOFF/WOFF2 (Web fonts)

**Other Assets:**
- CSS files (from theme)
- Template files (for components)

### 9.2 Directory Structure Examples

```
project/
├── content/
│   ├── document.md
│   └── images/
│       ├── diagram.png
│       └── photo.jpg
├── themes/
│   ├── corporate.yaml
│   └── fonts/
│       ├── corporate-regular.ttf
│       └── corporate-bold.ttf
└── templates/
    ├── tip_box.html
    └── assets/
        └── icons/
            └── lightbulb.svg
```

### 9.3 Integration Points
- **PDF Generation**: Assets copied to temp directory for WeasyPrint
- **Theme System**: Font assets loaded from theme configuration
- **Component System**: Component templates can reference assets
- **HTML Processing**: Image references updated with resolved paths

---

*This PRD will be updated as implementation progresses and requirements are refined.* 