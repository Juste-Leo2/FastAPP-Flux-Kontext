@echo off
cd /d %~dp0
echo === Mise à jour du projet depuis GitHub ===

:: Exclure update.bat des modifications suivies par Git (si pas déjà fait)
git update-index --assume-unchanged update.bat

:: Lancer la mise à jour depuis la branche main
git pull origin main

echo === Terminé. Appuie sur une touche pour quitter. ===
pause
