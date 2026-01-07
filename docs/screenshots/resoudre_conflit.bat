@echo off
REM Script pour résoudre le conflit de serveur Django

echo ============================================================
echo Resolution du conflit de serveur Django
echo ============================================================
echo.

cd /d "%~dp0"
python resoudre_conflit_serveur.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Le serveur correct est maintenant demarre!
    echo Laissez la console du serveur ouverte.
) else (
    echo.
    echo Il y a encore un probleme.
    echo Verifiez manuellement les processus.
)

pause

