# Guide de Déploiement - Django Appointment

Ce guide vous aidera à déployer votre application Django Appointment de différentes manières.

## 📋 Table des matières

1. [Déploiement avec Docker (Recommandé)](#déploiement-avec-docker)
2. [Déploiement local (Sans Docker)](#déploiement-local)
3. [Déploiement en production](#déploiement-en-production)
4. [Configuration requise](#configuration-requise)

---

## 🐳 Déploiement avec Docker

### Prérequis
- Docker installé
- Docker Compose installé

### Étapes de déploiement

#### 1. Créer le fichier `.env`

Créez un fichier `.env` à la racine du projet avec le contenu suivant :

```env
# Configuration Django
SECRET_KEY=votre-clé-secrète-générée
DEBUG=False
ALLOWED_HOSTS=votre-domaine.com,www.votre-domaine.com


# Configuration Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=votre-email@gmail.com
EMAIL_HOST_PASSWORD=votre-mot-de-passe-application

# Configuration Admin
ADMIN_NAME=Super Admin
ADMIN_EMAIL=admin@example.com

# Configuration Django Q
USE_DJANGO_Q=True
USE_DJANGO_Q_FOR_EMAILS=True

# Nom du site web
APPOINTMENT_WEBSITE_NAME=Maw3idi

# Configuration des réseaux sociaux (optionnel)
SOCIAL_MEDIA_FACEBOOK_URL=https://www.facebook.com/
SOCIAL_MEDIA_INSTAGRAM_URL=https://www.instagram.com/
SOCIAL_MEDIA_LINKEDIN_URL=https://www.linkedin.com/

# Configuration de paiement (optionnel)
PAYMENT_CARD_ENABLED=False
STRIPE_PUBLIC_KEY=
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
```

**⚠️ Important :** 
- Générez une SECRET_KEY sécurisée avec : `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
- Pour Gmail, utilisez un "Mot de passe d'application" et non votre mot de passe habituel

#### 2. Construire et lancer les conteneurs

```bash
# Construire et démarrer les conteneurs
docker-compose up -d --build

# Ou avec la nouvelle syntaxe
docker compose up -d --build
```

#### 3. Créer les migrations

```bash
# Créer les migrations
docker-compose exec web python manage.py makemigrations appointment

# Appliquer les migrations
docker-compose exec web python manage.py migrate
```

#### 4. Collecter les fichiers statiques

```bash
docker-compose exec web python manage.py collectstatic --noinput
```

#### 5. Créer un superutilisateur

```bash
docker-compose exec web python manage.py createsuperuser
```

#### 6. Vérifier que tout fonctionne

- Accédez à `http://localhost:8000` pour voir l'application
- Accédez à `http://localhost:8000/admin` pour l'interface d'administration

#### 7. Arrêter les conteneurs

```bash
docker-compose down
```

---

## 💻 Déploiement local (Sans Docker)

### Prérequis
- Python 3.8 ou supérieur
- pip
- Base de données (SQLite par défaut, ou PostgreSQL/MySQL pour la production)

### Étapes de déploiement

#### 1. Créer un environnement virtuel

**Windows :**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac :**
```bash
python3 -m venv venv
source venv/bin/activate
```

#### 2. Installer les dépendances

```bash
pip install -r requirements.txt
```

Si vous voulez utiliser Django Q :
```bash
pip install django-q2
```

#### 3. Créer le fichier `.env`

Créez un fichier `.env` à la racine du projet (voir le contenu dans la section Docker ci-dessus).

#### 4. Créer et appliquer les migrations

```bash
python manage.py makemigrations appointment
python manage.py migrate
```

#### 5. Collecter les fichiers statiques

```bash
python manage.py collectstatic
```

#### 6. Créer un superutilisateur

```bash
python manage.py createsuperuser
```

#### 7. Lancer le serveur de développement

```bash
python manage.py runserver
```

#### 8. Lancer Django Q (si activé)

Dans un terminal séparé :
```bash
python manage.py qcluster
```

---

## 🚀 Déploiement en production

### Options de déploiement

#### Option 1 : Déploiement avec Docker en production

1. **Modifier `docker-compose.yml` pour la production :**

Créez un fichier `docker-compose.prod.yml` :

```yaml
services:
  web:
    build:
      context: .
      dockerfile: Dockerfile
      args:
        USE_DJANGO_Q: "True"
    image: django_appointment_web_prod
    command: gunicorn appointments.wsgi:application --bind 0.0.0.0:8000 --workers 4
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    ports:
      - "8000:8000"
    env_file:
      - .env.prod
    depends_on:
      - db
      - redis

  qcluster:
    build:
      context: .
      dockerfile: Dockerfile
      args:
        USE_DJANGO_Q: "True"
    image: django_appointment_qcluster_prod
    command: python manage.py qcluster
    depends_on:
      - web
      - db
      - redis
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    env_file:
      - .env.prod

  db:
    image: postgres:15-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: appointment_db
      POSTGRES_USER: appointment_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    env_file:
      - .env.prod

  redis:
    image: redis:alpine
    volumes:
      - redis-data:/data

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - static_volume:/static
      - media_volume:/media
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - web

volumes:
  postgres_data:
  redis-data:
  static_volume:
  media_volume:
```

2. **Installer Gunicorn dans `requirements.txt` :**

Ajoutez `gunicorn` à votre fichier `requirements.txt`.

3. **Créer un fichier `nginx.conf` :**

```nginx
upstream django {
    server web:8000;
}

server {
    listen 80;
    server_name votre-domaine.com;

    location /static/ {
        alias /static/;
    }

    location /media/ {
        alias /media/;
    }

    location / {
        proxy_pass http://django;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
        proxy_redirect off;
    }
}
```

4. **Déployer :**

```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

#### Option 2 : Déploiement sur un serveur VPS

1. **Installer les dépendances système :**
```bash
sudo apt update
sudo apt install python3-pip python3-venv nginx postgresql redis-server
```

2. **Configurer PostgreSQL :**
```bash
sudo -u postgres psql
CREATE DATABASE appointment_db;
CREATE USER appointment_user WITH PASSWORD 'votre-mot-de-passe';
GRANT ALL PRIVILEGES ON DATABASE appointment_db TO appointment_user;
\q
```

3. **Modifier `appointments/settings.py` pour la production :**

```python
# Sécurité
DEBUG = False
SECRET_KEY = os.getenv('SECRET_KEY')  # Depuis .env
ALLOWED_HOSTS = ['votre-domaine.com', 'www.votre-domaine.com']

# Base de données PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'appointment_db'),
        'USER': os.getenv('DB_USER', 'appointment_user'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# Fichiers statiques
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

4. **Installer Gunicorn :**
```bash
pip install gunicorn
```

5. **Créer un service systemd pour Gunicorn :**

Créez `/etc/systemd/system/appointment.service` :

```ini
[Unit]
Description=Gunicorn daemon for Django Appointment
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/chemin/vers/votre/projet
ExecStart=/chemin/vers/venv/bin/gunicorn \
    --access-logfile - \
    --workers 4 \
    --bind unix:/run/gunicorn.sock \
    appointments.wsgi:application

[Install]
WantedBy=multi-user.target
```

6. **Créer un service systemd pour Django Q :**

Créez `/etc/systemd/system/appointment-qcluster.service` :

```ini
[Unit]
Description=Django Q Cluster for Django Appointment
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/chemin/vers/votre/projet
ExecStart=/chemin/vers/venv/bin/python manage.py qcluster
Restart=always

[Install]
WantedBy=multi-user.target
```

7. **Démarrer les services :**
```bash
sudo systemctl start appointment
sudo systemctl start appointment-qcluster
sudo systemctl enable appointment
sudo systemctl enable appointment-qcluster
```

8. **Configurer Nginx :**

Créez `/etc/nginx/sites-available/appointment` :

```nginx
server {
    listen 80;
    server_name votre-domaine.com www.votre-domaine.com;

    location /static/ {
        alias /chemin/vers/votre/projet/staticfiles/;
    }

    location /media/ {
        alias /chemin/vers/votre/projet/media/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
    }
}
```

Activez le site :
```bash
sudo ln -s /etc/nginx/sites-available/appointment /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### Option 3 : Déploiement sur Heroku

1. **Installer Heroku CLI**

2. **Créer un fichier `Procfile` :**
```
web: gunicorn appointments.wsgi:application --bind 0.0.0.0:$PORT
worker: python manage.py qcluster
```

3. **Créer un fichier `runtime.txt` :**
```
python-3.10.0
```

4. **Déployer :**
```bash
heroku create votre-app-name
heroku addons:create heroku-postgresql:hobby-dev
heroku addons:create heroku-redis:hobby-dev
git push heroku main
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

---

## ⚙️ Configuration requise

### Variables d'environnement essentielles

| Variable | Description | Exemple |
|----------|-------------|---------|
| `SECRET_KEY` | Clé secrète Django (OBLIGATOIRE) | Générée automatiquement |
| `DEBUG` | Mode debug (False en production) | `False` |
| `ALLOWED_HOSTS` | Domaines autorisés | `votre-domaine.com` |
| `EMAIL_HOST_USER` | Email pour l'envoi | `noreply@example.com` |
| `EMAIL_HOST_PASSWORD` | Mot de passe email | Mot de passe d'application |
| `USE_DJANGO_Q` | Activer Django Q | `True` |

### Checklist de sécurité pour la production

- [ ] `DEBUG = False` dans les settings
- [ ] `SECRET_KEY` unique et sécurisée
- [ ] `ALLOWED_HOSTS` configuré correctement
- [ ] Base de données sécurisée (PostgreSQL recommandé)
- [ ] HTTPS activé (certificat SSL)
- [ ] Fichier `.env` non versionné (dans `.gitignore`)
- [ ] Mots de passe forts pour la base de données
- [ ] Sauvegardes automatiques configurées
- [ ] Logs configurés et surveillés

---

## 🔧 Dépannage

### Problèmes courants

#### Le serveur ne démarre pas
- Vérifiez que le port 8000 n'est pas utilisé : `netstat -ano | findstr :8000` (Windows) ou `lsof -i :8000` (Linux/Mac)
- Vérifiez les logs : `docker-compose logs web`

#### Les emails ne sont pas envoyés
- Vérifiez la configuration SMTP dans `.env`
- Pour Gmail, utilisez un "Mot de passe d'application"
- Vérifiez les logs Django pour les erreurs

#### Erreurs de migrations
- Vérifiez que la base de données est accessible
- Exécutez : `python manage.py migrate --run-syncdb`

#### Fichiers statiques non chargés
- Exécutez : `python manage.py collectstatic --noinput`
- Vérifiez la configuration `STATIC_ROOT` et `STATIC_URL`

---

## 📞 Support

Pour toute question ou problème :
- Consultez la documentation : `docs/README.md`
- Vérifiez les issues GitHub
- Consultez les logs : `docker-compose logs` ou les logs système

---

**Bon déploiement ! 🚀**

