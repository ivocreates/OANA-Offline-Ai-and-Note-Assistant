#!/usr/bin/env python3
"""
OANA (Offline AI and Note Assistant) - Quick Launch Script
This script provides a safe way to launch OANA with proper error handling.
"""

import sys
import os
import traceback
from pathlib import Path

def main():
    """Main launch function with error handling"""
    try:
        # Add the current directory to Python path
        current_dir = Path(__file__).parent.absolute()
        sys.path.insert(0, str(current_dir))
        
        # Check for required directories
        utils_dir = current_dir / "utils"
        if not utils_dir.exists():
            print("❌ Error: utils directory not found!")
            print("Please ensure you're running this script from the OANA directory.")
            input("Press Enter to exit...")
            return
        
        # Import and run the main application
        print("🚀 Starting OANA (Offline AI and Note Assistant)...")
        print("📍 Working directory:", current_dir)
        
        try:
            from app import OANA
            app = OANA()
            app.run()
        except ImportError as e:
            print(f"❌ Import Error: {e}")
            print("\n🔧 This might be due to missing dependencies.")
            print("Please run: python -m pip install -r requirements.txt")
        except Exception as e:
            print(f"❌ Application Error: {e}")
            print("\n📋 Full error details:")
            traceback.print_exc()
            
    except Exception as e:
        print(f"❌ Launch Error: {e}")
        print("\n📋 Full error details:")
        traceback.print_exc()
    
    print("\n👋 OANA has closed.")
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()
