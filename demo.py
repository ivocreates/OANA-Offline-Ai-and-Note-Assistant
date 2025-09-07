"""
Quick demo script to test the application functionality
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from ai_engine import AIEngine
from pdf_parser import PDFParser
from docx_parser import DocxParser
from summarizer import Summarizer

def test_components():
    print("🧪 Testing Application Components")
    print("=" * 40)
    
    # Test AI Engine
    print("1. Testing AI Engine...")
    try:
        ai = AIEngine()
        print(f"   Backend: {ai.backend}")
        print(f"   Ready: {ai.is_ready()}")
        
        # Test response generation
        response = ai.generate_response("Hello, how are you?")
        print(f"   Sample response: {response[:100]}...")
        print("   ✅ AI Engine works")
    except Exception as e:
        print(f"   ❌ AI Engine error: {e}")
    
    # Test PDF Parser
    print("\n2. Testing PDF Parser...")
    try:
        pdf_parser = PDFParser()
        print(f"   Available: {pdf_parser.is_available()}")
        print("   ✅ PDF Parser ready")
    except Exception as e:
        print(f"   ❌ PDF Parser error: {e}")
    
    # Test DOCX Parser  
    print("\n3. Testing DOCX Parser...")
    try:
        docx_parser = DocxParser()
        print(f"   Available: {docx_parser.is_available()}")
        print("   ✅ DOCX Parser ready")
    except Exception as e:
        print(f"   ❌ DOCX Parser error: {e}")
    
    # Test Summarizer
    print("\n4. Testing Summarizer...")
    try:
        ai = AIEngine()
        summarizer = Summarizer(ai)
        
        test_text = "This is a test document with some text content. It contains multiple sentences to test the summarization functionality. The summarizer should be able to process this text and create a meaningful summary."
        
        summary = summarizer.summarize(test_text, max_length=100)
        print(f"   Sample summary: {summary[:100]}...")
        print("   ✅ Summarizer works")
    except Exception as e:
        print(f"   ❌ Summarizer error: {e}")
    
    print("\n🎉 Component testing complete!")

if __name__ == "__main__":
    test_components()
