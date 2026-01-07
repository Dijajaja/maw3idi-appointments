# Script de demarrage pour Django Appointment

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Demarrage Django Appointment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Activer l'environnement virtuel
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "[ETAPE] Activation de l'environnement virtuel..." -ForegroundColor Yellow
    & .\venv\Scripts\Activate.ps1
} else {
    Write-Host "[ATTENTION] Environnement virtuel non trouve. Creation..." -ForegroundColor Yellow
    python -m venv venv
    & .\venv\Scripts\Activate.ps1
    pip install -r requirements.txt
}

Write-Host ""
Write-Host "[INFO] Application disponible sur: http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "[INFO] Interface admin: http://127.0.0.1:8000/admin" -ForegroundColor Green
Write-Host ""
Write-Host "[ASTUCE] Pour arreter le serveur, appuyez sur Ctrl+C" -ForegroundColor Yellow
Write-Host ""

# Demarrer le serveur
python manage.py runserver

