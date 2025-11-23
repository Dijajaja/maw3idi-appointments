# Script PowerShell pour préparer le projet pour GitHub
# Ce script vérifie les fichiers sensibles et prépare le projet

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Préparation du projet pour GitHub" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier si .env existe et n'est pas dans Git
Write-Host "Vérification des fichiers sensibles..." -ForegroundColor Yellow
if (Test-Path ".env") {
    $envInGit = git ls-files .env 2>$null
    if ($envInGit) {
        Write-Host "⚠️  ATTENTION: .env est suivi par Git!" -ForegroundColor Red
        Write-Host "   Exécutez: git rm --cached .env" -ForegroundColor Yellow
    } else {
        Write-Host "✅ .env n'est pas dans Git (correct)" -ForegroundColor Green
    }
} else {
    Write-Host "ℹ️  .env n'existe pas encore (normal)" -ForegroundColor Blue
}

# Vérifier si db.sqlite3 existe et n'est pas dans Git
if (Test-Path "db.sqlite3") {
    $dbInGit = git ls-files db.sqlite3 2>$null
    if ($dbInGit) {
        Write-Host "⚠️  ATTENTION: db.sqlite3 est suivi par Git!" -ForegroundColor Red
        Write-Host "   Exécutez: git rm --cached db.sqlite3" -ForegroundColor Yellow
    } else {
        Write-Host "✅ db.sqlite3 n'est pas dans Git (correct)" -ForegroundColor Green
    }
} else {
    Write-Host "ℹ️  db.sqlite3 n'existe pas (normal)" -ForegroundColor Blue
}

# Créer .env.example si ENV_EXAMPLE.txt existe
if (Test-Path "ENV_EXAMPLE.txt") {
    if (-not (Test-Path ".env.example")) {
        Copy-Item "ENV_EXAMPLE.txt" ".env.example"
        Write-Host "✅ .env.example créé depuis ENV_EXAMPLE.txt" -ForegroundColor Green
    } else {
        Write-Host "ℹ️  .env.example existe déjà" -ForegroundColor Blue
    }
}

Write-Host ""
Write-Host "Vérification de l'état Git..." -ForegroundColor Yellow
git status --short

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Prochaines étapes:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Vérifiez les fichiers ci-dessus" -ForegroundColor White
Write-Host "2. Ajoutez les fichiers: git add ." -ForegroundColor White
Write-Host "3. Créez un commit: git commit -m 'Votre message'" -ForegroundColor White
Write-Host "4. Poussez sur GitHub: git push origin main" -ForegroundColor White
Write-Host ""
Write-Host "Consultez GUIDE_GITHUB.md pour plus de détails" -ForegroundColor Cyan
Write-Host ""

