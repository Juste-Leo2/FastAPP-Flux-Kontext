@echo off
setlocal

:: =================================================================
:: ==            INSTALLATION TASK EXECUTOR (FLUX KONTEXT)      ==
:: =================================================================

set "STEP_TO_RUN=%1"
if not defined STEP_TO_RUN (
    echo [ERREUR] Ce script doit etre appele avec un numero d'etape.
    exit /b 1
)

:: --- Chemins ---
:: Le script est maintenant lance depuis la racine du projet, rendant les chemins simples et directs.
set "MINICONDA_PATH=.\miniconda"
set "MODELS_PATH=.\models"
set "REQUIREMENTS_FILE=.\requirements.txt"

:: --- Activation de l'environnement Conda ---
call "%MINICONDA_PATH%\Scripts\activate.bat" "%MINICONDA_PATH%"
if %errorlevel% neq 0 (
    echo [ERREUR] Echec de l'activation de l'environnement Conda.
    exit /b 1
)

:: --- Saut vers l'etape demandee ---
goto STEP_%STEP_TO_RUN%


:STEP_1
echo --- Execution Etape 1/9: Installation de Python 3.12.1...
call conda install -y -c conda-forge python=3.12.1 ca-certificates certifi openssl
if %errorlevel% neq 0 ( echo [ERREUR] L'installation de Python a echoue. & exit /b 1 )
goto END

:STEP_2
echo --- Execution Etape 2/9: Installation des librairies CUDA (12.6)...
call conda install -y -c nvidia/label/cuda-12.6.0 cuda
if %errorlevel% neq 0 ( echo [ERREUR] L'installation de CUDA a echoue. & exit /b 1 )
goto END

:STEP_3
echo --- Execution Etape 3/9: Installation de l'outil 'uv'...
call pip install uv
if %errorlevel% neq 0 ( echo [ERREUR] L'installation de 'uv' a echoue. & exit /b 1 )
goto END

:STEP_4
echo --- Execution Etape 4/9: Installation des dependances depuis requirements.txt...
call uv pip install -r "%REQUIREMENTS_FILE%" --system
if %errorlevel% neq 0 ( echo [ERREUR] L'installation des dependances a echoue. & exit /b 1 )
goto END

:STEP_5
echo --- Execution Etape 5/9: Installation de PyTorch pour GPU NVIDIA...
call uv pip install torch torchvision torchaudio --system --extra-index-url https://download.pytorch.org/whl/cu126 --reinstall
if %errorlevel% neq 0 ( echo [ERREUR] L'installation de PyTorch a echoue. & exit /b 1 )
goto END

:STEP_6
echo --- Execution Etape 6/9: Verification de l'integration PyTorch + CUDA...
call python -c "import torch; assert torch.cuda.is_available(), 'PyTorch ne detecte pas CUDA.'"
if %errorlevel% neq 0 (
    echo [ERREUR] TEST CRITIQUE ECHOUE: PyTorch ne peut pas communiquer avec le GPU.
    echo Verifiez que vos pilotes NVIDIA sont a jour et compatibles avec CUDA 12.6.
    exit /b 1
)
echo PyTorch et CUDA communiquent avec succes !
goto END

:STEP_7
echo --- Execution Etape 7/9: Installation du client HuggingFace Hub...
call uv pip install huggingface-hub --system
if %errorlevel% neq 0 ( echo [ERREUR] L'installation de huggingface-hub a echoue. & exit /b 1 )
goto END

:STEP_8
echo --- Execution Etape 8/9: Telechargement de tous les modeles requis...
echo Cette operation peut prendre beaucoup de temps.

echo   - Telechargement du Modele Diffuser (FLUX.1)...
call huggingface-cli download mit-han-lab/nunchaku-flux.1-kontext-dev svdq-int4_r32-flux.1-kontext-dev.safetensors --local-dir "%MODELS_PATH%" --local-dir-use-symlinks False
if %errorlevel% neq 0 ( echo [ERREUR] Le telechargement du modele Diffuser a echoue. & exit /b 1 )

echo   - Telechargement du Modele Autoencoder (AE)...
call huggingface-cli download Comfy-Org/Lumina_Image_2.0_Repackaged split_files/vae/ae.safetensors --local-dir "%MODELS_PATH%" --local-dir-use-symlinks False
if %errorlevel% neq 0 ( echo [ERREUR] Le telechargement du modele AE a echoue. & exit /b 1 )

echo   - Telechargement du Modele T5 Encoder...
call huggingface-cli download comfyanonymous/flux_text_encoders t5xxl_fp8_e4m3fn_scaled.safetensors --local-dir "%MODELS_PATH%" --local-dir-use-symlinks False
if %errorlevel% neq 0 ( echo [ERREUR] Le telechargement du modele T5 a echoue. & exit /b 1 )

echo   - Telechargement du Modele CLIP-L Encoder...
call huggingface-cli download comfyanonymous/flux_text_encoders clip_l.safetensors --local-dir "%MODELS_PATH%" --local-dir-use-symlinks False
if %errorlevel% neq 0 ( echo [ERREUR] Le telechargement du modele CLIP-L a echoue. & exit /b 1 )

echo   - Telechargement du Modele LoRA (FLUX.1-Turbo)...
call huggingface-cli download alimama-creative/FLUX.1-Turbo-Alpha diffusion_pytorch_model.safetensors --local-dir "%MODELS_PATH%" --local-dir-use-symlinks False
if %errorlevel% neq 0 ( echo [ERREUR] Le telechargement du modele LoRA a echoue. & exit /b 1 )
goto END

:STEP_9
echo --- Execution Etape 9/9: Reorganisation des fichiers modeles...
move "%MODELS_PATH%\split_files\vae\ae.safetensors" "%MODELS_PATH%\ae.safetensors"
if %errorlevel% neq 0 ( echo [ERREUR] Echec du deplacement du modele AE. & exit /b 1 )
echo   - Nettoyage des dossiers vides...
rd /s /q "%MODELS_PATH%\split_files"
goto END


:UNKNOWN_STEP
echo [ERREUR] Numero d'etape inconnu: %STEP_TO_RUN%
exit /b 1

:END
exit /b 0