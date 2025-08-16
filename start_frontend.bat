@echo off
echo ===================================
echo Starting OANA Frontend
echo ===================================

cd frontend
echo Checking for Node modules...

if not exist node_modules (
    echo Installing Node dependencies...
    npm install
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to install Node dependencies. Make sure Node.js is installed.
        pause
        exit /b 1
    )
)

echo Checking for Tauri CLI...
call npm list -g @tauri-apps/cli >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Installing Tauri CLI...
    npm install -g @tauri-apps/cli
)

echo Starting frontend with Tauri...
npm run tauri dev

pause
