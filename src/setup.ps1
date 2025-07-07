# =================================================================
# ==            INSTALLATION SCRIPT FOR FAST FLUX KONTEXT        ==
# ==          (UI-Driven Orchestrator for Batch Tasks)           ==
# =================================================================

# --- Configuration ---
$AppName = "Fast Flux Kontext"
$MinicondaUrl = "https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe"
$InstallerName = "miniconda_installer.exe"
$MinicondaPath = "miniconda"
$BatchInstallerScript = "install_steps.bat"

# --- UI & Window Configuration (Clean, modern theme) ---
$newWidth = 120
$newHeight = 30
$newBackgroundColor = "Black"
$newForegroundColor = "Gray"

# --- Script Environment ---
# We assume this script is located in a sub-folder (e.g., /src) of the project.
# $ProjectRoot will therefore point to the parent folder (the root).
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$MinicondaFullPath = Join-Path $ProjectRoot $MinicondaPath
$CondaExecutable = Join-Path $MinicondaFullPath "Scripts\conda.exe"

# Save the original console state
$originalState = $Host.UI.RawUI
$originalTitle = $Host.UI.RawUI.WindowTitle

try {
    # --- Configure the new console window ---
    $Host.UI.RawUI.WindowTitle = "$AppName Setup"
    $Host.UI.RawUI.BackgroundColor = $newBackgroundColor
    $Host.UI.RawUI.ForegroundColor = $newForegroundColor
    $bufferSize = [System.Management.Automation.Host.Size]::new($newWidth, 9999)
    $windowSize = [System.Management.Automation.Host.Size]::new($newWidth, $newHeight)
    $Host.UI.RawUI.BufferSize = $bufferSize
    $Host.UI.RawUI.WindowSize = $windowSize
    Clear-Host

    # =================================================================
    # ==                 UI HELPER FUNCTIONS                         ==
    # =================================================================

    function Write-Centered-Box {
        param([string[]]$Content, [hashtable]$ColorMap = @{})
        $boxInnerWidth = $newWidth - 10
        $wrappedContent = [System.Collections.Generic.List[string]]::new()
        foreach ($line in $Content) {
            if ([string]::IsNullOrEmpty($line)) { $wrappedContent.Add(""); continue }
            $currentLine = $line
            while ($currentLine.Length -gt $boxInnerWidth) {
                $breakPoint = $currentLine.Substring(0, $boxInnerWidth).LastIndexOf(" ");
                if ($breakPoint -le 0) { $breakPoint = $boxInnerWidth };
                $wrappedContent.Add($currentLine.Substring(0, $breakPoint));
                $currentLine = $currentLine.Substring($breakPoint).TrimStart()
            }
            $wrappedContent.Add($currentLine)
        }
        $Content = $wrappedContent.ToArray()
        $boxWidth = $Content | ForEach-Object { $_.Length } | Measure-Object -Maximum | Select-Object -ExpandProperty Maximum;
        if ($boxWidth -eq $null) { $boxWidth = 0 }
        $winHeight = $Host.UI.RawUI.WindowSize.Height;
        $winWidth = $Host.UI.RawUI.WindowSize.Width;
        $startY = [math]::Floor(($winHeight - ($Content.Count + 2)) / 2);
        $startX = [math]::Floor(($winWidth - ($boxWidth + 4)) / 2);
        if ($startY -lt 0) { $startY = 0 }; if ($startX -lt 0) { $startX = 0 };
        $Host.UI.RawUI.CursorPosition = [System.Management.Automation.Host.Coordinates]::new($startX, $startY);
        Write-Host ("+" + ("-" * ($boxWidth + 2)) + "+") -ForegroundColor "DarkGray";
        for ($i = 0; $i -lt $Content.Count; $i++) {
            $startY++;
            $line = $Content[$i];
            $lineColor = $ColorMap[$i];
            if (-not $lineColor) { $lineColor = "Gray" };
            $Host.UI.RawUI.CursorPosition = [System.Management.Automation.Host.Coordinates]::new($startX, $startY);
            Write-Host ("| " + $line.PadRight($boxWidth) + " |") -ForegroundColor $lineColor
        }
        $startY++;
        $Host.UI.RawUI.CursorPosition = [System.Management.Automation.Host.Coordinates]::new($startX, $startY);
        Write-Host ("+" + ("-" * ($boxWidth + 2)) + "+") -ForegroundColor "DarkGray"
    }

    function Write-Progress-UI {
        param([string]$Message, [int]$CurrentStep, [int]$TotalSteps)
        Clear-Host; $progressPercentage = [math]::Round(($CurrentStep / $TotalSteps) * 100);
        $boxInnerWidth = 70; $title = "$AppName SETUP".ToUpper();
        $titleLine = $title.PadLeft($title.Length + [math]::Floor(($boxInnerWidth - $title.Length) / 2));
        $barWidth = $boxInnerWidth - 8;
        $filledLength = [math]::Round($barWidth * $progressPercentage / 100);
        $emptyLength = $barWidth - $filledLength;
        $progressBar = "[" + ("#" * $filledLength) + ("-" * $emptyLength) + "]";
        $progressText = " [{0,3}%]" -f $progressPercentage;
        $progressLine = ($progressBar + $progressText).PadRight($boxInnerWidth);
        $content = @($titleLine, (" " * $boxInnerWidth), $Message, (" " * $boxInnerWidth), $progressLine);
        $colors = @{ 0 = "White"; 2 = "Cyan"; 4 = "Green"; }; Write-Centered-Box -Content $content -ColorMap $colors
    }

    function Execute-Step {
        param([string]$Message, [int]$StepNumber, [ref]$CurrentStepCounter, [int]$TotalSteps, [string]$GpuTier)
        $CurrentStepCounter.Value++; Write-Progress-UI -Message $Message -CurrentStep $CurrentStepCounter.Value -TotalSteps $TotalSteps

        $batchScriptFullPath = Join-Path $PSScriptRoot $BatchInstallerScript
        $process = Start-Process "cmd.exe" -ArgumentList "/c `"$batchScriptFullPath`" $StepNumber $GpuTier" -WorkingDirectory $ProjectRoot -Wait -NoNewWindow -PassThru -RedirectStandardOutput "output.log" -RedirectStandardError "error.log"

        if ($process.ExitCode -ne 0) {
            Clear-Host
            $errorLog = Get-Content "error.log" -ErrorAction SilentlyContinue
            $outputLog = Get-Content "output.log" -ErrorAction SilentlyContinue
            $errorContent = @("CRITICAL ERROR", "", "The step failed: $Message", "The batch script returned an error code.", "--- Details from error.log ---", $errorLog, "--- Details from output.log ---", $outputLog)
            Write-Centered-Box -Content $errorContent -ColorMap @{ 0 = "Red"; 2 = "Red"; 3 = "Red" }; Read-Host "`n`nPress Enter to exit"; Exit 1
        }
    }
    
    function Get-GpuTier {
        Write-Host "Checking NVIDIA graphics card..." -ForegroundColor "Yellow"
        try {
            $gpu = Get-CimInstance -ClassName Win32_VideoController | Where-Object { $_.Name -like "*NVIDIA*" } | Select-Object -First 1
            if ($null -eq $gpu) { return "INCOMPATIBLE" }

            $gpuName = $gpu.Name
            Write-Host "Detected GPU: $gpuName" -ForegroundColor "Cyan"

            if ($gpuName -match " 50\d{2}") { return "SERIE_50" }
            if ($gpuName -match " (40|30|20)\d{2}") { return "SERIE_20_40" }
            
            return "INCOMPATIBLE"
        }
        catch { return "INCOMPATIBLE" }
    }

    # =================================================================
    # ==                       MAIN SCRIPT                           ==
    # =================================================================

    # --- GPU COMPATIBILITY CHECK ---
    $gpuTier = Get-GpuTier
    if ($gpuTier -eq "INCOMPATIBLE") {
        $errorMessage = @(
            "HARDWARE COMPATIBILITY ERROR",
            "",
            "Your graphics card is not supported.",
            "This program requires an NVIDIA GeForce RTX 20, 30, 40, or 50 series GPU.",
            "Setup cannot continue."
        )
        Write-Centered-Box -Content $errorMessage -ColorMap @{ 0="Red"; 2="Yellow"; 3="Yellow" }
        Read-Host "`n`nPress Enter to exit."
        exit 1
    }
    Write-Host "Compatible GPU detected. Tier: $gpuTier" -ForegroundColor "Green"
    Start-Sleep -Seconds 3

    # --- MODIFICATION: Expanded installation steps for better UI feedback ---
    $InstallationSteps = @(
        [pscustomobject]@{ Number = 1; Message = "Installing Python 3.12.1..." },
        [pscustomobject]@{ Number = 2; Message = "Installing CUDA 12.8 libraries..." },
        [pscustomobject]@{ Number = 3; Message = "Installing the 'uv' tool..." },
        [pscustomobject]@{ Number = 4; Message = "Installing Python dependencies..." },
        [pscustomobject]@{ Number = 5; Message = "Installing PyTorch for NVIDIA GPU..." },
        [pscustomobject]@{ Number = 6; Message = "Verifying PyTorch + CUDA integration..." },
        [pscustomobject]@{ Number = 7; Message = "Installing HuggingFace Hub client..." },
        # --- Model downloads are now individual steps ---
        [pscustomobject]@{ Number = 8; Message = "Downloading Diffuser Model (FLUX.1)..." },
        [pscustomobject]@{ Number = 9; Message = "Downloading Autoencoder Model (AE)..." },
        [pscustomobject]@{ Number = 10; Message = "Downloading T5 Encoder Model..." },
        [pscustomobject]@{ Number = 11; Message = "Downloading CLIP-L Encoder Model..." },
        [pscustomobject]@{ Number = 12; Message = "Downloading LoRA Model (FLUX.1-Turbo)..." },
        # --- Final cleanup step ---
        [pscustomobject]@{ Number = 13; Message = "Organizing model files..." }
    )
    $TotalSteps = $InstallationSteps.Count + 2; $currentStep = 0

    if (-not (Test-Path $CondaExecutable)) {
        $currentStep++; Write-Progress-UI -Message "Downloading Miniconda..." -CurrentStep $currentStep -Total $TotalSteps
        $installerFullPath = Join-Path $ProjectRoot $InstallerName
        try { Start-BitsTransfer -Source $MinicondaUrl -Destination $installerFullPath } catch { Write-Centered-Box -Content @("ERROR", "", "Miniconda download FAILED.") -ColorMap @{0="Red"; 2="Red"}; Read-Host "Press Enter to exit"; Exit 1 }
        
        $currentStep++; Write-Progress-UI -Message "Installing Miniconda..." -CurrentStep $currentStep -Total $TotalSteps
        Start-Process -FilePath $installerFullPath -ArgumentList "/InstallationType=JustMe /AddToPath=0 /RegisterPython=0 /NoRegistry=1 /S /D=$MinicondaFullPath" -Wait
        Remove-Item $installerFullPath -ErrorAction SilentlyContinue
    } else { $currentStep += 2 }

    if (-not (Test-Path $CondaExecutable)) { Write-Centered-Box -Content @("ERROR", "", "Miniconda installation FAILED.") -ColorMap @{0="Red"; 2="Red"}; Read-Host "Press Enter to exit"; Exit 1 }

    foreach ($step in $InstallationSteps) {
        Execute-Step -Message $step.Message -StepNumber $step.Number -CurrentStepCounter ([ref]$currentStep) -TotalSteps $TotalSteps -GpuTier $gpuTier
    }

    Clear-Host
    $finalMessage = @("INSTALLATION COMPLETED SUCCESSFULLY!", "", "You can now launch the application.")
    Write-Centered-Box -Content $finalMessage -ColorMap @{ 0 = "Green"; 2 = "Green" }; Read-Host "`n`n`nPress Enter to exit"

} finally {
    # Restore the original console state and clean up logs
    $Host.UI.RawUI.ForegroundColor = $originalState.ForegroundColor; $Host.UI.RawUI.BackgroundColor = $originalState.BackgroundColor
    $Host.UI.RawUI.WindowSize = $originalState.WindowSize; $Host.UI.RawUI.BufferSize = $originalState.BufferSize
    $Host.UI.RawUI.WindowTitle = $originalTitle; Remove-Item "output.log" -EA 0; Remove-Item "error.log" -EA 0
}