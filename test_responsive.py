#!/usr/bin/env python3
"""Test responsive window setup"""

import tkinter as tk
import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import OANA
    
    def test_responsive_window():
        """Test the responsive window functionality"""
        print("Testing responsive window setup...")
        
        root = tk.Tk()
        app = OANA(root)
        
        # Test responsive setup
        app._setup_responsive_window()
        
        print(f"Window geometry: {root.geometry()}")
        print(f"Screen dimensions: {app.screen_width}x{app.screen_height}")
        print(f"Minimum size: {root.minsize()}")
        
        # Show window briefly
        root.update()
        root.after(2000, root.destroy)  # Close after 2 seconds
        root.mainloop()
        
        print("Responsive window test completed!")
        return True
        
    if __name__ == "__main__":
        test_responsive_window()
        
except Exception as e:
    print(f"Error testing responsive window: {e}")
    if __name__ == "__main__":
        sys.exit(1)