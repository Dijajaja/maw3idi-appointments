@echo off
REM Script pour installer les dépendances nécessaires aux captures d'écran

echo ============================================================
echo Installation des dependances pour les captures d'ecran
echo ============================================================
echo.

echo Installation de Playwright...
pip install playwright

if %ERRORLEVEL% NEQ 0 (
    echo Erreur lors de l'installation de Playwright.
    pause
    exit /b 1
)

echo.
echo Installation du navigateur Chromium pour Playwright...
python -m playwright install chromium

if %ERRORLEVEL% NEQ 0 (
    echo Erreur lors de l'installation de Chromium.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo Installation terminee avec succes!
echo ============================================================
echo.
echo Vous pouvez maintenant executer: python capture_site.py
echo.

pause

