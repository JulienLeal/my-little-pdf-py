# WeasyPrint Setup

This section contains platform-specific setup guides for WeasyPrint PDF rendering engine.

## 📦 WeasyPrint Setup Guides

### [Windows Setup Guide](WEASYPRINT_WINDOWS_SETUP.md)
**Size**: 6.1KB | **Lines**: 184 | **Priority**: High

Complete Windows installation guide covering:
- MSYS2 installation and configuration
- Pango and GTK+ dependencies
- Environment variable setup
- Troubleshooting common issues

### [Setup Planning](WEASYPRINT_SETUP_PLAN.md)
**Size**: 3.1KB | **Lines**: 109 | **Purpose**: Strategy

Setup strategy document covering:
- Installation approach analysis
- Alternative solutions
- Risk assessment
- Implementation plan

### [MSYS2 Manual Installation](install_msys2_manual.md)
**Size**: 1.8KB | **Lines**: 64 | **Purpose**: Step-by-step

Detailed manual installation steps for:
- MSYS2 package manager setup
- System dependency installation
- Manual configuration steps
- Verification procedures

## 🎯 Why WeasyPrint Setup is Complex

WeasyPrint requires system-level dependencies that are not automatically available on all platforms:
- **Pango**: Text rendering library
- **GTK+**: GUI toolkit dependencies  
- **HarfBuzz**: Text shaping engine
- **FontConfig**: Font discovery system

## 🔧 Platform Support

| Platform | Status | Guide |
|----------|--------|-------|
| Windows | ⚠️ Complex | [Windows Setup](WEASYPRINT_WINDOWS_SETUP.md) |
| macOS | ✅ Homebrew | Coming soon |
| Linux | ✅ Package Manager | Coming soon |

## 🚨 Common Issues

- **DLL Loading Errors**: Missing system dependencies
- **Font Rendering Problems**: Incorrect font path configuration
- **Permission Errors**: Insufficient system privileges
- **Path Conflicts**: Multiple GTK installations

## 📋 Prerequisites

- Administrative access to install system packages
- Python 3.8+ with pip/uv package manager
- Git for downloading dependencies
- ~500MB disk space for system dependencies

## 🔍 Quick Troubleshooting

1. **Import Error**: Check WEASYPRINT_DLL_DIRECTORIES environment variable
2. **PDF Generation Fails**: Verify system dependencies are installed
3. **Font Issues**: Check font path configuration
4. **Permission Denied**: Run terminal as administrator 