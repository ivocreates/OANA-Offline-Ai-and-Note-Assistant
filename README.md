# OANA - Offline AI and Note Assistant

**OANA** (Offline AI and Note Assistant) is a lightweight, privacy-focused desktop application that brings AI chat capabilities and document analysis to your local machine - no internet connection required after setup!

## Features

🤖 **AI Chat Interface**
- ChatGPT-like conversational AI
- Multiple AI backend support (llama-cpp, Ollama, Transformers)
- Completely offline operation
- Customizable AI settings

📄 **Document Processing**
- Upload and process PDF files
- Support for Word documents (.docx, .doc)
- Text file support
- Document summarization
- Question & Answer from documents

💡 **Smart Features**
- Document-based Q&A
- Automatic summarization
- Note generation from documents
- Chat history management
- Export chat conversations

🛠️ **Easy Setup**
- One-click installer
- Minimal dependencies
- Built-in troubleshooting
- Model downloader included
- Works on Windows, macOS, Linux

## Quick Start

### Option 1: Automated Setup (Recommended)

1. **Download and extract** the project files
2. **Run the setup script**:
   ```bash
   python setup.py
   ```
3. **Download an AI model** (recommended):
   - TinyLlama-1.1B (637 MB) - for basic use
   - Llama-2-7B (4.1 GB) - for better quality
4. **Start the application**:
   ```bash
   python app.py
   ```

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
