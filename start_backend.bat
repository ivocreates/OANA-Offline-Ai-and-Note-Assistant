@echo off
echo ===================================
echo Starting OANA Backend Server
echo ===================================

cd backend
echo Checking for Python virtual environment...

if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to create virtual environment. Make sure Python is installed and in your PATH.
        pause
        exit /b 1
    )
)

echo Activating virtual environment...
call venv\Scripts\activate

echo Installing compatible dependencies...
pip install -r requirements.compatible.txt

echo Starting backend server...
python app.py

pause
