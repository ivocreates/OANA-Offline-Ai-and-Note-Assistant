#!/usr/bin/env python3
"""
Test script for Offline AI ChatBot
Verifies that all components are working correctly
"""

import os
import sys
import importlib
from pathlib import Path

def test_python_version():
    """Test Python version"""
    print("Testing Python version...")
    version = sys.version_info
    
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print(f"❌ FAIL: Python 3.9+ required. Current: {version.major}.{version.minor}")
        return False
    else:
        print(f"✅ PASS: Python {version.major}.{version.minor}.{version.micro}")
        return True

def test_dependencies():
    """Test required dependencies"""
    print("\nTesting dependencies...")
    
    required_modules = [
        ('tkinter', 'tkinter (GUI framework)'),
        ('fitz', 'PyMuPDF (PDF processing)'), 
        ('docx', 'python-docx (Word document processing)'),
        ('llama_cpp', 'llama-cpp-python (AI backend)'),
        ('nltk', 'NLTK (text processing)'),
        ('numpy', 'NumPy (numerical computing)'),
        ('requests', 'Requests (HTTP library)')
    ]
    
    results = []
    for module_name, description in required_modules:
        try:
            importlib.import_module(module_name)
            print(f"✅ PASS: {description}")
            results.append(True)
        except ImportError:
            print(f"❌ FAIL: {description} - Not installed")
            results.append(False)
        except Exception as e:
            print(f"⚠️  WARN: {description} - Error: {e}")
            results.append(False)
    
    return all(results)

def test_project_structure():
    """Test project directory structure"""
    print("\nTesting project structure...")
    
    required_files = [
        'app.py',
        'setup.py', 
        'requirements.txt',
        'config.json',
        'README.md'
    ]
    
    required_dirs = [
        'utils',
        'models',
        'data'
    ]
    
    project_root = Path(__file__).parent
    results = []
    
    # Check files
    for filename in required_files:
        filepath = project_root / filename
        if filepath.exists():
            print(f"✅ PASS: {filename} exists")
            results.append(True)
        else:
            print(f"❌ FAIL: {filename} missing")
            results.append(False)
    
    # Check directories  
    for dirname in required_dirs:
        dirpath = project_root / dirname
        if dirpath.exists() and dirpath.is_dir():
            print(f"✅ PASS: {dirname}/ directory exists")
            results.append(True)
        else:
            print(f"❌ FAIL: {dirname}/ directory missing")
            results.append(False)
            
    return all(results)

def test_utility_modules():
    """Test utility modules"""
    print("\nTesting utility modules...")
    
    sys.path.append(str(Path(__file__).parent / 'utils'))
    
    modules_to_test = [
        ('pdf_parser', 'PDFParser'),
        ('docx_parser', 'DocxParser'),
        ('ai_engine', 'AIEngine'),
        ('summarizer', 'Summarizer')
    ]
    
    results = []
    for module_name, class_name in modules_to_test:
        try:
            module = importlib.import_module(module_name)
            cls = getattr(module, class_name)
            print(f"✅ PASS: {module_name}.{class_name} can be imported")
            results.append(True)
        except ImportError as e:
            print(f"❌ FAIL: {module_name}.{class_name} import error: {e}")
            results.append(False)
        except AttributeError as e:
            print(f"❌ FAIL: {module_name}.{class_name} class not found: {e}")
            results.append(False)
        except Exception as e:
            print(f"⚠️  WARN: {module_name}.{class_name} error: {e}")
            results.append(False)
    
    return all(results)

def test_ai_models():
    """Test AI models availability"""
    print("\nTesting AI models...")
    
    models_dir = Path(__file__).parent / 'models'
    
    if not models_dir.exists():
        print("❌ FAIL: models/ directory not found")
        return False
        
    model_files = list(models_dir.glob('*.gguf'))
    
    if not model_files:
        print("⚠️  WARN: No .gguf model files found in models/")
        print("   Download models using: python download_models.py")
        return False
    else:
        total_size = 0
        for model_file in model_files:
            size_mb = model_file.stat().st_size / (1024 * 1024)
            total_size += size_mb
            print(f"✅ PASS: Found {model_file.name} ({size_mb:.1f} MB)")
            
        print(f"📊 Total: {len(model_files)} models ({total_size:.1f} MB)")
        return True

def test_gui_components():
    """Test GUI components"""
    print("\nTesting GUI components...")
    
    try:
        import tkinter as tk
        
        # Try creating a test window
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        # Test basic widgets
        frame = tk.Frame(root)
        label = tk.Label(frame, text="Test")
        button = tk.Button(frame, text="Test")
        entry = tk.Entry(frame)
        
        print("✅ PASS: Basic tkinter widgets work")
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"❌ FAIL: GUI test failed: {e}")
        return False

def test_configuration():
    """Test configuration file"""
    print("\nTesting configuration...")
    
    config_file = Path(__file__).parent / 'config.json'
    
    if not config_file.exists():
        print("⚠️  WARN: config.json not found, will use defaults")
        return True
        
    try:
        import json
        with open(config_file, 'r') as f:
            config = json.load(f)
            
        required_sections = ['ai_settings', 'ui_settings', 'document_settings']
        
        for section in required_sections:
            if section in config:
                print(f"✅ PASS: Configuration section '{section}' found")
            else:
                print(f"⚠️  WARN: Configuration section '{section}' missing")
                
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ FAIL: config.json is invalid JSON: {e}")
        return False
    except Exception as e:
        print(f"❌ FAIL: Configuration test error: {e}")
        return False

def run_comprehensive_test():
    """Run all tests"""
    print("🧪 Running Offline AI ChatBot Tests")
    print("=" * 50)
    
    tests = [
        ("Python Version", test_python_version),
        ("Dependencies", test_dependencies),
        ("Project Structure", test_project_structure),
        ("Utility Modules", test_utility_modules),
        ("AI Models", test_ai_models),
        ("GUI Components", test_gui_components),
        ("Configuration", test_configuration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Test: {test_name}")
        print("-" * 30)
        
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ FAIL: Test crashed: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Application should work correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Check the issues above.")
        return False

def main():
    """Main function"""
    if len(sys.argv) > 1:
        test_name = sys.argv[1].lower()
        
        test_map = {
            'python': test_python_version,
            'deps': test_dependencies,
            'structure': test_project_structure,
            'modules': test_utility_modules,
            'models': test_ai_models,
            'gui': test_gui_components,
            'config': test_configuration
        }
        
        if test_name in test_map:
            print(f"Running {test_name} test...")
            test_map[test_name]()
        else:
            print(f"Unknown test: {test_name}")
            print(f"Available tests: {', '.join(test_map.keys())}")
    else:
        run_comprehensive_test()

if __name__ == "__main__":
    main()
