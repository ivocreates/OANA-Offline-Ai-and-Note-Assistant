@echo off
echo OANA - LLM Model Downloader
echo ==========================
echo.

echo Creating models directory if it doesn't exist...
if not exist "data\models" mkdir data\models

echo Please select a model to download:
echo 1. phi-2.Q4_K_M.gguf (Phi-2, ~1.6GB, efficient but may have compatibility issues)
echo 2. mistral-7b-v0.1.Q4_K_M.gguf (Mistral, ~3.8GB, better compatibility)
echo 3. tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf (TinyLlama, ~600MB, very small)
echo.

choice /C 123 /N /M "Enter your choice (1-3): "

if %ERRORLEVEL% EQU 1 (
    set MODEL_NAME=phi-2.Q4_K_M.gguf
    set MODEL_URL=https://huggingface.co/TheBloke/Phi-2-GGUF/resolve/main/phi-2.Q4_K_M.gguf
    set MODEL_SIZE=1.6GB
    set MODEL_HF=TheBloke/Phi-2-GGUF/tree/main
) else if %ERRORLEVEL% EQU 2 (
    set MODEL_NAME=mistral-7b-v0.1.Q4_K_M.gguf
    set MODEL_URL=https://huggingface.co/TheBloke/Mistral-7B-v0.1-GGUF/resolve/main/mistral-7b-v0.1.Q4_K_M.gguf
    set MODEL_SIZE=3.8GB
    set MODEL_HF=TheBloke/Mistral-7B-v0.1-GGUF/tree/main
) else if %ERRORLEVEL% EQU 3 (
    set MODEL_NAME=tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf
    set MODEL_URL=https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf
    set MODEL_SIZE=600MB
    set MODEL_HF=TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/tree/main
)

echo.
echo Downloading %MODEL_NAME% (approx. %MODEL_SIZE%)...
echo This may take a while depending on your internet connection.
echo.

powershell -Command "Invoke-WebRequest -Uri %MODEL_URL% -OutFile data\models\%MODEL_NAME%"

if %errorlevel% neq 0 (
    echo.
    echo Download failed. Please download the model manually:
    echo 1. Visit https://huggingface.co/%MODEL_HF%
    echo 2. Download the %MODEL_NAME% file
    echo 3. Place it in the data/models folder
) else (
    echo.
    echo Download complete! The model has been saved to data\models\%MODEL_NAME%
    
    echo.
    echo Updating config to use this model...
    powershell -Command "(Get-Content backend\config.py) -replace 'llm_model_file: str = \".*\"', 'llm_model_file: str = \"%MODEL_NAME%\"' | Set-Content backend\config.py"
)

echo.
pause
