# Manual MSYS2 Installation for WeasyPrint

## Step 1: Download and Install MSYS2

1. **Download MSYS2**:
   - Go to: https://www.msys2.org/
   - Download the installer: `msys2-x86_64-[latest-date].exe`
   - Run the installer with default settings
   - Install to the default location: `C:\msys64`

2. **Initial Setup**:
   - After installation, MSYS2 terminal should open automatically
   - If not, open "MSYS2 MSYS" from Start Menu
   - Run these commands in the MSYS2 terminal:
   ```bash
   pacman -Syu
   ```
   - Close the terminal when prompted, then reopen "MSYS2 MSYS"
   - Run:
   ```bash
   pacman -Su
   ```

## Step 2: Install Pango and Dependencies

In the MSYS2 terminal, run:
```bash
pacman -S mingw-w64-x86_64-pango
```

This will install all required libraries including:
- libgobject-2.0-0.dll
- libcairo-2.dll  
- libpango-1.0-0.dll
- libgdk_pixbuf-2.0-0.dll
- libharfbuzz-0.dll
- libfontconfig-1.dll

## Step 3: Return to this Project

After MSYS2 installation is complete:

1. Come back to this terminal
2. Run: `powershell check_msys2.ps1`
3. Continue with the automated setup

## Alternative: Use WeasyPrint Executable

If MSYS2 installation is problematic, you can:

1. Download the WeasyPrint executable from: https://github.com/Kozea/WeasyPrint/releases
2. Extract it to a folder
3. Use it as an external command instead of the Python library

## What These Libraries Do

- **libgobject-2.0-0**: Core GObject system (required by GTK+)
- **libcairo**: 2D graphics library for rendering
- **libpango**: Text layout and rendering engine  
- **libgdk_pixbuf**: Image loading library
- **libharfbuzz**: Text shaping engine
- **libfontconfig**: Font configuration library

All of these are needed for WeasyPrint to render HTML/CSS to PDF properly on Windows. 