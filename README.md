# Markdown-to-PDF Engine

A configurable Python-based PDF generation engine that converts Markdown documents into visually appealing PDFs with custom components, styling, and layout control.

## Features

- Convert Markdown to beautiful PDFs
- Custom component system (tip boxes, callouts, etc.)
- YAML-based theme configuration
- Asset management (fonts, images)
- Professional layout control

## Installation

```bash
pip install md-to-pdf-engine
```

### Windows Setup (WeasyPrint Dependencies)

On Windows, WeasyPrint requires additional system dependencies. For detailed setup instructions:

1. **Quick Setup**: Run the automated helper script:
   ```powershell
   .\setup_windows_weasyprint.ps1
   ```

2. **Manual Setup**: Follow the step-by-step guide in [docs/setup/weasyprint/WEASYPRINT_WINDOWS_SETUP.md](docs/setup/weasyprint/WEASYPRINT_WINDOWS_SETUP.md)

3. **Test Installation**: Run the dependency test:
   ```bash
   python test_dependencies.py
   ```

## Quick Start

```bash
md2pdf input.md output.pdf --theme my-theme.yaml
```

For complete getting started guide, see [docs/setup/QUICK_START.md](docs/setup/QUICK_START.md).

## 📚 Documentation

Our documentation is organized for easy navigation:

- **[📖 Full Documentation](docs/)** - Complete documentation hub
- **[🚀 Quick Start](docs/setup/QUICK_START.md)** - Get up and running quickly
- **[🎨 Design Document](docs/design/DESIGN_DOCUMENT.md)** - System architecture and design
- **[📋 Implementation Plan](docs/planning/IMPLEMENTATION_PLAN.md)** - Development roadmap
- **[📈 Progress Updates](docs/progress/)** - Development milestones and achievements

## Development Status

This project is currently in active development. Key milestones:

- ✅ **WeasyPrint Setup** - Cross-platform PDF engine
- ✅ **Templating System** - Jinja2-based component rendering  
- ✅ **CSS Styling** - Modern, responsive component design
- ✅ **Test Organization** - Professional test structure
- 🔄 **Documentation Organization** - Improved documentation structure

See [docs/planning/TASKS.md](docs/planning/TASKS.md) for detailed task tracking.

## License

MIT License 