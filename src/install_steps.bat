@echo off
setlocal enabledelayedexpansion

:: =================================================================
:: ==            INSTALLATION TASK EXECUTOR (FLUX KONTEXT)      ==
:: =================================================================

set "STEP_TO_RUN=%1"
set "GPU_TIER=%2"

if not defined STEP_TO_RUN (
    echo [ERROR] This script must be called with a step number.
    exit /b 1
)

:: --- Paths ---
set "MINICONDA_PATH=.\miniconda"
set "MODELS_PATH=.\models"
set "REQUIREMENTS_FILE=.\requirements.txt"

:: --- Activate the Conda environment ---
call "%MINICONDA_PATH%\Scripts\activate.bat" "%MINICONDA_PATH%"
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate the Conda environment.
    exit /b 1
)

:: --- Jump to the requested step ---
goto STEP_%STEP_TO_RUN%


:STEP_1
echo --- Executing Step 1/13: Installing Python 3.12.1...
call conda install -y -c conda-forge python=3.12.1 ca-certificates certifi openssl
if %errorlevel% neq 0 ( echo [ERROR] Python installation failed. & exit /b 1 )
goto END

:STEP_2
echo --- Executing Step 2/13: Installing CUDA libraries (12.8)...
call conda install -y -c nvidia/label/cuda-12.8.0 cuda
if %errorlevel% neq 0 ( echo [ERROR] CUDA installation failed. & exit /b 1 )
goto END

:STEP_3
echo --- Executing Step 3/13: Installing the 'uv' tool...
call pip install uv
if %errorlevel% neq 0 ( echo [ERROR] 'uv' installation failed. & exit /b 1 )
goto END

:STEP_4
echo --- Executing Step 4/13: Installing dependencies from requirements.txt...
call uv pip install -r "%REQUIREMENTS_FILE%" --system
if %errorlevel% neq 0 ( echo [ERROR] Dependency installation failed. & exit /b 1 )
goto END

:STEP_5
echo --- Executing Step 5/13: Installing PyTorch for NVIDIA GPU...
call uv pip install torch torchvision torchaudio --system --extra-index-url https://download.pytorch.org/whl/cu128 --reinstall
if %errorlevel% neq 0 ( echo [ERROR] PyTorch installation failed. & exit /b 1 )
goto END

:STEP_6
echo --- Executing Step 6/13: Verifying PyTorch + CUDA integration...
call python -c "import torch; assert torch.cuda.is_available(), 'PyTorch does not detect CUDA.'"
if %errorlevel% neq 0 (
    echo [ERROR] CRITICAL TEST FAILED: PyTorch cannot communicate with the GPU.
    echo Verify that your NVIDIA drivers are up to date and compatible with CUDA 12.8.
    exit /b 1
)
echo PyTorch and CUDA are communicating successfully!
goto END

:STEP_7
echo --- Executing Step 7/13: Installing HuggingFace Hub client...
call uv pip install huggingface-hub --system
if %errorlevel% neq 0 ( echo [ERROR] huggingface-hub installation failed. & exit /b 1 )
goto END

:STEP_8
echo --- Executing Step 8/13: Downloading Diffuser Model (FLUX.1)...

:: 1. Détermine le nom du fichier modèle à télécharger en fonction du GPU
set "MODEL_TO_DOWNLOAD="
if /i "!GPU_TIER!"=="SERIE_50" (
    set "MODEL_TO_DOWNLOAD=svdq-fp4_r32-flux.1-kontext-dev.safetensors"
    echo      Target Model: svdq-fp4_r32-flux.1-kontext-dev.safetensors (for RTX 5000 series)
)
if /i "!GPU_TIER!"=="SERIE_20_40" (
    set "MODEL_TO_DOWNLOAD=svdq-int4_r32-flux.1-kontext-dev.safetensors"
    echo      Target Model: svdq-int4_r32-flux.1-kontext-dev.safetensors (for RTX 2000-4000 series)
)

:: 2. Vérifie si un modèle a bien été sélectionné
if not defined MODEL_TO_DOWNLOAD (
    echo [ERROR] GPU Tier '!GPU_TIER!' is unknown or invalid. Cannot select a diffuser model.
    exit /b 1
)

:: 3. Lance le téléchargement de l'unique fichier sélectionné
call huggingface-cli download mit-han-lab/nunchaku-flux.1-kontext-dev !MODEL_TO_DOWNLOAD! --local-dir "%MODELS_PATH%" --local-dir-use-symlinks False
if %errorlevel% neq 0 ( echo [ERROR] Diffuser model download failed. & exit /b 1 )
goto END

:STEP_9
echo --- Executing Step 9/13: Downloading Autoencoder Model (AE)...
call huggingface-cli download Comfy-Org/Lumina_Image_2.0_Repackaged split_files/vae/ae.safetensors --local-dir "%MODELS_PATH%" --local-dir-use-symlinks False
if %errorlevel% neq 0 ( echo [ERROR] AE model download failed. & exit /b 1 )
goto END

:STEP_10
echo --- Executing Step 10/13: Downloading T5 Encoder Model...
call huggingface-cli download comfyanonymous/flux_text_encoders t5xxl_fp8_e4m3fn_scaled.safetensors --local-dir "%MODELS_PATH%" --local-dir-use-symlinks False
if %errorlevel% neq 0 ( echo [ERROR] T5 model download failed. & exit /b 1 )
goto END

:STEP_11
echo --- Executing Step 11/13: Downloading CLIP-L Encoder Model...
call huggingface-cli download comfyanonymous/flux_text_encoders clip_l.safetensors --local-dir "%MODELS_PATH%" --local-dir-use-symlinks False
if %errorlevel% neq 0 ( echo [ERROR] CLIP-L model download failed. & exit /b 1 )
goto END

:STEP_12
echo --- Executing Step 12/13: Downloading LoRA Model (FLUX.1-Turbo)...
call huggingface-cli download alimama-creative/FLUX.1-Turbo-Alpha diffusion_pytorch_model.safetensors --local-dir "%MODELS_PATH%" --local-dir-use-symlinks False
if %errorlevel% neq 0 ( echo [ERROR] LoRA model download failed. & exit /b 1 )
goto END

:STEP_13
echo --- Executing Step 13/13: Reorganizing model files...
move "%MODELS_PATH%\split_files\vae\ae.safetensors" "%MODELS_PATH%\ae.safetensors"
if %errorlevel% neq 0 ( echo [ERROR] Failed to move the AE model. & exit /b 1 )
echo   - Cleaning up empty folders...
rd /s /q "%MODELS_PATH%\split_files"
goto END


:UNKNOWN_STEP
echo [ERROR] Unknown step number: %STEP_TO_RUN%
exit /b 1

:END
exit /b 0