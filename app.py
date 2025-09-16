#!/usr/bin/env python3
"""
OANA - Offline AI and Note Assistant
A powerful desktop application for AI chat, document processing, and note-taking
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox, colorchooser, simpledialog
import threading
import os
import sys
import json
from datetime import datetime
import webbrowser
from pathlib import Path
import tempfile
import subprocess
import sqlite3
import platform

# Add utils to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

try:
    from pdf_parser import PDFParser
    from docx_parser import DocxParser
    from ai_engine import AIEngine
    from summarizer import Summarizer
    from database import OANADatabase
except ImportError as e:
    print(f"Import error: {e}")
    print("Some modules are not available. Please install dependencies.")

class OANA:
    def __init__(self, root):
        self.root = root
        self.root.title("OANA - Offline AI and Note Assistant")
        self.root.geometry("1400x900")
        self.root.minsize(1000, 700)
        
        # Theme and styling with enhanced visual design
        self.current_theme = "light"
        self.themes = {
            "light": {
                "bg": "#ffffff",
                "fg": "#2c3e50",
                "select_bg": "#3498db",
                "select_fg": "#ffffff",
                "entry_bg": "#f8f9fa",
                "panel_bg": "#ecf0f1",
                "accent": "#3498db",
                "success": "#27ae60",
                "warning": "#f39c12",
                "danger": "#e74c3c",
                "border": "#bdc3c7",
                "hover": "#e8f4fd",
                "button_bg": "#3498db",
                "button_fg": "#ffffff",
                "button_hover": "#2980b9"
            },
            "dark": {
                "bg": "#1a1a1a",
                "fg": "#e1e1e1",
                "select_bg": "#3498db",
                "select_fg": "#ffffff",
                "entry_bg": "#2d2d2d",
                "panel_bg": "#252525",
                "accent": "#3498db",
                "success": "#27ae60",
                "warning": "#f39c12",
                "danger": "#e74c3c",
                "border": "#404040",
                "hover": "#333333",
                "button_bg": "#3498db",
                "button_fg": "#ffffff",
                "button_hover": "#2980b9"
            },
            "blue": {
                "bg": "#1e3a5f",
                "fg": "#ffffff",
                "select_bg": "#4a90e2",
                "select_fg": "#ffffff", 
                "entry_bg": "#2c5282",
                "panel_bg": "#2d4a73",
                "accent": "#4a90e2",
                "success": "#48bb78",
                "warning": "#ed8936",
                "danger": "#f56565",
                "border": "#4a6fa5",
                "hover": "#3d5a8a",
                "button_bg": "#4a90e2",
                "button_fg": "#ffffff",
                "button_hover": "#357abd"
            },
            "modern": {
                "bg": "#fafafa",
                "fg": "#1a1a1a",
                "select_bg": "#667eea",
                "select_fg": "#ffffff",
                "entry_bg": "#ffffff",
                "panel_bg": "#f0f0f0",
                "accent": "#667eea",
                "success": "#10b981",
                "warning": "#f59e0b",
                "danger": "#ef4444",
                "border": "#e5e5e5",
                "hover": "#f3f4f6",
                "button_bg": "#667eea",
                "button_fg": "#ffffff",
                "button_hover": "#5a67d8"
            }
        }
        
        # Emoji fallbacks for better cross-platform compatibility
        self.emoji_fallbacks = {
            "📁": "File",
            "💾": "Save",
            "📊": "Export", 
            "🗑️": "Clear",
            "🚪": "Exit",
            "🤖": "AI",
            "📥": "Download",
            "🔄": "Reload",
            "⚙️": "Settings",
            "🎨": "Themes",
            "💬": "Chat",
            "🔧": "Tools",
            "🗂️": "Files",
            "🆘": "Help",
            "ℹ️": "About",
            "🔍": "Search",
            "📝": "Note",
            "🔒": "Security",
            "✅": "Success",
            "❌": "Error",
            "⚠️": "Warning"
        }
        
        # Initialize components
        self.ai_engine = None
        self.pdf_parser = PDFParser()
        self.docx_parser = DocxParser()
        self.summarizer = None
        
        # Initialize database
        try:
            data_dir = os.path.join(os.path.dirname(__file__), "data")
            os.makedirs(data_dir, exist_ok=True)
            self.db = OANADatabase(os.path.join(data_dir, "oana.db"))
        except Exception as e:
            print(f"Database initialization failed: {e}")
            self.db = None
        
        # Data storage (now backed by database)
        self.chat_history = []
        self.uploaded_documents = []
        self.current_context = ""
        self.current_session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.settings = self._load_settings()
        
        # Create new chat session
        if self.db:
            try:
                self.db.create_chat_session(self.current_session_id)
            except Exception as e:
                print(f"Failed to create chat session: {e}")
                
        # Apply theme
        self.apply_theme()
        
        # Load data from database
        self.load_data_from_database()
        
        # Initialize UI
        self.setup_styles()
        self.setup_ui()
        self.setup_menu()
        
        # Initialize AI engine in background
        self.initialize_ai_engine()
        
        # Auto-save settings
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def load_data_from_database(self):
        """Load chat history and documents from database"""
        if not self.db:
            return
            
        try:
            # Load chat history for current session
            db_chat_history = self.db.get_chat_history(self.current_session_id)
            for msg in db_chat_history:
                self.chat_history.append({
                    'sender': msg['role'],
                    'content': msg['message'],
                    'timestamp': msg['timestamp']
                })
            
            # Load documents
            db_documents = self.db.get_documents()
            self.uploaded_documents = []
            for doc in db_documents:
                doc_info = {
                    'id': doc['id'],
                    'name': doc['name'],
                    'path': doc['path'],
                    'content': doc['content'],
                    'upload_time': doc['upload_time'],
                    'size': doc['size'],
                    'type': doc['type']
                }
                self.uploaded_documents.append(doc_info)
                
        except Exception as e:
            print(f"Failed to load data from database: {e}")
    
    def get_emoji_label(self, emoji, text):
        """Get emoji with fallback for better compatibility"""
        try:
            # Test if emoji can be displayed (simple check)
            test_label = tk.Label(self.root, text=emoji)
            test_label.destroy()  # Clean up test widget
            return f"{emoji} {text}"
        except:
            # Use fallback if emoji fails
            fallback = self.emoji_fallbacks.get(emoji, "")
            if fallback:
                return f"[{fallback}] {text}"
            return text
    
    def _load_settings(self):
        """Load user settings"""
        settings_file = Path(__file__).parent / "user_settings.json"
        default_settings = {
            "theme": "light",
            "auto_save_chat": True,
            "chat_history_limit": 1000,
            "auto_export_format": "txt",
            "ai_settings": {
                "temperature": 0.7,
                "max_tokens": 512,
                "top_p": 0.9,
                "system_prompt": "You are OANA, a helpful offline AI assistant specialized in document analysis and note-taking."
            },
            "ui_settings": {
                "font_size": 10,
                "show_timestamps": True,
                "compact_mode": False
            },
            "model_settings": {
                "preferred_backend": "llama-cpp",
                "auto_load_model": True
            }
        }
        
        try:
            if settings_file.exists():
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    # Merge with defaults
                    for key, value in default_settings.items():
                        if key not in settings:
                            settings[key] = value
                        elif isinstance(value, dict):
                            for subkey, subvalue in value.items():
                                if subkey not in settings[key]:
                                    settings[key][subkey] = subvalue
                    return settings
        except Exception as e:
            print(f"Error loading settings: {e}")
            
        return default_settings
        
    def save_settings(self):
        """Save user settings"""
        try:
            settings_file = Path(__file__).parent / "user_settings.json"
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving settings: {e}")
            
    def apply_theme(self):
        """Apply current theme and refresh all UI elements"""
        theme = self.themes[self.settings.get("theme", "light")]
        self.root.configure(bg=theme["bg"])
        
        # Refresh styles with new theme
        self.setup_styles()
        
        # Update existing UI elements if they exist
        if hasattr(self, 'chat_display'):
            self.chat_display.configure(
                bg=theme["entry_bg"], 
                fg=theme["fg"],
                selectbackground=theme["select_bg"],
                selectforeground=theme["select_fg"]
            )
            
        if hasattr(self, 'message_entry'):
            self.message_entry.configure(
                bg=theme["entry_bg"],
                fg=theme["fg"],
                insertbackground=theme["fg"]
            )
            
        # Update any text widgets
        for widget in self.root.winfo_children():
            self._update_widget_theme(widget, theme)
    
    def _update_widget_theme(self, widget, theme):
        """Recursively update widget themes"""
        try:
            widget_class = widget.winfo_class()
            
            if widget_class == 'Text':
                widget.configure(
                    bg=theme["entry_bg"],
                    fg=theme["fg"],
                    selectbackground=theme["select_bg"],
                    selectforeground=theme["select_fg"],
                    insertbackground=theme["fg"]
                )
            elif widget_class == 'Entry':
                widget.configure(
                    bg=theme["entry_bg"],
                    fg=theme["fg"],
                    selectbackground=theme["select_bg"],
                    selectforeground=theme["select_fg"],
                    insertbackground=theme["fg"]
                )
            elif widget_class == 'Frame':
                widget.configure(bg=theme["bg"])
            elif widget_class == 'Label':
                widget.configure(bg=theme["bg"], fg=theme["fg"])
                
            # Recursively update children
            for child in widget.winfo_children():
                self._update_widget_theme(child, theme)
                
        except Exception:
            # Some widgets might not support certain options
            pass
        
    def setup_styles(self):
        """Setup enhanced ttk styles for modern theming"""
        style = ttk.Style()
        theme = self.themes[self.settings.get("theme", "light")]
        
        # Configure default ttk button style to ensure all buttons have proper theming
        style.configure("TButton",
                       padding=(12, 8),
                       relief="flat",
                       borderwidth=0,
                       font=("Segoe UI", 9, "bold"),
                       background=theme["button_bg"],
                       foreground=theme["button_fg"])
        
        style.map("TButton",
                  background=[('active', theme["button_hover"]),
                            ('pressed', theme["accent"]),
                            ('disabled', theme["border"])],
                  foreground=[('disabled', theme["fg"])])
        
        # Configure modern button styles with hover effects
        style.configure("Modern.TButton",
                       padding=(12, 8),
                       relief="flat",
                       borderwidth=0,
                       font=("Segoe UI", 9, "bold"),
                       background=theme["button_bg"],
                       foreground=theme["button_fg"])
        
        style.map("Modern.TButton",
                  background=[('active', theme["button_hover"]),
                            ('pressed', theme["accent"])])
        
        # Enhanced label styles
        style.configure("TLabel", 
                       font=("Segoe UI", 9), 
                       foreground=theme["fg"],
                       background=theme["bg"])
        
        style.configure("Title.TLabel", 
                       font=("Segoe UI", 16, "bold"), 
                       foreground=theme["accent"],
                       background=theme["bg"])
        
        style.configure("Heading.TLabel", 
                       font=("Segoe UI", 11, "bold"), 
                       foreground=theme["fg"],
                       background=theme["bg"])
        
        style.configure("Subtitle.TLabel", 
                       font=("Segoe UI", 9), 
                       foreground=theme["fg"],
                       background=theme["bg"])
        
        # Enhanced frame styles
        style.configure("Card.TFrame",
                       relief="flat",
                       borderwidth=1,
                       background=theme["panel_bg"])
        
        # Enhanced entry styles
        style.configure("Modern.TEntry",
                       relief="flat",
                       borderwidth=1,
                       fieldbackground=theme["entry_bg"],
                       foreground=theme["fg"],
                       font=("Segoe UI", 9))
        
        # Enhanced treeview styles
        style.configure("Modern.Treeview",
                       background=theme["entry_bg"],
                       foreground=theme["fg"],
                       fieldbackground=theme["entry_bg"],
                       font=("Segoe UI", 9))
        
        style.configure("Modern.Treeview.Heading",
                       background=theme["panel_bg"],
                       foreground=theme["fg"],
                       font=("Segoe UI", 9, "bold"))
        
        # Button variants with high contrast
        style.configure("Success.TButton", 
                       background=theme["success"],
                       foreground="white",
                       font=("Segoe UI", 9, "bold"))
        style.map("Success.TButton",
                  background=[('active', '#219a52'),
                            ('pressed', '#1e8449')])
        
        style.configure("Warning.TButton", 
                       background=theme["warning"],
                       foreground="white",
                       font=("Segoe UI", 9, "bold"))
        style.map("Warning.TButton",
                  background=[('active', '#e67e22'),
                            ('pressed', '#d35400')])
        
        style.configure("Danger.TButton", 
                       background=theme["danger"],
                       foreground="white",
                       font=("Segoe UI", 9, "bold"))
        style.map("Danger.TButton",
                  background=[('active', '#c0392b'),
                            ('pressed', '#a93226')])
        
        style.configure("Info.TButton", 
                       background=theme["accent"],
                       foreground="white",
                       font=("Segoe UI", 9, "bold"))
        style.map("Info.TButton",
                  background=[('active', theme["button_hover"]),
                            ('pressed', '#2471a3')])
        
        # Enhanced frame styles
        style.configure("TFrame",
                       background=theme["bg"],
                       relief="flat")
        
        style.configure("Card.TFrame",
                       background=theme["panel_bg"],
                       relief="flat",
                       borderwidth=1)
        
        # Enhanced panedwindow styles
        style.configure("TPanedwindow",
                       background=theme["bg"])
        
        # Enhanced notebook styles
        style.configure("Modern.TNotebook",
                       background=theme["bg"],
                       borderwidth=0)
        
        style.configure("Modern.TNotebook.Tab",
                       background=theme["panel_bg"],
                       foreground=theme["fg"],
                       padding=[12, 8],
                       font=("Segoe UI", 9))
        
        style.map("Modern.TNotebook.Tab",
                  background=[('selected', theme["accent"]),
                            ('active', theme["hover"])],
                  foreground=[('selected', theme["select_fg"])])
        
        # Enhanced progressbar
        style.configure("Modern.TProgressbar",
                       background=theme["accent"],
                       borderwidth=0,
                       lightcolor=theme["accent"],
                       darkcolor=theme["accent"])
        
    def setup_menu(self):
        """Setup enhanced menu bar with better emoji support"""
        menubar = tk.Menu(self.root, bg=self.themes[self.current_theme]["panel_bg"],
                         font=("Segoe UI", 9))
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0, font=("Segoe UI", 9))
        menubar.add_cascade(label=self.get_emoji_label("📁", "File"), menu=file_menu)
        file_menu.add_command(label=self.get_emoji_label("📤", "Upload Document"), 
                             command=self.upload_document, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label=self.get_emoji_label("💾", "Save Chat History"), 
                             command=self.save_chat_history, accelerator="Ctrl+S")
        file_menu.add_command(label=self.get_emoji_label("📄", "Export Chat as PDF"), 
                             command=self.export_chat_pdf)
        file_menu.add_command(label=self.get_emoji_label("📊", "Export Chat as HTML"), 
                             command=self.export_chat_html)
        file_menu.add_separator()
        file_menu.add_command(label=self.get_emoji_label("🧹", "Clear Chat History"), 
                             command=self.clear_chat_confirm)
        file_menu.add_command(label=self.get_emoji_label("🗑️", "Clear All Documents"), 
                             command=self.clear_documents)
        file_menu.add_separator()
        file_menu.add_command(label=self.get_emoji_label("🚪", "Exit"), 
                             command=self.on_closing, accelerator="Alt+F4")
        
        # AI Models menu
        models_menu = tk.Menu(menubar, tearoff=0, font=("Segoe UI", 9))
        menubar.add_cascade(label=self.get_emoji_label("🤖", "AI Models"), menu=models_menu)
        models_menu.add_command(label=self.get_emoji_label("📥", "Download Models"), 
                               command=self.show_model_downloader)
        models_menu.add_command(label=self.get_emoji_label("🔄", "Reload Model"), 
                               command=self.reload_ai_model)
        models_menu.add_command(label=self.get_emoji_label("⚙️", "Model Settings"), 
                               command=self.show_ai_settings)
        models_menu.add_separator()
        models_menu.add_command(label=self.get_emoji_label("📊", "Model Status"), 
                               command=self.show_model_status)
        
        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0, font=("Segoe UI", 9))
        menubar.add_cascade(label=self.get_emoji_label("⚙️", "Settings"), menu=settings_menu)
        settings_menu.add_command(label=self.get_emoji_label("🎨", "Themes"), 
                                 command=self.show_theme_settings)
        settings_menu.add_command(label=self.get_emoji_label("💬", "Chat Settings"), 
                                 command=self.show_chat_settings)
        settings_menu.add_command(label=self.get_emoji_label("🤖", "AI Configuration"), 
                                 command=self.show_ai_settings)
        settings_menu.add_command(label=self.get_emoji_label("🔧", "Advanced Settings"), 
                                 command=self.show_advanced_settings)
        settings_menu.add_separator()
        settings_menu.add_command(label=self.get_emoji_label("↩️", "Reset to Defaults"), 
                                 command=self.reset_settings)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0, font=("Segoe UI", 9))
        menubar.add_cascade(label=self.get_emoji_label("🔧", "Tools"), menu=tools_menu)
        tools_menu.add_command(label=self.get_emoji_label("🤖", "AI Model Selector"), 
                              command=self.show_model_selector)
        tools_menu.add_separator()
        tools_menu.add_command(label=self.get_emoji_label("📊", "Statistics"), 
                              command=self.show_statistics)
        tools_menu.add_command(label=self.get_emoji_label("🗂️", "File Manager"), 
                              command=self.show_file_manager)
        tools_menu.add_command(label=self.get_emoji_label("🧪", "Test Components"), 
                              command=self.run_component_test)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0, font=("Segoe UI", 9))
        menubar.add_cascade(label=self.get_emoji_label("❓", "Help"), menu=help_menu)
        help_menu.add_command(label=self.get_emoji_label("📖", "User Guide"), 
                             command=self.show_user_guide)
        help_menu.add_command(label=self.get_emoji_label("🆘", "Troubleshooting"), 
                             command=self.show_troubleshooting)
        help_menu.add_command(label=self.get_emoji_label("🎯", "Keyboard Shortcuts"), 
                             command=self.show_shortcuts)
        help_menu.add_separator()
        help_menu.add_command(label=self.get_emoji_label("ℹ️", "About OANA"), 
                             command=self.show_about)
        
        # Bind keyboard shortcuts
        self.root.bind('<Control-o>', lambda e: self.upload_document())
        self.root.bind('<Control-s>', lambda e: self.save_chat_history())
        self.root.bind('<Control-n>', lambda e: self.clear_chat_confirm())
        self.root.bind('<F1>', lambda e: self.show_user_guide())
        self.root.bind('<F5>', lambda e: self.reload_ai_model())
        
    def setup_ui(self):
        """Setup the enhanced user interface with modern styling"""
        # Create main container with theme colors
        theme = self.themes[self.settings.get("theme", "light")]
        
        # Modern title bar with gradient-like appearance
        title_frame = tk.Frame(self.root, bg=theme["accent"], height=60)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        # Main title with better typography
        title_label = tk.Label(title_frame, 
                              text=self.get_emoji_label("🧠", "OANA - Offline AI Assistant"), 
                              font=("Segoe UI", 16, "bold"), 
                              fg="white", 
                              bg=theme["accent"])
        title_label.pack(side=tk.LEFT, padx=20, pady=15)
        
        # Enhanced status indicators
        status_frame = tk.Frame(title_frame, bg=theme["accent"])
        status_frame.pack(side=tk.RIGHT, padx=20, pady=15)
        
        self.connection_status = tk.Label(status_frame, 
                                        text=self.get_emoji_label("⚡", "Initializing..."), 
                                        font=("Segoe UI", 10), 
                                        fg="white", 
                                        bg=theme["accent"])
        self.connection_status.pack(side=tk.TOP, anchor=tk.E)
        
        # Create main frame with modern card-like appearance
        main_container = tk.Frame(self.root, bg=theme["bg"])
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        main_frame = ttk.Frame(main_container, padding="15", style="Card.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid weights for responsive design
        main_frame.columnconfigure(1, weight=2)  # Chat gets more space
        main_frame.rowconfigure(1, weight=1)
        
        # Left panel for documents (enhanced)
        self.setup_document_panel(main_frame)
        
        # Right panel for chat (enhanced)
        self.setup_chat_panel(main_frame)
        
        # Status bar with more information
        self.setup_enhanced_status_bar()
        
    def setup_document_panel(self, parent):
        """Setup enhanced document management panel"""
        theme = self.themes[self.settings.get("theme", "light")]
        
        # Document frame with modern styling
        doc_frame = ttk.LabelFrame(parent, text="📚 Document Library", padding="10")
        doc_frame.grid(row=0, column=0, rowspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        doc_frame.configure(width=350)
        
        # Upload section with drag & drop hint
        upload_frame = ttk.Frame(doc_frame)
        upload_frame.pack(fill=tk.X, pady=(0, 10))
        
        upload_btn = ttk.Button(upload_frame, text="📤 Upload Document", 
                              command=self.upload_document, style="Accent.TButton")
        upload_btn.pack(fill=tk.X)
        
        hint_label = tk.Label(upload_frame, text="Supports: PDF, DOCX, DOC, TXT", 
                             font=("Arial", 8), fg=theme["fg"], bg=theme["panel_bg"])
        hint_label.pack(pady=(5, 0))
        
        # Document list with enhanced display
        list_frame = ttk.Frame(doc_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Treeview for better document display
        columns = ("Size", "Type", "Date")
        self.doc_tree = ttk.Treeview(list_frame, columns=columns, show="tree headings", height=8)
        self.doc_tree.heading("#0", text="Document")
        self.doc_tree.heading("Size", text="Size")
        self.doc_tree.heading("Type", text="Type") 
        self.doc_tree.heading("Date", text="Uploaded")
        
        # Configure column widths
        self.doc_tree.column("#0", width=150, minwidth=100)
        self.doc_tree.column("Size", width=60, minwidth=50)
        self.doc_tree.column("Type", width=50, minwidth=40)
        self.doc_tree.column("Date", width=80, minwidth=70)
        
        # Scrollbar for document tree
        doc_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.doc_tree.yview)
        self.doc_tree.configure(yscrollcommand=doc_scrollbar.set)
        
        self.doc_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        doc_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Document actions with icons
        doc_actions_frame = ttk.Frame(doc_frame)
        doc_actions_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(doc_actions_frame, text="📄 Summarize", 
                  command=self.summarize_selected, style="Success.TButton").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(doc_actions_frame, text="❓ Ask Question", 
                  command=self.ask_about_document, style="Custom.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(doc_actions_frame, text="🗑️ Remove", 
                  command=self.remove_selected, style="Danger.TButton").pack(side=tk.RIGHT)
        
        # Document preview with syntax highlighting
        preview_frame = ttk.LabelFrame(doc_frame, text="📖 Preview", padding="5")
        preview_frame.pack(fill=tk.BOTH, expand=True)
        
        self.doc_preview = scrolledtext.ScrolledText(preview_frame, height=8, wrap=tk.WORD,
                                                   font=("Consolas", 9))
        self.doc_preview.pack(fill=tk.BOTH, expand=True)
        
        # Bind selection event
        self.doc_tree.bind('<<TreeviewSelect>>', self.on_document_select)
        
        # Configure grid weights for document panel
        doc_frame.columnconfigure(0, weight=1)
        doc_frame.rowconfigure(1, weight=1)
        
    def setup_chat_panel(self, parent):
        """Setup enhanced chat interface panel with modern styling"""
        theme = self.themes[self.settings.get("theme", "light")]
        
        # Chat frame with modern card design
        chat_frame = ttk.LabelFrame(parent, 
                                   text=self.get_emoji_label("💬", "AI Conversation"), 
                                   padding="15", 
                                   style="Card.TFrame")
        chat_frame.grid(row=0, column=1, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        
        # Enhanced chat display with better styling
        chat_display_frame = tk.Frame(chat_frame, bg=theme["panel_bg"])
        chat_display_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Chat display with modern appearance
        self.chat_display = scrolledtext.ScrolledText(
            chat_display_frame, 
            height=25, 
            wrap=tk.WORD,
            state=tk.DISABLED,
            font=("Segoe UI", int(self.settings["ui_settings"]["font_size"])),
            bg=theme["entry_bg"],
            fg=theme["fg"],
            selectbackground=theme["select_bg"],
            relief=tk.FLAT,
            borderwidth=1,
            highlightthickness=1,
            highlightcolor=theme["accent"],
            highlightbackground=theme["border"],
            padx=12,
            pady=8
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        
        # Configure chat display tags for better message styling
        self.chat_display.tag_configure("user", foreground=theme["accent"], font=("Segoe UI", 10, "bold"))
        self.chat_display.tag_configure("assistant", foreground=theme["success"], font=("Segoe UI", 10, "bold"))
        self.chat_display.tag_configure("system", foreground=theme["warning"], font=("Segoe UI", 9, "italic"))
        self.chat_display.tag_configure("timestamp", foreground=theme["fg"], font=("Segoe UI", 8))
        
        # Modern input section
        input_section = ttk.Frame(chat_frame, style="Card.TFrame")
        input_section.pack(fill=tk.X)
        
        # Message input with modern styling
        input_frame = tk.Frame(input_section, bg=theme["panel_bg"])
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.message_var = tk.StringVar()
        self.message_entry = tk.Entry(
            input_frame, 
            textvariable=self.message_var, 
            font=("Segoe UI", 11),
            bg=theme["entry_bg"],
            fg=theme["fg"],
            relief=tk.FLAT,
            borderwidth=1,
            highlightthickness=1,
            highlightcolor=theme["accent"],
            highlightbackground=theme["border"],
            insertbackground=theme["fg"]
        )
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 15))
        self.message_entry.bind("<Return>", self.send_message)
        self.message_entry.bind("<Shift-Return>", self.send_message)  # Also support Shift+Enter
        
        # Enhanced send button with modern styling
        self.send_btn = ttk.Button(input_frame, 
                                  text=self.get_emoji_label("🚀", "Send"), 
                                  command=self.send_message, 
                                  style="Modern.TButton")
        self.send_btn.pack(side=tk.RIGHT)
        
        # Modern quick action buttons
        actions_frame = tk.Frame(input_section, bg=theme["panel_bg"])
        actions_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Create modern action buttons with icons
        ttk.Button(actions_frame, 
                  text=self.get_emoji_label("📄", "Summarize All"), 
                  command=self.summarize_all_docs, 
                  style="Modern.TButton").pack(side=tk.LEFT, padx=(0, 8))
        
        ttk.Button(actions_frame, 
                  text=self.get_emoji_label("🔍", "Smart Search"), 
                  command=self.smart_search, 
                  style="Modern.TButton").pack(side=tk.LEFT, padx=4)
        
        ttk.Button(actions_frame, 
                  text=self.get_emoji_label("📝", "Take Notes"), 
                  command=self.take_notes, 
                  style="Modern.TButton").pack(side=tk.LEFT, padx=4)
        
        # Chat options and mode selection
        options_frame = ttk.LabelFrame(chat_frame, text="Chat Options", padding="5")
        options_frame.pack(fill=tk.X, pady=(10, 0))
        
        options_row1 = ttk.Frame(options_frame)
        options_row1.pack(fill=tk.X, pady=(0, 5))
        
        # Mode selection with descriptions
        ttk.Label(options_row1, text="Mode:").pack(side=tk.LEFT, padx=(0, 5))
        self.chat_mode = tk.StringVar(value="general")
        mode_combo = ttk.Combobox(options_row1, textvariable=self.chat_mode, 
                                 values=["general", "document_qa", "note_taking", "summarize", "creative"], 
                                 state="readonly", width=15)
        mode_combo.pack(side=tk.LEFT, padx=(0, 10))
        mode_combo.bind('<<ComboboxSelected>>', self.on_mode_change)
        
        # Quick tools
        ttk.Button(options_row1, text="🧹 Clear", command=self.clear_chat_confirm, style="Warning.TButton").pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(options_row1, text="💾 Save", command=self.save_chat_history, style="Success.TButton").pack(side=tk.RIGHT, padx=(5, 0))
        
        # Chat statistics
        options_row2 = ttk.Frame(options_frame)
        options_row2.pack(fill=tk.X)
        
        self.stats_label = ttk.Label(options_row2, text="Messages: 0 | Characters: 0")
        self.stats_label.pack(side=tk.LEFT)
        
        self.mode_desc_label = ttk.Label(options_row2, text="General conversation mode")
        self.mode_desc_label.pack(side=tk.RIGHT)
        
        # Configure grid weights for chat panel
        chat_frame.columnconfigure(0, weight=1)
        chat_frame.rowconfigure(0, weight=1)
        
    def setup_enhanced_status_bar(self):
        """Setup enhanced status bar with more information"""
        status_frame = ttk.Frame(self.root)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=2)
        
        # Main status
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        ttk.Label(status_frame, textvariable=self.status_var).pack(side=tk.LEFT)
        
        # Separator
        ttk.Separator(status_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # AI status with more details
        self.ai_status_var = tk.StringVar()
        self.ai_status_var.set("AI: Initializing...")
        ttk.Label(status_frame, textvariable=self.ai_status_var).pack(side=tk.LEFT, padx=(0, 10))
        
        # Document count
        self.doc_count_var = tk.StringVar()
        self.doc_count_var.set("Documents: 0")
        ttk.Label(status_frame, textvariable=self.doc_count_var).pack(side=tk.LEFT, padx=(0, 10))
        
        # Memory usage indicator
        self.memory_var = tk.StringVar()
        self.memory_var.set("Memory: Ready")
        ttk.Label(status_frame, textvariable=self.memory_var).pack(side=tk.RIGHT)
        
        # Theme indicator
        theme_name = self.settings.get("theme", "light").title()
        self.theme_var = tk.StringVar()
        self.theme_var.set(f"Theme: {theme_name}")
        ttk.Label(status_frame, textvariable=self.theme_var).pack(side=tk.RIGHT, padx=(0, 10))
        
    def on_document_select(self, event):
        """Handle document selection in tree"""
        selection = self.doc_tree.selection()
        if selection:
            item = self.doc_tree.item(selection[0])
            doc_name = item['text']
            
            # Find document and show preview
            for doc in self.uploaded_documents:
                if doc['name'] == doc_name:
                    preview_text = doc['content'][:1000] + "..." if len(doc['content']) > 1000 else doc['content']
                    self.doc_preview.delete(1.0, tk.END)
                    self.doc_preview.insert(tk.END, preview_text)
                    break
                    
    def on_mode_change(self, event):
        """Handle chat mode change"""
        mode = self.chat_mode.get()
        descriptions = {
            "general": "General conversation mode",
            "document_qa": "Ask questions about uploaded documents",
            "note_taking": "AI helps create structured notes",
            "summarize": "Generate summaries from text or documents",
            "creative": "Creative writing and brainstorming mode"
        }
        self.mode_desc_label.config(text=descriptions.get(mode, ""))
        
    def on_closing(self):
        """Handle application closing"""
        if self.settings.get("auto_save_chat", True) and self.chat_history:
            self.auto_save_chat_history()
        self.save_settings()
        self.root.quit()
        self.root.destroy()
        
    def setup_status_bar(self):
        """Setup status bar"""
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        
        status_frame = ttk.Frame(self.root)
        status_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        ttk.Label(status_frame, textvariable=self.status_var, relief=tk.SUNKEN).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # AI status indicator
        self.ai_status_var = tk.StringVar()
        self.ai_status_var.set("AI: Initializing...")
        ttk.Label(status_frame, textvariable=self.ai_status_var, relief=tk.SUNKEN).pack(side=tk.RIGHT, padx=(5, 0))
        
    def initialize_ai_engine(self):
        """Initialize AI engine in background thread"""
        def init_ai():
            try:
                self.ai_status_var.set("AI: Loading...")
                self.ai_engine = AIEngine()
                self.summarizer = Summarizer(self.ai_engine)
                
                if self.ai_engine.is_ready():
                    self.ai_status_var.set("AI: Ready")
                    self.send_btn.configure(state="normal")
                else:
                    self.ai_status_var.set("AI: No model found")
                    self.send_btn.configure(state="disabled")
                    
            except Exception as e:
                self.ai_status_var.set("AI: Error")
                print(f"AI initialization error: {e}")
                
        threading.Thread(target=init_ai, daemon=True).start()
        
    def upload_document(self):
        """Handle document upload"""
        filetypes = [
            ("All supported", "*.pdf;*.docx;*.doc;*.txt"),
            ("PDF files", "*.pdf"),
            ("Word documents", "*.docx;*.doc"),
            ("Text files", "*.txt"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Select document to upload",
            filetypes=filetypes
        )
        
        if filename:
            self.process_document(filename)
            
    def process_document(self, filepath):
        """Process uploaded document with enhanced display"""
        def process():
            try:
                self.status_var.set(f"Processing {os.path.basename(filepath)}...")
                
                # Parse document based on extension
                ext = os.path.splitext(filepath)[1].lower()
                text_content = ""
                
                if ext == '.pdf':
                    text_content = self.pdf_parser.extract_text(filepath)
                elif ext in ['.docx', '.doc']:
                    text_content = self.docx_parser.extract_text(filepath)
                elif ext == '.txt':
                    with open(filepath, 'r', encoding='utf-8') as f:
                        text_content = f.read()
                
                if text_content:
                    # Calculate file size
                    file_size = os.path.getsize(filepath)
                    size_str = f"{file_size // 1024} KB" if file_size > 1024 else f"{file_size} B"
                    
                    # Add to document list
                    doc_info = {
                        'name': os.path.basename(filepath),
                        'path': filepath,
                        'content': text_content,
                        'upload_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'size': file_size,
                        'type': ext.upper().replace('.', '')
                    }
                    
                    # Add to database
                    if self.db:
                        try:
                            doc_id = self.db.add_document(
                                doc_info['name'], 
                                doc_info['path'], 
                                doc_info['content'],
                                doc_info['type'], 
                                doc_info['size']
                            )
                            doc_info['id'] = doc_id
                        except Exception as e:
                            print(f"Failed to save document to database: {e}")
                    
                    self.uploaded_documents.append(doc_info)
                    
                    # Add to tree view
                    self.doc_tree.insert("", tk.END, text=doc_info['name'], 
                                       values=(size_str, doc_info['type'], doc_info['upload_time']))
                    
                    # Update document count
                    self.doc_count_var.set(f"Documents: {len(self.uploaded_documents)}")
                    
                    self.status_var.set(f"Document processed successfully: {doc_info['name']}")
                    
                    # Add to chat
                    self.add_to_chat("System", f"📄 Document uploaded: {doc_info['name']} ({size_str})")
                    
                    # Update statistics
                    self.update_stats()
                    
                else:
                    messagebox.showerror("Error", "Could not extract text from document")
                    self.status_var.set("Error processing document")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to process document: {str(e)}")
                self.status_var.set("Error processing document")
                
        threading.Thread(target=process, daemon=True).start()
        
    def send_message(self, event=None):
        """Send message to AI"""
        message = self.message_var.get().strip()
        if not message:
            return
            
        if not self.ai_engine or not self.ai_engine.is_ready():
            messagebox.showwarning("Warning", "AI engine is not ready. Please check model installation.")
            return
            
        # Clear input
        self.message_var.set("")
        
        # Add user message to chat
        self.add_to_chat("You", message)
        
        # Process in background
        def process_message():
            try:
                self.status_var.set("AI thinking...")
                self.send_btn.configure(state="disabled")
                
                # Get context based on mode
                context = self.get_context_for_mode()
                
                # Generate response
                response = self.ai_engine.generate_response(message, context)
                
                # Add AI response to chat
                self.add_to_chat("AI", response)
                
            except Exception as e:
                self.add_to_chat("System", f"Error: {str(e)}")
                print(f"Message processing error: {e}")
                
            finally:
                self.status_var.set("Ready")
                self.send_btn.configure(state="normal")
                
        threading.Thread(target=process_message, daemon=True).start()
        
    def get_context_for_mode(self):
        """Get context based on chat mode"""
        mode = self.chat_mode.get()
        context = ""
        
        if mode == "document_qa" and self.uploaded_documents:
            # Include all document contents as context
            context = "\n\n".join([doc['content'] for doc in self.uploaded_documents])
        elif mode == "general":
            # Include recent chat history
            context = "\n".join([f"{msg['sender']}: {msg['content']}" 
                               for msg in self.chat_history[-5:]])  # Last 5 messages
            
        return context
        
    def add_to_chat(self, sender, message):
        """Add message to chat display and database with enhanced styling"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Add to in-memory history
        chat_entry = {
            'sender': sender,
            'content': message,
            'timestamp': timestamp
        }
        self.chat_history.append(chat_entry)
        
        # Add to database
        if self.db:
            try:
                self.db.add_chat_message(sender, message, self.current_session_id)
            except Exception as e:
                print(f"Failed to save message to database: {e}")
        
        # Add to display with enhanced styling
        self.chat_display.configure(state=tk.NORMAL)
        
        # Add visual separator for better readability
        if len(self.chat_history) > 1:
            self.chat_display.insert(tk.END, "\n" + "─" * 50 + "\n")
        
        # Format message with enhanced styling
        if sender == "You":
            self.chat_display.insert(tk.END, f"[{timestamp}] ", "timestamp")
            self.chat_display.insert(tk.END, f"{self.get_emoji_label('🧑', 'You')}:\n", "user")
            self.chat_display.insert(tk.END, f"{message}\n", "user_msg")
        elif sender == "AI":
            self.chat_display.insert(tk.END, f"[{timestamp}] ", "timestamp")
            self.chat_display.insert(tk.END, f"{self.get_emoji_label('🤖', 'AI')}:\n", "assistant")
            self.chat_display.insert(tk.END, f"{message}\n", "ai_msg")
        else:
            self.chat_display.insert(tk.END, f"\n[{timestamp}] ℹ️  {sender}:\n", "system")
            self.chat_display.insert(tk.END, f"{message}\n", "system_msg")
            
        # Configure tags for styling
        self.chat_display.tag_configure("user", foreground="blue", font=("Arial", 10, "bold"))
        self.chat_display.tag_configure("ai", foreground="green", font=("Arial", 10, "bold"))
        self.chat_display.tag_configure("system", foreground="gray", font=("Arial", 10, "bold"))
        self.chat_display.tag_configure("user_msg", font=("Arial", 10))
        self.chat_display.tag_configure("ai_msg", font=("Arial", 10))
        self.chat_display.tag_configure("system_msg", font=("Arial", 9), foreground="gray")
        
        self.chat_display.configure(state=tk.DISABLED)
        self.chat_display.see(tk.END)
        
    def add_message_to_display_only(self, sender, message):
        """Add message to display without saving to database (for loading sessions)"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Add to display with enhanced styling
        self.chat_display.configure(state=tk.NORMAL)
        
        # Add visual separator for better readability
        if self.chat_display.get("1.0", "end-1c"):  # If display is not empty
            self.chat_display.insert(tk.END, "\n" + "─" * 50 + "\n")
        
        # Format message with enhanced styling
        if sender == "You":
            self.chat_display.insert(tk.END, f"[{timestamp}] ", "timestamp")
            self.chat_display.insert(tk.END, f"{self.get_emoji_label('🧑', 'You')}:\n", "user")
            self.chat_display.insert(tk.END, f"{message}\n", "user_msg")
        elif sender == "AI":
            self.chat_display.insert(tk.END, f"[{timestamp}] ", "timestamp")
            self.chat_display.insert(tk.END, f"{self.get_emoji_label('🤖', 'AI')}:\n", "assistant")
            self.chat_display.insert(tk.END, f"{message}\n", "ai_msg")
        else:
            self.chat_display.insert(tk.END, f"\n[{timestamp}] ℹ️  {sender}:\n", "system")
            self.chat_display.insert(tk.END, f"{message}\n", "system_msg")
            
        # Configure tags for styling
        self.chat_display.tag_configure("user", foreground="blue", font=("Arial", 10, "bold"))
        self.chat_display.tag_configure("assistant", foreground="green", font=("Arial", 10, "bold"))
        self.chat_display.tag_configure("system", foreground="gray", font=("Arial", 10, "bold"))
        self.chat_display.tag_configure("user_msg", font=("Arial", 10))
        self.chat_display.tag_configure("ai_msg", font=("Arial", 10))
        self.chat_display.tag_configure("system_msg", font=("Arial", 9), foreground="gray")
        self.chat_display.tag_configure("timestamp", font=("Arial", 8), foreground="gray")
        
        self.chat_display.configure(state=tk.DISABLED)
        self.chat_display.see(tk.END)
        
    def summarize_selected(self):
        """Summarize selected document"""
        selection = self.doc_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a document to summarize")
            return
            
        if not self.ai_engine or not self.ai_engine.is_ready():
            messagebox.showwarning("Warning", "AI engine is not ready")
            return
            
        # Get the selected item and find the corresponding document
        selected_item = selection[0]
        doc_name = self.doc_tree.item(selected_item, 'text')
        
        # Find document in uploaded_documents list
        doc_info = None
        for doc in self.uploaded_documents:
            if doc['name'] == doc_name:
                doc_info = doc
                break
                
        if not doc_info:
            messagebox.showerror("Error", "Document not found")
            return
        
        def summarize():
            try:
                self.status_var.set("Generating summary...")
                summary = self.summarizer.summarize(doc_info['content'])
                self.add_to_chat("AI", f"📄 Summary of '{doc_info['name']}':\n\n{summary}")
            except Exception as e:
                self.add_to_chat("System", f"Error generating summary: {str(e)}")
            finally:
                self.status_var.set("Ready")
                
        threading.Thread(target=summarize, daemon=True).start()
        
    def remove_selected(self):
        """Remove selected document"""
        selection = self.doc_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a document to remove")
            return
            
        selected_item = selection[0]
        doc_name = self.doc_tree.item(selected_item, 'text')
        
        # Find document in uploaded_documents list and get its index
        doc_index = None
        for i, doc in enumerate(self.uploaded_documents):
            if doc['name'] == doc_name:
                doc_index = i
                break
                
        if doc_index is None:
            messagebox.showerror("Error", "Document not found")
            return
        
        if messagebox.askyesno("Confirm", f"Remove document '{doc_name}'?"):
            self.uploaded_documents.pop(doc_index)
            self.doc_tree.delete(selected_item)
            self.doc_preview.delete(1.0, tk.END)
            self.add_to_chat("System", f"Document removed: {doc_name}")
            
    def clear_chat(self):
        """Clear chat history"""
        if messagebox.askyesno("Confirm", "Clear all chat history?"):
            self.chat_history.clear()
            self.chat_display.configure(state=tk.NORMAL)
            self.chat_display.delete(1.0, tk.END)
            self.chat_display.configure(state=tk.DISABLED)
            self.add_to_chat("System", "Chat cleared")
            
    def export_chat(self):
        """Export chat history"""
        if not self.chat_history:
            messagebox.showwarning("Warning", "No chat history to export")
            return
            
        filename = filedialog.asksaveasfilename(
            title="Export chat history",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("JSON files", "*.json")]
        )
        
        if filename:
            try:
                if filename.endswith('.json'):
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(self.chat_history, f, indent=2, ensure_ascii=False)
                else:
                    with open(filename, 'w', encoding='utf-8') as f:
                        for msg in self.chat_history:
                            f.write(f"[{msg['timestamp']}] {msg['sender']}: {msg['content']}\n\n")
                            
                messagebox.showinfo("Success", "Chat history exported successfully")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export chat: {str(e)}")
                
    def show_model_downloader(self):
        """Show model download dialog"""
        ModelDownloadDialog(self.root, self.ai_engine)
        
    def show_model_settings(self):
        """Show model settings dialog"""
        ModelSettingsDialog(self.root, self.ai_engine)
        
    def show_troubleshooting(self):
        """Show troubleshooting guide"""
        TroubleshootingDialog(self.root)
        
    def show_about(self):
        """Show about dialog"""
        AboutDialog(self.root)


    def on_closing(self):
        """Handle application closing"""
        if self.settings.get("auto_save_chat", True) and self.chat_history:
            self.auto_save_chat_history()
        self.save_settings()
        self.root.quit()
        self.root.destroy()
        
    # New enhanced methods
    def save_chat_history(self):
        """Save current chat to database with title"""
        if not self.chat_history:
            messagebox.showwarning("Warning", "No chat history to save")
            return
            
        # Ask for a title for this chat session
        title = simpledialog.askstring(
            "Save Chat", 
            "Enter a title for this chat:",
            initialvalue=self.db.generate_chat_summary(self.current_session_id) if self.db else f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )
        
        if title and self.db:
            try:
                # Update session title and generate summary
                summary = self.db.generate_chat_summary(self.current_session_id)
                self.db.update_chat_session(self.current_session_id, title=title, summary=summary)
                messagebox.showinfo("Success", f"Chat saved successfully as '{title}'")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save chat: {str(e)}")
        elif not self.db:
            messagebox.showerror("Error", "Database not available")
        else:
            messagebox.showinfo("Cancelled", "Chat not saved")
                
    def export_chat_pdf(self):
        """Export chat as PDF"""
        if not self.chat_history:
            messagebox.showwarning("Warning", "No chat history to export")
            return
            
        try:
            # Create HTML first, then convert to PDF if possible
            html_content = self.generate_chat_html()
            
            # Try to use weasyprint for PDF conversion
            try:
                from weasyprint import HTML, CSS
                filename = filedialog.asksaveasfilename(
                    title="Export chat as PDF",
                    defaultextension=".pdf",
                    filetypes=[("PDF files", "*.pdf")]
                )
                
                if filename:
                    HTML(string=html_content).write_pdf(filename)
                    messagebox.showinfo("Success", f"Chat exported as PDF: {Path(filename).name}")
                    
            except ImportError:
                # Fallback: save as HTML and show instructions
                filename = filedialog.asksaveasfilename(
                    title="Export chat as HTML (PDF conversion unavailable)",
                    defaultextension=".html",
                    filetypes=[("HTML files", "*.html")]
                )
                
                if filename:
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(html_content)
                    
                    messagebox.showinfo("PDF Export", 
                        "PDF export requires 'weasyprint' package.\n"
                        "Chat saved as HTML instead.\n\n"
                        "To enable PDF export:\n"
                        "pip install weasyprint")
                        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export chat: {str(e)}")
            
    def export_chat_html(self, filename=None):
        """Export chat as HTML"""
        if not filename:
            filename = filedialog.asksaveasfilename(
                title="Export chat as HTML",
                defaultextension=".html",
                filetypes=[("HTML files", "*.html")]
            )
            
        if filename:
            try:
                html_content = self.generate_chat_html()
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                messagebox.showinfo("Success", f"Chat exported as HTML: {Path(filename).name}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export HTML: {str(e)}")
                
    def export_chat_markdown(self, filename):
        """Export chat as Markdown"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"# OANA Chat History\n\n")
                f.write(f"**Exported:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write("---\n\n")
                
                for msg in self.chat_history:
                    sender_icon = "🧑" if msg['sender'] == "You" else "🤖" if msg['sender'] == "AI" else "ℹ️"
                    f.write(f"## {sender_icon} {msg['sender']} - {msg['timestamp']}\n\n")
                    f.write(f"{msg['content']}\n\n")
                    f.write("---\n\n")
                    
            messagebox.showinfo("Success", f"Chat exported as Markdown: {Path(filename).name}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export Markdown: {str(e)}")
            
    def generate_chat_html(self):
        """Generate HTML content for chat export"""
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OANA Chat History</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
            background-color: #f5f5f5;
        }}
        .header {{
            text-align: center;
            background: linear-gradient(135deg, #3498db, #2c3e50);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }}
        .message {{
            margin: 15px 0;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .user-message {{
            background-color: #e3f2fd;
            border-left: 4px solid #2196f3;
        }}
        .ai-message {{
            background-color: #e8f5e8;
            border-left: 4px solid #4caf50;
        }}
        .system-message {{
            background-color: #fff3e0;
            border-left: 4px solid #ff9800;
        }}
        .timestamp {{
            font-size: 0.8em;
            color: #666;
            margin-bottom: 5px;
        }}
        .sender {{
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .content {{
            white-space: pre-wrap;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🧠 OANA Chat History</h1>
        <p>Exported on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
"""
        
        for msg in self.chat_history:
            msg_class = "user-message" if msg['sender'] == "You" else "ai-message" if msg['sender'] == "AI" else "system-message"
            sender_icon = "🧑" if msg['sender'] == "You" else "🤖" if msg['sender'] == "AI" else "ℹ️"
            
            html += f"""
    <div class="message {msg_class}">
        <div class="timestamp">{msg['timestamp']}</div>
        <div class="sender">{sender_icon} {msg['sender']}</div>
        <div class="content">{msg['content']}</div>
    </div>
"""
        
        html += """
</body>
</html>
"""
        return html
        
    def auto_save_chat_history(self):
        """Auto-save chat to database"""
        try:
            if self.db and self.chat_history:
                # Update session with auto-generated title if not already set
                sessions = self.db.get_chat_sessions(1)
                current_session = next((s for s in sessions if s['session_id'] == self.current_session_id), None)
                
                if current_session and not current_session.get('title'):
                    # Generate title from chat content
                    title = f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                    summary = self.db.generate_chat_summary(self.current_session_id)
                    self.db.update_chat_session(self.current_session_id, title=title, summary=summary)
                
        except Exception as e:
            print(f"Auto-save failed: {e}")
            
    def clear_chat_confirm(self):
        """Confirm before clearing chat"""
        if not self.chat_history:
            return
            
        result = messagebox.askyesnocancel(
            "Clear Chat History",
            "Do you want to save the current chat before starting a new one?\n\n"
            "Yes: Save current and start new chat\n"
            "No: Start new chat without saving\n"
            "Cancel: Continue with current chat"
        )
        
        if result is True:  # Yes - save and start new
            self.save_chat_history()
            self.start_new_chat_session()
        elif result is False:  # No - start new without saving
            self.start_new_chat_session()
        # Cancel - do nothing
        
    def start_new_chat_session(self):
        """Start a new chat session"""
        try:
            # Create new session ID
            self.current_session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Create session in database
            if self.db:
                self.db.create_chat_session(self.current_session_id)
            
            # Clear current chat
            self.clear_chat()
            
            self.add_to_chat("System", "🆕 Started new chat session")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start new session: {str(e)}")
        
    def clear_documents(self):
        """Clear all uploaded documents"""
        if not self.uploaded_documents:
            messagebox.showinfo("Info", "No documents to clear")
            return
            
        if messagebox.askyesno("Confirm", f"Remove all {len(self.uploaded_documents)} documents?"):
            self.uploaded_documents.clear()
            for item in self.doc_tree.get_children():
                self.doc_tree.delete(item)
            self.doc_preview.delete(1.0, tk.END)
            self.doc_count_var.set("Documents: 0")
            self.add_to_chat("System", "All documents cleared")
            
    def ask_about_document(self):
        """Quick ask about selected document"""
        selection = self.doc_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a document first")
            return
            
        # Set mode to document QA and focus input
        self.chat_mode.set("document_qa")
        self.on_mode_change(None)
        self.message_entry.focus()
        
        # Add helpful message
        self.add_to_chat("System", "Document Q&A mode activated. Ask questions about the selected document.")
        
    def summarize_all_docs(self):
        """Summarize all uploaded documents"""
        if not self.uploaded_documents:
            messagebox.showwarning("Warning", "No documents to summarize")
            return
            
        def summarize():
            try:
                self.status_var.set("Generating summary of all documents...")
                
                all_content = "\n\n".join([doc['content'] for doc in self.uploaded_documents])
                summary = self.summarizer.summarize(all_content, max_length=500, style="detailed")
                
                self.add_to_chat("AI", f"📄 Summary of all {len(self.uploaded_documents)} documents:\n\n{summary}")
                
            except Exception as e:
                self.add_to_chat("System", f"Error generating summary: {str(e)}")
            finally:
                self.status_var.set("Ready")
                
        threading.Thread(target=summarize, daemon=True).start()
        
    def smart_search(self):
        """Smart search across documents"""
        if not self.uploaded_documents:
            messagebox.showwarning("Warning", "No documents to search")
            return
            
        query = simpledialog.askstring("Smart Search", "Enter search query:")
        if query:
            # Simple text search for now
            results = []
            for doc in self.uploaded_documents:
                if query.lower() in doc['content'].lower():
                    # Find context around the match
                    content = doc['content']
                    index = content.lower().find(query.lower())
                    start = max(0, index - 100)
                    end = min(len(content), index + 100)
                    context = content[start:end]
                    results.append(f"📄 {doc['name']}: ...{context}...")
                    
            if results:
                result_text = "\n\n".join(results[:5])  # Show top 5 results
                self.add_to_chat("System", f"🔍 Search results for '{query}':\n\n{result_text}")
            else:
                self.add_to_chat("System", f"🔍 No results found for '{query}'")
                
    def take_notes(self):
        """AI-assisted note taking"""
        if not self.uploaded_documents:
            messagebox.showwarning("Warning", "No documents available for note-taking")
            return
            
        self.chat_mode.set("note_taking")
        self.on_mode_change(None)
        self.add_to_chat("System", "📝 Note-taking mode activated. I'll help you create structured notes from your documents.")
        
    def reload_ai_model(self):
        """Reload AI model"""
        def reload():
            try:
                self.ai_status_var.set("AI: Reloading...")
                self.ai_engine.reload_model()
                
                if self.ai_engine.is_ready():
                    self.ai_status_var.set("AI: Ready")
                    self.add_to_chat("System", "✅ AI model reloaded successfully")
                else:
                    self.ai_status_var.set("AI: No model found")
                    self.add_to_chat("System", "⚠️ No AI model found. Please download a model.")
                    
            except Exception as e:
                self.ai_status_var.set("AI: Error")
                self.add_to_chat("System", f"❌ Error reloading model: {str(e)}")
                
        threading.Thread(target=reload, daemon=True).start()
        
    def show_model_status(self):
        """Show detailed model status"""
        status_window = tk.Toplevel(self.root)
        status_window.title("AI Model Status")
        status_window.geometry("600x400")
        status_window.transient(self.root)
        
        main_frame = ttk.Frame(status_window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create scrolled text widget
        status_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, font=("Courier", 10))
        status_text.pack(fill=tk.BOTH, expand=True)
        
        # Gather comprehensive status information
        status_lines = []
        status_lines.append("🤖 OANA AI MODEL STATUS")
        status_lines.append("=" * 50)
        
        if self.ai_engine:
            info = self.ai_engine.get_model_info()
            
            # Basic status
            status_lines.append(f"\n📊 Current Status:")
            status_lines.append(f"• Backend: {info.get('backend', 'None')}")
            status_lines.append(f"• Model Loaded: {'✅ Yes' if info.get('is_loaded', False) else '❌ No'}")
            
            if hasattr(self.ai_engine, 'model_name'):
                status_lines.append(f"• Model Name: {getattr(self.ai_engine, 'model_name', 'Unknown')}")
            
            if info.get('model_path'):
                status_lines.append(f"• Model Path: {info.get('model_path')}")
            
            # Backend availability
            status_lines.append(f"\n🔧 Available Backends:")
            available_backends = info.get('available_backends', {})
            for backend, available in available_backends.items():
                status = "✅ Available" if available else "❌ Not installed"
                status_lines.append(f"• {backend}: {status}")
            
            # Model directory status
            if hasattr(self.ai_engine, 'models_dir') and self.ai_engine.models_dir:
                status_lines.append(f"\n📁 Models Directory: {self.ai_engine.models_dir}")
                models_dir = Path(self.ai_engine.models_dir)
                if models_dir.exists():
                    gguf_files = list(models_dir.glob("*.gguf"))
                    status_lines.append(f"• GGUF Models Found: {len(gguf_files)}")
                    for model_file in gguf_files:
                        size_mb = model_file.stat().st_size / (1024 * 1024)
                        status_lines.append(f"  - {model_file.name} ({size_mb:.1f} MB)")
                else:
                    status_lines.append("• Directory does not exist")
            
            # Configuration
            if hasattr(self.ai_engine, 'config'):
                config = self.ai_engine.config
                status_lines.append(f"\n⚙️ Configuration:")
                status_lines.append(f"• Temperature: {config.get('temperature', 'N/A')}")
                status_lines.append(f"• Max Tokens: {config.get('max_tokens', 'N/A')}")
                status_lines.append(f"• Top P: {config.get('top_p', 'N/A')}")
                status_lines.append(f"• Top K: {config.get('top_k', 'N/A')}")
            
        else:
            status_lines.append("\n❌ AI engine not initialized")
        
        # Check for dependency issues
        status_lines.append(f"\n🔍 Quick Dependency Check:")
        try:
            import llama_cpp
            status_lines.append("• llama-cpp-python: ✅ Available")
        except ImportError:
            status_lines.append("• llama-cpp-python: ❌ Not installed")
        
        try:
            import ollama
            status_lines.append("• ollama: ✅ Available")
        except ImportError:
            status_lines.append("• ollama: ❌ Not installed")
            
        try:
            import torch
            import transformers
            status_lines.append("• transformers: ✅ Available")
        except ImportError:
            status_lines.append("• transformers: ❌ Not installed")
        
        # Recommendations
        status_lines.append(f"\n💡 Recommendations:")
        if not self.ai_engine or not self.ai_engine.is_ready():
            status_lines.append("• Install AI backend: pip install llama-cpp-python")
            status_lines.append("• Download models: python download_models.py")
            status_lines.append("• Or use the built-in model downloader")
        elif self.ai_engine.backend == "fallback":
            status_lines.append("• Running in fallback mode - install proper AI backend")
            status_lines.append("• Download GGUF models to enable full functionality")
        else:
            status_lines.append("• AI system is properly configured!")
            
        status_text.insert(1.0, "\n".join(status_lines))
        status_text.config(state=tk.DISABLED)
        
        # Add buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="Download Models", 
                  command=lambda: [status_window.destroy(), self.show_model_downloader()]).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="Reload AI Engine", 
                  command=lambda: [self.reload_ai_model(), status_window.destroy()]).pack(side=tk.LEFT, padx=(10, 0))
        ttk.Button(button_frame, text="Check Dependencies", 
                  command=self.run_dependency_check).pack(side=tk.LEFT, padx=(10, 0))
        ttk.Button(button_frame, text="Close", 
                  command=status_window.destroy).pack(side=tk.RIGHT)
    
    def run_dependency_check(self):
        """Run dependency checker"""
        try:
            from check_dependencies import DependencyChecker
            
            # Create a new window for dependency check results
            dep_window = tk.Toplevel(self.root)
            dep_window.title("Dependency Check")
            dep_window.geometry("600x400")
            dep_window.transient(self.root)
            
            main_frame = ttk.Frame(dep_window, padding="10")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            result_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, font=("Courier", 10))
            result_text.pack(fill=tk.BOTH, expand=True)
            
            # Capture dependency checker output
            import io
            import contextlib
            
            captured_output = io.StringIO()
            
            with contextlib.redirect_stdout(captured_output):
                checker = DependencyChecker()
                success = checker.run_full_check(fix=False)
            
            output = captured_output.getvalue()
            result_text.insert(1.0, output)
            result_text.config(state=tk.DISABLED)
            
            # Add buttons
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill=tk.X, pady=(10, 0))
            
            ttk.Button(button_frame, text="Install Missing", 
                      command=lambda: self.install_missing_deps(dep_window)).pack(side=tk.LEFT)
            ttk.Button(button_frame, text="Close", 
                      command=dep_window.destroy).pack(side=tk.RIGHT)
            
        except ImportError:
            messagebox.showerror("Error", "Dependency checker not available")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to run dependency check: {str(e)}")
    
    def install_missing_deps(self, parent_window):
        """Install missing dependencies"""
        result = messagebox.askyesno("Install Dependencies", 
                                   "This will try to install missing dependencies. Continue?")
        if result:
            try:
                from check_dependencies import DependencyChecker
                checker = DependencyChecker()
                
                # Run check with fix=True
                threading.Thread(target=lambda: self._install_deps_thread(checker, parent_window), 
                               daemon=True).start()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to install dependencies: {str(e)}")
    
    def _install_deps_thread(self, checker, parent_window):
        """Install dependencies in a separate thread"""
        try:
            success = checker.run_full_check(fix=True)
            parent_window.after(0, lambda: self._deps_install_complete(success, parent_window))
        except Exception as e:
            parent_window.after(0, lambda: messagebox.showerror("Error", f"Installation failed: {str(e)}"))
    
    def _deps_install_complete(self, success, parent_window):
        """Handle dependency installation completion"""
        if success:
            messagebox.showinfo("Success", "Dependencies installed successfully!")
            parent_window.destroy()
            # Offer to restart AI engine
            result = messagebox.askyesno("Restart AI Engine", 
                                       "Dependencies updated. Restart AI engine to use new components?")
            if result:
                self.reload_ai_model()
        else:
            messagebox.showwarning("Warning", "Some dependencies could not be installed automatically. Check console for details.")
            
    # Settings methods
    def show_theme_settings(self):
        """Show theme settings dialog"""
        ThemeSettingsDialog(self.root, self)
        
    def show_chat_settings(self):
        """Show chat settings dialog"""
        ChatSettingsDialog(self.root, self)
        
    def show_ai_settings(self):
        """Show AI configuration dialog"""
        AISettingsDialog(self.root, self)
        
    def show_advanced_settings(self):
        """Show advanced settings dialog"""
        AdvancedSettingsDialog(self.root, self)
        
    def reset_settings(self):
        """Reset all settings to defaults"""
        if messagebox.askyesno("Reset Settings", "Reset all settings to defaults?\nThis will restart the application."):
            try:
                settings_file = Path(__file__).parent / "user_settings.json"
                if settings_file.exists():
                    settings_file.unlink()
                messagebox.showinfo("Settings Reset", "Settings reset. Please restart OANA.")
                self.root.quit()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to reset settings: {e}")
                
    def show_model_selector(self):
        """Show AI model selector dialog"""
        ModelSelectorDialog(self.root, self)
                
    def show_statistics(self):
        """Show application statistics"""
        StatisticsDialog(self.root, self)
        
    def show_file_manager(self):
        """Show file manager for documents and chat history"""
        FileManagerDialog(self.root, self)
        
    def run_component_test(self):
        """Run component test"""
        try:
            # Run the test script
            import subprocess
            result = subprocess.run([sys.executable, "test.py"], 
                                  capture_output=True, text=True, cwd=Path(__file__).parent)
            
            TestResultDialog(self.root, result.stdout)
            
        except Exception as e:
            messagebox.showerror("Test Error", f"Failed to run tests: {e}")
            
    def show_user_guide(self):
        """Show user guide"""
        UserGuideDialog(self.root)
        
    def show_shortcuts(self):
        """Show keyboard shortcuts"""
        ShortcutsDialog(self.root)
        
    def update_stats(self):
        """Update chat statistics"""
        if hasattr(self, 'stats_label'):
            total_chars = sum(len(msg['content']) for msg in self.chat_history)
            self.stats_label.config(text=f"Messages: {len(self.chat_history)} | Characters: {total_chars}")
            
        if hasattr(self, 'doc_count_var'):
            self.doc_count_var.set(f"Documents: {len(self.uploaded_documents)}")


# Enhanced Dialog Classes

class ModelSelectorDialog:
    """Dialog for selecting and switching AI models"""
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        
        self.window = tk.Toplevel(parent)
        self.window.title("🤖 AI Model Selector")
        self.window.geometry("700x500")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.setup_ui()
        self.load_models()
        
    def setup_ui(self):
        """Setup the model selector UI"""
        main_frame = ttk.Frame(self.window, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(main_frame, text="🤖 AI Model Selector", 
                 font=("Arial", 16, "bold")).pack(pady=(0, 20))
        
        # Current model info
        info_frame = ttk.LabelFrame(main_frame, text="Current Model", padding="10")
        info_frame.pack(fill=tk.X, pady=(0, 20))
        
        if self.app.ai_engine:
            model_info = self.app.ai_engine.get_model_info()
            current_model = model_info.get('model_name', 'Unknown')
            backend = model_info.get('backend', 'Unknown')
            status = "✅ Loaded" if model_info.get('is_loaded', False) else "❌ Not Loaded"
        else:
            current_model = "None"
            backend = "None"
            status = "❌ Not Initialized"
            
        ttk.Label(info_frame, text=f"Model: {current_model}").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Backend: {backend}").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Status: {status}").pack(anchor=tk.W)
        
        # Available models
        models_frame = ttk.LabelFrame(main_frame, text="Available Models", padding="10")
        models_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Create treeview for models
        columns = ("backend", "size")
        self.models_tree = ttk.Treeview(models_frame, columns=columns, show="tree headings", height=12)
        
        self.models_tree.heading("#0", text="Model Name")
        self.models_tree.heading("backend", text="Backend")
        self.models_tree.heading("size", text="Size (MB)")
        
        self.models_tree.column("#0", width=300)
        self.models_tree.column("backend", width=120)
        self.models_tree.column("size", width=100)
        
        # Scrollbar for treeview
        tree_scrollbar = ttk.Scrollbar(models_frame, orient=tk.VERTICAL, command=self.models_tree.yview)
        self.models_tree.configure(yscrollcommand=tree_scrollbar.set)
        
        self.models_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="🔄 Refresh", 
                  command=self.load_models).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="⚡ Switch Model", 
                  command=self.switch_model).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="📥 Download Models", 
                  command=self.show_model_download).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="❌ Close", 
                  command=self.window.destroy).pack(side=tk.RIGHT)
                  
    def load_models(self):
        """Load available models into the tree"""
        # Clear existing items
        for item in self.models_tree.get_children():
            self.models_tree.delete(item)
            
        try:
            if self.app.ai_engine:
                models = self.app.ai_engine.get_available_models()
                
                for model in models:
                    name = model['name']
                    backend = model['backend']
                    size = f"{model['size_mb']:.1f}" if model['size_mb'] > 0 else "Unknown"
                    
                    self.models_tree.insert("", tk.END, 
                                          text=name,
                                          values=(backend, size),
                                          tags=(model['path'] or model['name'], backend))
                
                if not models:
                    self.models_tree.insert("", tk.END, 
                                          text="No models found", 
                                          values=("", ""))
            else:
                self.models_tree.insert("", tk.END, 
                                      text="AI Engine not initialized", 
                                      values=("", ""))
                                      
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load models: {str(e)}")
            
    def switch_model(self):
        """Switch to the selected model"""
        selection = self.models_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a model to switch to")
            return
            
        selected_item = selection[0]
        model_name = self.models_tree.item(selected_item, 'text')
        
        if model_name in ["No models found", "AI Engine not initialized"]:
            return
            
        tags = self.models_tree.item(selected_item, 'tags')
        if not tags:
            return
            
        model_path = tags[0]
        backend = tags[1] if len(tags) > 1 else "auto"
        
        # Confirm switch
        if not messagebox.askyesno("Switch Model", 
                                  f"Switch to model '{model_name}'?\nThis may take a moment to load."):
            return
            
        try:
            self.window.config(cursor="wait")
            self.window.update()
            
            if self.app.ai_engine:
                if backend == "ollama":
                    success = self.app.ai_engine.switch_model(model_name=model_path, backend=backend)
                else:
                    success = self.app.ai_engine.switch_model(model_path=model_path, backend=backend)
                
                if success:
                    messagebox.showinfo("Success", f"Successfully switched to model: {model_name}")
                    self.app.add_to_chat("System", f"🤖 Switched to AI model: {model_name}")
                    self.setup_ui()  # Refresh the dialog
                else:
                    messagebox.showerror("Error", f"Failed to switch to model: {model_name}")
            else:
                messagebox.showerror("Error", "AI Engine not available")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to switch model: {str(e)}")
        finally:
            self.window.config(cursor="")
            
    def show_model_download(self):
        """Show model download dialog"""
        self.window.destroy()
        ModelDownloadDialog(self.parent, self.app)

class ThemeSettingsDialog:
    """Dialog for theme settings"""
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        
        self.window = tk.Toplevel(parent)
        self.window.title("🎨 Theme Settings")
        self.window.geometry("600x500")  # Made larger
        self.window.transient(parent)
        self.window.grab_set()
        self.window.resizable(True, True)  # Allow resizing
        
        self.setup_ui()
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="🎨 Theme Settings", font=("Arial", 14, "bold")).pack(pady=(0, 20))
        
        # Theme selection
        theme_frame = ttk.LabelFrame(main_frame, text="Color Theme", padding="10")
        theme_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.theme_var = tk.StringVar(value=self.app.settings.get("theme", "light"))
        
        themes = [("Light Theme", "light"), ("Dark Theme", "dark"), ("Blue Theme", "blue")]
        for text, value in themes:
            ttk.Radiobutton(theme_frame, text=text, variable=self.theme_var, value=value).pack(anchor=tk.W, pady=2)
            
        # Font settings
        font_frame = ttk.LabelFrame(main_frame, text="Font Settings", padding="10")
        font_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(font_frame, text="Font Size:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.font_size = tk.IntVar(value=self.app.settings["ui_settings"]["font_size"])
        font_spin = ttk.Spinbox(font_frame, from_=8, to=16, textvariable=self.font_size, width=5)
        font_spin.grid(row=0, column=1, sticky=tk.W)
        
        # UI options
        ui_frame = ttk.LabelFrame(main_frame, text="Interface Options", padding="10")
        ui_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.show_timestamps = tk.BooleanVar(value=self.app.settings["ui_settings"]["show_timestamps"])
        ttk.Checkbutton(ui_frame, text="Show timestamps in chat", variable=self.show_timestamps).pack(anchor=tk.W, pady=2)
        
        self.compact_mode = tk.BooleanVar(value=self.app.settings["ui_settings"]["compact_mode"])
        ttk.Checkbutton(ui_frame, text="Compact mode", variable=self.compact_mode).pack(anchor=tk.W, pady=2)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Make buttons larger and more visible
        ttk.Button(button_frame, text="✅ Apply Theme", 
                  command=self.apply_settings, width=15).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="👁️ Preview", 
                  command=self.preview_theme, width=15).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="❌ Cancel", 
                  command=self.window.destroy, width=15).pack(side=tk.RIGHT)
        
    def apply_settings(self):
        """Apply the selected theme and settings"""
        # Update settings
        self.app.settings["theme"] = self.theme_var.get()
        self.app.settings["ui_settings"]["font_size"] = self.font_size.get()
        self.app.settings["ui_settings"]["show_timestamps"] = self.show_timestamps.get()
        self.app.settings["ui_settings"]["compact_mode"] = self.compact_mode.get()
        
        # Apply theme immediately
        self.app.current_theme = self.theme_var.get()
        self.app.apply_theme()
        
        # Save to database if available
        if self.app.db:
            try:
                self.app.db.save_setting("theme", self.theme_var.get())
                self.app.db.save_setting("font_size", str(self.font_size.get()))
                self.app.db.save_setting("show_timestamps", str(self.show_timestamps.get()))
                self.app.db.save_setting("compact_mode", str(self.compact_mode.get()))
            except Exception as e:
                print(f"Failed to save settings to database: {e}")
        
        # Also save to JSON file as backup
        self.app.save_settings()
        
        messagebox.showinfo("Theme Applied", "Theme has been applied successfully!")
        self.window.destroy()
        
    def preview_theme(self):
        # Simple preview by changing window background
        theme = self.app.themes[self.theme_var.get()]
        self.window.configure(bg=theme["bg"])


class ChatSettingsDialog:
    """Dialog for chat settings"""
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        
        self.window = tk.Toplevel(parent)
        self.window.title("💬 Chat Settings")
        self.window.geometry("500x450")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.setup_ui()
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="💬 Chat Settings", font=("Arial", 14, "bold")).pack(pady=(0, 20))
        
        # Auto-save settings
        autosave_frame = ttk.LabelFrame(main_frame, text="Auto-Save", padding="10")
        autosave_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.auto_save = tk.BooleanVar(value=self.app.settings.get("auto_save_chat", True))
        ttk.Checkbutton(autosave_frame, text="Auto-save chat on exit", variable=self.auto_save).pack(anchor=tk.W, pady=2)
        
        # History settings
        history_frame = ttk.LabelFrame(main_frame, text="Chat History", padding="10")
        history_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(history_frame, text="History limit:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.history_limit = tk.IntVar(value=self.app.settings.get("chat_history_limit", 1000))
        ttk.Spinbox(history_frame, from_=100, to=5000, textvariable=self.history_limit, width=8).grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(history_frame, text="Export format:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.export_format = tk.StringVar(value=self.app.settings.get("auto_export_format", "txt"))
        format_combo = ttk.Combobox(history_frame, textvariable=self.export_format, 
                                   values=["txt", "json", "html", "md"], state="readonly", width=8)
        format_combo.grid(row=1, column=1, sticky=tk.W, pady=(10, 0))
        
        # Clear history
        clear_frame = ttk.LabelFrame(main_frame, text="History Management", padding="10")
        clear_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Button(clear_frame, text="🗑️ Clear Current Chat", 
                  command=self.clear_current_chat, style="Warning.TButton").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(clear_frame, text="🗂️ Manage Saved Chats", 
                  command=self.manage_saved_chats).pack(side=tk.LEFT)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Save", command=self.save_settings).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=self.window.destroy).pack(side=tk.RIGHT)
        
    def save_settings(self):
        self.app.settings["auto_save_chat"] = self.auto_save.get()
        self.app.settings["chat_history_limit"] = self.history_limit.get()
        self.app.settings["auto_export_format"] = self.export_format.get()
        
        self.app.save_settings()
        messagebox.showinfo("Settings Saved", "Chat settings saved successfully!")
        self.window.destroy()
        
    def clear_current_chat(self):
        self.window.destroy()
        self.app.clear_chat_confirm()
        
    def manage_saved_chats(self):
        """Open chat history manager dialog"""
        ChatHistoryManagerDialog(self.window, self.app)


class ChatHistoryManagerDialog:
    """Dialog for managing chat history and sessions"""
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        
        self.window = tk.Toplevel(parent)
        self.window.title("💬 Chat History Manager")
        self.window.geometry("800x600")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.setup_ui()
        self.load_sessions()
        
    def setup_ui(self):
        """Setup the chat history manager UI"""
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(main_frame, text="💬 Chat History Manager", 
                 font=("Arial", 14, "bold")).pack(pady=(0, 15))
        
        # Create paned window for sessions and messages
        paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Left panel - Sessions
        sessions_frame = ttk.LabelFrame(paned, text="Chat Sessions", padding="5")
        paned.add(sessions_frame, weight=1)
        
        # Sessions list
        sessions_list_frame = ttk.Frame(sessions_frame)
        sessions_list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.sessions_tree = ttk.Treeview(sessions_list_frame, columns=("messages", "date"), show="tree headings")
        self.sessions_tree.heading("#0", text="Session")
        self.sessions_tree.heading("messages", text="Messages")
        self.sessions_tree.heading("date", text="Last Access")
        
        self.sessions_tree.column("#0", width=150)
        self.sessions_tree.column("messages", width=80)
        self.sessions_tree.column("date", width=120)
        
        sessions_scrollbar = ttk.Scrollbar(sessions_list_frame, orient=tk.VERTICAL, 
                                         command=self.sessions_tree.yview)
        self.sessions_tree.configure(yscrollcommand=sessions_scrollbar.set)
        
        self.sessions_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sessions_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Session buttons
        session_buttons = ttk.Frame(sessions_frame)
        session_buttons.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(session_buttons, text="Load Session", 
                  command=self.load_selected_session).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(session_buttons, text="Delete Session", 
                  command=self.delete_selected_session).pack(side=tk.LEFT, padx=5)
        ttk.Button(session_buttons, text="Export", 
                  command=self.export_session).pack(side=tk.RIGHT)
        
        # Right panel - Messages
        messages_frame = ttk.LabelFrame(paned, text="Messages", padding="5")
        paned.add(messages_frame, weight=2)
        
        # Messages display
        self.messages_text = scrolledtext.ScrolledText(messages_frame, wrap=tk.WORD, 
                                                      font=("Consolas", 9), state=tk.DISABLED)
        self.messages_text.pack(fill=tk.BOTH, expand=True)
        
        # Bottom buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="New Session", 
                  command=self.create_new_session).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Backup All", 
                  command=self.backup_all_chats).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Clear All History", 
                  command=self.clear_all_history).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="Close", 
                  command=self.window.destroy).pack(side=tk.RIGHT)
        
        # Bind selection event
        self.sessions_tree.bind('<<TreeviewSelect>>', self.on_session_select)
        
    def load_sessions(self):
        """Load chat sessions from database"""
        if not self.app.db:
            return
            
        try:
            sessions = self.app.db.get_chat_sessions()
            
            # Clear existing items
            for item in self.sessions_tree.get_children():
                self.sessions_tree.delete(item)
            
            for session in sessions:
                # Format date for display
                try:
                    updated_at = datetime.fromisoformat(session['updated_at']).strftime('%Y-%m-%d %H:%M')
                except:
                    updated_at = session['updated_at']
                
                title = session.get('title', session['session_id'])
                message_count = session.get('message_count', 0)
                
                self.sessions_tree.insert("", tk.END, 
                                        text=title,
                                        values=(f"{message_count} msgs", updated_at),
                                        tags=(session['session_id'],))
                                        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load sessions: {str(e)}")
            
    def on_session_select(self, event):
        """Handle session selection"""
        selection = self.sessions_tree.selection()
        if not selection:
            return
            
        selected_item = selection[0]
        tags = self.sessions_tree.item(selected_item, 'tags')
        if not tags:
            return
            
        session_id = tags[0]
        
        if not self.app.db:
            return
            
        try:
            messages = self.app.db.get_chat_history(session_id, limit=1000)
            
            self.messages_text.config(state=tk.NORMAL)
            self.messages_text.delete(1.0, tk.END)
            
            for msg in messages:
                try:
                    timestamp = datetime.fromisoformat(msg['timestamp']).strftime('%H:%M:%S')
                except:
                    timestamp = msg['timestamp'][:8] if len(msg['timestamp']) > 8 else msg['timestamp']
                
                role = msg['role']
                message = msg['message']
                
                if role == "user":
                    self.messages_text.insert(tk.END, f"[{timestamp}] 🧑 You:\n", "user")
                elif role == "assistant":
                    self.messages_text.insert(tk.END, f"[{timestamp}] 🤖 AI:\n", "ai")
                else:
                    self.messages_text.insert(tk.END, f"[{timestamp}] ℹ️  {role}:\n", "system")
                    
                self.messages_text.insert(tk.END, f"{message}\n\n")
                
            self.messages_text.config(state=tk.DISABLED)
            
            # Configure text tags for styling
            self.messages_text.tag_configure("user", foreground="blue", font=("Arial", 9, "bold"))
            self.messages_text.tag_configure("ai", foreground="green", font=("Arial", 9, "bold"))
            self.messages_text.tag_configure("system", foreground="gray", font=("Arial", 9, "bold"))
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load messages: {str(e)}")
            
    def load_selected_session(self):
        """Load selected session into main app"""
        selection = self.sessions_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a session to load")
            return
            
        selected_item = selection[0]
        tags = self.sessions_tree.item(selected_item, 'tags')
        if not tags:
            return
            
        session_id = tags[0]
        session_title = self.sessions_tree.item(selected_item, 'text')
        
        result = messagebox.askyesno("Load Session", 
                                   f"Load session '{session_title}' into main chat?\nThis will replace current conversation.")
        
        if result:
            try:
                # Save current session first
                if self.app.chat_history and messagebox.askyesno("Save Current", "Save current chat before loading?"):
                    self.app.save_chat_history()
                
                # Load selected session
                self.app.current_session_id = session_id
                
                # Clear current display
                self.app.chat_display.config(state=tk.NORMAL)
                self.app.chat_display.delete(1.0, tk.END)
                self.app.chat_display.config(state=tk.DISABLED)
                
                # Load messages from database
                self.app.chat_history.clear()
                messages = self.app.db.get_chat_history(session_id, limit=1000)
                
                for msg in messages:
                    # Convert role names for consistency
                    display_role = "You" if msg['role'] == "user" else "AI" if msg['role'] == "assistant" else msg['role']
                    
                    # Add to display (without saving to database again)
                    self.app.add_message_to_display_only(display_role, msg['message'])
                    
                    # Add to history
                    self.app.chat_history.append({
                        'role': display_role,
                        'content': msg['message'],
                        'timestamp': msg['timestamp']
                    })
                
                self.app.add_to_chat("System", f"📂 Loaded chat session: {session_title}")
                self.window.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load session: {str(e)}")
            
            # Refresh chat display
            for msg in self.app.chat_history:
                self.app.add_to_chat(msg['sender'], msg['content'])
                
            messagebox.showinfo("Success", f"Session '{session_id}' loaded successfully!")
            self.window.destroy()
            
    def delete_selected_session(self):
        """Delete selected session"""
        selection = self.sessions_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a session to delete")
            return
            
        selected_item = selection[0]
        session_id = self.sessions_tree.item(selected_item, 'text')
        
        result = messagebox.askyesno("Delete Session", 
                                   f"Are you sure you want to delete session '{session_id}'?\nThis action cannot be undone.")
        
        if result and self.app.db:
            try:
                deleted_count = self.app.db.clear_chat_history(session_id)
                self.sessions_tree.delete(selected_item)
                messagebox.showinfo("Success", f"Session '{session_id}' deleted ({deleted_count} messages removed)")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete session: {str(e)}")
                
    def export_session(self):
        """Export selected session to file"""
        selection = self.sessions_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a session to export")
            return
            
        selected_item = selection[0]
        session_id = self.sessions_tree.item(selected_item, 'text')
        
        filename = filedialog.asksaveasfilename(
            title=f"Export session '{session_id}'",
            defaultextension=".txt",
            filetypes=[
                ("Text files", "*.txt"),
                ("JSON files", "*.json"),
                ("HTML files", "*.html")
            ]
        )
        
        if filename and self.app.db:
            try:
                messages = self.app.db.get_chat_history(session_id, limit=10000)
                ext = os.path.splitext(filename)[1].lower()
                
                if ext == '.json':
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(messages, f, indent=2, ensure_ascii=False)
                        
                elif ext == '.html':
                    html_content = f"""<!DOCTYPE html>
<html><head><title>Chat Session: {session_id}</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 20px; }}
.message {{ margin-bottom: 15px; padding: 10px; border-radius: 5px; }}
.user {{ background-color: #e3f2fd; }}
.ai {{ background-color: #f1f8e9; }}
.system {{ background-color: #f5f5f5; }}
.timestamp {{ color: #666; font-size: 0.9em; }}
</style></head><body>
<h1>Chat Session: {session_id}</h1>
"""
                    for msg in messages:
                        role_class = msg['role'].lower()
                        message_html = msg['message'].replace('\n', '<br>')
                        html_content += f"""
<div class="message {role_class}">
    <div class="timestamp">[{msg['timestamp']}] {msg['role']}</div>
    <div>{message_html}</div>
</div>
"""
                    html_content += "</body></html>"
                    
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(html_content)
                        
                else:  # txt format
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(f"Chat Session: {session_id}\n")
                        f.write("=" * 50 + "\n\n")
                        
                        for msg in messages:
                            f.write(f"[{msg['timestamp']}] {msg['role']}:\n")
                            f.write(f"{msg['message']}\n\n")
                            
                messagebox.showinfo("Success", f"Session exported to {filename}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export session: {str(e)}")
                
    def create_new_session(self):
        """Create a new chat session"""
        session_id = simpledialog.askstring("New Session", "Enter session name:", 
                                           initialvalue=f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        
        if session_id and self.app.db:
            try:
                self.app.db.create_session(session_id, f"Session created on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                messagebox.showinfo("Success", f"Session '{session_id}' created!")
                self.load_sessions()  # Refresh the list
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create session: {str(e)}")
                
    def backup_all_chats(self):
        """Backup all chat history to JSON file"""
        filename = filedialog.asksaveasfilename(
            title="Backup all chat history",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )
        
        if filename and self.app.db:
            try:
                success = self.app.db.backup_to_json(filename)
                if success:
                    messagebox.showinfo("Success", f"All chat history backed up to {filename}")
                else:
                    messagebox.showerror("Error", "Failed to create backup")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to backup chats: {str(e)}")
                
    def clear_all_history(self):
        """Clear all chat history"""
        result = messagebox.askyesno("Clear All History", 
                                   "Are you sure you want to clear ALL chat history?\nThis action cannot be undone!")
        
        if result and self.app.db:
            try:
                # Clear all sessions
                with sqlite3.connect(self.app.db.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM chat_history")
                    cursor.execute("DELETE FROM sessions")
                    conn.commit()
                    
                messagebox.showinfo("Success", "All chat history cleared!")
                self.load_sessions()  # Refresh the list
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to clear history: {str(e)}")


class AISettingsDialog:
    """Dialog for AI configuration"""
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        
        self.window = tk.Toplevel(parent)
        self.window.title("🤖 AI Configuration")
        self.window.geometry("600x500")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.setup_ui()
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="🤖 AI Configuration", font=("Arial", 14, "bold")).pack(pady=(0, 20))
        
        # Model settings
        model_frame = ttk.LabelFrame(main_frame, text="Model Settings", padding="10")
        model_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Temperature
        ttk.Label(model_frame, text="Temperature (creativity):").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.temperature = tk.DoubleVar(value=self.app.settings["ai_settings"]["temperature"])
        temp_scale = ttk.Scale(model_frame, from_=0.1, to=2.0, variable=self.temperature, orient=tk.HORIZONTAL, length=200)
        temp_scale.grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
        temp_label = ttk.Label(model_frame, text="0.7")
        temp_label.grid(row=0, column=2)
        
        def update_temp_label(*args):
            temp_label.config(text=f"{self.temperature.get():.1f}")
        self.temperature.trace_add('write', update_temp_label)
        
        # Max tokens
        ttk.Label(model_frame, text="Max response length:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.max_tokens = tk.IntVar(value=self.app.settings["ai_settings"]["max_tokens"])
        ttk.Spinbox(model_frame, from_=100, to=2048, textvariable=self.max_tokens, width=8).grid(row=1, column=1, sticky=tk.W, pady=(10, 0))
        
        # System prompt
        prompt_frame = ttk.LabelFrame(main_frame, text="System Prompt", padding="10")
        prompt_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        self.system_prompt = scrolledtext.ScrolledText(prompt_frame, height=6, wrap=tk.WORD)
        self.system_prompt.pack(fill=tk.BOTH, expand=True)
        self.system_prompt.insert(tk.END, self.app.settings["ai_settings"]["system_prompt"])
        
        # Backend preferences
        backend_frame = ttk.LabelFrame(main_frame, text="Backend Preferences", padding="10")
        backend_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.preferred_backend = tk.StringVar(value=self.app.settings["model_settings"]["preferred_backend"])
        backends = [("llama-cpp-python", "llama-cpp"), ("Ollama", "ollama"), ("Transformers", "transformers")]
        for text, value in backends:
            ttk.Radiobutton(backend_frame, text=text, variable=self.preferred_backend, value=value).pack(anchor=tk.W, pady=2)
            
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Save", command=self.save_settings).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Reset to Defaults", command=self.reset_defaults).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Test Settings", command=self.test_settings).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=self.window.destroy).pack(side=tk.RIGHT)
        
    def save_settings(self):
        self.app.settings["ai_settings"]["temperature"] = self.temperature.get()
        self.app.settings["ai_settings"]["max_tokens"] = self.max_tokens.get()
        self.app.settings["ai_settings"]["system_prompt"] = self.system_prompt.get(1.0, tk.END).strip()
        self.app.settings["model_settings"]["preferred_backend"] = self.preferred_backend.get()
        
        self.app.save_settings()
        messagebox.showinfo("Settings Saved", "AI settings saved! Changes will apply to new conversations.")
        self.window.destroy()
        
    def reset_defaults(self):
        if messagebox.askyesno("Reset", "Reset AI settings to defaults?"):
            self.temperature.set(0.7)
            self.max_tokens.set(512)
            self.system_prompt.delete(1.0, tk.END)
            self.system_prompt.insert(tk.END, "You are OANA, a helpful offline AI assistant specialized in document analysis and note-taking.")
            self.preferred_backend.set("llama-cpp")
            
    def test_settings(self):
        """Test AI settings by sending a simple query"""
        try:
            # Create a test message
            test_prompt = "Test message: Please respond with 'AI test successful!'"
            
            # Show processing dialog
            test_window = tk.Toplevel(self.window)
            test_window.title("Testing AI Settings")
            test_window.geometry("300x150")
            test_window.transient(self.window)
            test_window.grab_set()
            
            ttk.Label(test_window, text="Testing AI with current settings...").pack(pady=20)
            progress = ttk.Progressbar(test_window, mode='indeterminate')
            progress.pack(pady=10, padx=20, fill=tk.X)
            progress.start()
            
            def run_test():
                try:
                    # Test if AI engine is available
                    if self.app.ai_engine and self.app.ai_engine.model:
                        # Try a simple generation
                        response = self.app.ai_engine.generate_response(
                            test_prompt, 
                            temperature=self.temperature.get(),
                            max_tokens=min(50, self.max_tokens.get())
                        )
                        progress.stop()
                        test_window.destroy()
                        
                        result_window = tk.Toplevel(self.window)
                        result_window.title("Test Results")
                        result_window.geometry("400x200")
                        result_window.transient(self.window)
                        
                        ttk.Label(result_window, text="✅ AI Test Successful!", 
                                 font=("Arial", 12, "bold"), foreground="green").pack(pady=10)
                        
                        result_text = scrolledtext.ScrolledText(result_window, height=6, wrap=tk.WORD)
                        result_text.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
                        result_text.insert(tk.END, f"Response: {response}")
                        result_text.config(state=tk.DISABLED)
                        
                        ttk.Button(result_window, text="Close", 
                                  command=result_window.destroy).pack(pady=5)
                    else:
                        progress.stop()
                        test_window.destroy()
                        messagebox.showwarning("Test Failed", 
                                             "AI model not loaded. Please load a model first.")
                        
                except Exception as e:
                    progress.stop()
                    test_window.destroy()
                    messagebox.showerror("Test Failed", 
                                       f"AI test failed: {str(e)}")
            
            # Run test in thread to avoid blocking UI
            threading.Thread(target=run_test, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to run test: {str(e)}")


class AdvancedSettingsDialog:
    """Dialog for advanced settings"""
    def __init__(self, parent, app):
        self.window = tk.Toplevel(parent)
        self.window.title("🔧 Advanced Settings")
        self.window.geometry("500x400")
        self.window.transient(parent)
        
        ttk.Label(self.window, text="🔧 Advanced Settings", font=("Arial", 14, "bold")).pack(pady=20)
        ttk.Label(self.window, text="Advanced configuration options will be added here.").pack(pady=20)
        ttk.Button(self.window, text="Close", command=self.window.destroy).pack(pady=20)


class StatisticsDialog:
    """Dialog showing application statistics"""
    def __init__(self, parent, app):
        self.app = app
        self.window = tk.Toplevel(parent)
        self.window.title("📊 Statistics")
        self.window.geometry("500x400")
        self.window.transient(parent)
        
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="📊 OANA Statistics", font=("Arial", 14, "bold")).pack(pady=(0, 20))
        
        # Calculate statistics
        total_messages = len(app.chat_history)
        total_chars = sum(len(msg['content']) for msg in app.chat_history)
        total_docs = len(app.uploaded_documents)
        total_doc_size = sum(len(doc['content']) for doc in app.uploaded_documents)
        
        stats_text = f"""
Chat Statistics:
• Total Messages: {total_messages}
• Total Characters: {total_chars:,}
• Average Message Length: {total_chars // max(total_messages, 1)} chars

Document Statistics:
• Documents Uploaded: {total_docs}
• Total Content Size: {total_doc_size:,} characters
• Average Document Size: {total_doc_size // max(total_docs, 1):,} chars

Session Information:
• Current Theme: {app.settings.get('theme', 'light').title()}
• AI Backend: {app.ai_engine.backend if app.ai_engine else 'None'}
• AI Status: {'Ready' if app.ai_engine and app.ai_engine.is_ready() else 'Not Ready'}
        """
        
        stats_label = ttk.Label(main_frame, text=stats_text, justify=tk.LEFT)
        stats_label.pack(fill=tk.BOTH, expand=True)
        
        ttk.Button(main_frame, text="Close", command=self.window.destroy).pack(pady=20)


class FileManagerDialog:
    """Dialog for managing files and chat history"""
    def __init__(self, parent, app):
        self.app = app
        self.window = tk.Toplevel(parent)
        self.window.title("🗂️ File Manager")
        self.window.geometry("700x600")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.setup_ui()
        self.refresh_files()
        
    def setup_ui(self):
        """Setup file manager UI"""
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(main_frame, text="🗂️ File Manager", 
                 font=("Arial", 14, "bold")).pack(pady=(0, 15))
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Documents tab
        docs_frame = ttk.Frame(notebook)
        notebook.add(docs_frame, text="📄 Documents")
        self.setup_documents_tab(docs_frame)
        
        # Chat History tab
        chat_frame = ttk.Frame(notebook)
        notebook.add(chat_frame, text="💬 Chat History")
        self.setup_chat_history_tab(chat_frame)
        
        # System Files tab
        system_frame = ttk.Frame(notebook)
        notebook.add(system_frame, text="⚙️ System Files")
        self.setup_system_files_tab(system_frame)
        
        # Bottom buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="Refresh", 
                  command=self.refresh_files).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Open Data Folder", 
                  command=self.open_data_folder).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="Close", 
                  command=self.window.destroy).pack(side=tk.RIGHT)
        
    def setup_documents_tab(self, parent):
        """Setup documents management tab"""
        # Document list
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True, padding="10")
        
        ttk.Label(list_frame, text="Uploaded Documents:").pack(anchor=tk.W, pady=(0, 5))
        
        self.docs_tree = ttk.Treeview(list_frame, columns=("size", "type"), show="tree headings")
        self.docs_tree.heading("#0", text="Document")
        self.docs_tree.heading("size", text="Size")
        self.docs_tree.heading("type", text="Type")
        
        self.docs_tree.column("#0", width=300)
        self.docs_tree.column("size", width=80)
        self.docs_tree.column("type", width=60)
        
        docs_scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.docs_tree.yview)
        self.docs_tree.configure(yscrollcommand=docs_scroll.set)
        
        self.docs_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        docs_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Document buttons
        doc_buttons = ttk.Frame(parent)
        doc_buttons.pack(fill=tk.X, padding="10")
        
        ttk.Button(doc_buttons, text="View Document", 
                  command=self.view_selected_doc).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(doc_buttons, text="Export Document", 
                  command=self.export_selected_doc).pack(side=tk.LEFT, padx=5)
        ttk.Button(doc_buttons, text="Remove Document", 
                  command=self.remove_selected_doc).pack(side=tk.LEFT, padx=5)
        
    def setup_chat_history_tab(self, parent):
        """Setup chat history management tab"""
        # Info label
        ttk.Label(parent, text="Chat History Management", 
                 font=("Arial", 11, "bold")).pack(pady=10)
        
        # Stats frame
        stats_frame = ttk.LabelFrame(parent, text="Statistics", padding="10")
        stats_frame.pack(fill=tk.X, padx=10, pady=5)
        
        total_messages = len(self.app.chat_history)
        self.chat_stats_label = ttk.Label(stats_frame, 
                                         text=f"Total Messages: {total_messages}")
        self.chat_stats_label.pack(anchor=tk.W)
        
        # Buttons
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(fill=tk.X, padx=10, pady=20)
        
        ttk.Button(buttons_frame, text="💬 Open Chat History Manager", 
                  command=self.open_chat_manager).pack(fill=tk.X, pady=5)
        ttk.Button(buttons_frame, text="📥 Export All Chats", 
                  command=self.export_all_chats).pack(fill=tk.X, pady=5)
        ttk.Button(buttons_frame, text="🗑️ Clear All Chat History", 
                  command=self.clear_all_chats).pack(fill=tk.X, pady=5)
        
    def setup_system_files_tab(self, parent):
        """Setup system files management tab"""
        # System info
        ttk.Label(parent, text="System Files & Settings", 
                 font=("Arial", 11, "bold")).pack(pady=10)
        
        info_frame = ttk.LabelFrame(parent, text="File Locations", padding="10")
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        app_dir = Path(__file__).parent
        
        locations_text = f"""
Application Directory: {app_dir}
Settings File: user_settings.json
Database: data/oana_database.db
Models Directory: models/
Logs Directory: logs/
        """
        
        ttk.Label(info_frame, text=locations_text, justify=tk.LEFT).pack(anchor=tk.W)
        
        # System buttons
        sys_buttons = ttk.Frame(parent)
        sys_buttons.pack(fill=tk.X, padx=10, pady=20)
        
        ttk.Button(sys_buttons, text="🔧 Open Settings File", 
                  command=self.open_settings_file).pack(fill=tk.X, pady=2)
        ttk.Button(sys_buttons, text="🗃️ Open Database File", 
                  command=self.open_database_file).pack(fill=tk.X, pady=2)
        ttk.Button(sys_buttons, text="📋 View Logs", 
                  command=self.view_logs).pack(fill=tk.X, pady=2)
        ttk.Button(sys_buttons, text="🧹 Clean Temp Files", 
                  command=self.clean_temp_files).pack(fill=tk.X, pady=2)
        
    def refresh_files(self):
        """Refresh file listings"""
        # Clear documents tree
        for item in self.docs_tree.get_children():
            self.docs_tree.delete(item)
            
        # Populate documents
        for i, doc in enumerate(self.app.uploaded_documents):
            filename = doc.get('filename', f'Document {i+1}')
            size = len(doc.get('content', ''))
            doc_type = Path(filename).suffix.upper() if '.' in filename else 'TXT'
            
            self.docs_tree.insert("", tk.END, text=filename, 
                                 values=(f"{size:,} chars", doc_type))
                                 
    def view_selected_doc(self):
        """View selected document content"""
        selection = self.docs_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a document to view")
            return
            
        item = selection[0]
        doc_name = self.docs_tree.item(item, 'text')
        
        # Find the document
        doc_content = None
        for doc in self.app.uploaded_documents:
            if doc.get('filename', '').endswith(doc_name.split('/')[-1]):
                doc_content = doc.get('content', '')
                break
                
        if doc_content:
            # Show content in new window
            view_window = tk.Toplevel(self.window)
            view_window.title(f"Document: {doc_name}")
            view_window.geometry("700x500")
            
            text_widget = scrolledtext.ScrolledText(view_window, wrap=tk.WORD)
            text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            text_widget.insert(tk.END, doc_content)
            text_widget.config(state=tk.DISABLED)
            
    def export_selected_doc(self):
        """Export selected document"""
        messagebox.showinfo("Info", "Document export feature available through main document panel")
        
    def remove_selected_doc(self):
        """Remove selected document"""
        selection = self.docs_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a document to remove")
            return
            
        if messagebox.askyesno("Confirm", "Remove selected document?"):
            item = selection[0]
            doc_name = self.docs_tree.item(item, 'text')
            
            # Remove from app's document list
            self.app.uploaded_documents = [
                doc for doc in self.app.uploaded_documents 
                if not doc.get('filename', '').endswith(doc_name.split('/')[-1])
            ]
            
            self.refresh_files()
            messagebox.showinfo("Success", "Document removed successfully")
            
    def open_chat_manager(self):
        """Open chat history manager"""
        from app import ChatHistoryManagerDialog
        ChatHistoryManagerDialog(self.window, self.app)
        
    def export_all_chats(self):
        """Export all chat history"""
        if self.app.db:
            filename = filedialog.asksaveasfilename(
                title="Export All Chats",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json")]
            )
            
            if filename:
                try:
                    success = self.app.db.backup_to_json(filename)
                    if success:
                        messagebox.showinfo("Success", f"All chats exported to {filename}")
                    else:
                        messagebox.showerror("Error", "Failed to export chats")
                except Exception as e:
                    messagebox.showerror("Error", f"Export failed: {str(e)}")
        else:
            messagebox.showwarning("Warning", "Database not available")
            
    def clear_all_chats(self):
        """Clear all chat history"""
        if messagebox.askyesno("Warning", "This will permanently delete ALL chat history. Continue?"):
            if self.app.db:
                try:
                    with sqlite3.connect(self.app.db.db_path) as conn:
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM chat_history")
                        cursor.execute("DELETE FROM sessions")
                        conn.commit()
                    messagebox.showinfo("Success", "All chat history cleared")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to clear history: {str(e)}")
            else:
                messagebox.showwarning("Warning", "Database not available")
                
    def open_data_folder(self):
        """Open data folder in file explorer"""
        app_dir = Path(__file__).parent
        data_dir = app_dir / "data"
        
        try:
            if platform.system() == "Windows":
                os.startfile(data_dir)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", data_dir])
            else:  # Linux
                subprocess.run(["xdg-open", data_dir])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open data folder: {str(e)}")
            
    def open_settings_file(self):
        """Open settings file in default editor"""
        settings_file = Path(__file__).parent / "user_settings.json"
        
        try:
            if platform.system() == "Windows":
                os.startfile(settings_file)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", settings_file])
            else:  # Linux
                subprocess.run(["xdg-open", settings_file])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open settings file: {str(e)}")
            
    def open_database_file(self):
        """Open database file location"""
        db_file = Path(__file__).parent / "data" / "oana_database.db"
        db_dir = db_file.parent
        
        try:
            if platform.system() == "Windows":
                os.startfile(db_dir)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", db_dir])
            else:  # Linux
                subprocess.run(["xdg-open", db_dir])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open database location: {str(e)}")
            
    def view_logs(self):
        """View application logs"""
        logs_dir = Path(__file__).parent / "logs"
        
        if not logs_dir.exists():
            messagebox.showinfo("Info", "No logs directory found")
            return
            
        log_files = list(logs_dir.glob("*.log"))
        
        if not log_files:
            messagebox.showinfo("Info", "No log files found")
            return
            
        # Show latest log file
        latest_log = max(log_files, key=lambda f: f.stat().st_mtime)
        
        try:
            with open(latest_log, 'r', encoding='utf-8') as f:
                content = f.read()
                
            log_window = tk.Toplevel(self.window)
            log_window.title(f"Log: {latest_log.name}")
            log_window.geometry("800x600")
            
            text_widget = scrolledtext.ScrolledText(log_window, wrap=tk.WORD, font=("Consolas", 9))
            text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            text_widget.insert(tk.END, content)
            text_widget.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read log file: {str(e)}")
            
    def clean_temp_files(self):
        """Clean temporary files"""
        try:
            temp_count = 0
            app_dir = Path(__file__).parent
            
            # Clean __pycache__ directories
            for pycache_dir in app_dir.rglob("__pycache__"):
                for pyc_file in pycache_dir.glob("*.pyc"):
                    pyc_file.unlink()
                    temp_count += 1
                    
            messagebox.showinfo("Success", f"Cleaned {temp_count} temporary files")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to clean temp files: {str(e)}")


class TestResultDialog:
    """Dialog showing test results"""
    def __init__(self, parent, results):
        self.window = tk.Toplevel(parent)
        self.window.title("🧪 Test Results")
        self.window.geometry("700x500")
        self.window.transient(parent)
        
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="🧪 Component Test Results", font=("Arial", 14, "bold")).pack(pady=(0, 20))
        
        text_widget = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, font=("Consolas", 10))
        text_widget.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        text_widget.insert(tk.END, results)
        text_widget.configure(state=tk.DISABLED)
        
        ttk.Button(main_frame, text="Close", command=self.window.destroy).pack()


class UserGuideDialog:
    """Dialog showing user guide"""
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("📖 User Guide")
        self.window.geometry("800x600")
        self.window.transient(parent)
        
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="📖 OANA User Guide", font=("Arial", 14, "bold")).pack(pady=(0, 20))
        
        guide_text = """
Welcome to OANA - Offline AI and Note Assistant!

🚀 GETTING STARTED:
1. Upload documents using the "Upload Document" button
2. Select a chat mode (General, Document Q&A, Note Taking, etc.)
3. Start chatting with the AI assistant

💬 CHAT MODES:
• General: Normal conversation with the AI
• Document Q&A: Ask questions about uploaded documents
• Note Taking: AI helps create structured notes
• Summarize: Generate summaries from documents
• Creative: Creative writing and brainstorming

📄 DOCUMENT FEATURES:
• Upload PDF, DOCX, DOC, and TXT files
• Automatic text extraction and processing
• Document summarization
• Smart search across all documents

⚙️ SETTINGS:
• Themes: Choose from Light, Dark, or Blue themes
• AI Configuration: Adjust temperature, response length, system prompt
• Chat Settings: Auto-save, history limits, export formats

🎯 KEYBOARD SHORTCUTS:
• Ctrl+O: Upload document
• Ctrl+S: Save chat history
• Ctrl+N: Clear chat
• F1: Show this user guide
• F5: Reload AI model

💡 TIPS:
• Use Document Q&A mode for best results when asking about uploaded files
• The AI works completely offline - your data stays private
• Save important conversations using the export features
• Try different AI settings to customize the assistant's behavior

For more help, check the Troubleshooting guide or visit our website.
        """
        
        text_widget = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, font=("Segoe UI", 10))
        text_widget.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        text_widget.insert(tk.END, guide_text)
        text_widget.configure(state=tk.DISABLED)
        
        ttk.Button(main_frame, text="Close", command=self.window.destroy).pack()


class ShortcutsDialog:
    """Dialog showing keyboard shortcuts"""
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("🎯 Keyboard Shortcuts")
        self.window.geometry("500x400")
        self.window.transient(parent)
        
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="🎯 Keyboard Shortcuts", font=("Arial", 14, "bold")).pack(pady=(0, 20))
        
        shortcuts_text = """
FILE OPERATIONS:
Ctrl+O          Upload document
Ctrl+S          Save chat history
Ctrl+N          Clear chat history

APPLICATION:
F1              Show user guide
F5              Reload AI model
Alt+F4          Exit application

CHAT:
Enter           Send message
Shift+Enter     Send message (alternative)

NAVIGATION:
Tab             Navigate between elements
Space           Activate buttons/checkboxes
Esc             Close dialogs

EDITING:
Ctrl+A          Select all text
Ctrl+C          Copy text
Ctrl+V          Paste text
Ctrl+Z          Undo (in text fields)

These shortcuts help you use OANA more efficiently!
        """
        
        text_widget = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, font=("Consolas", 10))
        text_widget.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        text_widget.insert(tk.END, shortcuts_text)
        text_widget.configure(state=tk.DISABLED)
        
        ttk.Button(main_frame, text="Close", command=self.window.destroy).pack()


# Continue with more dialog classes...


class ModelDownloadDialog:
    """Dialog for downloading AI models"""
    def __init__(self, parent, ai_engine):
        self.parent = parent
        self.ai_engine = ai_engine
        self.downloader = None
        
        # Import the model downloader
        try:
            from download_models import ModelDownloader
            self.downloader = ModelDownloader()
        except ImportError:
            messagebox.showerror("Error", "Model downloader not available. Please check download_models.py")
            return
        
        self.window = tk.Toplevel(parent)
        self.window.title("Download AI Models")
        self.window.geometry("700x500")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.setup_ui()
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="AI Model Downloader", font=("Arial", 14, "bold"))
        title_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="Current Status", padding="5")
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.status_text = scrolledtext.ScrolledText(status_frame, height=4, wrap=tk.WORD)
        self.status_text.pack(fill=tk.BOTH, expand=True)
        
        # Check current model status
        self.check_current_status()
        
        # Model list frame
        model_frame = ttk.LabelFrame(main_frame, text="Available Models", padding="5")
        model_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Model list
        columns = ("size", "description", "status")
        self.model_tree = ttk.Treeview(model_frame, columns=columns, show="tree headings", height=8)
        self.model_tree.heading("#0", text="Model Name")
        self.model_tree.heading("size", text="Size")
        self.model_tree.heading("description", text="Description")
        self.model_tree.heading("status", text="Status")
        
        # Configure column widths
        self.model_tree.column("#0", width=200)
        self.model_tree.column("size", width=100)
        self.model_tree.column("description", width=200)
        self.model_tree.column("status", width=150)
        
        self.model_tree.pack(fill=tk.BOTH, expand=True)
        
        # Populate model list
        self.populate_models()
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="Download Selected", 
                  command=self.download_selected_model).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="Download Recommended", 
                  command=self.download_recommended).pack(side=tk.LEFT, padx=(10, 0))
        ttk.Button(button_frame, text="Refresh Status", 
                  command=self.refresh_status).pack(side=tk.LEFT, padx=(10, 0))
        ttk.Button(button_frame, text="Browse Local Files", 
                  command=self.browse_local).pack(side=tk.LEFT, padx=(10, 0))
        ttk.Button(button_frame, text="Close", 
                  command=self.window.destroy).pack(side=tk.RIGHT)
        
    def check_current_status(self):
        """Check current AI engine and model status"""
        status_lines = []
        
        # Check AI engine status
        if self.ai_engine and hasattr(self.ai_engine, 'get_model_info'):
            model_info = self.ai_engine.get_model_info()
            status_lines.append(f"Current Backend: {model_info.get('backend', 'Unknown')}")
            status_lines.append(f"Model Loaded: {'Yes' if model_info.get('is_loaded', False) else 'No'}")
            
            available_backends = model_info.get('available_backends', {})
            status_lines.append("Available Backends:")
            for backend, available in available_backends.items():
                status = "✅" if available else "❌"
                status_lines.append(f"  • {backend}: {status}")
        else:
            status_lines.append("AI Engine not initialized")
        
        # Check for downloaded models
        if self.downloader:
            models_dir = self.downloader.models_dir
            if models_dir.exists():
                gguf_files = list(models_dir.glob("*.gguf"))
                status_lines.append(f"\nDownloaded Models: {len(gguf_files)}")
                for model_file in gguf_files:
                    size_mb = model_file.stat().st_size / (1024 * 1024)
                    status_lines.append(f"  • {model_file.name} ({size_mb:.1f} MB)")
            else:
                status_lines.append("\nNo models directory found")
        
        self.status_text.delete(1.0, tk.END)
        self.status_text.insert(1.0, "\n".join(status_lines))
        
    def populate_models(self):
        """Populate the model list"""
        if not self.downloader:
            return
            
        # Clear existing items
        for item in self.model_tree.get_children():
            self.model_tree.delete(item)
        
        # Add models from downloader
        for i, model in enumerate(self.downloader.recommended_models):
            # Check if model is already downloaded
            local_path = self.downloader.models_dir / model['filename']
            if local_path.exists():
                status = "✅ Downloaded"
            else:
                status = "⬇️ Available"
            
            # Add recommended tag
            name = model['name']
            if model.get('recommended', False):
                name += " ⭐"
            
            self.model_tree.insert("", tk.END, text=name, 
                                 values=(model['size'], model['description'], status))
    
    def download_selected_model(self):
        """Download the selected model"""
        selection = self.model_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a model to download")
            return
        
        if not self.downloader:
            messagebox.showerror("Error", "Model downloader not available")
            return
        
        # Get selected model index
        selected_item = selection[0]
        item_index = self.model_tree.index(selected_item)
        model_index = item_index + 1  # downloader uses 1-based indexing
        
        # Start download in a separate thread
        threading.Thread(target=self._download_model_thread, 
                        args=(model_index,), daemon=True).start()
    
    def download_recommended(self):
        """Download all recommended models"""
        if not self.downloader:
            messagebox.showerror("Error", "Model downloader not available")
            return
        
        result = messagebox.askyesno("Confirm Download", 
                                   "This will download all recommended models. This may take some time. Continue?")
        if result:
            threading.Thread(target=self._download_recommended_thread, daemon=True).start()
    
    def _download_model_thread(self, model_index):
        """Download a single model in a thread"""
        try:
            success = self.downloader.download_model(model_index)
            self.window.after(0, lambda: self._download_complete(success))
        except Exception as e:
            self.window.after(0, lambda: messagebox.showerror("Download Error", f"Failed to download model: {str(e)}"))
    
    def _download_recommended_thread(self):
        """Download recommended models in a thread"""
        try:
            self.downloader.download_recommended()
            self.window.after(0, lambda: self._download_complete(True))
        except Exception as e:
            self.window.after(0, lambda: messagebox.showerror("Download Error", f"Failed to download models: {str(e)}"))
    
    def _download_complete(self, success):
        """Handle download completion"""
        if success:
            messagebox.showinfo("Success", "Model download completed!")
            self.refresh_status()
            # Offer to reload AI engine
            result = messagebox.askyesno("Reload AI Engine", 
                                       "Model downloaded successfully. Would you like to reload the AI engine to use the new model?")
            if result and self.ai_engine:
                self.ai_engine.reload_model()
        else:
            messagebox.showerror("Error", "Model download failed. Check the console for details.")
    
    def refresh_status(self):
        """Refresh the status and model list"""
        self.check_current_status()
        self.populate_models()
        
    def browse_local(self):
        """Browse for local model files"""
        filename = filedialog.askopenfilename(
            title="Select local model file",
            filetypes=[("GGUF files", "*.gguf"), ("All files", "*.*")]
        )
        if filename:
            # Copy file to models directory
            if self.downloader:
                try:
                    import shutil
                    dest_path = self.downloader.models_dir / os.path.basename(filename)
                    shutil.copy2(filename, dest_path)
                    messagebox.showinfo("Success", f"Model copied to: {dest_path}")
                    self.refresh_status()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to copy model: {str(e)}")
            else:
                messagebox.showinfo("Info", f"Local model selected: {os.path.basename(filename)}")


class ModelSettingsDialog:
    """Dialog for model settings"""
    def __init__(self, parent, ai_engine):
        self.parent = parent
        self.ai_engine = ai_engine
        
        self.window = tk.Toplevel(parent)
        self.window.title("Model Settings")
        self.window.geometry("400x300")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.setup_ui()
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Temperature
        ttk.Label(main_frame, text="Temperature:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.temp_var = tk.DoubleVar(value=0.7)
        temp_scale = ttk.Scale(main_frame, from_=0.1, to=2.0, variable=self.temp_var, orient=tk.HORIZONTAL)
        temp_scale.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        ttk.Label(main_frame, textvariable=self.temp_var).grid(row=0, column=2, padx=(10, 0), pady=2)
        
        # Max tokens
        ttk.Label(main_frame, text="Max Tokens:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.tokens_var = tk.IntVar(value=512)
        tokens_spin = ttk.Spinbox(main_frame, from_=100, to=2048, textvariable=self.tokens_var, width=10)
        tokens_spin.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=10, column=0, columnspan=3, pady=20, sticky=(tk.W, tk.E))
        
        ttk.Button(button_frame, text="Apply", command=self.apply_settings).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="Reset", command=self.reset_settings).pack(side=tk.LEFT, padx=(10, 0))
        ttk.Button(button_frame, text="Close", command=self.window.destroy).pack(side=tk.RIGHT)
        
        main_frame.columnconfigure(1, weight=1)
        
    def apply_settings(self):
        messagebox.showinfo("Info", "Settings applied successfully")
        
    def reset_settings(self):
        self.temp_var.set(0.7)
        self.tokens_var.set(512)


class TroubleshootingDialog:
    """Dialog showing troubleshooting information"""
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Troubleshooting Guide")
        self.window.geometry("700x500")
        self.window.transient(parent)
        
        self.setup_ui()
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        text_widget = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True)
        
        troubleshooting_text = """
TROUBLESHOOTING GUIDE

🔧 COMMON ISSUES AND SOLUTIONS

1. AI Engine Not Ready
   • Problem: "AI engine is not ready" message
   • Solution: Download a compatible model file (.gguf format)
   • Check: Models folder should contain at least one .gguf file
   • Alternative: Use the Model Downloader in the Models menu

2. Document Upload Fails
   • Problem: Cannot process PDF or Word documents
   • Solution: Ensure file is not corrupted or password-protected
   • Supported: PDF, DOCX, DOC, TXT files
   • Try: Converting file to a different format

3. Slow Response Times
   • Problem: AI takes too long to respond
   • Solution: Use smaller models (TinyLlama recommended for older systems)
   • Check: Available RAM (8GB+ recommended for larger models)
   • Adjust: Model settings (reduce max tokens)

4. Installation Issues
   • Problem: Missing dependencies error
   • Solution: Run 'pip install -r requirements.txt'
   • Check: Python version (3.9+ required)
   • Try: Creating virtual environment

5. Memory Issues
   • Problem: Application crashes with memory error
   • Solution: Close other applications
   • Use: Smaller model (TinyLlama-1.1B)
   • Check: System has 8GB+ RAM

🛠️ SYSTEM REQUIREMENTS

Minimum Requirements:
• Windows 10/11
• Python 3.9+
• 4GB RAM (8GB recommended)
• 2GB free disk space

Recommended Requirements:
• 16GB RAM for larger models
• SSD storage for better performance
• Dedicated GPU (optional, for faster inference)

📝 GETTING HELP

• Check the README.md file
• Visit the GitHub repository for updates
• Report bugs through the issue tracker
• Join the community forum for support

💡 TIPS FOR BETTER PERFORMANCE

• Use document mode for PDF/Doc Q&A
• Clear chat history periodically
• Keep model files in the models/ folder
• Update to latest version regularly
• Close unused documents in the document list
        """
        
        text_widget.insert(tk.END, troubleshooting_text)
        text_widget.configure(state=tk.DISABLED)
        
        # Close button
        ttk.Button(main_frame, text="Close", command=self.window.destroy).pack(pady=(10, 0))


class AboutDialog:
    """About dialog for OANA"""
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("About OANA")
        self.window.geometry("450x350")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.setup_ui()
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title with icon
        ttk.Label(main_frame, text="🧠 OANA", font=("Arial", 18, "bold")).pack(pady=(0, 5))
        ttk.Label(main_frame, text="Offline AI and Note Assistant", font=("Arial", 12)).pack(pady=(0, 10))
        
        # Version
        ttk.Label(main_frame, text="Version 2.0.0", font=("Arial", 10)).pack(pady=(0, 20))
        
        # Description
        desc_text = """
OANA is a powerful offline AI assistant designed for 
document analysis, note-taking, and intelligent conversation.

🌟 Key Features:
• Complete offline operation for privacy
• Advanced document processing (PDF, Word, Text)
• Intelligent Q&A from your documents
• AI-powered summarization and note-taking
• Multiple themes and customization options
• Chat history management and export
• Professional desktop interface

🔒 Your data stays private - no internet required!

Built with Python, Tkinter, and modern AI technologies.
        """
        
        desc_label = ttk.Label(main_frame, text=desc_text, justify=tk.CENTER, font=("Arial", 9))
        desc_label.pack(pady=(0, 20))
        
        # Links frame
        links_frame = ttk.Frame(main_frame)
        links_frame.pack(pady=10)
        
        ttk.Button(links_frame, text="🌐 Website", 
                  command=lambda: webbrowser.open("https://github.com/user/oana")).pack(side=tk.LEFT, padx=5)
        ttk.Button(links_frame, text="📚 Documentation", 
                  command=lambda: webbrowser.open("https://github.com/user/oana/wiki")).pack(side=tk.LEFT, padx=5)
        
        # Close button
        ttk.Button(main_frame, text="Close", command=self.window.destroy).pack(pady=20)


def main():
    """Main function to run the application"""
    try:
        root = tk.Tk()
        app = OANA(root)
        
        # Set window icon (if available)
        try:
            root.iconbitmap("icon.ico")
        except:
            pass  # Icon file not found, ignore
            
        # Center window
        root.update_idletasks()
        x = (root.winfo_screenwidth() // 2) - (1400 // 2)
        y = (root.winfo_screenheight() // 2) - (900 // 2)
        root.geometry(f"1400x900+{x}+{y}")
        
        root.mainloop()
        
    except Exception as e:
        print(f"Application error: {e}")
        messagebox.showerror("Error", f"Failed to start OANA: {str(e)}")


if __name__ == "__main__":
    main()
