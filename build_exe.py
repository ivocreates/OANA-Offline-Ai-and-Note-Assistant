#!/usr/bin/env python3
"""
OANA Build Script - Creates distributable executable with lightweight AI model
Usage: python build_exe.py
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path

def check_requirements():
    """Check if all required packages are installed"""
    required_packages = ['PyInstaller']
    missing = []
    
    for package in required_packages:
        try:
            __import__(package.lower().replace('-', '_'))
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"Missing packages: {missing}")
        print("Installing missing packages...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing)

def clean_build():
    """Clean previous build artifacts"""
    dirs_to_clean = ['build', 'dist', 'prod']
    files_to_clean = ['*.spec', '*.exe']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"Cleaning {dir_name}/")
            shutil.rmtree(dir_name)
    
    for pattern in files_to_clean:
        import glob
        for file in glob.glob(pattern):
            print(f"Removing {file}")
            os.remove(file)

def create_spec_file():
    """Create PyInstaller spec file with proper configuration"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf', 'models/'),
        ('config.json', '.'),
        ('README.md', '.'),
        ('requirements.txt', '.'),
        ('utils', 'utils/'),
        ('data', 'data/'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.filedialog',
        'sqlite3',
        'json',
        'threading',
        'queue',
        'datetime',
        'llama_cpp',
        'docx',
        'PyPDF2',
        'requests',
        'weasyprint',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if os.path.exists('icon.ico') else None,
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
    
    with open('OANA.spec', 'w') as f:
        f.write(spec_content)
    print("Created OANA.spec")

def build_executable():
    """Build the executable using PyInstaller"""
    print("Building executable...")
    
    # Create the spec file
    create_spec_file()
    
    # Run PyInstaller
    cmd = [sys.executable, '-m', 'PyInstaller', '--clean', 'OANA.spec']
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print("Build failed!")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
        else:
            print("Build successful!")
            return True
    except Exception as e:
        print(f"Build error: {e}")
        return False

def create_installer():
    """Create NSIS installer if available"""
    if not shutil.which('makensis'):
        print("NSIS not found. Skipping installer creation.")
        print("To create installer, install NSIS from https://nsis.sourceforge.io/")
        return False
    
    # Check if build_installer.py exists
    if not os.path.exists('build_installer.py'):
        print("build_installer.py not found. Skipping installer creation.")
        return False
    
    print("Creating installer...")
    try:
        subprocess.check_call([sys.executable, 'build_installer.py'])
        print("Installer created successfully!")
        return True
    except Exception as e:
        print(f"Installer creation failed: {e}")
        return False

def create_portable_package():
    """Create portable package in prod/ directory"""
    if not os.path.exists('dist/OANA'):
        print("Executable not found in dist/OANA")
        return False
    
    print("Creating portable package...")
    
    # Create prod directory
    prod_dir = Path('prod')
    prod_dir.mkdir(exist_ok=True)
    
    # Copy executable files
    app_dir = prod_dir / 'OANA-Portable'
    if app_dir.exists():
        shutil.rmtree(app_dir)
    
    shutil.copytree('dist/OANA', app_dir)
    
    # Create run script
    run_script = app_dir / 'run_oana.bat'
    with open(run_script, 'w') as f:
        f.write('@echo off\n')
        f.write('echo Starting OANA...\n')
        f.write('OANA.exe\n')
        f.write('pause\n')
    
    # Copy documentation
    docs_to_copy = ['README.md', 'USAGE.py', 'requirements.txt']
    for doc in docs_to_copy:
        if os.path.exists(doc):
            shutil.copy(doc, app_dir)
    
    print(f"Portable package created in: {app_dir}")
    return True

def main():
    """Main build process"""
    print("=" * 50)
    print("OANA Build Script")
    print("=" * 50)
    
    # Check system
    print(f"Platform: {platform.system()} {platform.machine()}")
    print(f"Python: {sys.version}")
    
    # Check if model exists
    model_path = 'models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf'
    if not os.path.exists(model_path):
        print(f"Model not found at {model_path}")
        print("Downloading lightweight model...")
        try:
            # Try to download the model
            subprocess.check_call([sys.executable, 'download_models.py'])
        except Exception as e:
            print(f"Model download failed: {e}")
            print("Please manually download the model or run: python download_models.py")
            return 1
    
    # Check requirements
    print("\nChecking requirements...")
    check_requirements()
    
    # Clean previous builds
    print("\nCleaning previous builds...")
    clean_build()
    
    # Build executable
    print("\nBuilding executable...")
    if not build_executable():
        return 1
    
    # Create portable package
    print("\nCreating portable package...")
    create_portable_package()
    
    # Create installer (optional)
    print("\nCreating installer...")
    create_installer()
    
    print("\n" + "=" * 50)
    print("Build completed successfully!")
    print("\nOutput files:")
    if os.path.exists('dist/OANA'):
        print(f"- Executable: dist/OANA/")
    if os.path.exists('prod/OANA-Portable'):
        print(f"- Portable: prod/OANA-Portable/")
    
    # Find installer files
    for ext in ['.exe']:
        for name in ['oana-installer', 'setup', 'installer']:
            installer = f"{name}{ext}"
            if os.path.exists(installer):
                print(f"- Installer: {installer}")
    
    print("\nTo distribute:")
    print("1. Use prod/OANA-Portable/ for portable version")
    print("2. Use installer.exe for full installation")
    print("3. Both include the lightweight TinyLlama model")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())