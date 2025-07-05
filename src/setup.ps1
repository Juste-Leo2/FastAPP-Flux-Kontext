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
# On suppose que ce script se trouve dans un sous-dossier (ex: /src) du projet.
# $ProjectRoot pointera donc vers le dossier parent (la racine).
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$MinicondaFullPath = Join-Path $ProjectRoot $MinicondaPath
$CondaExecutable = Join-Path $MinicondaFullPath "Scripts\conda.exe"

# Sauvegarder l'état original de la console
$originalState = $Host.UI.RawUI
$originalTitle = $Host.UI.RawUI.WindowTitle

try {
    # --- Configuration de la nouvelle fenêtre de console ---
    $Host.UI.RawUI.WindowTitle = "$AppName Setup"
    $Host.UI.RawUI.BackgroundColor = $newBackgroundColor
    $Host.UI.RawUI.ForegroundColor = $newForegroundColor
    $bufferSize = [System.Management.Automation.Host.Size]::new($newWidth, 9999)
    $windowSize = [System.Management.Automation.Host.Size]::new($newWidth, $newHeight)
    $Host.UI.RawUI.BufferSize = $bufferSize
    $Host.UI.RawUI.WindowSize = $windowSize
    Clear-Host

    # =================================================================
    # ==                 FONCTIONS D'AIDE (UI)                       ==
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
        param([string]$Message, [int]$StepNumber, [ref]$CurrentStepCounter, [int]$TotalSteps)
        $CurrentStepCounter.Value++; Write-Progress-UI -Message $Message -CurrentStep $CurrentStepCounter.Value -TotalSteps $TotalSteps

        # --- CORRECTION DÉFINITIVE ---
        # On spécifie le chemin complet du script ET on force le répertoire de travail à être la RACINE DU PROJET.
        $batchScriptFullPath = Join-Path $PSScriptRoot $BatchInstallerScript
        $process = Start-Process "cmd.exe" -ArgumentList "/c `"$batchScriptFullPath`" $StepNumber" -WorkingDirectory $ProjectRoot -Wait -NoNewWindow -PassThru -RedirectStandardOutput "output.log" -RedirectStandardError "error.log"

        if ($process.ExitCode -ne 0) {
            Clear-Host
            $errorLog = Get-Content "error.log" -ErrorAction SilentlyContinue
            $outputLog = Get-Content "output.log" -ErrorAction SilentlyContinue
            $errorContent = @("ERREUR CRITIQUE", "", "L'étape a échoué: $Message", "Le script batch a retourné un code d'erreur.", "--- Détails depuis le journal d'erreurs ---", $errorLog, "--- Détails depuis le journal de sortie ---", $outputLog)
            Write-Centered-Box -Content $errorContent -ColorMap @{ 0 = "Red"; 2 = "Red"; 3 = "Red" }; Read-Host "`n`nAppuyez sur Entrée pour quitter"; Exit 1
        }
    }

    # =================================================================
    # ==                       SCRIPT PRINCIPAL                      ==
    # =================================================================

    $InstallationSteps = @(
        [pscustomobject]@{ Number = 1; Message = "Installation de Python 3.12.1..." },
        [pscustomobject]@{ Number = 2; Message = "Installation des librairies CUDA 12.6..." },
        [pscustomobject]@{ Number = 3; Message = "Installation de l'outil 'uv'..." },
        [pscustomobject]@{ Number = 4; Message = "Installation des dépendances Python..." },
        [pscustomobject]@{ Number = 5; Message = "Installation de PyTorch pour GPU NVIDIA..." },
        [pscustomobject]@{ Number = 6; Message = "Vérification de l'intégration PyTorch + CUDA..." },
        [pscustomobject]@{ Number = 7; Message = "Installation du client HuggingFace Hub..." },
        [pscustomobject]@{ Number = 8; Message = "Téléchargement des modèles (peut être long)..." },
        [pscustomobject]@{ Number = 9; Message = "Organisation des fichiers de modèles..." }
    )
    $TotalSteps = $InstallationSteps.Count + 2; $currentStep = 0

    if (-not (Test-Path $CondaExecutable)) {
        $currentStep++; Write-Progress-UI -Message "Téléchargement de Miniconda..." -CurrentStep $currentStep -Total $TotalSteps
        $installerFullPath = Join-Path $ProjectRoot $InstallerName
        try { Start-BitsTransfer -Source $MinicondaUrl -Destination $installerFullPath } catch { Write-Centered-Box -Content @("ERREUR", "", "Le téléchargement de Miniconda a ÉCHOUÉ.") -ColorMap @{0="Red"; 2="Red"}; Read-Host "Appuyez sur Entrée pour quitter"; Exit 1 }
        $currentStep++; Write-Progress-UI -Message "Installation de Miniconda..." -CurrentStep $currentStep -Total $TotalSteps
        Start-Process -FilePath $installerFullPath -ArgumentList "/InstallationType=JustMe /AddToPath=0 /RegisterPython=0 /NoRegistry=1 /S /D=$MinicondaFullPath" -Wait
        Remove-Item $installerFullPath -ErrorAction SilentlyContinue
    } else { $currentStep += 2 }

    if (-not (Test-Path $CondaExecutable)) { Write-Centered-Box -Content @("ERREUR", "", "L'installation de Miniconda a ÉCHOUÉ.") -ColorMap @{0="Red"; 2="Red"}; Read-Host "Appuyez sur Entrée pour quitter"; Exit 1 }

    foreach ($step in $InstallationSteps) { Execute-Step -Message $step.Message -StepNumber $step.Number -CurrentStepCounter ([ref]$currentStep) -TotalSteps $TotalSteps }

    Clear-Host
    $finalMessage = @("INSTALLATION TERMINÉE AVEC SUCCÈS !", "", "Vous pouvez maintenant lancer l'application.")
    Write-Centered-Box -Content $finalMessage -ColorMap @{ 0 = "Green"; 2 = "Green" }; Read-Host "`n`n`nAppuyez sur Entrée pour quitter"

} finally {
    $Host.UI.RawUI.ForegroundColor = $originalState.ForegroundColor; $Host.UI.RawUI.BackgroundColor = $originalState.BackgroundColor
    $Host.UI.RawUI.WindowSize = $originalState.WindowSize; $Host.UI.RawUI.BufferSize = $originalState.BufferSize
    $Host.UI.RawUI.WindowTitle = $originalTitle; Remove-Item "output.log" -EA 0; Remove-Item "error.log" -EA 0
}