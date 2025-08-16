@echo off
echo OANA - Offline AI Note Assistant Setup
echo ======================================
echo.

echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found! Please install Python 3.8+ and try again.
    pause
    exit /b
)

echo.
echo Setting up Python virtual environment...
cd backend
python -m venv venv
call venv\Scripts\activate

echo.
echo Installing Python dependencies (this may take a while)...
pip install -r requirements.txt

echo.
echo Creating necessary directories...
cd ..
if not exist "data" mkdir data
if not exist "data\models" mkdir data\models
if not exist "data\documents" mkdir data\documents
if not exist "data\embeddings" mkdir data\embeddings

echo.
echo Downloading default LLM model (this may take a while)...
echo You'll need to manually download a GGUF format model and place it in the data/models folder.
echo Recommended models:
echo - phi-2.Q4_K_M.gguf (1.6GB) - Best balance of size and quality
echo - mistral-7b-v0.1.Q4_K_M.gguf (3.8GB) - Better quality, larger size
echo.
echo Download from: https://huggingface.co/TheBloke/Phi-2-GGUF/tree/main
echo or: https://huggingface.co/TheBloke/Mistral-7B-v0.1-GGUF/tree/main

echo.
echo Setting up Node.js dependencies...
cd frontend
call npm install

echo.
echo Setup complete!
echo.
echo To start the application:
echo 1. Start backend: cd backend ^& venv\Scripts\activate ^& python app.py
echo 2. Start frontend: cd frontend ^& npm run tauri dev
echo.
echo Enjoy using OANA!

pause
