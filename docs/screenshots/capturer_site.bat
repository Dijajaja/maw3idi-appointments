@echo off
REM Script batch pour capturer les pages du site web

echo ============================================================
echo Capture des pages du site web
echo ============================================================
echo.

cd /d "%~dp0"
python capture_site.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Capture terminee avec succes!
    echo Les screenshots sont disponibles dans ce dossier.
) else (
    echo.
    echo Erreur lors de la capture.
    echo.
    echo Verifiez que:
    echo   1. Le serveur Django est demarre (python manage.py runserver)
    echo   2. Playwright est installe (pip install playwright)
    echo   3. Chromium est installe (playwright install chromium)
)

pause

