# OANA - Offline AI and Note Assistant

<div align="center">

![OANA Logo](https://img.shields.io/badge/OANA-Offline%20AI%20Assistant-blue?style=for-the-badge&logo=robot)

**A powerful, privacy-focused desktop AI assistant that works completely offline**

[![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)](https://github.com/ivocreates/OANA-Offline-Ai-and-Note-Assistant)

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Development](#-development) • [Troubleshooting](#-troubleshooting)

</div>

## 🌟 Features

### 🤖 AI Chat Interface
- **ChatGPT-like conversations** with local AI models
- **Multiple AI backends**: llama-cpp-python, Ollama, Transformers
- **Completely offline** - your data never leaves your computer  
- **Customizable settings**: temperature, tokens, system prompts
- **Chat history management** with SQLite database
- **Session management** - save, load, and organize conversations

### 📄 Document Processing
- **PDF support** - upload and analyze PDF documents
- **Word documents** - process .docx and .doc files
- **Text files** - plain text document support
- **Smart summarization** - AI-powered document summaries
- **Document Q&A** - ask questions about uploaded documents
- **Bulk processing** - handle multiple documents simultaneously

### 💡 Smart Features
- **Persistent storage** - SQLite database for chat history and documents
- **Export options** - save chats as PDF, HTML, Markdown, or text
- **Theme support** - light and dark themes with customization
- **Model management** - built-in model downloader and switcher
- **Advanced search** - find information across documents and chats
- **Note-taking** - AI-assisted note generation

### 🛡️ Privacy & Security  
- **100% offline operation** after initial setup
- **Local data storage** - everything stays on your computer
- **No telemetry or tracking** - your privacy is protected
- **Open source** - inspect and modify the code

## 🚀 Installation

### Quick Install (Recommended)

1. **Clone or download** this repository:
   ```bash
   git clone https://github.com/ivocreates/OANA-Offline-Ai-and-Note-Assistant.git
   cd OANA-Offline-Ai-and-Note-Assistant
   ```

2. **Run the installer**:
   ```bash
   # On Windows
   install.bat
   
   # On macOS/Linux
   python setup.py
   ```

3. **Start the application**:
   ```bash
   python app.py
   ```

### Manual Installation

1. **Install Python 3.8+** from [python.org](https://python.org)

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Create directories**:
   ```bash
   mkdir models data logs
   ```

4. **Download an AI model** (required for chat functionality):
   - Run the app and use "AI Models → Download Models" menu
   - Or manually download GGUF models to the `models/` folder

### Desktop Application

Build a standalone executable:

```bash
# Install build dependencies
pip install pyinstaller

# Build the application
python build_installer.py

# Find the executable in dist/OANA/ folder
```

## 📖 Usage

### First Run

1. **Start OANA**: Run `python app.py`
2. **Download models**: Go to "AI Models → Download Models" 
3. **Configure settings**: Use "Settings" menu to customize
4. **Start chatting**: Type in the chat input and press Enter

### Chat Mode

- **Normal Chat**: General conversations with the AI
- **Document Mode**: Upload documents and ask questions about them
- **Note Taking**: AI-assisted note generation and organization

### Document Processing

1. **Upload documents**: Click "Upload Document" or drag & drop files
2. **View documents**: Use the document panel to browse uploaded files
3. **Ask questions**: Reference documents in your chat queries
4. **Summarize**: Use "Summarize Selected" for quick document summaries

### Advanced Features

- **Session Management**: Save and load different conversation contexts
- **Export Options**: Export chats in various formats (PDF, HTML, etc.)
- **Theme Customization**: Switch between light/dark themes
- **Model Switching**: Change AI models without restarting

## 🛠️ Development

### Development Setup

```bash
# Clone repository
git clone https://github.com/ivocreates/OANA-Offline-Ai-and-Note-Assistant.git
cd OANA-Offline-Ai-and-Note-Assistant

# Setup development environment  
python setup.py --dev

# Install development dependencies
pip install pytest black flake8 mypy

# Run the application
python app.py
```

### Project Structure

```
OANA-Offline-Ai-and-Note-Assistant/
├── app.py                 # Main application
├── setup.py              # Setup and installation script
├── build_installer.py    # Desktop application builder
├── requirements.txt      # Python dependencies
├── utils/                # Core utilities
│   ├── ai_engine.py      # AI backend management
│   ├── database.py       # SQLite database handler
│   ├── pdf_parser.py     # PDF processing
│   ├── docx_parser.py    # Word document processing
│   └── summarizer.py     # Text summarization
├── models/               # AI model files (*.gguf)
├── data/                 # User data and documents
│   ├── chat_history/     # Legacy JSON chat files  
│   └── documents/        # Uploaded documents
└── logs/                 # Application logs
```

### Contributing

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Testing

```bash
# Run tests
pytest

# Code formatting
black .

# Linting  
flake8

# Type checking
mypy app.py
```

## 🔧 Troubleshooting

### Common Issues

**Application won't start**
- Ensure Python 3.8+ is installed
- Check that all dependencies are installed: `pip install -r requirements.txt`
- Try running with: `python -v app.py` for verbose output

**AI model not loading**
- Download models through the app menu: "AI Models → Download Models"
- Ensure models are in the `models/` folder with `.gguf` extension
- Check available disk space (models can be 1-7GB)
- Try a smaller model like TinyLlama first

**PDF/Document processing errors**
- Install additional dependencies: `pip install PyMuPDF python-docx`
- Check document file permissions
- Try with a smaller document first

**Performance issues**
- Use smaller AI models (TinyLlama vs Llama-2)
- Close unused documents in the document panel
- Clear chat history periodically
- Check available system RAM (4GB+ recommended)

### Getting Help

- **Issues**: [GitHub Issues](https://github.com/ivocreates/OANA-Offline-Ai-and-Note-Assistant/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ivocreates/OANA-Offline-Ai-and-Note-Assistant/discussions)
- **Documentation**: Check the built-in help menu in the application

### System Requirements

**Minimum:**
- Python 3.8+
- 4GB RAM
- 2GB free disk space
- Windows 10, macOS 10.14, or Linux

**Recommended:**
- Python 3.10+
- 8GB+ RAM
- 10GB+ free disk space (for larger models)
- SSD for better performance

## 📋 Supported Models

OANA supports GGUF format models optimized for CPU inference:

**Small Models (< 1GB)**
- TinyLlama-1.1B-Chat - Fast, basic conversations
- Phi-2-2.7B - Good balance of speed and quality

**Medium Models (1-4GB)**  
- Llama-2-7B-Chat - High quality conversations
- Code-Llama-7B - Programming assistance
- Mistral-7B - Excellent general purpose

**Large Models (4GB+)**
- Llama-2-13B-Chat - Best quality (requires 16GB+ RAM)
- WizardCoder-15B - Advanced programming help

Download models through the application or from [Hugging Face](https://huggingface.co/models?library=gguf).

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [llama-cpp-python](https://github.com/abetlen/llama-cpp-python) - Python bindings for llama.cpp
- [PyMuPDF](https://github.com/pymupdf/PyMuPDF) - PDF processing
- [python-docx](https://github.com/python-openxml/python-docx) - Word document processing  
- [Tkinter](https://docs.python.org/3/library/tkinter.html) - GUI framework

---

<div align="center">

**[⬆ Back to Top](#oana---offline-ai-and-note-assistant)**

Made with ❤️ for privacy-conscious AI users

</div>

### Option 2: Manual Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Create directories**:
   ```
   models/     # Place AI model files here
   data/       # Application data
   logs/       # Log files
   ```

3. **Download a model** (choose one):
   - Visit [Hugging Face GGUF models](https://huggingface.co/models?library=gguf)
   - Download a `.gguf` file to the `models/` directory
   - Recommended: `TinyLlama-1.1B-Chat-v1.0.Q4_K_M.gguf`

4. **Run the application**:
   ```bash
   python app.py
   ```

## System Requirements

**Minimum Requirements:**
- Windows 10/11, macOS 10.14+, or Linux
- Python 3.9 or higher
- 4GB RAM
- 2GB free disk space

**Recommended Requirements:**
- 8GB+ RAM (for larger models)
- SSD storage
- 16GB+ RAM for Llama-2-7B models

## How to Use

### 1. Basic Chat
- Type messages in the input box
- Press Enter or click "Send"
- Select "general" mode for normal conversations

### 2. Document Upload
- Click "Upload PDF/Doc" or use File menu
- Supported formats: PDF, DOCX, DOC, TXT
- View preview in the document panel

### 3. Document Q&A
- Upload documents first
- Switch to "document_qa" mode
- Ask questions about the uploaded content
- AI will answer based on document content

### 4. Summarization
- Upload a document
- Select it in the document list
- Click "Summarize" button
- Or switch to "summarize" mode and ask for summaries

## AI Backend Options

### 1. llama-cpp-python (Recommended)
```bash
pip install llama-cpp-python
```
- Best performance
- Supports GGUF model files
- Local CPU/GPU inference
- Download models from Hugging Face

### 2. Ollama (Alternative)
```bash
# Install Ollama separately, then:
pip install ollama
ollama pull llama2
```
- Easy model management
- Good performance
- Requires Ollama installation

### 3. Transformers (Fallback)
```bash
pip install torch transformers
```
- Uses Hugging Face models
- More memory intensive
- Good for experimentation

## Recommended Models

### Lightweight (< 1GB)
- **TinyLlama-1.1B-Chat**: Fast, basic conversations
- **Phi-2-2.7B**: Good balance of speed and quality

### Standard (2-5GB)
- **Llama-2-7B-Chat**: High quality conversations
- **CodeLlama-7B**: Good for code-related tasks
- **Mistral-7B**: Excellent general performance

### Large (> 8GB)
- **Llama-2-13B-Chat**: Best quality (requires 16GB+ RAM)
- **CodeLlama-13B**: Advanced code assistance

## Troubleshooting

### AI Engine Not Ready
- **Problem**: "AI engine is not ready" message
- **Solution**: Download a compatible `.gguf` model file
- **Check**: Models folder should contain at least one `.gguf` file

### Document Upload Fails
- **Problem**: Cannot process PDF or Word documents
- **Solution**: Ensure file is not corrupted or password-protected
- **Try**: Converting file to a different format

### Slow Performance
- **Problem**: AI takes too long to respond
- **Solution**: Use smaller models (TinyLlama recommended)
- **Check**: Available RAM (8GB+ recommended for larger models)

### Memory Issues
- **Problem**: Application crashes with memory error
- **Solution**: Use smaller model, close other applications
- **Requirement**: Check system has 8GB+ RAM

### Installation Issues
```bash
# Create virtual environment (recommended)
python -m venv chatbot_env
chatbot_env\Scripts\activate  # Windows
# or
source chatbot_env/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

## File Structure

```
offline-chatbot/
│
├── app.py              # Main application
├── setup.py            # Setup script
├── requirements.txt    # Python dependencies
├── config.json         # Configuration settings
├── README.md          # This file
│
├── models/            # AI model files (.gguf)
│   └── (place model files here)
│
├── data/              # Application data
│   ├── chat_history/
│   └── documents/
│
├── utils/             # Utility modules
│   ├── ai_engine.py   # AI backend management
│   ├── pdf_parser.py  # PDF text extraction
│   ├── docx_parser.py # Word document processing
│   └── summarizer.py  # Text summarization
│
└── logs/              # Application logs
```

## Configuration

Edit `config.json` to customize:

```json
{
  "ai_settings": {
    "temperature": 0.7,
    "max_tokens": 512,
    "system_prompt": "Your custom system prompt"
  },
  "ui_settings": {
    "window_width": 1200,
    "window_height": 800
  }
}
```

## Building Executable

To create a standalone executable:

```bash
# Install PyInstaller
pip install pyinstaller

# Create executable
pyinstaller --onefile --windowed --name "OfflineChatBot" app.py

# Find executable in dist/ folder
```

## Advanced Usage

### Custom Models
Place any GGUF format model in the `models/` directory. The application will automatically detect and load it.

### API Integration
The AI engine can be extended to support additional backends by modifying `utils/ai_engine.py`.

### Plugins
The application architecture supports plugins through the utils system.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source. Check the LICENSE file for details.

## Support

- **Documentation**: Check this README and built-in help
- **Troubleshooting**: Use the built-in troubleshooting guide (Help menu)
- **Issues**: Report bugs through the GitHub issue tracker
- **Community**: Join discussions in the project forums

## Privacy & Security

- **Completely Offline**: No data sent to external servers
- **Local Processing**: All AI inference happens on your device
- **Privacy First**: Your documents and conversations stay private
- **No Telemetry**: No usage tracking or data collection

---

**Enjoy your private, offline AI assistant!** 🤖✨
