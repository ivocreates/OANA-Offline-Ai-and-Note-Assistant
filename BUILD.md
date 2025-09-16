# OANA Build and Distribution Guide

## Quick Build Command

To build a distributable executable with the lightweight AI model included:

```bash
# Install build dependencies
pip install PyInstaller

# Build the application
python build_exe.py
```

This single command will:
- ✅ Automatically download the lightweight TinyLlama model if missing
- ✅ Create a standalone executable in `dist/OANA/`
- ✅ Package everything into `prod/OANA-Portable/` 
- ✅ Include all necessary files and the AI model
- ✅ Create an installer (if NSIS is available)

## What Gets Built

### Portable Version (`prod/OANA-Portable/`)
- Complete standalone application
- No installation required
- Includes the lightweight TinyLlama AI model
- Can be copied to any Windows PC
- Run with `OANA.exe` or `run_oana.bat`

### Installer Version (if NSIS installed)
- Professional installer with proper uninstall
- Desktop shortcuts and Start Menu entries
- System integration

## Distribution Files

The build creates these files you can share:

1. **For Users**: `prod/OANA-Portable/` - Complete portable folder
2. **For Installation**: `oana-installer.exe` - Professional installer
3. **Size**: ~650MB (includes AI model)

## System Requirements

**For Building:**
- Python 3.8+ with pip
- PyInstaller (`pip install PyInstaller`)
- NSIS (optional, for installer)

**For End Users:**
- Windows 7/8/10/11
- ~1GB free disk space
- No Python installation required

## Advanced Options

### Custom Build
```bash
# Clean build
python build_exe.py

# Just create spec file
python -c "from build_exe import create_spec_file; create_spec_file()"

# Manual PyInstaller
pyinstaller --clean OANA.spec
```

### Manual Model Setup
```bash
# Download models separately
python download_models.py

# Check available models
python -c "from utils.ai_engine import AIEngine; print(AIEngine.get_available_models())"
```

## Troubleshooting

### Common Issues
- **Model not found**: Run `python download_models.py` first
- **PyInstaller missing**: Run `pip install PyInstaller`
- **Build fails**: Check Python version (3.8+ required)
- **Large file size**: Normal - includes AI model for offline use

### File Structure After Build
```
prod/OANA-Portable/
├── OANA.exe              # Main executable
├── run_oana.bat         # Launcher script
├── README.md            # Documentation
├── models/              # AI model files
├── _internal/           # PyInstaller files
└── ...
```

## Distribution Checklist

Before sharing:
- ✅ Test `OANA.exe` runs properly
- ✅ Check AI model is included and working
- ✅ Verify chat history saves/loads
- ✅ Test on clean Windows machine
- ✅ Include README.md with the package

## Notes

- The lightweight TinyLlama model (~637MB) is included for offline AI functionality
- Build files are ignored by git (see `.gitignore`)
- The executable is portable and requires no installation
- All user data is stored locally in the application folder