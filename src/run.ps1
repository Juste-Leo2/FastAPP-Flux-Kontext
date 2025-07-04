# =================================================================
# ==            APPLICATION LAUNCHER FOR CHROMA-GGUF             ==
# =================================================================
#
# This script is designed to be run silently. Its only purpose is to:
# 1. Set up the Conda environment path.
# 2. Launch the main Python GUI application using pythonw.exe to suppress the console.
# 3. Exit immediately, leaving the GUI running on its own.
#

# --- Define Paths ---
# Get the project root directory (the parent of 'src')
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

# Construct paths to Miniconda and the main Python script
$MinicondaFullPath = Join-Path $ProjectRoot "miniconda"
$PythonScriptPath = Join-Path $ProjectRoot "src\main.py"

# --- Pre-launch Checks ---
if (-not (Test-Path $MinicondaFullPath)) {
    Write-Error "Miniconda directory not found at '$MinicondaFullPath'. Please run setup.bat first."
    Exit 1
}
if (-not (Test-Path $PythonScriptPath)) {
    Write-Error "Main application script not found at '$PythonScriptPath'."
    Exit 1
}

# --- Environment Activation ---
$env:Path = "$MinicondaFullPath;$MinicondaFullPath\Scripts;$MinicondaFullPath\Library\bin;$env:Path"

# --- Application Launch ---
# THIS IS THE KEY CHANGE: Use "pythonw.exe" to launch the GUI without any console window.
Start-Process -FilePath "pythonw.exe" -ArgumentList $PythonScriptPath

# The script ends here. The GUI is now running independently.