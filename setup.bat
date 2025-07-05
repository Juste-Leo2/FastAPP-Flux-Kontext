@echo off
setlocal

title Fast Flux Kontext Installer Launch

echo Launching the PowerShell installation script...
echo A new interface will appear. Please wait.
echo.

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0src\setup.ps1"

echo.
echo The installation script has completed.

endlocal
