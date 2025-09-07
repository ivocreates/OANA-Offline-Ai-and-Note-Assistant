@echo off
title Offline AI ChatBot - Quick Installer

echo ========================================
echo  Offline AI ChatBot - Quick Installer  
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.9+ from: https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo Found Python:
python --version
echo.

echo Installing required packages...
echo This may take a few minutes...
echo.

REM Install basic requirements
echo [1/4] Installing PDF processing...
pip install PyMuPDF>=1.23.0

echo [2/4] Installing document processing...
pip install python-docx>=0.8.11 docx2txt>=0.8

echo [3/4] Installing AI backend...
pip install llama-cpp-python>=0.2.0

echo [4/4] Installing utilities...
pip install nltk>=3.8.1 requests>=2.31.0 numpy>=1.24.0

echo.
echo ========================================
echo Installation completed!
echo ========================================
echo.

echo Next steps:
echo 1. Download an AI model using: python download_models.py
echo 2. Start the application using: python app.py
echo    or double-click start.bat
echo.

echo Recommended model for beginners:
echo - TinyLlama-1.1B (637 MB) - Good for basic chat
echo.

echo Would you like to download a model now? (y/n)
set /p download_choice=

if /i "%download_choice%"=="y" (
    echo.
    echo Starting model downloader...
    python download_models.py
)

echo.
echo Setup complete! You can now run: python app.py
echo.
pause
