#!/usr/bin/env python3
"""
Quick UI Test for OANA
Tests the enhanced UI components and styling
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# Add the project directory to path
sys.path.insert(0, os.path.dirname(__file__))

def test_ui_enhancements():
    """Test the enhanced UI components"""
    root = tk.Tk()
    root.title("OANA UI Test")
    root.geometry("600x400")
    
    # Test modern theme
    themes = {
        "light": {
            "bg": "#ffffff",
            "fg": "#2c3e50",
            "accent": "#3498db",
            "panel_bg": "#ecf0f1",
            "entry_bg": "#f8f9fa",
            "button_bg": "#3498db",
            "button_fg": "#ffffff"
        }
    }
    
    theme = themes["light"]
    root.configure(bg=theme["bg"])
    
    # Test title bar
    title_frame = tk.Frame(root, bg=theme["accent"], height=60)
    title_frame.pack(fill=tk.X)
    title_frame.pack_propagate(False)
    
    title_label = tk.Label(title_frame, 
                          text="🧠 OANA - UI Test", 
                          font=("Segoe UI", 16, "bold"), 
                          fg="white", 
                          bg=theme["accent"])
    title_label.pack(side=tk.LEFT, padx=20, pady=15)
    
    status_label = tk.Label(title_frame, 
                           text="✅ UI Test Running", 
                           font=("Segoe UI", 10), 
                           fg="white", 
                           bg=theme["accent"])
    status_label.pack(side=tk.RIGHT, padx=20, pady=15)
    
    # Test main content area
    main_frame = tk.Frame(root, bg=theme["bg"])
    main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
    
    # Test modern entry
    entry_frame = tk.Frame(main_frame, bg=theme["bg"])
    entry_frame.pack(fill=tk.X, pady=(0, 10))
    
    tk.Label(entry_frame, text="Modern Input:", 
             font=("Segoe UI", 11, "bold"), 
             bg=theme["bg"], fg=theme["fg"]).pack(anchor=tk.W)
    
    test_entry = tk.Entry(entry_frame,
                         font=("Segoe UI", 11),
                         bg=theme["entry_bg"],
                         fg=theme["fg"],
                         relief=tk.FLAT,
                         borderwidth=1)
    test_entry.pack(fill=tk.X, pady=5)
    test_entry.insert(0, "Test the modern input styling...")
    
    # Test modern buttons
    button_frame = tk.Frame(main_frame, bg=theme["bg"])
    button_frame.pack(fill=tk.X, pady=10)
    
    tk.Label(button_frame, text="Modern Buttons:", 
             font=("Segoe UI", 11, "bold"), 
             bg=theme["bg"], fg=theme["fg"]).pack(anchor=tk.W, pady=(0, 5))
    
    # Create modern-style buttons
    btn1 = tk.Button(button_frame, text="📁 Primary Action",
                     font=("Segoe UI", 9),
                     bg=theme["button_bg"], fg=theme["button_fg"],
                     relief=tk.FLAT, borderwidth=0,
                     padx=15, pady=8)
    btn1.pack(side=tk.LEFT, padx=(0, 10))
    
    btn2 = tk.Button(button_frame, text="⚙️ Secondary Action",
                     font=("Segoe UI", 9),
                     bg=theme["panel_bg"], fg=theme["fg"],
                     relief=tk.FLAT, borderwidth=1,
                     padx=15, pady=8)
    btn2.pack(side=tk.LEFT)
    
    # Test text area
    text_frame = tk.Frame(main_frame, bg=theme["bg"])
    text_frame.pack(fill=tk.BOTH, expand=True, pady=10)
    
    tk.Label(text_frame, text="Modern Text Area:", 
             font=("Segoe UI", 11, "bold"), 
             bg=theme["bg"], fg=theme["fg"]).pack(anchor=tk.W, pady=(0, 5))
    
    test_text = tk.Text(text_frame,
                       font=("Segoe UI", 10),
                       bg=theme["entry_bg"],
                       fg=theme["fg"],
                       relief=tk.FLAT,
                       borderwidth=1,
                       padx=12, pady=8)
    test_text.pack(fill=tk.BOTH, expand=True)
    test_text.insert(tk.END, """🎉 UI Enhancement Test

This is a test of the enhanced OANA user interface:
• Modern typography with Segoe UI font
• Clean flat design with subtle borders  
• Consistent color scheme and spacing
• Better emoji support with fallbacks
• Enhanced visual hierarchy

The new design should provide a more professional and pleasant user experience while maintaining excellent usability.""")
    
    # Status message
    status_frame = tk.Frame(root, bg=theme["panel_bg"], height=30)
    status_frame.pack(fill=tk.X)
    status_frame.pack_propagate(False)
    
    status_msg = tk.Label(status_frame, 
                         text="✨ UI enhancements loaded successfully", 
                         font=("Segoe UI", 9), 
                         bg=theme["panel_bg"], fg=theme["fg"])
    status_msg.pack(pady=5)
    
    root.mainloop()

if __name__ == "__main__":
    print("🚀 Testing OANA UI enhancements...")
    test_ui_enhancements()
    print("✅ UI test completed!")