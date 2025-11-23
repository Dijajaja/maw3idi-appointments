# Guide d'Installation - Système de Gestion de Rendez-vous

Ce guide vous aidera à installer et configurer le système de gestion de rendez-vous sur votre machine.

## Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)
- Git (pour cloner le projet)

## Installation

### 1. Cloner le projet

```bash
git clone <URL_DU_REPO_GITHUB>
cd django-appointment
```

### 2. Créer un environnement virtuel

**Sur Windows :**
```bash
python -m venv venv
venv\Scripts\activate
```

**Sur Linux/Mac :**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

Si vous voulez aussi installer les dépendances de test :
```bash
pip install -r requirements-test.txt
```

### 4. Configuration de l'environnement

1. Copiez le fichier `.env.example` vers `.env` :
   ```bash
   cp .env.example .env
   ```

2. Éditez le fichier `.env` et configurez les variables suivantes :
   - `SECRET_KEY` : Générez une clé secrète Django (voir ci-dessous)
   - `EMAIL_HOST_USER` : Votre adresse email pour l'envoi de notifications
   - `EMAIL_HOST_PASSWORD` : Le mot de passe de votre email
   - `APPOINTMENT_WEBSITE_NAME` : Le nom de votre site web

3. **Générer une SECRET_KEY Django :**
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```
   Copiez la clé générée et collez-la dans votre fichier `.env` pour `SECRET_KEY`.

### 5. Configuration de la base de données

Le projet utilise SQLite par défaut (pour le développement). Pour utiliser PostgreSQL ou MySQL, modifiez `appointments/settings.py`.

### 6. Créer les migrations et appliquer

```bash
python manage.py makemigrations appointment
python manage.py migrate
```

### 7. Créer un superutilisateur

```bash
python manage.py createsuperuser
```

Suivez les instructions pour créer votre compte administrateur.

### 8. Collecter les fichiers statiques

```bash
python manage.py collectstatic
```

### 9. Lancer le serveur de développement

```bash
python manage.py runserver
```

Le site sera accessible à l'adresse : `http://127.0.0.1:8000/`

## Configuration Email (Optionnel mais Recommandé)

Pour que les notifications par email fonctionnent :

1. **Gmail :**
   - Activez l'authentification à deux facteurs
   - Générez un "Mot de passe d'application"
   - Utilisez ce mot de passe dans `EMAIL_HOST_PASSWORD`

2. **Autres fournisseurs :**
   - Consultez la documentation de votre fournisseur email pour les paramètres SMTP

## Configuration Django Q (Optionnel)

Pour activer les rappels automatiques par email :

1. Installez django-q2 :
   ```bash
   pip install django-q2
   ```

2. Ajoutez `USE_DJANGO_Q=True` dans votre fichier `.env`

3. Dans un terminal séparé, lancez le cluster Django Q :
   ```bash
   python manage.py qcluster
   ```

## Première utilisation

1. Accédez à l'interface d'administration : `http://127.0.0.1:8000/admin/`
2. Connectez-vous avec votre compte superutilisateur
3. Créez au moins un **Service** dans l'interface admin
4. Créez un **StaffMember** (membre du personnel) si nécessaire
5. Configurez les **WorkingHours** (heures de travail) pour chaque membre du personnel

## Accès aux pages principales

- **Page d'accueil :** `http://127.0.0.1:8000/fr/`
- **Interface admin :** `http://127.0.0.1:8000/admin/`
- **Dashboard admin :** `http://127.0.0.1:8000/fr/admin-dashboard/`
- **Mes rendez-vous :** `http://127.0.0.1:8000/fr/my-appointments/`
- **Calendrier :** `http://127.0.0.1:8000/fr/calendar/`

## Dépannage

### Erreur : "No module named 'appointment'"
- Assurez-vous d'être dans le bon répertoire
- Vérifiez que l'environnement virtuel est activé

### Erreur : "ModuleNotFoundError"
- Réinstallez les dépendances : `pip install -r requirements.txt`

### Erreur : "Database does not exist"
- Exécutez les migrations : `python manage.py migrate`

### Les emails ne sont pas envoyés
- Vérifiez votre configuration dans `.env`
- Vérifiez les paramètres SMTP de votre fournisseur email
- Consultez les logs Django pour plus de détails

## Support

Pour toute question ou problème, consultez :
- Le fichier `RAPPORT_PROJET.md` pour une vue d'ensemble du projet
- La documentation Django : https://docs.djangoproject.com/
- Les issues GitHub du projet

## Notes importantes

⚠️ **Sécurité :**
- Ne commitez JAMAIS le fichier `.env` sur GitHub
- Changez la `SECRET_KEY` en production
- Utilisez `DEBUG=False` en production

⚠️ **Production :**
- Ce guide est pour le développement local
- Pour la production, consultez la documentation Django sur le déploiement
- Utilisez un serveur web (Nginx, Apache) et un serveur WSGI (Gunicorn, uWSGI)

