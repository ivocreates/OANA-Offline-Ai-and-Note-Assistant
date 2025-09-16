#!/usr/bin/env python3
"""
OANA Desktop Application Builder
Creates a standalone desktop application installer for Windows
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path
import json

class OANABuilder:
    def __init__(self):
        self.project_dir = Path(__file__).parent
        self.dist_dir = self.project_dir / "dist"
        self.build_dir = self.project_dir / "build"
        
    def check_dependencies(self):
        """Check if required build tools are installed"""
        print("🔍 Checking build dependencies...")
        
        try:
            import PyInstaller
            print("✅ PyInstaller found")
        except ImportError:
            print("❌ PyInstaller not found. Installing...")
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
            
        try:
            import requests
            print("✅ Requests found")
        except ImportError:
            subprocess.run([sys.executable, "-m", "pip", "install", "requests"], check=True)
            
    def install_requirements(self):
        """Install all project requirements"""
        print("📦 Installing project requirements...")
        requirements_file = self.project_dir / "requirements.txt"
        if requirements_file.exists():
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
            ], check=True)
        else:
            print("⚠️ requirements.txt not found")
            
    def create_spec_file(self):
        """Create PyInstaller spec file"""
        print("📝 Creating PyInstaller spec file...")
        
        spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['app.py'],
    pathex=['{self.project_dir}'],
    binaries=[],
    datas=[
        ('utils', 'utils'),
        ('data', 'data'),
        ('logs', 'logs'),
        ('*.json', '.'),
        ('README.md', '.'),
        ('LICENSE*', '.'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.scrolledtext',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.colorchooser',
        'tkinter.simpledialog',
        'sqlite3',
        'llama_cpp',
        'fitz',
        'docx',
        'docx2txt',
        'PIL',
        'requests',
        'weasyprint',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'jupyter',
        'IPython',
        'pytest',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='OANA',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Set to False for windowed app
    icon='icon.ico' if os.path.exists('icon.ico') else None,
    version='version_info.txt' if os.path.exists('version_info.txt') else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='OANA',
)
'''
        
        spec_file = self.project_dir / "oana.spec"
        with open(spec_file, 'w', encoding='utf-8') as f:
            f.write(spec_content)
            
        return spec_file
        
    def create_version_info(self):
        """Create version information file for Windows exe"""
        print("📋 Creating version info...")
        
        version_info = '''# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1,0,0,0),
    prodvers=(1,0,0,0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
    ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'OANA Project'),
        StringStruct(u'FileDescription', u'OANA - Offline AI and Note Assistant'),
        StringStruct(u'FileVersion', u'1.0.0'),
        StringStruct(u'InternalName', u'OANA'),
        StringStruct(u'LegalCopyright', u'© 2024 OANA Project'),
        StringStruct(u'OriginalFilename', u'OANA.exe'),
        StringStruct(u'ProductName', u'OANA - Offline AI and Note Assistant'),
        StringStruct(u'ProductVersion', u'1.0.0')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
'''
        
        version_file = self.project_dir / "version_info.txt"
        with open(version_file, 'w', encoding='utf-8') as f:
            f.write(version_info)
            
    def build_executable(self):
        """Build the executable using PyInstaller"""
        print("🏗️ Building executable...")
        
        # Clean previous builds
        if self.dist_dir.exists():
            shutil.rmtree(self.dist_dir)
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
            
        spec_file = self.create_spec_file()
        self.create_version_info()
        
        # Run PyInstaller
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--clean",
            str(spec_file)
        ]
        
        result = subprocess.run(cmd, cwd=self.project_dir)
        if result.returncode != 0:
            raise Exception("PyInstaller build failed")
            
        print("✅ Executable built successfully!")
        
    def create_installer_script(self):
        """Create NSIS installer script for Windows"""
        print("📦 Creating installer script...")
        
        nsis_script = '''!define APPNAME "OANA"
!define COMPANYNAME "OANA Project"
!define DESCRIPTION "Offline AI and Note Assistant"
!define VERSIONMAJOR 1
!define VERSIONMINOR 0
!define VERSIONBUILD 0
!define HELPURL "https://github.com/ivocreates/OANA-Offline-Ai-and-Note-Assistant"
!define UPDATEURL "https://github.com/ivocreates/OANA-Offline-Ai-and-Note-Assistant/releases"
!define ABOUTURL "https://github.com/ivocreates/OANA-Offline-Ai-and-Note-Assistant"
!define INSTALLSIZE 500000

RequestExecutionLevel admin
InstallDir "$PROGRAMFILES\\${COMPANYNAME}\\${APPNAME}"
Name "${APPNAME}"
Icon "icon.ico"
outFile "OANA-Setup.exe"

!include LogicLib.nsh
!include "MUI2.nsh"

!define MUI_ICON "icon.ico"
!define MUI_UNICON "icon.ico"
!define MUI_WELCOMEPAGE_TITLE "Welcome to OANA Setup"
!define MUI_WELCOMEPAGE_TEXT "OANA is an Offline AI and Note Assistant that runs entirely on your computer."

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"

Section "Install"
    SetOutPath $INSTDIR
    
    # Copy all files
    File /r "dist\\OANA\\*"
    
    # Create shortcuts
    CreateShortcut "$DESKTOP\\${APPNAME}.lnk" "$INSTDIR\\OANA.exe"
    CreateDirectory "$SMPROGRAMS\\${COMPANYNAME}"
    CreateShortcut "$SMPROGRAMS\\${COMPANYNAME}\\${APPNAME}.lnk" "$INSTDIR\\OANA.exe"
    CreateShortcut "$SMPROGRAMS\\${COMPANYNAME}\\Uninstall.lnk" "$INSTDIR\\uninstall.exe"
    
    # Registry entries
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "DisplayName" "${APPNAME}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "UninstallString" "$INSTDIR\\uninstall.exe"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "InstallLocation" "$INSTDIR"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "Publisher" "${COMPANYNAME}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "HelpLink" "${HELPURL}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "URLUpdateInfo" "${UPDATEURL}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "URLInfoAbout" "${ABOUTURL}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "DisplayVersion" "${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONBUILD}"
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "EstimatedSize" ${INSTALLSIZE}
    
    # Create uninstaller
    WriteUninstaller "$INSTDIR\\uninstall.exe"
SectionEnd

Section "Uninstall"
    Delete "$DESKTOP\\${APPNAME}.lnk"
    Delete "$SMPROGRAMS\\${COMPANYNAME}\\${APPNAME}.lnk"
    Delete "$SMPROGRAMS\\${COMPANYNAME}\\Uninstall.lnk"
    RMDir "$SMPROGRAMS\\${COMPANYNAME}"
    
    RMDir /r "$INSTDIR"
    
    DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}"
SectionEnd
'''
        
        nsis_file = self.project_dir / "installer.nsi"
        with open(nsis_file, 'w', encoding='utf-8') as f:
            f.write(nsis_script)
            
        return nsis_file
        
    def create_portable_package(self):
        """Create a portable package"""
        print("📁 Creating portable package...")
        
        portable_dir = self.project_dir / "OANA-Portable"
        if portable_dir.exists():
            shutil.rmtree(portable_dir)
            
        # Copy dist folder contents
        dist_app_dir = self.dist_dir / "OANA"
        if dist_app_dir.exists():
            shutil.copytree(dist_app_dir, portable_dir)
            
            # Create run script
            run_script = portable_dir / "run_oana.bat"
            with open(run_script, 'w') as f:
                f.write('''@echo off
echo Starting OANA - Offline AI Assistant...
cd /d "%~dp0"
OANA.exe
if errorlevel 1 (
    echo.
    echo Error occurred. Press any key to close...
    pause >nul
)
''')
                
            # Create README for portable
            readme_portable = portable_dir / "README_PORTABLE.txt"
            with open(readme_portable, 'w') as f:
                f.write('''OANA - Offline AI Assistant (Portable Version)
=====================================================

This is a portable version of OANA that doesn't require installation.

QUICK START:
1. Double-click "run_oana.bat" to start the application
2. Or directly run "OANA.exe"

FIRST TIME SETUP:
- The app will create necessary folders (models, data, logs) on first run
- Download AI models through the "AI Models" menu
- Configure settings through the Settings menu

FEATURES:
- Chat with AI models completely offline
- Upload and analyze PDF/Word documents
- Save and manage conversation history
- Multiple themes and customization options

TROUBLESHOOTING:
- If the app won't start, try running as administrator
- Check that your antivirus isn't blocking the executable
- Ensure you have enough disk space for AI models (1-4 GB)

For more help, visit: https://github.com/ivocreates/OANA-Offline-Ai-and-Note-Assistant
''')
                
            print(f"✅ Portable package created at: {portable_dir}")
            
    def create_batch_installer(self):
        """Create a simple batch file installer for development setup"""
        print("⚙️ Creating development setup script...")
        
        setup_script = '''@echo off
echo ===============================================
echo OANA - Development Environment Setup
echo ===============================================
echo.

echo Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python 3.8+ first.
    echo Download from: https://python.org/downloads/
    pause
    exit /b 1
)

echo.
echo Installing/upgrading pip...
python -m pip install --upgrade pip

echo.
echo Installing project dependencies...
if exist requirements.txt (
    python -m pip install -r requirements.txt
) else (
    echo WARNING: requirements.txt not found
    echo Installing basic dependencies...
    python -m pip install llama-cpp-python PyMuPDF python-docx docx2txt requests
)

echo.
echo Creating necessary directories...
if not exist "models" mkdir models
if not exist "data" mkdir data
if not exist "data\\chat_history" mkdir data\\chat_history
if not exist "logs" mkdir logs

echo.
echo Setting up database...
python -c "from utils.database import OANADatabase; db = OANADatabase(); print('Database initialized')"

echo.
echo ===============================================
echo Setup complete! You can now run OANA with:
echo   python app.py
echo.
echo For first-time use:
echo 1. Download AI models via the app menu
echo 2. Configure settings as needed
echo ===============================================
pause
'''
        
        setup_file = self.project_dir / "setup_dev.bat"
        with open(setup_file, 'w') as f:
            f.write(setup_script)
            
        print(f"✅ Development setup script created: {setup_file}")
        
    def build(self):
        """Main build process"""
        print("🚀 Starting OANA desktop application build...")
        print(f"📂 Project directory: {self.project_dir}")
        print(f"🖥️ Platform: {platform.system()} {platform.release()}")
        print()
        
        try:
            # Step 1: Check dependencies
            self.check_dependencies()
            
            # Step 2: Install requirements
            self.install_requirements()
            
            # Step 3: Build executable
            self.build_executable()
            
            # Step 4: Create portable package
            self.create_portable_package()
            
            # Step 5: Create installer script (for future use with NSIS)
            self.create_installer_script()
            
            # Step 6: Create development setup
            self.create_batch_installer()
            
            print()
            print("🎉 Build completed successfully!")
            print()
            print("📦 Generated files:")
            print(f"   - Executable: {self.dist_dir / 'OANA'}")
            print(f"   - Portable package: {self.project_dir / 'OANA-Portable'}")
            print(f"   - Installer script: {self.project_dir / 'installer.nsi'}")
            print(f"   - Dev setup: {self.project_dir / 'setup_dev.bat'}")
            print()
            print("📋 Next steps:")
            print("   1. Test the portable version")
            print("   2. Install NSIS to create Windows installer")
            print("   3. Distribute OANA-Portable folder or setup.exe")
            
        except Exception as e:
            print(f"❌ Build failed: {e}")
            sys.exit(1)

if __name__ == "__main__":
    builder = OANABuilder()
    builder.build()