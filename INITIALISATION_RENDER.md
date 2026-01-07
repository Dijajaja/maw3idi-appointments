# 🔧 Comment Initialiser la Base de Données sur Render

## 📍 Où Trouver le Shell dans Render

Le Shell n'est disponible que sur les **plans payants**. Sur le plan Free, vous devez utiliser une autre méthode.

## ✅ Solution : Utiliser les Commandes de Build

### Méthode 1 : Ajouter les Commandes dans le Build Command

Modifiez le **Build Command** dans Render pour inclure les migrations :

**Build Command actuel :**
```
pip install -r requirements.txt && python manage.py collectstatic --noinput
```

**Build Command modifié :**
```
pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate --noinput
```

⚠️ **Note :** Cette méthode exécute les migrations à chaque déploiement, ce qui est généralement OK.

### Méthode 2 : Créer un Script de Déploiement (Recommandé)

Créez un fichier `build.sh` à la racine du projet :

```bash
#!/usr/bin/env bash
# build.sh

set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate --noinput
```

Puis modifiez le **Build Command** dans Render :
```
chmod +x build.sh && ./build.sh
```

### Méthode 3 : Utiliser Render CLI (Si Installé)

Si vous avez Render CLI installé localement :

```bash
render run python manage.py migrate
render run python manage.py createsuperuser
```

## 🎯 Solution Simple : Modifier le Build Command

**Étape 1 :** Dans le dashboard Render, ouvrez votre service "maw3idi"

**Étape 2 :** Allez dans l'onglet **"Settings"**

**Étape 3 :** Trouvez la section **"Build Command"**

**Étape 4 :** Modifiez pour :
```
pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate --noinput
```

**Étape 5 :** Cliquez sur **"Save Changes"**

**Étape 6 :** Cliquez sur **"Manual Deploy"** → **"Deploy latest commit"**

## 👤 Créer un Superutilisateur

Pour créer un superutilisateur sans Shell, vous avez plusieurs options :

### Option 1 : Créer via Django Management Command (Recommandé)

Créez un fichier `create_superuser.py` à la racine :

```python
# create_superuser.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appointments.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Créer le superutilisateur
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        username='admin',
        email=os.getenv('ADMIN_EMAIL', 'admin@example.com'),
        password=os.getenv('ADMIN_PASSWORD', 'changeme123')
    )
    print("Superutilisateur créé avec succès!")
else:
    print("Le superutilisateur existe déjà.")
```

Puis ajoutez dans le **Build Command** :
```
pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate --noinput && python create_superuser.py
```

**⚠️ Important :** Ajoutez `ADMIN_PASSWORD` dans les variables d'environnement Render.

### Option 2 : Utiliser un Script de Déploiement Automatique

Créez `deploy.sh` :

```bash
#!/usr/bin/env bash
set -o errexit

echo "Installation des dépendances..."
pip install -r requirements.txt

echo "Collecte des fichiers statiques..."
python manage.py collectstatic --noinput

echo "Application des migrations..."
python manage.py migrate --noinput

echo "Création du superutilisateur (si nécessaire)..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
import os

User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        username='admin',
        email=os.getenv('ADMIN_EMAIL', 'admin@example.com'),
        password=os.getenv('ADMIN_PASSWORD', 'changeme123')
    )
    print("Superutilisateur créé!")
else:
    print("Superutilisateur existe déjà.")
EOF
```

Puis dans Render, **Build Command** :
```
chmod +x deploy.sh && ./deploy.sh
```

## 🚀 Solution la Plus Simple (Recommandée)

**Modifiez simplement le Build Command dans Render :**

```
pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate --noinput
```

Cela exécutera les migrations à chaque déploiement.

**Pour le superutilisateur :** Vous pouvez le créer manuellement la première fois en accédant à votre site et en utilisant la commande Django, ou utilisez l'Option 1 ci-dessus.

## 📝 Variables d'Environnement à Ajouter

N'oubliez pas d'ajouter dans Render :

```
ADMIN_PASSWORD=votre-mot-de-passe-admin
```

(Utilisé uniquement si vous utilisez le script de création automatique)

## ✅ Checklist

- [ ] Build Command modifié pour inclure `python manage.py migrate --noinput`
- [ ] Variables d'environnement configurées
- [ ] Redéploiement effectué
- [ ] Migrations appliquées (vérifier les logs)
- [ ] Superutilisateur créé (via script ou manuellement)

**Votre application sera prête après le redéploiement ! 🎉**

