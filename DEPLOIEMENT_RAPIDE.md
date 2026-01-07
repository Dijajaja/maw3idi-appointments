# 🚀 Déploiement Rapide - Django Appointment

## Option 1 : Déploiement Automatique avec le Script (Windows)

### Étapes simples :

1. **Ouvrez PowerShell dans le dossier du projet**

2. **Exécutez le script de déploiement :**
   ```powershell
   .\deploy.ps1
   ```

3. **Choisissez l'option 1** pour déployer avec Docker

4. **Modifiez le fichier `.env`** avec vos paramètres :
   - `SECRET_KEY` (déjà générée)
   - `EMAIL_HOST_USER` (votre email)
   - `EMAIL_HOST_PASSWORD` (mot de passe d'application Gmail)
   - `ADMIN_EMAIL` (email de l'administrateur)

5. **Créez un superutilisateur :**
   ```powershell
   docker-compose exec web python manage.py createsuperuser
   ```

6. **Accédez à l'application :**
   - Application : http://localhost:8000
   - Admin : http://localhost:8000/admin

---

## Option 2 : Déploiement Manuel avec Docker

### Commandes à exécuter :

```powershell
# 1. Créer le fichier .env (copiez ENV_EXAMPLE.txt vers .env et modifiez-le)
copy ENV_EXAMPLE.txt .env

# 2. Construire et démarrer
docker-compose up -d --build

# 3. Créer les migrations
docker-compose exec web python manage.py makemigrations appointment

# 4. Appliquer les migrations
docker-compose exec web python manage.py migrate

# 5. Collecter les fichiers statiques
docker-compose exec web python manage.py collectstatic --noinput

# 6. Créer un superutilisateur
docker-compose exec web python manage.py createsuperuser
```

---

## Option 3 : Déploiement Local (Sans Docker)

### Commandes à exécuter :

```powershell
# 1. Créer l'environnement virtuel
python -m venv venv

# 2. Activer l'environnement virtuel
.\venv\Scripts\Activate.ps1

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Créer le fichier .env
copy ENV_EXAMPLE.txt .env
# Puis modifiez .env avec vos paramètres

# 5. Créer les migrations
python manage.py makemigrations appointment

# 6. Appliquer les migrations
python manage.py migrate

# 7. Collecter les fichiers statiques
python manage.py collectstatic

# 8. Créer un superutilisateur
python manage.py createsuperuser

# 9. Démarrer le serveur
python manage.py runserver

# 10. Dans un autre terminal, démarrer Django Q (si activé)
python manage.py qcluster
```

---

## ⚙️ Configuration Email (Gmail)

Pour utiliser Gmail pour l'envoi d'emails :

1. **Activez l'authentification à deux facteurs** sur votre compte Gmail
2. **Générez un "Mot de passe d'application"** :
   - Allez sur https://myaccount.google.com/apppasswords
   - Créez un mot de passe d'application
   - Utilisez ce mot de passe (pas votre mot de passe Gmail) dans `.env` pour `EMAIL_HOST_PASSWORD`

3. **Configurez dans `.env` :**
   ```env
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=votre-email@gmail.com
   EMAIL_HOST_PASSWORD=votre-mot-de-passe-application
   ```

---

## 📋 Checklist de Déploiement

- [ ] Fichier `.env` créé et configuré
- [ ] `SECRET_KEY` générée et unique
- [ ] Configuration email complétée
- [ ] Migrations créées et appliquées
- [ ] Superutilisateur créé
- [ ] Fichiers statiques collectés
- [ ] Serveur accessible sur http://localhost:8000
- [ ] Interface admin accessible sur http://localhost:8000/admin

---

## 🆘 Problèmes Courants

### Le port 8000 est déjà utilisé
```powershell
# Trouver le processus
netstat -ano | findstr :8000

# Tuer le processus (remplacez PID par le numéro trouvé)
taskkill /F /PID <PID>
```

### Erreur "Module not found"
```powershell
# Réinstaller les dépendances
pip install -r requirements.txt
```

### Les emails ne sont pas envoyés
- Vérifiez la configuration dans `.env`
- Pour Gmail, utilisez un "Mot de passe d'application"
- Vérifiez les logs : `docker-compose logs web`

---

## 📚 Documentation Complète

Pour plus de détails, consultez :
- **Guide complet** : `GUIDE_DEPLOIEMENT.md`
- **Installation** : `INSTALLATION.md`
- **Documentation Django** : https://docs.djangoproject.com/

---

**Bon déploiement ! 🎉**

