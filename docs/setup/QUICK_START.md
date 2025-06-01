# Quick Start Guide: Building the Markdown-to-PDF Engine

## Immediate Next Steps (Start Here!)

### 1. Set Up Your Development Environment

```bash
# Make sure you have Python 3.8+ installed
python --version

# Install uv if you haven't already
pip install uv

# Navigate to your project directory
cd /c:/projects/my-little-pdf-py

# Initialize the project
uv init --name md-to-pdf-engine
```

### 2. Create Initial Project Structure

```bash
# Create the recommended directory structure
mkdir -p src/md_to_pdf
mkdir -p tests
mkdir -p templates
mkdir -p assets/{fonts,css,images}
mkdir -p examples
mkdir -p docs

# Create empty __init__.py files
touch src/__init__.py
touch src/md_to_pdf/__init__.py
touch tests/__init__.py
```

### 3. Set Up Dependencies

Create or update your `pyproject.toml`:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "md-to-pdf-engine"
dynamic = ["version"]
description = "Configurable Markdown-to-PDF conversion engine"
readme = "README.md"
requires-python = ">=3.8"
license = "MIT"
keywords = ["markdown", "pdf", "conversion", "document-generation"]
authors = [
    { name = "Your Name", email = "your.email@example.com" },
]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
]
dependencies = [
    "markdown>=3.4",
    "jinja2>=3.1",
    "weasyprint>=57.0",
    "pyyaml>=6.0",
    "click>=8.0",  # For CLI
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov",
    "ruff",
    "black",
    "mypy",
]

[project.urls]
Documentation = "https://github.com/yourusername/md-to-pdf-engine#readme"
Issues = "https://github.com/yourusername/md-to-pdf-engine/issues"
Source = "https://github.com/yourusername/md-to-pdf-engine"

[project.scripts]
md2pdf = "md_to_pdf.cli:main"

[tool.hatch.version]
path = "src/md_to_pdf/__about__.py"

[tool.ruff]
target-version = "py38"
line-length = 88

[tool.black]
target-version = ['py38']
line-length = 88

[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
```

### 4. Install Dependencies

```bash
# Install all dependencies including dev tools
uv sync
uv add --dev pytest pytest-cov ruff black mypy

# Activate the virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 5. Create Your First Files

#### `src/md_to_pdf/__about__.py`
```python
__version__ = "0.1.0"
```

#### `src/md_to_pdf/__init__.py`
```python
"""Markdown to PDF conversion engine."""

from .core import MarkdownToPDFConverter

__version__ = "0.1.0"
__all__ = ["MarkdownToPDFConverter"]
```

#### `src/md_to_pdf/core.py` (Starter)
```python
"""Core functionality for Markdown to PDF conversion."""

import markdown
from jinja2 import Environment, FileSystemLoader
import weasyprint
from pathlib import Path
from typing import Optional, Dict, Any

class MarkdownToPDFConverter:
    """Main converter class for Markdown to PDF transformation."""
    
    def __init__(self, theme_config_path: Optional[Path] = None):
        """Initialize the converter with optional theme configuration."""
        self.theme_config = theme_config_path
        self.md_parser = markdown.Markdown()
        self.jinja_env = Environment(loader=FileSystemLoader('templates'))
    
    def convert_file(self, input_path: Path, output_path: Path) -> None:
        """Convert a Markdown file to PDF."""
        # Read the markdown file
        with open(input_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # Convert to HTML
        html_content = self.md_parser.convert(md_content)
        
        # Basic HTML template for now
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Generated PDF</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 2cm; }}
                h1 {{ color: #333; }}
            </style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        
        # Convert to PDF
        weasyprint.HTML(string=full_html).write_pdf(output_path)
        print(f"PDF generated: {output_path}")
```

### 6. Create a Test File

#### `tests/test_basic.py`
```python
"""Basic tests for the MD to PDF converter."""

import pytest
from pathlib import Path
import tempfile
from md_to_pdf.core import MarkdownToPDFConverter

def test_basic_conversion():
    """Test basic markdown to PDF conversion."""
    converter = MarkdownToPDFConverter()
    
    # Create a simple test markdown file
    test_md = "# Hello World\n\nThis is a **test** document."
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        input_file = tmp_path / "test.md"
        output_file = tmp_path / "test.pdf"
        
        # Write test content
        input_file.write_text(test_md)
        
        # Convert
        converter.convert_file(input_file, output_file)
        
        # Check that PDF was created
        assert output_file.exists()
        assert output_file.stat().st_size > 0
```

### 7. Test Your Setup

```bash
# Run the basic test
pytest tests/test_basic.py -v

# If WeasyPrint has issues, you might need system dependencies:
# On Ubuntu/Debian: sudo apt-get install python3-dev python3-pip python3-cffi python3-brotli libpango-1.0-0 libharfbuzz0b libpangoft2-1.0-0
# On macOS: brew install pango
# On Windows: May work out of the box, or you might need to install GTK+
```

### 8. Create an Example

#### `examples/sample.md`
```markdown
# My First Document

This is a **sample** document to test our PDF generator.

## Features

- Markdown parsing
- PDF generation
- Basic styling

### Next Steps

1. Add custom components
2. Implement themes
3. Test with complex documents
```

### 9. Test End-to-End

```bash
# Create a simple CLI test script
cat > test_conversion.py << 'EOF'
#!/usr/bin/env python3

from pathlib import Path
from src.md_to_pdf.core import MarkdownToPDFConverter

def main():
    converter = MarkdownToPDFConverter()
    input_file = Path("examples/sample.md")
    output_file = Path("examples/sample.pdf")
    
    if input_file.exists():
        converter.convert_file(input_file, output_file)
        print(f"Success! Check {output_file}")
    else:
        print(f"Input file not found: {input_file}")

if __name__ == "__main__":
    main()
EOF

# Run the test
python test_conversion.py
```

## What You've Accomplished

After following these steps, you'll have:

✅ **Working Development Environment**: Project structure with `uv` package management  
✅ **Basic Dependencies**: All core libraries installed and tested  
✅ **Minimal Pipeline**: Simple Markdown → HTML → PDF conversion  
✅ **Test Framework**: Basic testing setup with pytest  
✅ **Example Document**: Sample markdown file for testing  

## Immediate Next Tasks

1. **Verify Everything Works**: Run the test conversion and check the output PDF
2. **Explore WeasyPrint**: Try different CSS styles in the basic template
3. **Study python-markdown**: Look at the extension API documentation
4. **Plan Sprint 1**: Review the TASKS.md file and pick your first custom component

## Common Issues & Solutions

### WeasyPrint Installation Problems
- **Linux**: Install system dependencies for Pango/Cairo
- **macOS**: Use Homebrew to install required libraries  
- **Windows**: May need additional setup for GTK+

### Import Errors
- Make sure you're in the activated virtual environment
- Run `uv sync` to ensure all dependencies are installed
- Check Python path includes your src directory

### PDF Generation Fails
- Start with very simple HTML to isolate issues
- Check WeasyPrint error messages for CSS problems
- Verify file permissions for output directory

## Ready for Phase 2?

Once you have the basic pipeline working, you can start implementing the custom component system following the detailed tasks in `TASKS.md`. The next major milestone is parsing `::: component_name :::` syntax and rendering it with Jinja2 templates.

Good luck with your implementation! 🚀 