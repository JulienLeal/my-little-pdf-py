# WeasyPrint Windows Installation Fix

## Task Overview
**Priority**: 🔴 High Priority / Blocking  
**Status**: ⏳ In Progress  
**Estimated Hours**: 4  
**Dependencies**: pyproject.toml exists  

## Problem Description
WeasyPrint requires system-level dependencies (Pango, GTK+) that are not automatically available on Windows. The current installation via `uv add weasyprint` only installs the Python package but not the required system libraries, causing PDF generation to fail.

## Reference Documentation
- [WeasyPrint Windows Installation Guide](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#windows)

## Current Status Check
Based on `test_dependencies.py`, WeasyPrint imports successfully but PDF generation fails with system dependency errors.

## Solution Steps

### Step 1: Install MSYS2 (Windows Package Manager)
1. **Download and install MSYS2**:
   - Visit: https://www.msys2.org/
   - Download the installer for your architecture (usually x86_64)
   - Run the installer with default options
   - Location should be: `C:\msys64\`

2. **Initial MSYS2 setup**:
   ```bash
   # These commands should be run in MSYS2 terminal (not PowerShell)
   pacman -Syu  # Update package database and core packages
   # Close terminal when prompted, then reopen MSYS2
   pacman -Su   # Update remaining packages
   ```

### Step 2: Install Pango and Dependencies via MSYS2
```bash
# Run in MSYS2 terminal
pacman -S mingw-w64-x86_64-pango
```

This installs:
- Pango (text rendering library)
- GTK+ dependencies
- HarfBuzz (text shaping)
- FontConfig (font discovery)
- Other required libraries

### Step 3: Configure Environment Variables
WeasyPrint needs to find the MSYS2 libraries. Add to system environment:

**Method A: Set via PowerShell (temporary)**
```powershell
$env:WEASYPRINT_DLL_DIRECTORIES = "C:\msys64\mingw64\bin"
```

**Method B: Set via System Properties (permanent)**
1. Open System Properties → Environment Variables
2. Add new system variable:
   - Variable: `WEASYPRINT_DLL_DIRECTORIES`
   - Value: `C:\msys64\mingw64\bin`

### Step 4: Verify Installation
Update the `test_dependencies.py` file to test the fix:

```python
def test_weasyprint_windows_fix():
    """Test WeasyPrint with Windows system dependencies."""
    print("\nTesting WeasyPrint Windows fix...")
    
    import os
    
    # Check if WEASYPRINT_DLL_DIRECTORIES is set
    dll_dirs = os.environ.get('WEASYPRINT_DLL_DIRECTORIES')
    if dll_dirs:
        print(f"✅ WEASYPRINT_DLL_DIRECTORIES set: {dll_dirs}")
    else:
        print("⚠️ WEASYPRINT_DLL_DIRECTORIES not set")
    
    # Check if MSYS2 libraries exist
    expected_path = "C:\\msys64\\mingw64\\bin"
    if os.path.exists(expected_path):
        print(f"✅ MSYS2 directory found: {expected_path}")
        
        # Check for key libraries
        key_dlls = ['libpango-1.0-0.dll', 'libcairo-2.dll', 'libgdk_pixbuf-2.0-0.dll']
        for dll in key_dlls:
            dll_path = os.path.join(expected_path, dll)
            if os.path.exists(dll_path):
                print(f"✅ Found: {dll}")
            else:
                print(f"❌ Missing: {dll}")
    else:
        print(f"❌ MSYS2 directory not found: {expected_path}")
    
    # Test WeasyPrint functionality
    try:
        import weasyprint
        html_content = "<html><body><h1>Windows Test</h1></body></html>"
        doc = weasyprint.HTML(string=html_content)
        pdf_bytes = doc.write_pdf()
        print(f"✅ PDF generation successful ({len(pdf_bytes)} bytes)")
        return True
    except Exception as e:
        print(f"❌ PDF generation failed: {e}")
        return False
```

### Step 5: Alternative Solutions (if MSYS2 fails)

**Option A: Use WeasyPrint Executable**
- Download pre-built executable from WeasyPrint releases
- Use as external command instead of Python library
- Less integrated but more reliable on Windows

**Option B: Docker Container**
- Run WeasyPrint in a Linux container
- Use Docker Desktop for Windows
- More complex setup but fully isolated

**Option C: Windows Subsystem for Linux (WSL)**
- Install WeasyPrint in WSL environment
- Access from Windows via WSL integration
- Good for development, complex for distribution

## Testing Checklist
- [ ] MSYS2 installed successfully
- [ ] Pango package installed via pacman
- [ ] Environment variable set correctly
- [ ] WeasyPrint imports without errors
- [ ] PDF generation produces valid output
- [ ] Test with complex HTML/CSS
- [ ] Verify font rendering works
- [ ] Test with images

## Expected Outcomes
After successful completion:
1. WeasyPrint PDF generation works on Windows
2. No "missing library" errors
3. Fonts render correctly in PDFs
4. Images embed properly
5. `test_dependencies.py` passes all tests

## Troubleshooting

### Common Issues:
1. **"cannot load library" errors**:
   - Verify WEASYPRINT_DLL_DIRECTORIES points to correct path
   - Check that DLL files exist in the directory
   
2. **Font rendering issues**:
   - Install additional font packages via MSYS2
   - Verify system fonts are accessible

3. **Permission errors**:
   - Run terminal as administrator during installation
   - Check file permissions on MSYS2 directory

4. **Path conflicts**:
   - Ensure no conflicting GTK installations
   - Use full paths in environment variables

### Verification Commands:
```powershell
# Check environment variable
echo $env:WEASYPRINT_DLL_DIRECTORIES

# Test Python import
python -c "import weasyprint; print('Import successful')"

# Run dependency test
python test_dependencies.py
```

## Success Criteria
- [ ] WeasyPrint PDF generation works without system dependency errors
- [ ] Test suite passes completely
- [ ] Documentation updated with Windows-specific setup instructions
- [ ] Other team members can reproduce the setup

## Next Steps After Completion
1. Update main README.md with Windows setup instructions
2. Create automated setup script for Windows users
3. Document the fix in troubleshooting guide
4. Continue with Phase 1.2 tasks (WeasyPrint testing) 