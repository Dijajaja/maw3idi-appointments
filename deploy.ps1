# Script de déploiement pour Windows PowerShell
# Ce script vous aide a deployer l'application Django Appointment

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Deploiement Django Appointment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verifier si Docker est installe
$dockerInstalled = Get-Command docker -ErrorAction SilentlyContinue
$dockerComposeInstalled = Get-Command docker-compose -ErrorAction SilentlyContinue

if ($dockerInstalled) {
    Write-Host "[OK] Docker est installe" -ForegroundColor Green
} else {
    Write-Host "[ATTENTION] Docker n'est pas installe." -ForegroundColor Yellow
    Write-Host "   L'option 1 (Docker) ne sera pas disponible." -ForegroundColor Yellow
    Write-Host "   Telechargez Docker Desktop depuis: https://www.docker.com/products/docker-desktop" -ForegroundColor Cyan
    Write-Host ""
}

# Verifier si le fichier .env existe
if (-not (Test-Path ".env")) {
    Write-Host "[ATTENTION] Le fichier .env n'existe pas. Creation a partir de ENV_EXAMPLE.txt..." -ForegroundColor Yellow
    
    if (Test-Path "ENV_EXAMPLE.txt") {
        Copy-Item "ENV_EXAMPLE.txt" ".env"
        Write-Host "[OK] Fichier .env cree. Veuillez le modifier avec vos parametres." -ForegroundColor Green
        Write-Host "  [IMPORTANT] Modifiez SECRET_KEY, EMAIL_HOST_USER, etc. dans .env" -ForegroundColor Yellow
    } else {
        Write-Host "[ERREUR] ENV_EXAMPLE.txt n'existe pas. Creation d'un fichier .env basique..." -ForegroundColor Red
        
        # Generer une SECRET_KEY
        $secretKey = python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
        
        $envContent = @"
# Configuration Django
SECRET_KEY=$secretKey
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,*

# Configuration Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-email-password

# Configuration Admin
ADMIN_NAME=Super Admin
ADMIN_EMAIL=admin@example.com

# Configuration Django Q
USE_DJANGO_Q=True
USE_DJANGO_Q_FOR_EMAILS=True

# Nom du site web
APPOINTMENT_WEBSITE_NAME=Maw3idi
"@
        Set-Content -Path ".env" -Value $envContent -Encoding UTF8
        Write-Host "[OK] Fichier .env cree avec une SECRET_KEY generee." -ForegroundColor Green
        Write-Host "  [IMPORTANT] Modifiez les parametres email dans .env" -ForegroundColor Yellow
    }
} else {
    Write-Host "[OK] Fichier .env existe deja" -ForegroundColor Green
}

Write-Host ""
Write-Host "Choisissez une option de deploiement:" -ForegroundColor Cyan
if ($dockerInstalled) {
    Write-Host "1. Deploiement avec Docker (Recommandé)" -ForegroundColor White
} else {
    Write-Host "1. Deploiement avec Docker (NON DISPONIBLE - Docker requis)" -ForegroundColor DarkGray
}
Write-Host "2. Deploiement local (Sans Docker)" -ForegroundColor White
if ($dockerInstalled) {
    Write-Host "3. Arreter les conteneurs Docker" -ForegroundColor White
    Write-Host "4. Voir les logs Docker" -ForegroundColor White
} else {
    Write-Host "3. Arreter les conteneurs Docker (NON DISPONIBLE)" -ForegroundColor DarkGray
    Write-Host "4. Voir les logs Docker (NON DISPONIBLE)" -ForegroundColor DarkGray
}
Write-Host "5. Quitter" -ForegroundColor White
Write-Host ""

$choice = Read-Host "Votre choix (1-5)"

switch ($choice) {
    "1" {
        if (-not $dockerInstalled) {
            Write-Host ""
            Write-Host "[ERREUR] Docker n'est pas installe." -ForegroundColor Red
            Write-Host "   Veuillez installer Docker Desktop ou choisir l'option 2 (Deploiement local)." -ForegroundColor Yellow
            Write-Host "   Telechargez Docker Desktop depuis: https://www.docker.com/products/docker-desktop" -ForegroundColor Cyan
            break
        }
        
        Write-Host ""
        Write-Host "[DOCKER] Deploiement avec Docker..." -ForegroundColor Cyan
        
        # Construire et demarrer
        Write-Host "[ETAPE] Construction des images Docker..." -ForegroundColor Yellow
        docker-compose up -d --build
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[OK] Conteneurs demarres" -ForegroundColor Green
            
            # Attendre que le serveur soit pret
            Write-Host "[ATTENTE] Demarrage du serveur..." -ForegroundColor Yellow
            Start-Sleep -Seconds 5
            
            # Creer les migrations
            Write-Host "[ETAPE] Creation des migrations..." -ForegroundColor Yellow
            docker-compose exec -T web python manage.py makemigrations appointment
            
            # Appliquer les migrations
            Write-Host "[ETAPE] Application des migrations..." -ForegroundColor Yellow
            docker-compose exec -T web python manage.py migrate
            
            # Collecter les fichiers statiques
            Write-Host "[ETAPE] Collecte des fichiers statiques..." -ForegroundColor Yellow
            docker-compose exec -T web python manage.py collectstatic --noinput
            
            Write-Host ""
            Write-Host "[SUCCES] Deploiement termine!" -ForegroundColor Green
            Write-Host ""
            Write-Host "Application disponible sur: http://localhost:8000" -ForegroundColor Cyan
            Write-Host "Interface admin: http://localhost:8000/admin" -ForegroundColor Cyan
            Write-Host ""
            Write-Host "Pour creer un superutilisateur, executez:" -ForegroundColor Yellow
            Write-Host "   docker-compose exec web python manage.py createsuperuser" -ForegroundColor White
        } else {
            Write-Host "[ERREUR] Erreur lors du deploiement Docker" -ForegroundColor Red
        }
    }
    "2" {
        Write-Host ""
        Write-Host "[LOCAL] Deploiement local..." -ForegroundColor Cyan
        
        # Verifier si Python est installe
        $pythonInstalled = Get-Command python -ErrorAction SilentlyContinue
        if (-not $pythonInstalled) {
            Write-Host "[ERREUR] Python n'est pas installe ou n'est pas dans le PATH" -ForegroundColor Red
            exit 1
        }
        
        # Verifier si l'environnement virtuel existe
        if (-not (Test-Path "venv")) {
            Write-Host "[ETAPE] Creation de l'environnement virtuel..." -ForegroundColor Yellow
            python -m venv venv
        }
        
        Write-Host "[ETAPE] Activation de l'environnement virtuel..." -ForegroundColor Yellow
        & .\venv\Scripts\Activate.ps1
        
        Write-Host "[ETAPE] Installation des dependances..." -ForegroundColor Yellow
        pip install -r requirements.txt
        
        Write-Host "[ETAPE] Creation des migrations..." -ForegroundColor Yellow
        python manage.py makemigrations appointment
        
        Write-Host "[ETAPE] Application des migrations..." -ForegroundColor Yellow
        python manage.py migrate
        
        Write-Host "[ETAPE] Collecte des fichiers statiques..." -ForegroundColor Yellow
        $collectResult = python manage.py collectstatic --noinput 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[ATTENTION] Erreur lors de la collecte des fichiers statiques." -ForegroundColor Yellow
            Write-Host "   Cela peut etre normal si STATIC_ROOT n'est pas configure." -ForegroundColor Yellow
            Write-Host "   Verifiez le fichier appointments/settings.py" -ForegroundColor Yellow
        } else {
            Write-Host "[OK] Fichiers statiques collectes" -ForegroundColor Green
        }
        
        Write-Host ""
        Write-Host "[SUCCES] Configuration terminee!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Pour demarrer le serveur, executez:" -ForegroundColor Yellow
        Write-Host "   python manage.py runserver" -ForegroundColor White
        Write-Host ""
        Write-Host "Pour creer un superutilisateur, executez:" -ForegroundColor Yellow
        Write-Host "   python manage.py createsuperuser" -ForegroundColor White
        Write-Host ""
        Write-Host "Pour demarrer Django Q (si active), executez dans un autre terminal:" -ForegroundColor Yellow
        Write-Host "   python manage.py qcluster" -ForegroundColor White
    }
    "3" {
        if (-not $dockerInstalled) {
            Write-Host ""
            Write-Host "[ERREUR] Docker n'est pas installe." -ForegroundColor Red
            break
        }
        Write-Host ""
        Write-Host "[ETAPE] Arret des conteneurs Docker..." -ForegroundColor Yellow
        docker-compose down
        Write-Host "[OK] Conteneurs arretes" -ForegroundColor Green
    }
    "4" {
        if (-not $dockerInstalled) {
            Write-Host ""
            Write-Host "[ERREUR] Docker n'est pas installe." -ForegroundColor Red
            break
        }
        Write-Host ""
        Write-Host "[LOGS] Logs Docker (Ctrl+C pour quitter)..." -ForegroundColor Yellow
        docker-compose logs -f
    }
    "5" {
        Write-Host "Au revoir!" -ForegroundColor Cyan
        exit 0
    }
    default {
        Write-Host "[ERREUR] Choix invalide" -ForegroundColor Red
    }
}

