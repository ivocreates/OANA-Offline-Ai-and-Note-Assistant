#!/usr/bin/env python3
"""
Dependency checker for OANA
Checks for required dependencies and AI backends
"""

import sys
import importlib
import subprocess
from pathlib import Path

class DependencyChecker:
    def __init__(self):
        self.required_packages = [
            ("PyMuPDF", "fitz", "PDF processing"),
            ("python-docx", "docx", "Word document processing"),
            ("nltk", "nltk", "Text processing"),
            ("requests", "requests", "HTTP requests"),
            ("numpy", "numpy", "Numerical operations"),
        ]
        
        self.ai_backends = [
            ("llama-cpp-python", "llama_cpp", "Local GGUF model support", True),
            ("ollama", "ollama", "Ollama integration", False),
            ("torch", "torch", "PyTorch for transformers", False),
            ("transformers", "transformers", "Hugging Face models", False),
        ]
        
    def check_python_version(self):
        """Check Python version"""
        print("🐍 Checking Python version...")
        version = sys.version_info
        
        if version.major < 3 or (version.major == 3 and version.minor < 9):
            print(f"❌ Python 3.9+ required. Current: {version.major}.{version.minor}")
            return False
        else:
            print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
            return True
    
    def check_package(self, package_name, import_name, description=""):
        """Check if a package is installed"""
        try:
            importlib.import_module(import_name)
            print(f"✅ {package_name} - {description}")
            return True
        except ImportError:
            print(f"❌ {package_name} - {description} (Not installed)")
            return False
    
    def check_required_packages(self):
        """Check all required packages"""
        print("\n📦 Checking required packages...")
        all_present = True
        missing_packages = []
        
        for package_name, import_name, description in self.required_packages:
            if not self.check_package(package_name, import_name, description):
                all_present = False
                missing_packages.append(package_name)
        
        if missing_packages:
            print(f"\n❌ Missing required packages: {', '.join(missing_packages)}")
            print("Install with: pip install " + " ".join(missing_packages))
        
        return all_present, missing_packages
    
    def check_ai_backends(self):
        """Check AI backend availability"""
        print("\n🤖 Checking AI backends...")
        available_backends = []
        recommended_missing = []
        
        for package_name, import_name, description, recommended in self.ai_backends:
            if self.check_package(package_name, import_name, description):
                available_backends.append(package_name)
            elif recommended:
                recommended_missing.append(package_name)
        
        if not available_backends:
            print("\n⚠️  No AI backends available!")
            print("Install at least one AI backend:")
            print("  Recommended: pip install llama-cpp-python")
            print("  Alternative: pip install torch transformers")
            print("  Alternative: Install Ollama separately")
        elif recommended_missing:
            print(f"\n⚠️  Recommended backend missing: {', '.join(recommended_missing)}")
            print("For best performance, install: pip install " + " ".join(recommended_missing))
        
        return available_backends, recommended_missing
    
    def check_models(self):
        """Check for downloaded models"""
        print("\n📁 Checking for AI models...")
        
        possible_model_dirs = [
            Path(__file__).parent / "models",
            Path.cwd() / "models",
            Path.home() / ".oana" / "models"
        ]
        
        model_found = False
        for models_dir in possible_model_dirs:
            if models_dir.exists():
                gguf_files = list(models_dir.glob("*.gguf"))
                if gguf_files:
                    model_found = True
                    print(f"✅ Found {len(gguf_files)} GGUF model(s) in {models_dir}")
                    for model_file in gguf_files:
                        size_mb = model_file.stat().st_size / (1024 * 1024)
                        print(f"   • {model_file.name} ({size_mb:.1f} MB)")
                    break
        
        if not model_found:
            print("❌ No GGUF models found")
            print("Download models with: python download_models.py")
            print("Or place .gguf files in the 'models/' directory")
        
        return model_found
    
    def install_missing_packages(self, missing_packages):
        """Install missing packages"""
        if not missing_packages:
            return True
        
        print(f"\n📥 Installing missing packages: {', '.join(missing_packages)}")
        
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install"
            ] + missing_packages, check=True)
            
            print("✅ Packages installed successfully!")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install packages: {e}")
            print("Try installing manually:")
            print(f"pip install {' '.join(missing_packages)}")
            return False
    
    def run_full_check(self, fix=False):
        """Run full dependency check"""
        print("🔍 OANA Dependency Check")
        print("=" * 40)
        
        all_good = True
        
        # Check Python version
        if not self.check_python_version():
            all_good = False
        
        # Check required packages
        packages_ok, missing_packages = self.check_required_packages()
        if not packages_ok:
            all_good = False
            if fix:
                if self.install_missing_packages(missing_packages):
                    packages_ok = True
        
        # Check AI backends
        available_backends, missing_backends = self.check_ai_backends()
        if not available_backends:
            all_good = False
            if fix and missing_backends:
                if self.install_missing_packages(missing_backends):
                    available_backends = missing_backends
        
        # Check models
        models_found = self.check_models()
        if not models_found:
            print("\n💡 Tip: Run 'python download_models.py' to download AI models")
        
        print("\n" + "=" * 40)
        
        if all_good and models_found:
            print("✅ All dependencies satisfied! OANA should work perfectly.")
        elif packages_ok and available_backends:
            print("✅ Core dependencies satisfied! Download models to enable AI features.")
        else:
            print("❌ Missing dependencies. OANA may not work properly.")
            print("\nQuick fix commands:")
            if missing_packages:
                print(f"pip install {' '.join(missing_packages)}")
            if not available_backends:
                print("pip install llama-cpp-python")
            if not models_found:
                print("python download_models.py")
        
        return all_good and models_found


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Check OANA dependencies")
    parser.add_argument("--fix", action="store_true", 
                       help="Try to install missing packages automatically")
    parser.add_argument("--quiet", "-q", action="store_true",
                       help="Only show errors and warnings")
    
    args = parser.parse_args()
    
    checker = DependencyChecker()
    success = checker.run_full_check(fix=args.fix)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()