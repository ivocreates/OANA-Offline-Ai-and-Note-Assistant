#!/usr/bin/env python3
"""
Quick test to verify button text visibility
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# Add the utils directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

def test_button_styles():
    """Test button styles and text visibility"""
    root = tk.Tk()
    root.title("Button Visibility Test")
    root.geometry("600x400")
    
    # Configure ttk style
    style = ttk.Style()
    
    # Try to use a theme that supports better customization
    try:
        style.theme_use('clam')
        print("Using 'clam' theme")
    except:
        try:
            style.theme_use('alt')
            print("Using 'alt' theme")
        except:
            print("Using default theme")
    
    # Configure button styles with high contrast
    style.configure("TButton",
                   padding=(10, 6),
                   relief="raised",
                   borderwidth=1,
                   focuscolor="none",
                   font=("Segoe UI", 9, "bold"),
                   foreground="#ffffff",
                   background="#3498db")
    
    style.map("TButton",
              background=[('active', '#2980b9'),
                        ('pressed', '#21618c')],
              foreground=[('active', '#ffffff'),
                        ('pressed', '#ffffff')],
              relief=[('pressed', 'sunken'),
                     ('active', 'raised')])
    
    # Success button
    style.configure("Success.TButton",
                   foreground="#ffffff",
                   background="#27ae60")
    style.map("Success.TButton",
              background=[('active', '#219a52')],
              foreground=[('active', '#ffffff')])
    
    # Warning button  
    style.configure("Warning.TButton",
                   foreground="#ffffff",
                   background="#f39c12")
    style.map("Warning.TButton",
              background=[('active', '#e67e22')],
              foreground=[('active', '#ffffff')])
    
    # Danger button
    style.configure("Danger.TButton",
                   foreground="#ffffff", 
                   background="#e74c3c")
    style.map("Danger.TButton",
              background=[('active', '#c0392b')],
              foreground=[('active', '#ffffff')])
    
    # Create test frame
    frame = ttk.Frame(root, padding="20")
    frame.pack(fill=tk.BOTH, expand=True)
    
    ttk.Label(frame, text="Button Visibility Test", 
             font=("Segoe UI", 16, "bold")).pack(pady=20)
    
    # Test buttons
    button_frame = ttk.Frame(frame)
    button_frame.pack(pady=20)
    
    ttk.Button(button_frame, text="Default Button").pack(side=tk.LEFT, padx=10)
    ttk.Button(button_frame, text="Success Button", style="Success.TButton").pack(side=tk.LEFT, padx=10)
    ttk.Button(button_frame, text="Warning Button", style="Warning.TButton").pack(side=tk.LEFT, padx=10)
    ttk.Button(button_frame, text="Danger Button", style="Danger.TButton").pack(side=tk.LEFT, padx=10)
    
    # Test with emojis
    emoji_frame = ttk.Frame(frame)
    emoji_frame.pack(pady=20)
    
    ttk.Button(emoji_frame, text="📤 Upload").pack(side=tk.LEFT, padx=10)
    ttk.Button(emoji_frame, text="💾 Save", style="Success.TButton").pack(side=tk.LEFT, padx=10)
    ttk.Button(emoji_frame, text="🧹 Clear", style="Warning.TButton").pack(side=tk.LEFT, padx=10)
    ttk.Button(emoji_frame, text="🗑️ Delete", style="Danger.TButton").pack(side=tk.LEFT, padx=10)
    
    def close_test():
        print("✅ Button test completed!")
        root.destroy()
    
    ttk.Button(frame, text="Close Test", command=close_test).pack(pady=20)
    
    print("🔍 Testing button visibility...")
    print("Check if all button text is clearly visible!")
    
    root.mainloop()

if __name__ == "__main__":
    test_button_styles()