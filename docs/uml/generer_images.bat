@echo off
REM Script batch pour générer les images PNG à partir des fichiers PlantUML
REM Utilisation: double-cliquer sur ce fichier ou exécuter depuis la ligne de commande

echo ============================================================
echo Generation des diagrammes UML en images PNG
echo ============================================================
echo.

cd /d "%~dp0"
python generate_images.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Generation terminee avec succes!
    echo Les images PNG sont disponibles dans ce dossier.
) else (
    echo.
    echo Erreur lors de la generation.
    echo Assurez-vous que Python est installe et accessible.
)

pause

