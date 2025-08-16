# OANA - Offline AI Note Assistant

OANA is a privacy-first, offline-capable AI assistant that allows students and researchers to interact with their notes without requiring internet connectivity.

## Key Features

- **Note Upload**: Support for PDF, DOCX, TXT, and Markdown files
- **Chat Interface**: Natural language Q&A with your uploaded notes
- **Summarization**: Generate summaries of your notes
- **Semantic Search**: Search your notes using natural language
- **Offline LLMs**: Runs completely offline using lightweight LLMs
- **Local Data Storage**: All data stays on your device
- **Cross-platform**: Works on Windows, macOS, and Linux

## Project Structure

```
oana/
├── frontend/        # React-based Tauri frontend
├── backend/         # Python FastAPI backend
└── data/            # Local data storage
```

## System Requirements

- **RAM**: 4GB+
- **Disk Space**: 500MB–2GB (depends on LLM model)
- **OS**: Windows, Linux, macOS

## Getting Started

### Quick Start (Windows)

1. Run `setup_complete.bat` to install all dependencies including Rust
2. Run `download_model.bat` to download the LLM model file
3. Run `start_oana.bat` to launch the application

### Manual Setup

#### Backend Setup

```bash
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/macOS
# source venv/bin/activate
pip install -r requirements.txt
```

#### Frontend Setup

```bash
# Install Rust (required for Tauri)
# Windows: Visit https://www.rust-lang.org/tools/install
# Linux/macOS: curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Install frontend dependencies
cd frontend
npm install

# Install Tauri CLI globally
npm install -g @tauri-apps/cli
```

#### LLM Model

Download a GGUF model file and place it in the `data/models` directory:
- Recommended: [phi-2.Q4_K_M.gguf](https://huggingface.co/TheBloke/Phi-2-GGUF/resolve/main/phi-2.Q4_K_M.gguf) (1.6GB)
- Alternative: [mistral-7b-v0.1.Q4_K_M.gguf](https://huggingface.co/TheBloke/Mistral-7B-v0.1-GGUF/resolve/main/mistral-7b-v0.1.Q4_K_M.gguf) (3.8GB)

### Running the Application

```bash
# Start the backend server
cd backend
# Windows
venv\Scripts\activate
# Linux/macOS
# source venv/bin/activate
python app.py

# In a new terminal, start the frontend
cd frontend
npm run tauri dev
```

### Helper Scripts

- `setup_complete.bat` - Sets up all dependencies (Windows)
- `download_model.bat` - Downloads the LLM model file (Windows)
- `start_oana.bat` - Starts both the backend and frontend (Windows)
- `start_oana.ps1` - PowerShell version of the startup script (Windows)

## Troubleshooting

If you encounter any issues:

- **Missing Rust**: Download and install Rust from https://www.rust-lang.org/tools/install
- **Missing Tauri CLI**: Run `npm install -g @tauri-apps/cli`
- **Python Package Issues**: Run `pip install -r requirements.txt` in the backend folder
- **Model Not Found**: Make sure `phi-2.Q4_K_M.gguf` is in the `data/models` directory
- **Backend Not Starting**: Check Python version (3.8+ required) and verify all dependencies are installed
- **Frontend Not Starting**: Ensure Rust and Tauri CLI are properly installed
- **Connection Error**: Make sure backend server is running on port 8000
- **Dependency Conflicts**:
  - If you see `ImportError: cannot import name 'cached_download' from 'huggingface_hub'`, run:
    ```
    pip install huggingface_hub==0.16.4 transformers==4.30.2 sentence-transformers==2.2.2
    ```
- **Model Compatibility Issues**: 
  - If you see `unknown model architecture: 'phi2'`, try using a different LLM model compatible with llama-cpp-python:
    - Update `config.py` to use a different model file, such as `mistral-7b-v0.1.Q4_K_M.gguf`
    - Download the recommended model file using `download_model.bat` or manually place it in the `data/models` directory

## Detailed Project Structure

```
oana/
├── frontend/                # React-based Tauri frontend
│   ├── src/                 # React source code
│   │   ├── pages/           # React pages (Dashboard, Chat, Upload, Settings)
│   │   ├── components/      # Reusable UI components
│   │   └── api/             # Frontend API integration
│   └── src-tauri/           # Tauri configuration and native code
├── backend/                 # Python FastAPI backend
│   ├── app.py               # Main FastAPI application
│   ├── config.py            # Backend configuration
│   └── modules/             # Backend modules
│       ├── parser.py        # Document parsing (PDF, DOCX, TXT, MD)
│       ├── embeddings.py    # Text embedding generation
│       ├── vector_store.py  # Vector database (FAISS)
│       ├── llm.py           # LLM interface (llama-cpp-python)
│       └── rag.py           # Retrieval-Augmented Generation
└── data/                    # Local data storage
    ├── documents/           # Uploaded document storage
    ├── embeddings/          # Vector embeddings storage
    └── models/              # LLM model files
```

## How It Works

OANA is designed as a modular, privacy-first AI note assistant that works completely offline:

1. **Document Processing**: Upload your PDF, DOCX, TXT, or Markdown documents
2. **Text Extraction**: Documents are parsed and text is extracted
3. **Embedding Generation**: Text chunks are converted to vector embeddings
4. **Vector Storage**: Embeddings are stored in a local FAISS database
5. **Query Processing**: User questions are processed through a RAG pipeline
6. **LLM Response**: A lightweight local LLM generates responses using retrieved context
7. **User Interface**: Clean, intuitive Tauri+React interface for interaction

The application uses a FastAPI backend for document processing and AI functionality, while the frontend is built with React and Tauri for a native-like experience across platforms. All data remains on your local machine, ensuring complete privacy.

## License

MIT
