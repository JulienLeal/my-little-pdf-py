Write-Host "Checking MSYS2 Installation..." -ForegroundColor Green

# Check if MSYS2 is installed
$msys2Path = "C:\msys64"
$msys2BinPath = "$msys2Path\mingw64\bin"

if (Test-Path $msys2Path) {
    Write-Host "✅ MSYS2 found at $msys2Path" -ForegroundColor Green
    
    if (Test-Path $msys2BinPath) {
        Write-Host "✅ MSYS2 bin directory found" -ForegroundColor Green
        
        # Check for key DLL files
        $requiredDlls = @(
            "libgobject-2.0-0.dll",
            "libcairo-2.dll", 
            "libpango-1.0-0.dll"
        )
        
        $foundDlls = 0
        foreach ($dll in $requiredDlls) {
            $dllPath = Join-Path $msys2BinPath $dll
            if (Test-Path $dllPath) {
                Write-Host "✅ Found: $dll" -ForegroundColor Green
                $foundDlls++
            } else {
                Write-Host "❌ Missing: $dll" -ForegroundColor Red
            }
        }
        
        if ($foundDlls -eq $requiredDlls.Count) {
            Write-Host "✅ All required DLLs found!" -ForegroundColor Green
            
            # Set environment variable
            Write-Host "Setting WEASYPRINT_DLL_DIRECTORIES..." -ForegroundColor Yellow
            $env:WEASYPRINT_DLL_DIRECTORIES = $msys2BinPath
            [System.Environment]::SetEnvironmentVariable("WEASYPRINT_DLL_DIRECTORIES", $msys2BinPath, "User")
            
            Write-Host "✅ Environment variable set for current session and user" -ForegroundColor Green
            Write-Host "Testing WeasyPrint..." -ForegroundColor Yellow
            
            # Test WeasyPrint
            try {
                $result = uv run python -c "
import weasyprint
html = '<html><body><h1>Test</h1></body></html>'
doc = weasyprint.HTML(string=html)
pdf = doc.write_pdf()
print(f'✅ Success! Generated PDF with {len(pdf)} bytes')
"
                Write-Host $result -ForegroundColor Green
                Write-Host "🎉 WeasyPrint is now working!" -ForegroundColor Green
                return
            } catch {
                Write-Host "❌ WeasyPrint test failed: $_" -ForegroundColor Red
            }
        } else {
            Write-Host "❌ Missing required DLLs. Run in MSYS2: pacman -S mingw-w64-x86_64-pango" -ForegroundColor Red
        }
    } else {
        Write-Host "❌ MSYS2 bin directory not found" -ForegroundColor Red
    }
} else {
    Write-Host "❌ MSYS2 not found at $msys2Path" -ForegroundColor Red
    Write-Host "Please install MSYS2 manually. See install_msys2_manual.md" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Install MSYS2 from https://www.msys2.org/" -ForegroundColor White
Write-Host "2. Run: pacman -S mingw-w64-x86_64-pango" -ForegroundColor White
Write-Host "3. Run this script again: powershell check_msys2.ps1" -ForegroundColor White 