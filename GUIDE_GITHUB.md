# Guide pour Partager le Projet sur GitHub

Ce guide vous explique comment pousser votre projet sur GitHub et le partager avec votre ami.

## Étape 1 : Préparer le projet

### Vérifier les fichiers sensibles

Avant de pousser sur GitHub, assurez-vous que les fichiers suivants ne sont PAS commités :
- `.env` (fichier de configuration avec mots de passe)
- `db.sqlite3` (base de données locale)
- `*.pyc` (fichiers compilés Python)
- `__pycache__/` (cache Python)

Ces fichiers sont déjà dans `.gitignore`, mais vérifiez quand même.

### Créer le fichier .env.example

Si vous avez un fichier `.env`, créez un fichier `.env.example` avec les mêmes variables mais sans les valeurs sensibles :

```bash
# Sur Windows PowerShell
Copy-Item ENV_EXAMPLE.txt .env.example
```

Ou créez-le manuellement en copiant `ENV_EXAMPLE.txt` et en le renommant en `.env.example`.

## Étape 2 : Ajouter tous les fichiers

```bash
# Ajouter tous les fichiers modifiés et nouveaux
git add .

# Vérifier ce qui sera commité
git status
```

## Étape 3 : Créer un commit

```bash
git commit -m "Amélioration du design et correction des bugs

- Application du design glassmorphism sur toutes les pages
- Correction des problèmes d'autorisation et de permissions
- Amélioration du système de reprogrammation
- Ajout du rapport de projet
- Configuration pour GitHub"
```

## Étape 4 : Pousser sur GitHub

### Si le dépôt distant existe déjà

```bash
# Pousser sur la branche main
git push origin main
```

### Si vous devez créer un nouveau dépôt sur GitHub

1. **Créer un nouveau dépôt sur GitHub :**
   - Allez sur https://github.com
   - Cliquez sur "New repository"
   - Donnez un nom (ex: "django-appointment-maw3idi")
   - Ne cochez PAS "Initialize with README" (vous avez déjà des fichiers)
   - Cliquez sur "Create repository"

2. **Connecter votre dépôt local au dépôt GitHub :**
   ```bash
   # Remplacez <VOTRE_USERNAME> et <NOM_DU_REPO> par vos valeurs
   git remote add origin https://github.com/<VOTRE_USERNAME>/<NOM_DU_REPO>.git
   
   # Pousser le code
   git push -u origin main
   ```

## Étape 5 : Partager avec votre ami

### Option 1 : Inviter comme collaborateur

1. Allez sur votre dépôt GitHub
2. Cliquez sur "Settings" → "Collaborators"
3. Cliquez sur "Add people"
4. Entrez le nom d'utilisateur GitHub de votre ami
5. Votre ami recevra une invitation par email

### Option 2 : Partager le lien

Donnez simplement le lien du dépôt à votre ami :
```
https://github.com/<VOTRE_USERNAME>/<NOM_DU_REPO>
```

Votre ami pourra cloner le projet avec :
```bash
git clone https://github.com/<VOTRE_USERNAME>/<NOM_DU_REPO>.git
```

## Instructions pour votre ami

Envoyez ces instructions à votre ami :

### 1. Cloner le projet

```bash
git clone https://github.com/<VOTRE_USERNAME>/<NOM_DU_REPO>.git
cd <NOM_DU_REPO>
```

### 2. Suivre le guide d'installation

Votre ami doit suivre le fichier `INSTALLATION.md` qui contient toutes les étapes nécessaires.

### 3. Configuration rapide

```bash
# Créer l'environnement virtuel
python -m venv venv
venv\Scripts\activate  # Windows
# ou
source venv/bin/activate  # Linux/Mac

# Installer les dépendances
pip install -r requirements.txt

# Créer le fichier .env
# Sur Windows PowerShell
Copy-Item ENV_EXAMPLE.txt .env
# Sur Linux/Mac
cp ENV_EXAMPLE.txt .env

# Éditer .env et configurer SECRET_KEY, EMAIL, etc.

# Créer les migrations
python manage.py makemigrations appointment
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser

# Lancer le serveur
python manage.py runserver
```

## Commandes Git utiles

### Voir l'état actuel
```bash
git status
```

### Voir l'historique des commits
```bash
git log
```

### Créer une nouvelle branche
```bash
git checkout -b nom-de-la-branche
```

### Changer de branche
```bash
git checkout main
```

### Récupérer les dernières modifications
```bash
git pull origin main
```

## Sécurité - Points importants

⚠️ **AVANT DE PUSHER :**

1. Vérifiez que `.env` n'est PAS dans Git :
   ```bash
   git status
   # .env ne doit PAS apparaître dans la liste
   ```

2. Vérifiez que `db.sqlite3` n'est PAS dans Git

3. Si vous avez accidentellement commité un fichier sensible :
   ```bash
   # Retirer le fichier de Git (mais le garder localement)
   git rm --cached .env
   git commit -m "Remove .env from repository"
   git push
   ```

## Résolution de problèmes

### Erreur : "remote origin already exists"
```bash
# Voir les remotes existants
git remote -v

# Supprimer l'ancien remote
git remote remove origin

# Ajouter le nouveau
git remote add origin <URL>
```

### Erreur : "failed to push some refs"
```bash
# Récupérer d'abord les modifications distantes
git pull origin main --rebase

# Puis pousser
git push origin main
```

### Changer l'URL du remote
```bash
git remote set-url origin <NOUVELLE_URL>
```

## Fichiers importants à partager

Assurez-vous que ces fichiers sont bien dans le dépôt :
- ✅ `INSTALLATION.md` - Guide d'installation
- ✅ `RAPPORT_PROJET.md` - Documentation du projet
- ✅ `ENV_EXAMPLE.txt` - Exemple de configuration
- ✅ `requirements.txt` - Dépendances Python
- ✅ `README.md` - Documentation principale
- ✅ `.gitignore` - Fichiers à ignorer

## Support

Si vous rencontrez des problèmes :
1. Vérifiez que Git est bien installé : `git --version`
2. Vérifiez que vous êtes connecté à GitHub
3. Consultez la documentation GitHub : https://docs.github.com

