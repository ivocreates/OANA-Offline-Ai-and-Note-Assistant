@echo off
echo OANA - Offline AI Note Assistant
echo ==============================
echo.
echo Starting OANA...
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found! Please install Python 3.8+ and try again.
    pause
    exit /b
)

:: Check if backend dependencies are installed
if not exist "backend\venv\Lib\site-packages\fastapi" (
    echo Installing backend dependencies...
    cd backend
    pip install -r requirements.txt
    cd ..
)

:: Check if model file exists
if not exist "data\models\phi-2.Q4_K_M.gguf" (
    echo.
    echo GGUF model file not found!
    echo Please download the phi-2.Q4_K_M.gguf file from:
    echo https://huggingface.co/TheBloke/Phi-2-GGUF/tree/main
    echo And place it in the data/models folder
    echo.
    pause
    exit /b
)

:: Check if frontend dependencies are installed
if not exist "frontend\node_modules" (
    echo Installing frontend dependencies...
    cd frontend
    call npm install
    cd ..
)

:: Check if Rust is installed
rustc --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Rust is not installed. Please run setup_complete.bat first.
    pause
    exit /b
)

:: Check if Tauri CLI is installed
call npm list -g @tauri-apps/cli >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing Tauri CLI...
    call npm install -g @tauri-apps/cli
)

:: Start the backend server
echo Starting backend server...
start cmd /k "call start_backend.bat"

:: Give the backend a moment to start
echo Waiting for backend to initialize...
timeout /t 5 /nobreak > nul

:: Start the Tauri frontend
echo Starting frontend application...
start cmd /k "call start_frontend.bat"

echo.
echo OANA is starting up! The application window should appear shortly.
echo If the application doesn't start, check the terminal windows for any error messages.
echo.
echo To stop the application, close the application window and the terminal windows.
echo.

pause
