@echo off
REM Script pour arrêter tous les serveurs Django sur le port 8000

echo ============================================================
echo Arret de tous les serveurs Django sur le port 8000
echo ============================================================
echo.

echo Recherche des processus utilisant le port 8000...
netstat -ano | findstr :8000

echo.
echo Arret de tous les processus Python...
taskkill /F /IM python.exe 2>nul

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✓ Tous les processus Python ont ete arretes.
    echo.
    echo Vous pouvez maintenant demarrer le bon serveur avec:
    echo   python manage.py runserver
) else (
    echo.
    echo ⚠️  Aucun processus Python trouve ou erreur lors de l'arret.
)

echo.
pause

