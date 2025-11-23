# Script de vérification des assets Black Dashboard
# Exécutez ce script pour vérifier si les assets sont correctement installés

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Vérification des assets Black Dashboard" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$assetsPath = "appointment\static\assets"
$requiredFiles = @(
    # CSS
    "css\black-dashboard.css",
    "css\nucleo-icons.css",
    # JS Core
    "js\core\jquery.min.js",
    "js\core\popper.min.js",
    "js\core\bootstrap.min.js",
    # JS Plugins
    "js\plugins\perfect-scrollbar.jquery.min.js",
    "js\plugins\chartjs.min.js",
    "js\plugins\bootstrap-notify.js",
    # JS Principaux
    "js\black-dashboard.min.js",
    "js\demos.js",
    # Demo
    "demo\demo.css",
    "demo\demo.js",
    # Images (optionnel mais recommandé)
    "img\favicon.png"
)

$allOk = $true

if (Test-Path $assetsPath) {
    Write-Host "✓ Le dossier assets existe" -ForegroundColor Green
    Write-Host ""
    
    foreach ($file in $requiredFiles) {
        $fullPath = Join-Path $assetsPath $file
        if (Test-Path $fullPath) {
            Write-Host "✓ $file" -ForegroundColor Green
        } else {
            Write-Host "✗ $file - MANQUANT" -ForegroundColor Red
            $allOk = $false
        }
    }
    
    Write-Host ""
    if ($allOk) {
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "Tous les fichiers requis sont présents !" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
    } else {
        Write-Host "========================================" -ForegroundColor Red
        Write-Host "Certains fichiers sont manquants." -ForegroundColor Red
        Write-Host "Veuillez copier le dossier 'assets' complet" -ForegroundColor Yellow
        Write-Host "depuis le template Black Dashboard dans:" -ForegroundColor Yellow
        Write-Host "appointment\static\" -ForegroundColor Yellow
        Write-Host "========================================" -ForegroundColor Red
    }
} else {
    Write-Host "✗ Le dossier assets n'existe pas" -ForegroundColor Red
    Write-Host ""
    Write-Host "ACTION REQUISE:" -ForegroundColor Yellow
    Write-Host "1. Trouvez le dossier 'assets' dans le template Black Dashboard décompressé" -ForegroundColor Yellow
    Write-Host "2. Copiez-le dans: appointment\static\assets" -ForegroundColor Yellow
    Write-Host "3. Relancez ce script pour vérifier" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Structure attendue:" -ForegroundColor Cyan
    Write-Host "  appointment\static\assets\" -ForegroundColor Cyan
    Write-Host "    ├── css\" -ForegroundColor Cyan
    Write-Host "    ├── js\" -ForegroundColor Cyan
    Write-Host "    ├── img\" -ForegroundColor Cyan
    Write-Host "    └── demo\" -ForegroundColor Cyan
}

Write-Host ""

