@echo off
echo OANA - Offline AI Note Assistant Setup
echo ======================================
echo.

echo Checking for Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found! Please install Python 3.8+ and try again.
    pause
    exit /b
)

echo.
echo Setting up Python virtual environment...
cd backend
if not exist venv (
    python -m venv venv
)
call venv\Scripts\activate

echo.
echo Installing Python dependencies...
pip install -r requirements.txt

echo.
echo Creating necessary directories...
cd ..
if not exist "data" mkdir data
if not exist "data\models" mkdir data\models
if not exist "data\documents" mkdir data\documents
if not exist "data\embeddings" mkdir data\embeddings

echo.
echo Checking if Rust is installed...
rustc --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Rust is not installed. Installing Rust...
    echo Please wait while the Rust installer is downloaded...
    powershell -Command "Invoke-WebRequest -Uri https://static.rust-lang.org/rustup/dist/i686-pc-windows-gnu/rustup-init.exe -OutFile rustup-init.exe"
    rustup-init.exe -y
    set PATH=%PATH%;%USERPROFILE%\.cargo\bin
    echo Rust installation completed!
) else (
    echo Rust is already installed.
)

echo.
echo Setting up Node.js dependencies...
cd frontend
call npm install
echo Installing Tauri CLI...
call npm install -g @tauri-apps/cli

echo.
echo Setup complete!
echo.
echo IMPORTANT: You need to download a GGUF model file:
echo 1. Visit https://huggingface.co/TheBloke/Phi-2-GGUF/tree/main
echo 2. Download the phi-2.Q4_K_M.gguf file
echo 3. Place it in the data/models folder
echo.
echo To start the application:
echo 1. Open a new command prompt
echo 2. Run: start_oana.bat
echo.
echo Enjoy using OANA!

pause
