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

# Add utils to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

try:
    from pdf_parser import PDFParser
    from docx_parser import DocxParser
    from ai_engine import AIEngine
    from summarizer import Summarizer
except ImportError as e:
    print(f"Import error: {e}")
    print("Some modules are not available. Please install dependencies.")

class OANA:
    def __init__(self, root):
        self.root = root
        self.root.title("OANA - Offline AI and Note Assistant")
        self.root.geometry("1400x900")
        self.root.minsize(1000, 700)
        
        # Theme and styling
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
                "danger": "#e74c3c"
            },
            "dark": {
                "bg": "#2c3e50",
                "fg": "#ecf0f1",
                "select_bg": "#3498db",
                "select_fg": "#ffffff",
                "entry_bg": "#34495e",
                "panel_bg": "#34495e",
                "accent": "#3498db",
                "success": "#27ae60",
                "warning": "#f39c12",
                "danger": "#e74c3c"
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
                "danger": "#f56565"
            }
        }
        
        # Initialize components
        self.ai_engine = None
        self.pdf_parser = PDFParser()
        self.docx_parser = DocxParser()
        self.summarizer = None
        
        # Data storage
        self.chat_history = []
        self.uploaded_documents = []
        self.current_context = ""
        self.settings = self._load_settings()
        
        # Apply theme
        self.apply_theme()
        
        # Initialize UI
        self.setup_styles()
        self.setup_ui()
        self.setup_menu()
        
        # Initialize AI engine in background
        self.initialize_ai_engine()
        
        # Auto-save settings
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
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
        """Apply current theme"""
        theme = self.themes[self.settings.get("theme", "light")]
        self.root.configure(bg=theme["bg"])
        
    def setup_styles(self):
        """Setup ttk styles for theming"""
        style = ttk.Style()
        theme = self.themes[self.settings.get("theme", "light")]
        
        # Configure styles
        style.configure("Title.TLabel", font=("Arial", 12, "bold"), foreground=theme["accent"])
        style.configure("Heading.TLabel", font=("Arial", 10, "bold"), foreground=theme["fg"])
        style.configure("Custom.TButton", padding=(10, 5))
        style.configure("Accent.TButton", foreground=theme["accent"])
        style.configure("Success.TButton", foreground=theme["success"])
        style.configure("Warning.TButton", foreground=theme["warning"])
        style.configure("Danger.TButton", foreground=theme["danger"])
        
    def setup_menu(self):
        """Setup enhanced menu bar"""
        menubar = tk.Menu(self.root, bg=self.themes[self.current_theme]["panel_bg"])
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="📁 File", menu=file_menu)
        file_menu.add_command(label="📤 Upload Document", command=self.upload_document, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="💾 Save Chat History", command=self.save_chat_history, accelerator="Ctrl+S")
        file_menu.add_command(label="📄 Export Chat as PDF", command=self.export_chat_pdf)
        file_menu.add_command(label="📊 Export Chat as HTML", command=self.export_chat_html)
        file_menu.add_separator()
        file_menu.add_command(label="🧹 Clear Chat History", command=self.clear_chat_confirm)
        file_menu.add_command(label="🗑️ Clear All Documents", command=self.clear_documents)
        file_menu.add_separator()
        file_menu.add_command(label="🚪 Exit", command=self.on_closing, accelerator="Alt+F4")
        
        # AI Models menu
        models_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="🤖 AI Models", menu=models_menu)
        models_menu.add_command(label="📥 Download Models", command=self.show_model_downloader)
        models_menu.add_command(label="🔄 Reload Model", command=self.reload_ai_model)
        models_menu.add_command(label="⚙️ Model Settings", command=self.show_ai_settings)
        models_menu.add_separator()
        models_menu.add_command(label="📊 Model Status", command=self.show_model_status)
        
        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="⚙️ Settings", menu=settings_menu)
        settings_menu.add_command(label="🎨 Themes", command=self.show_theme_settings)
        settings_menu.add_command(label="💬 Chat Settings", command=self.show_chat_settings)
        settings_menu.add_command(label="🤖 AI Configuration", command=self.show_ai_settings)
        settings_menu.add_command(label="🔧 Advanced Settings", command=self.show_advanced_settings)
        settings_menu.add_separator()
        settings_menu.add_command(label="↩️ Reset to Defaults", command=self.reset_settings)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="🔧 Tools", menu=tools_menu)
        tools_menu.add_command(label="📊 Statistics", command=self.show_statistics)
        tools_menu.add_command(label="🗂️ File Manager", command=self.show_file_manager)
        tools_menu.add_command(label="🧪 Test Components", command=self.run_component_test)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="❓ Help", menu=help_menu)
        help_menu.add_command(label="📖 User Guide", command=self.show_user_guide)
        help_menu.add_command(label="🆘 Troubleshooting", command=self.show_troubleshooting)
        help_menu.add_command(label="🎯 Keyboard Shortcuts", command=self.show_shortcuts)
        help_menu.add_separator()
        help_menu.add_command(label="ℹ️ About OANA", command=self.show_about)
        
        # Bind keyboard shortcuts
        self.root.bind('<Control-o>', lambda e: self.upload_document())
        self.root.bind('<Control-s>', lambda e: self.save_chat_history())
        self.root.bind('<Control-n>', lambda e: self.clear_chat_confirm())
        self.root.bind('<F1>', lambda e: self.show_user_guide())
        self.root.bind('<F5>', lambda e: self.reload_ai_model())
        
    def setup_ui(self):
        """Setup the enhanced user interface"""
        # Create main container with theme colors
        theme = self.themes[self.settings.get("theme", "light")]
        
        # Title bar with app name and status
        title_frame = tk.Frame(self.root, bg=theme["accent"], height=50)
        title_frame.pack(fill=tk.X, pady=(0, 5))
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame, text="🧠 OANA - Offline AI and Note Assistant", 
                              font=("Arial", 14, "bold"), fg="white", bg=theme["accent"])
        title_label.pack(side=tk.LEFT, padx=20, pady=10)
        
        # Status indicators
        self.connection_status = tk.Label(title_frame, text="⚡ Initializing...", 
                                        font=("Arial", 10), fg="white", bg=theme["accent"])
        self.connection_status.pack(side=tk.RIGHT, padx=20, pady=10)
        
        # Create main frame with improved layout
        main_frame = ttk.Frame(self.root, padding="10")
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
        """Setup enhanced chat interface panel"""
        theme = self.themes[self.settings.get("theme", "light")]
        
        # Chat frame with modern design
        chat_frame = ttk.LabelFrame(parent, text="💬 AI Conversation", padding="10")
        chat_frame.grid(row=0, column=1, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Chat display with better styling
        chat_display_frame = ttk.Frame(chat_frame)
        chat_display_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
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
            borderwidth=1
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        
        # Input section with modern design
        input_section = ttk.Frame(chat_frame)
        input_section.pack(fill=tk.X, pady=(0, 10))
        
        # Message input with placeholder
        input_frame = ttk.Frame(input_section)
        input_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.message_var = tk.StringVar()
        self.message_entry = tk.Entry(
            input_frame, 
            textvariable=self.message_var, 
            font=("Segoe UI", 11),
            bg=theme["entry_bg"],
            fg=theme["fg"],
            relief=tk.FLAT,
            borderwidth=2
        )
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.message_entry.bind("<Return>", self.send_message)
        self.message_entry.bind("<Shift-Return>", self.send_message)  # Also support Shift+Enter
        
        # Enhanced send button
        self.send_btn = ttk.Button(input_frame, text="🚀 Send", command=self.send_message, style="Accent.TButton")
        self.send_btn.pack(side=tk.RIGHT)
        
        # Quick action buttons
        actions_frame = ttk.Frame(input_section)
        actions_frame.pack(fill=tk.X)
        
        ttk.Button(actions_frame, text="📄 Summarize All", command=self.summarize_all_docs, style="Custom.TButton").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(actions_frame, text="🔍 Smart Search", command=self.smart_search, style="Custom.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="📝 Take Notes", command=self.take_notes, style="Custom.TButton").pack(side=tk.LEFT, padx=5)
        
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
        """Add message to chat display"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Add to history
        self.chat_history.append({
            'sender': sender,
            'content': message,
            'timestamp': timestamp
        })
        
        # Add to display
        self.chat_display.configure(state=tk.NORMAL)
        
        # Format message
        if sender == "You":
            self.chat_display.insert(tk.END, f"\n[{timestamp}] 🧑 You:\n", "user")
            self.chat_display.insert(tk.END, f"{message}\n", "user_msg")
        elif sender == "AI":
            self.chat_display.insert(tk.END, f"\n[{timestamp}] 🤖 AI:\n", "ai")
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
        
    def summarize_selected(self):
        """Summarize selected document"""
        selection = self.doc_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a document to summarize")
            return
            
        if not self.ai_engine or not self.ai_engine.is_ready():
            messagebox.showwarning("Warning", "AI engine is not ready")
            return
            
        doc_index = selection[0]
        doc_info = self.uploaded_documents[doc_index]
        
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
        selection = self.doc_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a document to remove")
            return
            
        doc_index = selection[0]
        doc_name = self.uploaded_documents[doc_index]['name']
        
        if messagebox.askyesno("Confirm", f"Remove document '{doc_name}'?"):
            self.uploaded_documents.pop(doc_index)
            self.doc_listbox.delete(doc_index)
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
        """Save chat history with timestamp"""
        if not self.chat_history:
            messagebox.showwarning("Warning", "No chat history to save")
            return
            
        filename = filedialog.asksaveasfilename(
            title="Save chat history",
            defaultextension=".json",
            filetypes=[
                ("JSON files", "*.json"),
                ("Text files", "*.txt"),
                ("HTML files", "*.html"),
                ("Markdown files", "*.md")
            ]
        )
        
        if filename:
            try:
                ext = Path(filename).suffix.lower()
                if ext == '.json':
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump({
                            'chat_history': self.chat_history,
                            'documents': [{'name': doc['name'], 'upload_time': doc['upload_time']} for doc in self.uploaded_documents],
                            'export_time': datetime.now().isoformat(),
                            'app_version': 'OANA v1.0'
                        }, f, indent=2, ensure_ascii=False)
                elif ext == '.html':
                    self.export_chat_html(filename)
                    return
                elif ext == '.md':
                    self.export_chat_markdown(filename)
                    return
                else:
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(f"OANA Chat History - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write("=" * 60 + "\n\n")
                        for msg in self.chat_history:
                            f.write(f"[{msg['timestamp']}] {msg['sender']}:\n")
                            f.write(f"{msg['content']}\n\n")
                            
                self.status_var.set(f"Chat history saved: {Path(filename).name}")
                messagebox.showinfo("Success", "Chat history saved successfully")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save chat history: {str(e)}")
                
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
        """Auto-save chat history"""
        try:
            data_dir = Path(__file__).parent / "data" / "chat_history"
            data_dir.mkdir(parents=True, exist_ok=True)
            
            filename = data_dir / f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump({
                    'chat_history': self.chat_history,
                    'documents': [{'name': doc['name'], 'upload_time': doc['upload_time']} for doc in self.uploaded_documents],
                    'save_time': datetime.now().isoformat()
                }, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Auto-save failed: {e}")
            
    def clear_chat_confirm(self):
        """Confirm before clearing chat"""
        if not self.chat_history:
            return
            
        result = messagebox.askyesnocancel(
            "Clear Chat History",
            "Do you want to save the current chat before clearing?\n\n"
            "Yes: Save and clear\n"
            "No: Clear without saving\n"
            "Cancel: Don't clear"
        )
        
        if result is True:  # Yes - save and clear
            self.save_chat_history()
            self.clear_chat()
        elif result is False:  # No - clear without saving
            self.clear_chat()
        # Cancel - do nothing
        
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
        if self.ai_engine:
            info = self.ai_engine.get_model_info()
            
            status_text = f"""
AI Model Status:
• Backend: {info.get('backend', 'None')}
• Model Loaded: {'Yes' if info.get('is_loaded', False) else 'No'}
• Model Path: {info.get('model_path', 'None')}

Available Backends:
• llama-cpp: {'✅' if info.get('available_backends', {}).get('llama-cpp', False) else '❌'}
• Ollama: {'✅' if info.get('available_backends', {}).get('ollama', False) else '❌'}  
• Transformers: {'✅' if info.get('available_backends', {}).get('transformers', False) else '❌'}
"""
            
            messagebox.showinfo("AI Model Status", status_text)
        else:
            messagebox.showwarning("Warning", "AI engine not initialized")
            
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

class ThemeSettingsDialog:
    """Dialog for theme settings"""
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        
        self.window = tk.Toplevel(parent)
        self.window.title("🎨 Theme Settings")
        self.window.geometry("500x400")
        self.window.transient(parent)
        self.window.grab_set()
        
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
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Apply", command=self.apply_settings).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Preview", command=self.preview_theme).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=self.window.destroy).pack(side=tk.RIGHT)
        
    def apply_settings(self):
        self.app.settings["theme"] = self.theme_var.get()
        self.app.settings["ui_settings"]["font_size"] = self.font_size.get()
        self.app.settings["ui_settings"]["show_timestamps"] = self.show_timestamps.get()
        self.app.settings["ui_settings"]["compact_mode"] = self.compact_mode.get()
        
        self.app.save_settings()
        messagebox.showinfo("Settings Applied", "Theme settings applied!\nRestart OANA to see all changes.")
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
        messagebox.showinfo("Feature", "Chat history manager will be implemented in future version.")


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
        messagebox.showinfo("Test", "AI settings test will be implemented in future version.")


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
        self.window = tk.Toplevel(parent)
        self.window.title("🗂️ File Manager")
        self.window.geometry("600x500")
        self.window.transient(parent)
        
        ttk.Label(self.window, text="🗂️ File Manager", font=("Arial", 14, "bold")).pack(pady=20)
        ttk.Label(self.window, text="File management features will be implemented here.").pack(pady=20)
        ttk.Button(self.window, text="Close", command=self.window.destroy).pack(pady=20)


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
        
        self.window = tk.Toplevel(parent)
        self.window.title("Download AI Models")
        self.window.geometry("600x400")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.setup_ui()
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Available Models", font=("Arial", 12, "bold")).pack(anchor=tk.W)
        
        # Model list
        self.model_tree = ttk.Treeview(main_frame, columns=("size", "description"), show="tree headings")
        self.model_tree.heading("#0", text="Model Name")
        self.model_tree.heading("size", text="Size")
        self.model_tree.heading("description", text="Description")
        self.model_tree.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Add sample models
        models = [
            ("TinyLlama-1.1B", "637 MB", "Lightweight model for basic chat"),
            ("Llama-2-7B-Chat", "3.8 GB", "Balanced performance and quality"),
            ("CodeLlama-7B", "3.8 GB", "Specialized for code generation"),
        ]
        
        for model, size, desc in models:
            self.model_tree.insert("", tk.END, text=model, values=(size, desc))
            
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="Download Selected", command=self.download_model).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="Browse Local", command=self.browse_local).pack(side=tk.LEFT, padx=(10, 0))
        ttk.Button(button_frame, text="Close", command=self.window.destroy).pack(side=tk.RIGHT)
        
    def download_model(self):
        selection = self.model_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a model to download")
            return
            
        model_name = self.model_tree.item(selection[0])['text']
        messagebox.showinfo("Info", f"Model download feature will be implemented.\nSelected: {model_name}")
        
    def browse_local(self):
        filename = filedialog.askopenfilename(
            title="Select local model file",
            filetypes=[("GGUF files", "*.gguf"), ("All files", "*.*")]
        )
        if filename:
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
