# Script PowerShell pour preparer le projet pour GitHub
# Ce script verifie les fichiers sensibles et prepare le projet

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Preparation du projet pour GitHub" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verifier si .env existe et n'est pas dans Git
Write-Host "Verification des fichiers sensibles..." -ForegroundColor Yellow
if (Test-Path ".env") {
    $envInGit = git ls-files .env 2>$null
    if ($envInGit) {
        Write-Host "ATTENTION: .env est suivi par Git!" -ForegroundColor Red
        Write-Host "   Executez: git rm --cached .env" -ForegroundColor Yellow
    } else {
        Write-Host "OK: .env n'est pas dans Git (correct)" -ForegroundColor Green
    }
} else {
    Write-Host "INFO: .env n'existe pas encore (normal)" -ForegroundColor Blue
}

# Verifier si db.sqlite3 existe et n'est pas dans Git
if (Test-Path "db.sqlite3") {
    $dbInGit = git ls-files db.sqlite3 2>$null
    if ($dbInGit) {
        Write-Host "ATTENTION: db.sqlite3 est suivi par Git!" -ForegroundColor Red
        Write-Host "   Executez: git rm --cached db.sqlite3" -ForegroundColor Yellow
    } else {
        Write-Host "OK: db.sqlite3 n'est pas dans Git (correct)" -ForegroundColor Green
    }
} else {
    Write-Host "INFO: db.sqlite3 n'existe pas (normal)" -ForegroundColor Blue
}

# Creer .env.example si ENV_EXAMPLE.txt existe
if (Test-Path "ENV_EXAMPLE.txt") {
    if (-not (Test-Path ".env.example")) {
        Copy-Item "ENV_EXAMPLE.txt" ".env.example"
        Write-Host "OK: .env.example cree depuis ENV_EXAMPLE.txt" -ForegroundColor Green
    } else {
        Write-Host "INFO: .env.example existe deja" -ForegroundColor Blue
    }
}

Write-Host ""
Write-Host "Verification de l'etat Git..." -ForegroundColor Yellow
git status --short

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Prochaines etapes:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Verifiez les fichiers ci-dessus" -ForegroundColor White
Write-Host "2. Ajoutez les fichiers: git add ." -ForegroundColor White
Write-Host "3. Creez un commit: git commit -m 'Votre message'" -ForegroundColor White
Write-Host "4. Poussez sur GitHub: git push origin main" -ForegroundColor White
Write-Host ""
Write-Host "Consultez GUIDE_GITHUB.md pour plus de details" -ForegroundColor Cyan
Write-Host ""
