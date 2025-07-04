; ====================================================================
; ==  Inno Setup Script for Fast Flux Kontext                     ==
; ====================================================================

[Setup]
AppName=Fast_Flux_Kontext
AppVersion=1.0
AppPublisher=Juste_Leo
DefaultDirName={autopf}\Flux_context_app
DefaultGroupName=Fast Flux Kontext
OutputBaseFilename=setup-fast-flux-kontext-v1.0
WizardStyle=modern
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=admin
UsePreviousAppDir=no
; Icon for the installer itself, located in the parent 'docs' folder
SetupIconFile=..\docs\flux.ico

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Dirs]
Name: "{app}\models"
Name: "{app}\src"
Name: "{app}\output"

[Files]
; IMPORTANT: All source paths now use '..\' because the script is in the 'executable' subfolder.
Source: "..\src\*"; DestDir: "{app}\src"; Flags: recursesubdirs createallsubdirs
Source: "..\LICENSE"; DestDir: "{app}"
Source: "..\README.md"; DestDir: "{app}"
Source: "..\requirements.txt"; DestDir: "{app}"
Source: "..\docs\*"; DestDir: "{app}\docs"; Flags: recursesubdirs createallsubdirs

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}";
Name: "appdirshortcut"; Description: "Create a shortcut in the application folder"; GroupDescription: "{cm:AdditionalIcons}";

[Icons]
; Start Menu Shortcut (always created)
Name: "{group}\Fast Flux Kontext"; Filename: "powershell.exe"; Parameters: "-WindowStyle Hidden -NoProfile -ExecutionPolicy Bypass -File ""{app}\src\run.ps1"""; WorkingDir: "{app}"; IconFilename: "{app}\docs\flux.ico"

; Desktop Shortcut (optional)
Name: "{autodesktop}\Fast Flux Kontext"; Filename: "powershell.exe"; Parameters: "-WindowStyle Hidden -NoProfile -ExecutionPolicy Bypass -File ""{app}\src\run.ps1"""; WorkingDir: "{app}"; Tasks: desktopicon; IconFilename: "{app}\docs\flux.ico"

; Installation Folder Shortcut (optional)
Name: "{app}\Fast Flux Kontext"; Filename: "powershell.exe"; Parameters: "-WindowStyle Hidden -NoProfile -ExecutionPolicy Bypass -File ""{app}\src\run.ps1"""; WorkingDir: "{app}"; Tasks: appdirshortcut; IconFilename: "{app}\docs\flux.ico"

; Uninstaller Shortcut (always created)
Name: "{group}\Uninstall Fast Flux Kontext"; Filename: "{uninstallexe}"

[Run]
Filename: "powershell.exe"; \
    Parameters: "-NoProfile -Command ""Invoke-WebRequest -Uri 'https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe' -OutFile '{tmp}\miniconda_installer.exe'"""; \
    StatusMsg: "Downloading Python installer (Miniconda)..."; \
    Flags: waituntilterminated

Filename: "{tmp}\miniconda_installer.exe"; \
    Parameters: "/InstallationType=JustMe /AddToPath=0 /RegisterPython=0 /NoRegistry=1 /S /D={app}\miniconda"; \
    StatusMsg: "Installing Python environment..."; \
    Flags: waituntilterminated

Filename: "{tmp}\full_install_script.bat"; \
    StatusMsg: "Installing dependencies and models (a console window will open)..."; \
    WorkingDir: "{app}"; Flags: waituntilterminated

[Code]
var
  InstallScript: TStringList;

procedure AddStep(Script: TStringList; Command: string; ErrorMessage: string);
begin
  Script.Add('echo.');
  Script.Add(Command);
  Script.Add('if %errorlevel% neq 0 (');
  Script.Add('  echo [CRITICAL ERROR] ' + ErrorMessage);
  Script.Add('  echo.');
  Script.Add('  pause');
  Script.Add('  exit /b 1');
  Script.Add(')');
end;

// Helper procedure for model downloads with progress bar
procedure AddModelDownload(Script: TStringList; ModelName: string; Url: string; DestFile: string);
var
  PowerShellCommand: string;
begin
  Script.Add('echo.');
  Script.Add('echo --- Downloading ' + ModelName + ' Model ---');
  Script.Add('echo This may take some time depending on your internet connection.');
  // Using Invoke-WebRequest from PowerShell to get a progress bar in the console
  PowerShellCommand := 'powershell -NoProfile -Command "Invoke-WebRequest -Uri ''' + Url + ''' -OutFile ''' + DestFile + '''"';
  AddStep(Script, PowerShellCommand, 'Failed to download the ' + ModelName + ' model.');
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  BatchFilePath: string;
begin
  if CurStep = ssInstall then
  begin
    BatchFilePath := ExpandConstant('{tmp}\full_install_script.bat');
    InstallScript := TStringList.Create;
    
    InstallScript.Add('@echo off');
    InstallScript.Add('title Fast Flux Kontext Component Installation');
    InstallScript.Add('echo This script will now install all required components.');
    InstallScript.Add('echo Please do not close this window.');
    
    AddStep(InstallScript, 'echo --- Activating Conda Environment ---', '');
    AddStep(InstallScript, 'call "miniconda\Scripts\activate.bat"', 'Failed to activate Conda.');
    
    AddStep(InstallScript, 'echo --- Installing Python 3.12.1 ---', '');
    AddStep(InstallScript, 'call conda install -y -c conda-forge python=3.12.1 ca-certificates certifi openssl', 'Failed to install Python.');
    
    AddStep(InstallScript, 'echo --- Installing CUDA Libraries (v12.6) ---', '');
    AddStep(InstallScript, 'call conda install -y -c nvidia/label/cuda-12.6.0 cuda', 'Failed to install CUDA libraries.');
    
    AddStep(InstallScript, 'echo --- Installing ''uv'' tool ---', '');
    AddStep(InstallScript, 'call pip install uv', 'Failed to install "uv".');
    
    AddStep(InstallScript, 'echo --- Installing Python dependencies from requirements.txt ---', '');
    AddStep(InstallScript, 'call uv pip install -r "requirements.txt" --system', 'Failed to install Python dependencies.');
    
    AddStep(InstallScript, 'echo --- Installing PyTorch for NVIDIA GPU ---', '');
    AddStep(InstallScript, 'call uv pip install torch torchvision torchaudio --system --extra-index-url https://download.pytorch.org/whl/cu126 --reinstall', 'Failed to install PyTorch.');

    AddStep(InstallScript, 'echo --- Verifying GPU integration ---', '');
    AddStep(InstallScript, 'call python -c "import torch; assert torch.cuda.is_available(), \"PyTorch cannot see CUDA.\""', 'PyTorch+CUDA verification failed.');

    // --- Model Downloads with Progress ---

    
    AddStep(InstallScript, 'echo --- Installing HuggingFace Hub client ---', '');
    AddStep(InstallScript, 'call uv pip install huggingface-hub --system', 'Failed to install huggingface-hub.');

    AddStep(InstallScript, 'echo --- Downloading Diffuser (FLUX.1) Model ---', '');
    AddStep(InstallScript, 'call huggingface-cli download mit-han-lab/nunchaku-flux.1-kontext-dev svdq-int4_r32-flux.1-kontext-dev.safetensors --local-dir "models" --local-dir-use-symlinks False', 'Failed to download Diffuser model.');
    
    AddStep(InstallScript, 'echo --- Downloading Autoencoder (AE) Model ---', '');
    AddStep(InstallScript, 'call huggingface-cli download Comfy-Org/Lumina_Image_2.0_Repackaged split_files/vae/ae.safetensors --local-dir "models" --local-dir-use-symlinks False', 'Failed to download AE model.');

    AddStep(InstallScript, 'echo --- Downloading T5 Encoder Model ---', '');
    AddStep(InstallScript, 'call huggingface-cli download comfyanonymous/flux_text_encoders t5xxl_fp8_e4m3fn_scaled.safetensors --local-dir "models" --local-dir-use-symlinks False', 'Failed to download T5 Encoder model.');

    AddStep(InstallScript, 'echo --- Downloading CLIP-L Encoder Model ---', '');
    AddStep(InstallScript, 'call huggingface-cli download comfyanonymous/flux_text_encoders clip_l.safetensors --local-dir "models" --local-dir-use-symlinks False', 'Failed to download CLIP-L model.');
    
    AddStep(InstallScript, 'echo --- Downloading LoRA (FLUX.1-Turbo) Model ---', '');
    AddStep(InstallScript, 'call huggingface-cli download alimama-creative/FLUX.1-Turbo-Alpha diffusion_pytorch_model.safetensors --local-dir "models" --local-dir-use-symlinks False', 'Failed to download LoRA model.');

    AddStep(InstallScript, 'echo --- Reorganizing model files for the application ---', '');
    AddStep(InstallScript, 'move "models\split_files\vae\ae.safetensors" "models\ae.safetensors"', 'Failed to move the AE model file.');
    
    AddStep(InstallScript, 'echo --- Cleaning up empty directories ---', '');
    AddStep(InstallScript, 'rd /s /q "models\split_files"', 'Failed to clean up temporary directories.');

    InstallScript.Add('echo.');
    InstallScript.Add('echo --------------------------------------------------');
    InstallScript.Add('echo -- INSTALLATION COMPLETED SUCCESSFULLY! --');
    InstallScript.Add('echo --------------------------------------------------');
    InstallScript.Add('echo.');
    InstallScript.Add('pause');
    
    InstallScript.SaveToFile(BatchFilePath);
    InstallScript.Free;
  end;
end;

procedure DeinitializeSetup();
begin
  DeleteFile(ExpandConstant('{tmp}\full_install_script.bat'));
end;