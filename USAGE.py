"""
🤖 Offline AI ChatBot - Usage Guide
==================================

This application is now ready to use! Here's how to get started:

QUICK START:
1. Run: python app.py (or double-click start.bat)
2. For AI functionality: python download_models.py
3. Download TinyLlama-1.1B (recommended for beginners)

FEATURES:
✅ ChatGPT-like conversational interface
✅ PDF/Word document processing and Q&A
✅ Document summarization
✅ Completely offline operation
✅ Multiple AI backend support
✅ Built-in troubleshooting

HOW TO USE:
1. Basic Chat: Type messages and press Enter
2. Upload Documents: File > Upload PDF/Doc
3. Ask Questions: Switch to "document_qa" mode
4. Summarize: Select document and click "Summarize"

NEXT STEPS:
- Download an AI model for full functionality
- Upload PDF/Word documents for processing
- Explore the settings and help menus
"""

import os
import sys
from pathlib import Path

def show_usage_guide():
    print(__doc__)
    
    # Show current status
    print("\n📊 CURRENT STATUS:")
    print("=" * 30)
    
    # Check models
    models_dir = Path(__file__).parent / "models"
    model_files = list(models_dir.glob("*.gguf")) if models_dir.exists() else []
    
    if model_files:
        print(f"✅ AI Models: {len(model_files)} found")
        for model in model_files:
            size_mb = model.stat().st_size / (1024 * 1024)
            print(f"   - {model.name} ({size_mb:.1f} MB)")
    else:
        print("⚠️  AI Models: None found")
        print("   Run: python download_models.py")
    
    # Check dependencies
    try:
        import fitz, docx, llama_cpp
        print("✅ Dependencies: All installed")
    except ImportError as e:
        print(f"❌ Dependencies: Missing {e}")
    
    print("\n🚀 READY TO START!")
    print("Run: python app.py")

if __name__ == "__main__":
    show_usage_guide()
