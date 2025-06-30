@echo off
cd /d %~dp0
setlocal enabledelayedexpansion

echo ================================
echo 🔧 Initialisation du projet Git
echo ================================

:: Vérifie si le dossier est déjà un dépôt git
if exist ".git" (
    echo Ce dossier est déjà un dépôt Git.
    goto FIN
)

:: Initialise le dépôt
git init

:: Demande l'URL du dépôt distant
set /p repo_url="Entre l'URL de ton dépôt GitHub (ex: https://github.com/ton-user/ton-repo.git) : "

:: Lier le dépôt distant
git remote add origin %repo_url%

:: Ajouter tous les fichiers
git add .

:: Crée un premier commit
git commit -m "Initial commit"

:: Renomme la branche principale en main
git branch -M main

:: Pousse sur GitHub
git push -u origin main

:: Empêche Git de suivre update.bat et ce script
git update-index --assume-unchanged update.bat
git update-index --assume-unchanged setup_github.bat

echo.
echo ✅ Dépôt configuré avec succès !
echo.
pause
goto :eof

:FIN
echo.
echo 🚫 Ce projet est déjà lié à Git.
pause
