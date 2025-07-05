@echo off
setlocal

:: =================================================================
:: ==            INSTALLATION TASK EXECUTOR (FLUX KONTEXT)      ==
:: =================================================================
::
:: This script executes a single installation step based on the
:: argument it receives (%1). It is called by setup.ps1.
:: It ensures every command runs inside the activated Conda env.
::

:: --- Get the step number to execute ---
set "STEP_TO_RUN=%1"
if not defined STEP_TO_RUN (
    echo [ERROR] This script must be called with a step number.
    exit /b 1
)

:: --- Paths ---
:: Assumes this script is in a subdirectory (e.g., 'setup') of the project root.
set "PROJECT_ROOT=%~dp0.."
set "MINICONDA_PATH=%PROJECT_ROOT%\miniconda"
set "MODELS_PATH=%PROJECT_ROOT%\models"
set "REQUIREMENTS_FILE=%PROJECT_ROOT%\requirements.txt"

:: --- Activate Conda Environment ---
:: This MUST be done before any other step.
call "%MINICONDA_PATH%\Scripts\activate.bat" "%MINICONDA_PATH%"
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate the Conda environment.
    exit /b 1
)

:: --- JUMP to the requested step ---
goto STEP_%STEP_TO_RUN%


:STEP_1
echo --- Running Step 1/9: Installing Python 3.12.1...
call conda install -y -c conda-forge python=3.12.1 ca-certificates certifi openssl
if %errorlevel% neq 0 ( echo [ERROR] Python installation failed. & exit /b 1 )
goto END

:STEP_2
echo --- Running Step 2/9: Installing CUDA libraries (12.6)...
call conda install -y -c nvidia/label/cuda-12.6.0 cuda
if %errorlevel% neq 0 ( echo [ERROR] CUDA installation failed. & exit /b 1 )
goto END

:STEP_3
echo --- Running Step 3/9: Installing 'uv' tool...
call pip install uv
if %errorlevel% neq 0 ( echo [ERROR] Failed to install 'uv'. & exit /b 1 )
goto END

:STEP_4
echo --- Running Step 4/9: Installing dependencies from requirements.txt...
call uv pip install -r "%REQUIREMENTS_FILE%" --system
if %errorlevel% neq 0 ( echo [ERROR] Failed to install dependencies from requirements.txt. & exit /b 1 )
goto END

:STEP_5
echo --- Running Step 5/9: Installing PyTorch for NVIDIA GPU...
call uv pip install torch torchvision torchaudio --system --extra-index-url https://download.pytorch.org/whl/cu126 --reinstall
if %errorlevel% neq 0 ( echo [ERROR] PyTorch installation failed. & exit /b 1 )
goto END

:STEP_6
echo --- Running Step 6/9: Verifying PyTorch + CUDA integration...
call python -c "import torch; assert torch.cuda.is_available(), 'PyTorch cannot see CUDA.'"
if %errorlevel% neq 0 (
    echo [ERROR] CRITICAL TEST FAILED: PyTorch cannot communicate with the GPU.
    echo Verify your NVIDIA drivers are up-to-date and compatible with CUDA 12.6.
    exit /b 1
)
echo PyTorch and CUDA are communicating successfully!
goto END

:STEP_7
echo --- Running Step 7/9: Installing HuggingFace Hub client...
call uv pip install huggingface-hub --system
if %errorlevel% neq 0 ( echo [ERROR] Failed to install huggingface-hub. & exit /b 1 )
goto END

:STEP_8
echo --- Running Step 8/9: Downloading all required models...
echo This may take a significant amount of time.

echo   - Downloading Diffuser (FLUX.1) Model...
call huggingface-cli download mit-han-lab/nunchaku-flux.1-kontext-dev svdq-int4_r32-flux.1-kontext-dev.safetensors --local-dir "%MODELS_PATH%" --local-dir-use-symlinks False
if %errorlevel% neq 0 ( echo [ERROR] Diffuser model download failed. & exit /b 1 )

echo   - Downloading Autoencoder (AE) Model...
call huggingface-cli download Comfy-Org/Lumina_Image_2.0_Repackaged split_files/vae/ae.safetensors --local-dir "%MODELS_PATH%" --local-dir-use-symlinks False
if %errorlevel% neq 0 ( echo [ERROR] AE model download failed. & exit /b 1 )

echo   - Downloading T5 Encoder Model...
call huggingface-cli download comfyanonymous/flux_text_encoders t5xxl_fp8_e4m3fn_scaled.safetensors --local-dir "%MODELS_PATH%" --local-dir-use-symlinks False
if %errorlevel% neq 0 ( echo [ERROR] T5 Encoder model download failed. & exit /b 1 )

echo   - Downloading CLIP-L Encoder Model...
call huggingface-cli download comfyanonymous/flux_text_encoders clip_l.safetensors --local-dir "%MODELS_PATH%" --local-dir-use-symlinks False
if %errorlevel% neq 0 ( echo [ERROR] CLIP-L model download failed. & exit /b 1 )

echo   - Downloading LoRA (FLUX.1-Turbo) Model...
call huggingface-cli download alimama-creative/FLUX.1-Turbo-Alpha diffusion_pytorch_model.safetensors --local-dir "%MODELS_PATH%" --local-dir-use-symlinks False
if %errorlevel% neq 0 ( echo [ERROR] LoRA model download failed. & exit /b 1 )

goto END

:STEP_9
echo --- Running Step 9/9: Reorganizing model files...
move "%MODELS_PATH%\split_files\vae\ae.safetensors" "%MODELS_PATH%\ae.safetensors"
if %errorlevel% neq 0 ( echo [ERROR] Failed to move the AE model file. & exit /b 1 )
echo   - Cleaning up empty directories...
rd /s /q "%MODELS_PATH%\split_files"
if %errorlevel% neq 0 ( echo [WARN] Could not remove temporary 'split_files' directory. This is not critical. )
goto END


:UNKNOWN_STEP
echo [ERROR] Unknown step number provided: %STEP_TO_RUN%
exit /b 1

:END
exit /b 0