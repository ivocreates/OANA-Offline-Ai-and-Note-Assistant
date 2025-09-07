#!/usr/bin/env python3
"""
Model downloader utility for Offline AI ChatBot
Downloads recommended AI models from Hugging Face
"""

import os
import sys
import urllib.request
import urllib.error
from pathlib import Path
import json

class ModelDownloader:
    def __init__(self):
        self.models_dir = Path(__file__).parent / "models"
        self.models_dir.mkdir(exist_ok=True)
        
        # Recommended models with direct download links
        self.recommended_models = [
            {
                "name": "TinyLlama-1.1B-Chat",
                "filename": "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",
                "size": "637 MB",
                "description": "Lightweight model, good for basic chat",
                "url": "https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf",
                "recommended": True
            },
            {
                "name": "Phi-2",
                "filename": "phi-2.Q4_K_M.gguf", 
                "size": "1.6 GB",
                "description": "Microsoft Phi-2, excellent quality",
                "url": "https://huggingface.co/TheBloke/phi-2-GGUF/resolve/main/phi-2.Q4_K_M.gguf",
                "recommended": True
            },
            {
                "name": "Llama-2-7B-Chat",
                "filename": "llama-2-7b-chat.Q4_K_M.gguf",
                "size": "4.1 GB", 
                "description": "High quality conversational AI",
                "url": "https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF/resolve/main/llama-2-7b-chat.Q4_K_M.gguf",
                "recommended": False
            },
            {
                "name": "CodeLlama-7B",
                "filename": "codellama-7b-instruct.Q4_K_M.gguf",
                "size": "4.1 GB",
                "description": "Specialized for code generation",
                "url": "https://huggingface.co/TheBloke/CodeLlama-7B-Instruct-GGUF/resolve/main/codellama-7b-instruct.Q4_K_M.gguf", 
                "recommended": False
            }
        ]
        
    def list_models(self):
        """List available models"""
        print("🤖 Available AI Models")
        print("=" * 50)
        
        for i, model in enumerate(self.recommended_models, 1):
            status = "⭐ RECOMMENDED" if model["recommended"] else ""
            print(f"{i}. {model['name']} {status}")
            print(f"   Size: {model['size']}")
            print(f"   Description: {model['description']}")
            
            # Check if already downloaded
            local_path = self.models_dir / model['filename']
            if local_path.exists():
                size_mb = local_path.stat().st_size / (1024 * 1024)
                print(f"   Status: ✅ Downloaded ({size_mb:.1f} MB)")
            else:
                print(f"   Status: ⬇️  Available for download")
            print()
            
    def download_model(self, model_index):
        """Download a specific model"""
        if model_index < 1 or model_index > len(self.recommended_models):
            print("❌ Invalid model selection")
            return False
            
        model = self.recommended_models[model_index - 1]
        local_path = self.models_dir / model['filename']
        
        if local_path.exists():
            print(f"✅ Model {model['name']} already exists")
            return True
            
        print(f"📥 Downloading {model['name']} ({model['size']})...")
        print(f"URL: {model['url']}")
        print(f"Destination: {local_path}")
        print()
        
        try:
            def progress_hook(block_num, block_size, total_size):
                if total_size > 0:
                    percent = block_num * block_size * 100 / total_size
                    downloaded = block_num * block_size
                    downloaded_mb = downloaded / (1024 * 1024)
                    total_mb = total_size / (1024 * 1024)
                    
                    print(f"\rProgress: {percent:.1f}% ({downloaded_mb:.1f}/{total_mb:.1f} MB)", end="")
                    
            urllib.request.urlretrieve(model['url'], local_path, progress_hook)
            print(f"\n✅ Successfully downloaded {model['name']}")
            return True
            
        except urllib.error.URLError as e:
            print(f"\n❌ Download failed: {e}")
            if local_path.exists():
                local_path.unlink()  # Remove partial file
            return False
        except KeyboardInterrupt:
            print(f"\n⚠️  Download cancelled by user")
            if local_path.exists():
                local_path.unlink()  # Remove partial file
            return False
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            if local_path.exists():
                local_path.unlink()  # Remove partial file
            return False
            
    def download_recommended(self):
        """Download all recommended models"""
        recommended = [i for i, model in enumerate(self.recommended_models, 1) if model["recommended"]]
        
        print(f"📥 Downloading {len(recommended)} recommended models...")
        print()
        
        success_count = 0
        for model_index in recommended:
            if self.download_model(model_index):
                success_count += 1
            print()
            
        print(f"✅ Downloaded {success_count}/{len(recommended)} recommended models")
        
    def get_model_info(self, filename):
        """Get information about a model file"""
        for model in self.recommended_models:
            if model['filename'] == filename:
                return model
        return None
        
    def interactive_download(self):
        """Interactive model selection and download"""
        while True:
            print("\n🤖 Model Download Menu")
            print("=" * 30)
            print("1. List available models")
            print("2. Download specific model")
            print("3. Download all recommended models") 
            print("4. Check downloaded models")
            print("5. Exit")
            
            try:
                choice = input("\nSelect option (1-5): ").strip()
                
                if choice == '1':
                    self.list_models()
                    
                elif choice == '2':
                    self.list_models()
                    try:
                        model_num = int(input(f"\nEnter model number (1-{len(self.recommended_models)}): "))
                        self.download_model(model_num)
                    except ValueError:
                        print("❌ Please enter a valid number")
                        
                elif choice == '3':
                    self.download_recommended()
                    
                elif choice == '4':
                    self.check_downloaded_models()
                    
                elif choice == '5':
                    print("👋 Goodbye!")
                    break
                    
                else:
                    print("❌ Invalid option. Please select 1-5.")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
                
    def check_downloaded_models(self):
        """Check what models are already downloaded"""
        print("\n📁 Downloaded Models")
        print("=" * 30)
        
        model_files = list(self.models_dir.glob("*.gguf"))
        
        if not model_files:
            print("❌ No model files found in models/ directory")
            print("Use this script to download models or place them manually")
            return
            
        total_size = 0
        for model_file in model_files:
            size_mb = model_file.stat().st_size / (1024 * 1024)
            total_size += size_mb
            
            # Try to get model info
            model_info = self.get_model_info(model_file.name)
            if model_info:
                print(f"✅ {model_info['name']}")
                print(f"   File: {model_file.name}")
                print(f"   Size: {size_mb:.1f} MB")
                print(f"   Description: {model_info['description']}")
            else:
                print(f"✅ {model_file.name}")
                print(f"   Size: {size_mb:.1f} MB")
                print(f"   Description: Custom model")
            print()
            
        print(f"📊 Total: {len(model_files)} models ({total_size:.1f} MB)")


def main():
    """Main function"""
    downloader = ModelDownloader()
    
    if len(sys.argv) == 1:
        # Interactive mode
        downloader.interactive_download()
    else:
        # Command line mode
        command = sys.argv[1].lower()
        
        if command in ['list', 'ls']:
            downloader.list_models()
            
        elif command in ['download', 'dl']:
            if len(sys.argv) > 2:
                try:
                    model_num = int(sys.argv[2])
                    downloader.download_model(model_num)
                except ValueError:
                    print("❌ Please provide a valid model number")
            else:
                print("❌ Please specify model number: python download_models.py download 1")
                
        elif command in ['recommended', 'rec']:
            downloader.download_recommended()
            
        elif command in ['check', 'status']:
            downloader.check_downloaded_models()
            
        elif command in ['help', '--help', '-h']:
            print("""
Model Downloader for Offline AI ChatBot

Usage:
    python download_models.py                    # Interactive mode
    python download_models.py list              # List available models  
    python download_models.py download 1        # Download specific model
    python download_models.py recommended       # Download recommended models
    python download_models.py check             # Check downloaded models
    python download_models.py help              # Show this help

Models are downloaded to the 'models/' directory.
            """)
        else:
            print(f"❌ Unknown command: {command}")
            print("Use 'python download_models.py help' for usage information")


if __name__ == "__main__":
    main()
