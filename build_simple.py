#!/usr/bin/env python3
"""
Simple OANA Build Script - Direct PyInstaller Command
Creates distributable executable avoiding problematic hooks
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Build OANA with direct PyInstaller command"""
    
    print("🚀 Building OANA with optimized PyInstaller command...")
    print("=" * 60)
    
    # Check if model exists
    model_path = Path('models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf')
    if not model_path.exists():
        print("❌ AI model not found. Please run: python download_models.py")
        return 1
    
    # Direct PyInstaller command with all necessary options
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onedir',                    # Create one directory
        '--windowed',                  # No console window
        '--name=OANA',                 # Executable name
        '--icon=icon.ico',             # Icon (if exists)
        '--clean',                     # Clean cache
        '--noconfirm',                 # Overwrite without asking
        
        # Add data files
        '--add-data', f'{model_path};models/',
        '--add-data', 'config.json;.',
        '--add-data', 'README.md;.',
        '--add-data', 'utils;utils/',
        '--add-data', 'data;data/',
        
        # Hidden imports for core functionality
        '--hidden-import', 'tkinter',
        '--hidden-import', 'tkinter.ttk',
        '--hidden-import', 'tkinter.messagebox',
        '--hidden-import', 'tkinter.filedialog',
        '--hidden-import', 'tkinter.scrolledtext',
        '--hidden-import', 'sqlite3',
        '--hidden-import', 'json',
        '--hidden-import', 'threading',
        '--hidden-import', 'datetime',
        '--hidden-import', 'pathlib',
        
        # AI and document processing
        '--hidden-import', 'llama_cpp',
        '--hidden-import', 'llama_cpp.llama_cpp',
        '--hidden-import', 'numpy',
        '--hidden-import', 'docx',
        '--hidden-import', 'docx2txt',
        '--hidden-import', 'PyMuPDF',
        '--hidden-import', 'fitz',
        '--hidden-import', 'requests',
        
        # Our custom modules
        '--hidden-import', 'utils.ai_engine',
        '--hidden-import', 'utils.pdf_parser',
        '--hidden-import', 'utils.docx_parser',
        '--hidden-import', 'utils.summarizer',
        '--hidden-import', 'utils.database',
        
        # Exclude problematic packages
        '--exclude-module', 'tensorflow',
        '--exclude-module', 'torch',
        '--exclude-module', 'matplotlib',
        '--exclude-module', 'scipy',
        '--exclude-module', 'pandas',
        '--exclude-module', 'jupyter',
        '--exclude-module', 'IPython',
        '--exclude-module', 'PyQt5',
        '--exclude-module', 'PyQt6',
        '--exclude-module', 'PySide2',
        '--exclude-module', 'PySide6',
        
        # Main script
        'app.py'
    ]
    
    print("Command to execute:")
    print(' '.join(f'"{arg}"' if ' ' in arg else arg for arg in cmd))
    print("\nBuilding... This may take several minutes...")
    
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if result.returncode == 0:
            print("✅ Build completed successfully!")
            
            # Check if executable was created
            exe_path = Path('dist/OANA/OANA.exe')
            if exe_path.exists():
                size_mb = sum(f.stat().st_size for f in Path('dist/OANA').rglob('*') if f.is_file()) / (1024*1024)
                print(f"📦 Executable created: {exe_path} (~{size_mb:.1f} MB)")
                
                # Create portable folder
                print("📁 Creating portable package...")
                import shutil
                portable_dir = Path('OANA_Portable')
                if portable_dir.exists():
                    shutil.rmtree(portable_dir)
                shutil.copytree('dist/OANA', portable_dir)
                
                # Create launcher
                with open(portable_dir / 'Launch_OANA.bat', 'w') as f:
                    f.write('@echo off\n')
                    f.write('echo Starting OANA...\n')
                    f.write('OANA.exe\n')
                    f.write('pause\n')
                
                print("✅ Portable package created: OANA_Portable/")
                print("\n🎉 BUILD COMPLETE!")
                print("You can now distribute the OANA_Portable/ folder")
                return 0
            else:
                print("❌ Executable not found after build")
                return 1
        else:
            print("❌ Build failed!")
            print("STDERR:", result.stderr[-2000:])
            return 1
            
    except Exception as e:
        print(f"❌ Error during build: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())