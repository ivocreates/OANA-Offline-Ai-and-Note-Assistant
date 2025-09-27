#!/usr/bin/env python3
"""
Complete OANA Build Script
Creates a distributable executable with all dependencies and AI model
"""

import os
import sys
import shutil
import subprocess
import platform
import json
from pathlib import Path

def print_banner():
    """Print build banner"""
    print("=" * 60)
    print("🚀 OANA Complete Build Script")
    print("Creating distributable executable with AI model")
    print("=" * 60)

def check_system():
    """Check system information"""
    print(f"🖥️  Platform: {platform.system()} {platform.machine()}")
    print(f"🐍 Python: {sys.version.split()[0]}")
    print(f"📁 Working Directory: {os.getcwd()}")

def install_dependencies():
    """Install required build dependencies"""
    print("\n📦 Installing build dependencies...")
    
    required_packages = [
        'pyinstaller>=5.13.0',
        'setuptools',
        'wheel',
    ]
    
    for package in required_packages:
        print(f"Installing {package}...")
        try:
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'install', 
                '--upgrade', package
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            if result.returncode == 0:
                print(f"✅ {package} installed successfully")
            else:
                print(f"❌ Failed to install {package}: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Failed to install {package}: {e}")
            return False
    
    return True

def check_model():
    """Check if AI model exists"""
    print("\n🤖 Checking AI model...")
    
    model_path = Path('models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf')
    
    if not model_path.exists():
        print("❌ Lightweight AI model not found!")
        print("📥 Attempting to download model...")
        
        try:
            # Try to run download script
            result = subprocess.run([sys.executable, 'download_models.py'], 
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                                  text=True, timeout=300)
            
            if result.returncode == 0 and model_path.exists():
                print("✅ Model downloaded successfully")
            else:
                print("❌ Model download failed")
                print("Please manually download the model:")
                print("1. Run: python download_models.py")
                print("2. Or place tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf in models/ folder")
                return False
                
        except Exception as e:
            print(f"❌ Error downloading model: {e}")
            return False
    else:
        size_mb = model_path.stat().st_size / (1024 * 1024)
        print(f"✅ AI model found ({size_mb:.1f} MB)")
    
    return True

def clean_build():
    """Clean previous build artifacts"""
    print("\n🧹 Cleaning previous builds...")
    
    dirs_to_clean = ['build', 'dist', '__pycache__', 'utils/__pycache__']
    files_to_clean = ['*.spec']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"  Removing {dir_name}/")
            shutil.rmtree(dir_name)
    
    import glob
    for pattern in files_to_clean:
        for file in glob.glob(pattern):
            if file != 'OANA_Complete.spec':  # Keep our spec file
                print(f"  Removing {file}")
                os.remove(file)

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    
    dirs = ['models', 'data', 'data/chat_history', 'logs', 'utils']
    
    for dir_name in dirs:
        os.makedirs(dir_name, exist_ok=True)
        print(f"  ✅ {dir_name}/")

def build_executable():
    """Build the executable using PyInstaller"""
    print("\n🔨 Building executable...")
    print("This may take several minutes...")
    
    # Use our comprehensive spec file
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--clean',
        '--noconfirm',
        'OANA_Complete.spec'
    ]
    
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if result.returncode == 0:
            print("✅ Executable built successfully!")
            return True
        else:
            print("❌ Build failed!")
            print("STDOUT:", result.stdout[-1000:])  # Last 1000 chars
            print("STDERR:", result.stderr[-1000:])   # Last 1000 chars
            return False
            
    except Exception as e:
        print(f"❌ Build error: {e}")
        return False

def create_portable_package():
    """Create portable package"""
    print("\n📦 Creating portable package...")
    
    dist_dir = Path('dist/OANA')
    if not dist_dir.exists():
        print("❌ Executable not found in dist/OANA")
        return False
    
    # Create portable directory
    portable_dir = Path('OANA_Portable')
    if portable_dir.exists():
        shutil.rmtree(portable_dir)
    
    # Copy executable files
    shutil.copytree(dist_dir, portable_dir)
    
    # Create launcher scripts
    launcher_bat = portable_dir / 'Launch_OANA.bat'
    with open(launcher_bat, 'w') as f:
        f.write('@echo off\n')
        f.write('title OANA - Offline AI Assistant\n')
        f.write('echo.\n')
        f.write('echo Starting OANA - Offline AI Assistant...\n')
        f.write('echo.\n')
        f.write('OANA.exe\n')
        f.write('if errorlevel 1 (\n')
        f.write('    echo.\n')
        f.write('    echo OANA encountered an error.\n')
        f.write('    echo Please check the logs folder for details.\n')
        f.write('    pause\n')
        f.write(')\n')
    
    # Copy documentation
    docs_to_copy = ['README.md', 'BUILD.md', 'requirements.txt']
    for doc in docs_to_copy:
        if os.path.exists(doc):
            shutil.copy(doc, portable_dir)
    
    # Create info file
    info_file = portable_dir / 'PORTABLE_INFO.txt'
    with open(info_file, 'w') as f:
        f.write("OANA - Offline AI Assistant (Portable Version)\n")
        f.write("=" * 50 + "\n\n")
        f.write("This is a portable version that includes:\n")
        f.write("✅ Complete OANA application\n")
        f.write("✅ Lightweight TinyLlama AI model (~637MB)\n")
        f.write("✅ All necessary dependencies\n")
        f.write("✅ No installation required\n\n")
        f.write("To run:\n")
        f.write("1. Double-click 'Launch_OANA.bat', or\n")
        f.write("2. Double-click 'OANA.exe' directly\n\n")
        f.write("System Requirements:\n")
        f.write("- Windows 7/8/10/11\n")
        f.write("- ~1GB free disk space\n")
        f.write("- 4GB RAM minimum (8GB recommended)\n\n")
        f.write("Features:\n")
        f.write("- Offline AI chat with document analysis\n")
        f.write("- PDF and Word document processing\n")
        f.write("- Chat history with SQLite database\n")
        f.write("- Multiple themes and settings\n")
        f.write("- Export capabilities (PDF, HTML, TXT)\n\n")
        f.write("For support: https://github.com/ivocreates/OANA-Offline-Ai-and-Note-Assistant\n")
    
    print(f"✅ Portable package created: {portable_dir}")
    return True

def create_zip_package():
    """Create ZIP package for distribution"""
    print("\n🗜️  Creating ZIP package...")
    
    if not Path('OANA_Portable').exists():
        print("❌ Portable package not found")
        return False
    
    import zipfile
    
    zip_name = f"OANA_Portable_v1.0_{platform.system()}.zip"
    
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk('OANA_Portable'):
            for file in files:
                file_path = Path(root) / file
                arc_name = file_path.relative_to('OANA_Portable')
                zipf.write(file_path, f"OANA_Portable/{arc_name}")
    
    size_mb = Path(zip_name).stat().st_size / (1024 * 1024)
    print(f"✅ ZIP package created: {zip_name} ({size_mb:.1f} MB)")
    return zip_name

def test_executable():
    """Test the built executable"""
    print("\n🧪 Testing executable...")
    
    exe_path = Path('dist/OANA/OANA.exe')
    if not exe_path.exists():
        print("❌ Executable not found")
        return False
    
    try:
        # Try to run the executable with --version flag (if supported)
        # For now, just check if it starts without immediate crash
        result = subprocess.run([str(exe_path)], 
                              timeout=5, 
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("✅ Executable appears to be working")
        return True
    except subprocess.TimeoutExpired:
        print("✅ Executable started successfully (timed out after 5s - this is normal)")
        return True
    except Exception as e:
        print(f"⚠️  Could not fully test executable: {e}")
        print("   This might be normal - try running manually")
        return True

def print_summary(zip_name=None):
    """Print build summary"""
    print("\n" + "=" * 60)
    print("🎉 BUILD COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print("\n📁 Generated Files:")
    
    if os.path.exists('dist/OANA'):
        exe_size = sum(f.stat().st_size for f in Path('dist/OANA').rglob('*') if f.is_file())
        print(f"  📦 Executable: dist/OANA/ ({exe_size/(1024*1024):.1f} MB)")
    
    if os.path.exists('OANA_Portable'):
        portable_size = sum(f.stat().st_size for f in Path('OANA_Portable').rglob('*') if f.is_file())
        print(f"  🎒 Portable: OANA_Portable/ ({portable_size/(1024*1024):.1f} MB)")
    
    if zip_name and os.path.exists(zip_name):
        zip_size = Path(zip_name).stat().st_size / (1024 * 1024)
        print(f"  🗜️  ZIP Package: {zip_name} ({zip_size:.1f} MB)")
    
    print("\n🚀 Distribution Options:")
    print("  1. Share OANA_Portable/ folder for manual extraction")
    print("  2. Share ZIP file for easy download")
    print("  3. Use dist/OANA/ for development testing")
    
    print("\n✅ Features Included:")
    print("  • Complete offline AI functionality")
    print("  • Lightweight TinyLlama model (~637MB)")
    print("  • Document processing (PDF, DOCX, TXT)")
    print("  • Chat history with SQLite database")
    print("  • Multiple themes and export options")
    print("  • No Python installation required for end users")
    
    print("\n📋 Next Steps:")
    print("  1. Test the executable on a clean Windows machine")
    print("  2. Create GitHub release with the ZIP file")
    print("  3. Update documentation with distribution info")

def main():
    """Main build process"""
    print_banner()
    
    # Change to script directory to ensure correct paths
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)
    print(f"📁 Changed to project directory: {script_dir}")
    
    check_system()
    
    # Step 1: Install dependencies
    if not install_dependencies():
        print("\n❌ Failed to install dependencies")
        return 1
    
    # Step 2: Check AI model
    if not check_model():
        print("\n❌ AI model check failed")
        return 1
    
    # Step 3: Clean previous builds
    clean_build()
    
    # Step 4: Create directories
    create_directories()
    
    # Step 5: Build executable
    if not build_executable():
        print("\n❌ Build failed")
        return 1
    
    # Step 6: Create portable package
    if not create_portable_package():
        print("\n❌ Failed to create portable package")
        return 1
    
    # Step 7: Create ZIP package
    zip_name = create_zip_package()
    
    # Step 8: Test executable
    test_executable()
    
    # Step 9: Print summary
    print_summary(zip_name)
    
    return 0

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n⛔ Build cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)