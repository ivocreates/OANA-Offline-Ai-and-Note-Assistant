#!/usr/bin/env python3
"""
OANA Setup and Development Environment Configuration
Comprehensive setup script for development and deployment
"""

import os
import sys
import subprocess
import json
import urllib.request
import shutil
import platform
import importlib
from pathlib import Path

class OANASetup:
    def __init__(self):
        self.project_root = Path(__file__).parent.resolve()
        self.models_dir = self.project_root / "models"
        self.data_dir = self.project_root / "data"
        self.logs_dir = self.project_root / "logs"
        self.utils_dir = self.project_root / "utils"
        
        # Platform detection
        self.is_windows = platform.system() == "Windows"
        self.is_linux = platform.system() == "Linux"
        self.is_macos = platform.system() == "Darwin"
        
    def run_full_setup(self, dev_mode=False):
        """Run complete setup process"""
        print("🚀 Starting OANA Setup")
        print("=" * 60)
        print(f"📍 Project root: {self.project_root}")
        print(f"🖥️  Platform: {platform.system()} {platform.release()}")
        print(f"🐍 Python: {sys.version}")
        if dev_mode:
            print("🔧 Development mode enabled")
        print("=" * 60)
        
        try:
            # Step 1: Environment validation
            self.check_python_version()
            self.check_system_requirements()
            
            # Step 2: Directory structure
            self.create_directories()
            
            # Step 3: Dependencies
            if dev_mode:
                self.setup_development_environment()
            else:
                self.install_dependencies()
                
            # Step 4: Database initialization
            self.initialize_database()
            
            # Step 5: Configuration
            self.create_default_configs()
            
            # Step 6: Model management
            self.setup_model_management()
            
            # Step 7: Final validation
            self.validate_installation()
            
            self.print_success_message(dev_mode)
            
        except Exception as e:
            print(f"\n❌ Setup failed: {e}")
            print("📋 Troubleshooting:")
            print("   1. Ensure Python 3.8+ is installed")
            print("   2. Check internet connection for downloads")
            print("   3. Run as administrator if permission issues")
            print("   4. Check antivirus settings")
            sys.exit(1)
            
    def check_python_version(self):
        """Check if Python version is compatible"""
        print("🐍 Checking Python version...")
        
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            raise Exception(f"Python 3.8+ required. Current version: {version.major}.{version.minor}")
            
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
        
    def check_system_requirements(self):
        """Check system requirements"""
        print("🖥️  Checking system requirements...")
        
        # Check available disk space (at least 2GB for models)
        try:
            total, used, free = shutil.disk_usage(self.project_root)
            free_gb = free // (1024**3)
            
            if free_gb < 2:
                print("⚠️  Warning: Less than 2GB free space available")
                print("   AI models require significant disk space")
                
            print(f"✅ {free_gb}GB free disk space available")
        except:
            print("✅ System check completed")
        
    def create_directories(self):
        """Create necessary directories"""
        print("📁 Creating directories...")
        
        directories = [
            self.models_dir,
            self.data_dir,
            self.logs_dir,
            self.data_dir / "chat_history",
            self.data_dir / "documents"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"✅ {directory.relative_to(self.project_root)}")
            
    def setup_development_environment(self):
        """Setup development environment with additional tools"""
        print("🔧 Setting up development environment...")
        
        # Install main requirements first
        self.install_dependencies()
        
    def initialize_database(self):
        """Initialize SQLite database"""
        print("💾 Initializing database...")
        
        try:
            # Import and initialize database
            sys.path.append(str(self.utils_dir))
            from database import OANADatabase
            
            db = OANADatabase(str(self.project_root / "oana.db"))
            print("✅ Database initialized successfully")
            
        except Exception as e:
            print(f"⚠️  Database initialization failed: {e}")
            print("   Database will be created on first app run")
            
    def create_default_configs(self):
        """Create default configuration files"""
        print("⚙️ Creating default configurations...")
        
        # Default settings
        default_settings = {
            "theme": "light",
            "auto_save_chat": True,
            "chat_history_limit": 1000,
            "auto_export_format": "txt",
            "ui_settings": {
                "font_size": 10,
                "show_timestamps": True,
                "compact_mode": False
            },
            "ai_settings": {
                "temperature": 0.7,
                "max_tokens": 512,
                "system_prompt": "You are OANA, a helpful offline AI assistant."
            },
            "model_settings": {
                "preferred_backend": "llama-cpp",
                "model_path": "",
                "auto_load": False
            }
        }
        
        config_file = self.project_root / "user_settings.json"
        if not config_file.exists():
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(default_settings, f, indent=2)
            print("✅ Default settings created")
        else:
            print("✅ Settings file exists")
            
    def setup_model_management(self):
        """Setup model management"""
        print("🤖 Setting up model management...")
        
        # Check for existing models
        model_files = list(self.models_dir.glob("*.gguf"))
        if model_files:
            print(f"✅ Found {len(model_files)} model(s)")
            for model in model_files:
                try:
                    size_mb = model.stat().st_size / (1024*1024)
                    print(f"   - {model.name} ({size_mb:.1f}MB)")
                except:
                    print(f"   - {model.name}")
        else:
            print("⚠️  No models found")
            print("   Download models through the application menu")
            
    def validate_installation(self):
        """Validate the installation"""
        print("✅ Validating installation...")
        
        # Check critical files
        critical_files = [
            "app.py",
            "utils/ai_engine.py",
            "utils/database.py",
            "requirements.txt"
        ]
        
        for file_path in critical_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                print(f"✅ {file_path}")
            else:
                print(f"❌ Missing: {file_path}")
                
        # Test imports
        try:
            import tkinter
            print("✅ Tkinter available")
        except ImportError:
            print("❌ Tkinter not available")
            
    def print_success_message(self, dev_mode=False):
        """Print success message with instructions"""
        print("\n" + "=" * 60)
        print("🎉 OANA Setup Completed Successfully!")
        print("=" * 60)
        print()
        print("📋 Next steps:")
        print("   1. Run: python app.py")
        print("   2. Download AI models through the app menu")
        print("   3. Configure settings as needed")
        print()
        
        if dev_mode:
            print("🔧 Development environment ready!")
            print()
            
        print("📚 Documentation: README.md")
        print("🐛 Issues: https://github.com/ivocreates/OANA-Offline-Ai-and-Note-Assistant/issues")
        print("=" * 60)
            
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
        self.install_ai_backend()
        
        print("✓ Dependencies installation completed")
        
    def install_ai_backend(self):
        """Install AI backend with user choice"""
        print("\n🤖 Setting up AI Backend")
        print("Choose an AI backend to install:")
        print("1. llama-cpp-python (Recommended - for local GGUF models)")
        print("2. Skip AI backend installation (install manually later)")
        
        while True:
            try:
                choice = input("Enter choice (1-2): ").strip()
                
                if choice == "1":
                    print("Installing llama-cpp-python...")
                    try:
                        subprocess.run([sys.executable, "-m", "pip", "install", "llama-cpp-python>=0.2.0"], 
                                     check=True)
                        print("✅ llama-cpp-python installed successfully")
                        break
                    except subprocess.CalledProcessError:
                        print("⚠️  Failed to install llama-cpp-python")
                        print("You can install it manually later with: pip install llama-cpp-python")
                        break
                        
                elif choice == "2":
                    print("⚠️  Skipping AI backend installation")
                    print("Install manually later with one of:")
                    print("  pip install llama-cpp-python")
                    print("  pip install ollama")
                    break
                else:
                    print("Invalid choice. Please enter 1 or 2.")
                    
            except KeyboardInterrupt:
                print("\nSkipping AI backend installation...")
                break
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
        
        # Check multiple possible model locations
        possible_model_dirs = [
            self.models_dir,
            Path.cwd() / "models",
            Path.home() / ".oana" / "models"
        ]
        
        model_found = False
        for models_dir in possible_model_dirs:
            if models_dir.exists():
                model_files = list(models_dir.glob("*.gguf"))
                if model_files:
                    model_found = True
                    print(f"✅ Found {len(model_files)} GGUF model(s) in {models_dir}")
                    for model_file in model_files:
                        size_mb = model_file.stat().st_size / (1024 * 1024)
                        print(f"   - {model_file.name} ({size_mb:.1f} MB)")
                    break
        
        if not model_found:
            print("⚠️  No GGUF models found")
            print("To use AI functionality, you need to download models.")
            print("\nOptions:")
            print("1. Run: python download_models.py")
            print("2. Manually place .gguf files in the 'models/' directory")
            print("3. Use Ollama (install separately)")
            
            self.suggest_models()
            
            # Offer to download models
            try:
                choice = input("\nWould you like to download recommended models now? (y/n): ").strip().lower()
                if choice in ['y', 'yes']:
                    self.download_recommended_models()
                else:
                    print("You can download models later using 'python download_models.py'")
            except KeyboardInterrupt:
                print("\nSkipping model download...")
            
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
        
    def download_recommended_models(self):
        """Download recommended models using the model downloader"""
        try:
            from download_models import ModelDownloader
            downloader = ModelDownloader()
            print("Starting download of recommended models...")
            downloader.download_recommended()
            print("✅ Model download completed!")
        except ImportError:
            print("❌ Model downloader not available")
            print("Please run: python download_models.py")
        except Exception as e:
            print(f"❌ Model download failed: {e}")
            print("You can try downloading manually with: python download_models.py")
        
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
    
    # Determine if development mode
    dev_mode = "--dev" in sys.argv or "--development" in sys.argv
    
    setup_manager = OANASetup()
    setup_manager.run_full_setup(dev_mode)
    

if __name__ == "__main__":
    main()
