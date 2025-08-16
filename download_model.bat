@echo off
echo OANA - LLM Model Downloader
echo ==========================
echo.
echo This script will download the Phi-2 GGUF model for OANA.
echo.

echo Creating models directory if it doesn't exist...
if not exist "data\models" mkdir data\models

echo.
echo Downloading phi-2.Q4_K_M.gguf model (approx. 1.6GB)...
echo This may take a while depending on your internet connection.
echo.

powershell -Command "Invoke-WebRequest -Uri https://huggingface.co/TheBloke/Phi-2-GGUF/resolve/main/phi-2.Q4_K_M.gguf -OutFile data\models\phi-2.Q4_K_M.gguf"

if %errorlevel% neq 0 (
    echo.
    echo Download failed. Please download the model manually:
    echo 1. Visit https://huggingface.co/TheBloke/Phi-2-GGUF/tree/main
    echo 2. Download the phi-2.Q4_K_M.gguf file
    echo 3. Place it in the data/models folder
) else (
    echo.
    echo Download complete! The model has been saved to data/models/phi-2.Q4_K_M.gguf
)

echo.
pause
