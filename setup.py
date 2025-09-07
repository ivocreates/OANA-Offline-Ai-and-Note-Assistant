#!/usr/bin/env python3
"""
Setup script for Offline AI ChatBot
Handles initial setup, dependency installation, and model downloading
"""

import os
import sys
import subprocess
import json
import urllib.request
import shutil
from pathlib import Path

class SetupManager:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.models_dir = self.project_root / "models"
        self.data_dir = self.project_root / "data"
        
    def run_setup(self):
        """Run complete setup process"""
        print("🚀 Starting Offline AI ChatBot Setup")
        print("=" * 50)
        
        try:
            # Step 1: Check Python version
            self.check_python_version()
            
            # Step 2: Create directories
            self.create_directories()
            
            # Step 3: Install dependencies
            self.install_dependencies()
            
            # Step 4: Check for models
            self.check_models()
            
            # Step 5: Final setup
            self.final_setup()
            
            print("\n✅ Setup completed successfully!")
            print("Run 'python app.py' to start the application.")
            
        except Exception as e:
            print(f"\n❌ Setup failed: {e}")
            print("Please check the troubleshooting guide in README.md")
            sys.exit(1)
            
    def check_python_version(self):
        """Check Python version compatibility"""
        print("Checking Python version...")
        
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 9):
            raise Exception(f"Python 3.9+ required. Current version: {version.major}.{version.minor}")
            
        print(f"✓ Python {version.major}.{version.minor}.{version.micro} detected")
        
    def create_directories(self):
        """Create necessary directories"""
        print("Creating directories...")
        
        directories = [
            self.models_dir,
            self.data_dir,
            self.project_root / "logs"
        ]
        
        for directory in directories:
            directory.mkdir(exist_ok=True)
            print(f"✓ Created {directory}")
            
    def install_dependencies(self):
        """Install required dependencies"""
        print("Installing dependencies...")
        
        requirements_file = self.project_root / "requirements.txt"
        if not requirements_file.exists():
            raise Exception("requirements.txt not found")
            
        # Install basic requirements first
        basic_requirements = [
            "PyMuPDF>=1.23.0",
            "python-docx>=0.8.11",
            "nltk>=3.8.1",
            "requests>=2.31.0",
            "numpy>=1.24.0"
        ]
        
        print("Installing basic requirements...")
        for req in basic_requirements:
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", req], 
                             check=True, capture_output=True)
                print(f"✓ Installed {req}")
            except subprocess.CalledProcessError as e:
                print(f"⚠️  Warning: Failed to install {req}")
                
        # Try to install AI backend
        print("Installing AI backend...")
        ai_backends = [
            "llama-cpp-python>=0.2.0",
            # "torch",
            # "transformers>=4.30.0"
        ]
        
        for backend in ai_backends:
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", backend], 
                             check=True, capture_output=True, timeout=300)
                print(f"✓ Installed {backend}")
                break
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                print(f"⚠️  Failed to install {backend}")
                
    def check_models(self):
        """Check for available models"""
        print("Checking for AI models...")
        
        model_files = list(self.models_dir.glob("*.gguf"))
        
        if model_files:
            print(f"✓ Found {len(model_files)} model file(s):")
            for model in model_files:
                size_mb = model.stat().st_size / (1024 * 1024)
                print(f"  - {model.name} ({size_mb:.1f} MB)")
        else:
            print("⚠️  No model files found in models/ directory")
            print("You can:")
            print("  1. Download models manually to the models/ directory")
            print("  2. Use the built-in model downloader in the app")
            print("  3. Install Ollama for alternative AI backend")
            
            self.suggest_models()
            
    def suggest_models(self):
        """Suggest models to download"""
        print("\n📋 Recommended models for download:")
        
        models = [
            {
                "name": "TinyLlama-1.1B-Chat-v1.0.Q4_K_M.gguf",
                "size": "637 MB",
                "description": "Lightweight, good for basic chat",
                "url": "https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/blob/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
            },
            {
                "name": "Llama-2-7B-Chat.Q4_K_M.gguf",
                "size": "4.1 GB",
                "description": "Better quality, requires more RAM",
                "url": "https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF"
            }
        ]
        
        for i, model in enumerate(models, 1):
            print(f"{i}. {model['name']}")
            print(f"   Size: {model['size']}")
            print(f"   Description: {model['description']}")
            print(f"   URL: {model['url']}")
            print()
            
        print("Download these files to the 'models/' directory to enable AI functionality.")
        
    def final_setup(self):
        """Final setup steps"""
        print("Performing final setup...")
        
        # Create example config if it doesn't exist
        config_file = self.project_root / "config.json"
        if config_file.exists():
            print("✓ Configuration file found")
        else:
            print("✓ Using default configuration")
            
        # Download NLTK data
        try:
            import nltk
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            print("✓ Downloaded NLTK data")
        except:
            print("⚠️  NLTK data download failed (not critical)")
            
    def create_launcher_script(self):
        """Create launcher script"""
        if os.name == 'nt':  # Windows
            launcher_content = '''@echo off
cd /d "%~dp0"
python app.py
pause
'''
            with open(self.project_root / "start.bat", 'w') as f:
                f.write(launcher_content)
            print("✓ Created start.bat launcher")
        else:  # Unix-like
            launcher_content = '''#!/bin/bash
cd "$(dirname "$0")"
python3 app.py
'''
            launcher_file = self.project_root / "start.sh"
            with open(launcher_file, 'w') as f:
                f.write(launcher_content)
            launcher_file.chmod(0o755)
            print("✓ Created start.sh launcher")


def main():
    """Main setup function"""
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h']:
        print("""
Offline AI ChatBot Setup Script

Usage:
    python setup.py          # Run full setup
    python setup.py --help   # Show this help message

This script will:
1. Check Python version compatibility
2. Create necessary directories  
3. Install required dependencies
4. Check for AI models
5. Prepare the application for first run

After setup, run: python app.py
        """)
        return
        
    setup_manager = SetupManager()
    setup_manager.run_setup()
    

if __name__ == "__main__":
    main()
