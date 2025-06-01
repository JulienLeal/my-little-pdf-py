# WeasyPrint Windows Setup Script
# This script helps automate the setup process for WeasyPrint on Windows

Write-Host "🔧 WeasyPrint Windows Setup Helper" -ForegroundColor Green
Write-Host "This script will help you set up WeasyPrint on Windows with MSYS2" -ForegroundColor Yellow
Write-Host ""

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "⚠️ This script is not running as Administrator" -ForegroundColor Yellow
    Write-Host "Some operations may require administrator privileges" -ForegroundColor Yellow
    Write-Host ""
}

# Check if MSYS2 is installed
$msys2Path = "C:\msys64"
$msys2BinPath = "$msys2Path\mingw64\bin"

Write-Host "🔍 Checking MSYS2 installation..." -ForegroundColor Cyan

if (Test-Path $msys2Path) {
    Write-Host "✅ MSYS2 found at $msys2Path" -ForegroundColor Green
    
    # Check for key DLL files
    $keyDlls = @(
        "libpango-1.0-0.dll",
        "libcairo-2.dll", 
        "libgdk_pixbuf-2.0-0.dll",
        "libharfbuzz-0.dll",
        "libfontconfig-1.dll"
    )
    
    $foundDlls = 0
    foreach ($dll in $keyDlls) {
        $dllPath = Join-Path $msys2BinPath $dll
        if (Test-Path $dllPath) {
            Write-Host "✅ Found: $dll" -ForegroundColor Green
            $foundDlls++
        } else {
            Write-Host "❌ Missing: $dll" -ForegroundColor Red
        }
    }
    
    if ($foundDlls -eq 0) {
        Write-Host "⚠️ Pango libraries not found. You need to install them via MSYS2" -ForegroundColor Yellow
        Write-Host "Run this command in MSYS2 terminal: pacman -S mingw-w64-x86_64-pango" -ForegroundColor Yellow
    } elseif ($foundDlls -lt $keyDlls.Count) {
        Write-Host "⚠️ Some libraries are missing. Consider reinstalling Pango" -ForegroundColor Yellow
    } else {
        Write-Host "✅ All required libraries found!" -ForegroundColor Green
    }
    
} else {
    Write-Host "❌ MSYS2 not found at $msys2Path" -ForegroundColor Red
    Write-Host "Please install MSYS2 from: https://www.msys2.org/" -ForegroundColor Yellow
    Write-Host "After installation, run: pacman -S mingw-w64-x86_64-pango" -ForegroundColor Yellow
    return
}

# Check environment variable
Write-Host ""
Write-Host "🔍 Checking environment variables..." -ForegroundColor Cyan

$currentDllDir = [System.Environment]::GetEnvironmentVariable("WEASYPRINT_DLL_DIRECTORIES", "User")
$systemDllDir = [System.Environment]::GetEnvironmentVariable("WEASYPRINT_DLL_DIRECTORIES", "Machine")

if ($currentDllDir -or $systemDllDir) {
    Write-Host "✅ WEASYPRINT_DLL_DIRECTORIES is set" -ForegroundColor Green
    if ($currentDllDir) { Write-Host "   User: $currentDllDir" -ForegroundColor Gray }
    if ($systemDllDir) { Write-Host "   System: $systemDllDir" -ForegroundColor Gray }
} else {
    Write-Host "❌ WEASYPRINT_DLL_DIRECTORIES not set" -ForegroundColor Red
    
    Write-Host ""
    Write-Host "🛠️ Setting environment variable..." -ForegroundColor Cyan
    
    try {
        # Set for current user
        [System.Environment]::SetEnvironmentVariable("WEASYPRINT_DLL_DIRECTORIES", $msys2BinPath, "User")
        
        # Also set for current session
        $env:WEASYPRINT_DLL_DIRECTORIES = $msys2BinPath
        
        Write-Host "✅ Environment variable set: $msys2BinPath" -ForegroundColor Green
        Write-Host "ℹ️ You may need to restart your terminal for this to take effect" -ForegroundColor Yellow
    } catch {
        Write-Host "❌ Failed to set environment variable: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "Try setting it manually in System Properties > Environment Variables" -ForegroundColor Yellow
    }
}

# Test WeasyPrint
Write-Host ""
Write-Host "🔍 Testing WeasyPrint functionality..." -ForegroundColor Cyan

try {
    # Set the environment variable for this session
    $env:WEASYPRINT_DLL_DIRECTORIES = $msys2BinPath
    
    # Test Python import and PDF generation
    $testScript = @'
import sys
try:
    import weasyprint
    print("✅ WeasyPrint imported successfully")
    
    html_content = "<html><body><h1>Test</h1><p>Windows setup test</p></body></html>"
    doc = weasyprint.HTML(string=html_content)
    pdf_bytes = doc.write_pdf()
    print(f"✅ PDF generation successful ({len(pdf_bytes)} bytes)")
    sys.exit(0)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
'@
    
    # Run the test with current environment
    $result = python -c $testScript
    if ($LASTEXITCODE -eq 0) {
        Write-Host $result -ForegroundColor Green
        Write-Host ""
        Write-Host "🎉 WeasyPrint setup completed successfully!" -ForegroundColor Green
    } else {
        Write-Host $result -ForegroundColor Red
        Write-Host "❌ WeasyPrint test failed" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Python test failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "📋 Next steps:" -ForegroundColor Cyan
Write-Host "1. Restart your terminal/IDE to pick up environment variables" -ForegroundColor White
Write-Host "2. Run: python test_dependencies.py" -ForegroundColor White
Write-Host "3. If tests still fail, check WEASYPRINT_WINDOWS_SETUP.md for detailed troubleshooting" -ForegroundColor White
Write-Host "" 