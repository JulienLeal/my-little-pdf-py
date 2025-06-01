# 🎯 WeasyPrint Windows Setup - Action Plan

## Current Status ✅
- ✅ Python dependencies are working (Markdown, Jinja2, PyYAML, Click)
- ✅ WeasyPrint Python package is installed
- ❌ WeasyPrint fails due to missing system libraries (libgobject-2.0-0)
- ❌ MSYS2 not installed
- ❌ Environment variables not set

## The Problem
WeasyPrint imports successfully but fails when trying to generate PDFs because it can't find the required GTK+/Pango libraries on Windows. The error message is:
```
cannot load library 'libgobject-2.0-0': error 0x7e
```

## 🚀 Action Plan (Choose One Option)

### Option A: Manual MSYS2 Installation (Recommended)

**Step 1: Download and Install MSYS2**
1. Go to https://www.msys2.org/
2. Download `msys2-x86_64-[date].exe` 
3. Run the installer as Administrator
4. Install to default location: `C:\msys64`
5. When installation completes, MSYS2 terminal should open

**Step 2: Update MSYS2**
In the MSYS2 terminal, run:
```bash
pacman -Syu
```
When prompted to close the terminal, close it and reopen "MSYS2 MSYS" from Start Menu.
Then run:
```bash
pacman -Su
```

**Step 3: Install Pango and Dependencies**
In MSYS2 terminal:
```bash
pacman -S mingw-w64-x86_64-pango
```
This installs all required libraries including libgobject-2.0-0.dll, libcairo-2.dll, etc.

**Step 4: Test Installation**
Come back to this project and run:
```powershell
powershell -ExecutionPolicy Bypass -File check_msys2.ps1
```

### Option B: Use Pre-built WeasyPrint Executable

If MSYS2 installation is problematic:
1. Download WeasyPrint executable from: https://github.com/Kozea/WeasyPrint/releases
2. Extract to a folder (e.g., `C:\weasyprint\`)
3. Use it as external command instead of Python library
4. Modify our code to call the executable instead of importing the library

### Option C: Docker Solution

For development environments:
1. Install Docker Desktop for Windows
2. Use a Linux container with WeasyPrint
3. Mount project files to container
4. Generate PDFs inside container

## 🧪 Testing Commands

After completing any option, test with:
```bash
# Check MSYS2 installation
powershell check_msys2.ps1

# Test all dependencies
uv run python test_dependencies.py

# Quick WeasyPrint test
uv run python -c "import weasyprint; print('WeasyPrint ready!')"
```

## 📝 Why This Happens

WeasyPrint needs these system libraries for PDF generation:
- **libgobject-2.0-0**: Core GObject system
- **libcairo**: 2D graphics rendering
- **libpango**: Text layout and rendering
- **libgdk_pixbuf**: Image loading
- **libharfbuzz**: Text shaping
- **libfontconfig**: Font management

These are standard on Linux but must be manually installed on Windows.

## 🎯 Success Criteria

When setup is complete, you should see:
```
✅ PDF generation successful (XXXX bytes)
🎉 WeasyPrint is now working!
```

## 📞 Next Steps After Success

1. Update task status in TASKS.md
2. Continue with Phase 1.2 tasks
3. Begin basic pipeline proof of concept

---

**Choose Option A (MSYS2) for the best integration with our Python workflow.** 