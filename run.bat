@echo off
setlocal

powershell.exe -WindowStyle Hidden -NoProfile -ExecutionPolicy Bypass -File "%~dp0src\run.ps1"

endlocal