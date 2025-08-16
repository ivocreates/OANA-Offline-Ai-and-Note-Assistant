Write-Host "OANA - Offline AI Note Assistant" -ForegroundColor Cyan
Write-Host "==============================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Starting OANA..." -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
try {
    python --version | Out-Null
}
catch {
    Write-Host "Python not found! Please install Python 3.8+ and try again." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit
}

# Check if backend dependencies are installed
if (-Not (Test-Path "backend\venv\Lib\site-packages\fastapi")) {
    Write-Host "Installing backend dependencies..." -ForegroundColor Yellow
    Push-Location backend
    pip install -r requirements.txt
    Pop-Location
}

# Check if model file exists
if (-Not (Test-Path "data\models\phi-2.Q4_K_M.gguf")) {
    Write-Host "GGUF model file not found!" -ForegroundColor Red
    Write-Host "Please download the phi-2.Q4_K_M.gguf file from:" -ForegroundColor Yellow
    Write-Host "https://huggingface.co/TheBloke/Phi-2-GGUF/tree/main" -ForegroundColor Yellow
    Write-Host "And place it in the data/models folder" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit
}

# Check if frontend dependencies are installed
if (-Not (Test-Path "frontend\node_modules")) {
    Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
    Push-Location frontend
    npm install
    Pop-Location
}

# Check if Rust is installed
try {
    rustc --version | Out-Null
}
catch {
    Write-Host "Rust is not installed. Please run setup_complete.bat first." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit
}

# Check if Tauri CLI is installed globally
try {
    npm list -g @tauri-apps/cli | Out-Null
}
catch {
    Write-Host "Installing Tauri CLI..." -ForegroundColor Yellow
    npm install -g @tauri-apps/cli
}

# Start the backend server
Write-Host "Starting backend server..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\backend'; .\venv\Scripts\activate; python app.py"

# Give the backend a moment to start
Write-Host "Waiting for backend to initialize..." -ForegroundColor Green
Start-Sleep -Seconds 5

# Start the Tauri frontend
Write-Host "Starting frontend application..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\frontend'; npm run tauri dev"

Write-Host ""
Write-Host "OANA is starting up! The application window should appear shortly." -ForegroundColor Green
Write-Host "If the application doesn't start, check the terminal windows for any error messages." -ForegroundColor Yellow
Write-Host ""
Write-Host "To stop the application, close the application window and the terminal windows." -ForegroundColor Yellow
Write-Host ""

Read-Host "Press Enter to close this window"
