@echo off
title OANA - Offline AI and Note Assistant

echo ========================================
echo  OANA - Offline AI and Note Assistant
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9+ from https://python.org
    echo.
    pause
    exit /b 1
)

echo Python found: 
python --version

REM Check if app.py exists
if not exist "app.py" (
    echo ERROR: app.py not found in current directory
    echo Please run this script from the project root directory
    echo.
    pause
    exit /b 1
)

echo.
echo Starting OANA...
echo.

REM Try the launcher first, fallback to app.py
python launch_oana.py
if errorlevel 1 (
    echo.
    echo Trying alternative launch method...
    python app.py
)

REM Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo Application exited with an error.
    echo Check the error messages above.
    echo.
    pause
)
