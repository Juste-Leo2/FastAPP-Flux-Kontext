# =================================================================
# ==            INSTALLATION SCRIPT FOR FAST FLUX KONTEXT        ==
# ==          (UI-Driven Orchestrator for Batch Tasks)           ==
# =================================================================

# --- Configuration ---
$AppName = "Fast Flux Kontext"
$MinicondaUrl = "https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe"
$InstallerName = "miniconda_installer.exe"
$MinicondaPath = "miniconda"
$BatchInstallerScript = "install_steps.bat" # The name of your .bat file

# --- UI & Window Configuration (Clean, modern theme) ---
$newWidth = 120
$newHeight = 30
$newBackgroundColor = "Black"
$newForegroundColor = "Gray"

# --- Script Environment ---
# Assumes this script is in a subdirectory (e.g., /setup) of the project.
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$MinicondaFullPath = Join-Path $ProjectRoot $MinicondaPath
$CondaExecutable = Join-Path $MinicondaFullPath "Scripts\conda.exe"

# Save the original console state
$originalState = $Host.UI.RawUI
$originalTitle = $Host.UI.RawUI.WindowTitle

# This 'finally' block ensures that the console is restored even if the script fails.
try {
    # --- Setup the new console window ---
    $Host.UI.RawUI.WindowTitle = "$AppName Setup"
    $Host.UI.RawUI.BackgroundColor = $newBackgroundColor
    $Host.UI.RawUI.ForegroundColor = $newForegroundColor
    $bufferSize = [System.Management.Automation.Host.Size]::new($newWidth, 9999)
    $windowSize = [System.Management.Automation.Host.Size]::new($newWidth, $newHeight)
    $Host.UI.RawUI.BufferSize = $bufferSize
    $Host.UI.RawUI.WindowSize = $windowSize
    Clear-Host

    # =================================================================
    # ==                     HELPER FUNCTIONS (UI)                   ==
    # =================================================================

    function Write-Centered-Box {
        param(
            [string[]]$Content,
            [hashtable]$ColorMap = @{}
        )
        
        # --- FIX: Word wrapping to prevent coordinate errors ---
        $boxInnerWidth = $newWidth - 10 # Define a safe maximum width for content
        $wrappedContent = [System.Collections.Generic.List[string]]::new()
        foreach ($line in $Content) {
            if ([string]::IsNullOrEmpty($line)) {
                $wrappedContent.Add("")
                continue
            }
            $currentLine = $line
            while ($currentLine.Length > $boxInnerWidth) {
                $breakPoint = $currentLine.Substring(0, $boxInnerWidth).LastIndexOf(" ")
                if ($breakPoint -le 0) { $breakPoint = $boxInnerWidth } # Hard break if no space found
                $wrappedContent.Add($currentLine.Substring(0, $breakPoint))
                $currentLine = $currentLine.Substring($breakPoint).TrimStart()
            }
            $wrappedContent.Add($currentLine)
        }
        $Content = $wrappedContent.ToArray()
        # --- End of FIX ---

        $boxWidth = $Content | ForEach-Object { $_.Length } | Measure-Object -Maximum | Select-Object -ExpandProperty Maximum
        if ($boxWidth -eq $null) { $boxWidth = 0 }

        $winHeight = $Host.UI.RawUI.WindowSize.Height
        $winWidth = $Host.UI.RawUI.WindowSize.Width
        $startY = [math]::Floor(($winHeight - ($Content.Count + 2)) / 2)
        $startX = [math]::Floor(($winWidth - ($boxWidth + 4)) / 2)

        # Ensure coordinates are not negative
        if ($startY -lt 0) { $startY = 0 }
        if ($startX -lt 0) { $startX = 0 }
        
        $Host.UI.RawUI.CursorPosition = [System.Management.Automation.Host.Coordinates]::new($startX, $startY)
        Write-Host ("+" + ("-" * ($boxWidth + 2)) + "+") -ForegroundColor "DarkGray"

        for ($i = 0; $i -lt $Content.Count; $i++) {
            $startY++
            $line = $Content[$i]
            $lineColor = $ColorMap[$i]
            if (-not $lineColor) { $lineColor = "Gray" }
            $Host.UI.RawUI.CursorPosition = [System.Management.Automation.Host.Coordinates]::new($startX, $startY)
            Write-Host ("| " + $line.PadRight($boxWidth) + " |") -ForegroundColor $lineColor
        }

        $startY++
        $Host.UI.RawUI.CursorPosition = [System.Management.Automation.Host.Coordinates]::new($startX, $startY)
        Write-Host ("+" + ("-" * ($boxWidth + 2)) + "+") -ForegroundColor "DarkGray"
    }

    function Write-Progress-UI {
        param(
            [string]$Message,
            [int]$CurrentStep,
            [int]$TotalSteps
        )
        Clear-Host # Ensure a clean slate for every redraw
        $progressPercentage = [math]::Round(($CurrentStep / $TotalSteps) * 100)
        
        $boxInnerWidth = 70
        $title = "$AppName SETUP".ToUpper()
        $titleLine = $title.PadLeft($title.Length + [math]::Floor(($boxInnerWidth - $title.Length) / 2))

        # 100% ASCII-safe progress bar
        $barWidth = $boxInnerWidth - 8
        $filledLength = [math]::Round($barWidth * $progressPercentage / 100)
        $emptyLength = $barWidth - $filledLength
        $progressBar = "[" + ("#" * $filledLength) + ("-" * $emptyLength) + "]"
        $progressText = " [{0,3}%]" -f $progressPercentage
        $progressLine = ($progressBar + $progressText).PadRight($boxInnerWidth)

        $content = @($titleLine, (" " * $boxInnerWidth), $Message, (" " * $boxInnerWidth), $progressLine)
        $colors = @{ 0 = "White"; 2 = "Cyan"; 4 = "Green"; }
        
        Write-Centered-Box -Content $content -ColorMap $colors
    }

    function Execute-Step {
        param(
            [string]$Message,
            [int]$StepNumber,
            [ref]$CurrentStepCounter,
            [int]$TotalSteps
        )
        $CurrentStepCounter.Value++
        Write-Progress-UI -Message $Message -CurrentStep $CurrentStepCounter.Value -TotalSteps $TotalSteps

        # Execute the batch script for the specified step
        # Run it hidden and capture output for error reporting
        $process = Start-Process "cmd.exe" -ArgumentList "/c `"$BatchInstallerScript`" $StepNumber" -WorkingDirectory $PSScriptRoot -Wait -NoNewWindow -PassThru -RedirectStandardOutput "output.log" -RedirectStandardError "error.log"

        if ($process.ExitCode -ne 0) {
            Clear-Host
            $errorLog = Get-Content "error.log" -ErrorAction SilentlyContinue
            $outputLog = Get-Content "output.log" -ErrorAction SilentlyContinue
            $errorContent = @(
                "CRITICAL ERROR", 
                "", 
                "Step failed: $Message", 
                "The batch script returned a non-zero exit code.",
                "--- Details from error log ---",
                $errorLog,
                "--- Details from output log ---",
                $outputLog
            )
            Write-Centered-Box -Content $errorContent -ColorMap @{ 0 = "Red"; 2 = "Red"; 3 = "Red" }
            Read-Host "`n`nPress Enter to exit"
            Exit 1
        }
    }

    # =================================================================
    # ==                       MAIN SCRIPT                           ==
    # =================================================================

    # Define all installation steps for "Fast Flux Kontext"
    # These must match the step numbers in install_steps.bat
    $InstallationSteps = @(
        [pscustomobject]@{ Number = 1; Message = "Installing Python 3.12.1..." },
        [pscustomobject]@{ Number = 2; Message = "Installing CUDA libraries 12.6..." },
        [pscustomobject]@{ Number = 3; Message = "Installing 'uv' tool..." },
        [pscustomobject]@{ Number = 4; Message = "Installing Python dependencies..." },
        [pscustomobject]@{ Number = 5; Message = "Installing PyTorch for NVIDIA GPU..." },
        [pscustomobject]@{ Number = 6; Message = "Verifying PyTorch + CUDA integration..." },
        [pscustomobject]@{ Number = 7; Message = "Installing HuggingFace Hub client..." },
        [pscustomobject]@{ Number = 8; Message = "Downloading models (this may take a while)..." },
        [pscustomobject]@{ Number = 9; Message = "Organizing model files..." }
    )

    $TotalSteps = $InstallationSteps.Count + 2 # +2 for Miniconda download/install
    $currentStep = 0

    # --- Step 1 & 2: Miniconda Installation ---
    if (-not (Test-Path $CondaExecutable)) {
        $currentStep++; Write-Progress-UI -Message "Downloading Miniconda..." -CurrentStep $currentStep -Total $TotalSteps
        $installerFullPath = Join-Path $ProjectRoot $InstallerName
        try {
            Start-BitsTransfer -Source $MinicondaUrl -Destination $installerFullPath -DisplayName "Downloading Miniconda" -Description "From anaconda.com"
        } catch {
            Write-Centered-Box -Content @("ERROR", "", "Miniconda download FAILED.", "Check your internet connection.") -ColorMap @{0="Red"; 2="Red"}
            Read-Host "Press Enter to exit"; Exit 1
        }
        
        $currentStep++; Write-Progress-UI -Message "Installing Miniconda (this may take a moment)..." -CurrentStep $currentStep -Total $TotalSteps
        Start-Process -FilePath $installerFullPath -ArgumentList "/InstallationType=JustMe /AddToPath=0 /RegisterPython=0 /NoRegistry=1 /S /D=$MinicondaFullPath" -Wait
        Remove-Item $installerFullPath -ErrorAction SilentlyContinue
    } else {
        $currentStep += 2 # Skip these two steps if already installed
    }

    if (-not (Test-Path $CondaExecutable)) {
        Write-Centered-Box -Content @("ERROR", "", "Miniconda installation FAILED or could not be verified.") -ColorMap @{0="Red"; 2="Red"}
        Read-Host "Press Enter to exit"; Exit 1
    }

    # --- Step 3 onwards: Execute batch tasks ---
    foreach ($step in $InstallationSteps) {
        Execute-Step -Message $step.Message -StepNumber $step.Number -CurrentStepCounter ([ref]$currentStep) -TotalSteps $TotalSteps
    }

    # --- Finalization ---
    Clear-Host
    $finalMessage = @(
        "INSTALLATION COMPLETE!", 
        "", 
        "You can now close this window and run the application."
    )
    Write-Centered-Box -Content $finalMessage -ColorMap @{ 0 = "Green"; 2 = "Green" }
    Read-Host "`n`n`nPress Enter to exit"

} finally {
    # Restore original console state
    $Host.UI.RawUI.ForegroundColor = $originalState.ForegroundColor
    $Host.UI.RawUI.BackgroundColor = $originalState.BackgroundColor
    $Host.UI.RawUI.WindowSize = $originalState.WindowSize
    $Host.UI.RawUI.BufferSize = $originalState.BufferSize
    $Host.UI.RawUI.WindowTitle = $originalTitle
    
    # Clean up log files
    Remove-Item "output.log" -ErrorAction SilentlyContinue
    Remove-Item "error.log" -ErrorAction SilentlyContinue
}