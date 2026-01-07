# 🚀 Créer une Instance Blueprint sur Render

## ✅ Vous Êtes au Bon Endroit !

Vous voyez :
- "You haven't created any Blueprint instances yet"
- "New Blueprint Instance" ← Cliquez ici !

## 📋 Étapes pour Créer le Blueprint

### Étape 1 : Cliquer sur "New Blueprint Instance"

Cliquez sur le bouton **"New Blueprint Instance"**.

### Étape 2 : Connecter votre Repository GitHub

1. Render vous demandera de **connecter votre repository GitHub**
2. Si ce n'est pas déjà fait :
   - Cliquez sur "Connect GitHub" ou "Authorize Render"
   - Autorisez Render à accéder à vos repositories
3. Sélectionnez votre repository : **"maw3idi-appointments"** (ou le nom exact de votre repo)

### Étape 3 : Render Détectera Automatiquement render.yaml

1. Render va scanner votre repository
2. Il trouvera automatiquement le fichier `render.yaml` à la racine
3. Il vous montrera un aperçu de ce qui sera créé :
   - ✅ Web Service (maw3idi)
   - ✅ Background Worker (django-appointment-worker)
   - ✅ PostgreSQL Database (django-appointment-db)

### Étape 4 : Configurer les Variables d'Environnement

Render vous demandera de configurer les variables d'environnement qui sont marquées `sync: false` dans render.yaml :

**Variables à configurer :**
```
EMAIL_HOST_USER=votre-email@gmail.com
EMAIL_HOST_PASSWORD=votre-mot-de-passe-application-gmail
ADMIN_EMAIL=admin@example.com
```

**Variables optionnelles (mais recommandées) :**
```
ADMIN_USERNAME=admin
ADMIN_PASSWORD=votre-mot-de-passe-securise
```

### Étape 5 : Créer le Blueprint

1. Vérifiez que tout est correct
2. Cliquez sur **"Apply"** ou **"Create Blueprint"**
3. Render commencera à créer tous les services

### Étape 6 : Attendre le Déploiement

Render va :
1. Créer la base de données PostgreSQL
2. Créer le Web Service
3. Créer le Worker
4. Installer les dépendances
5. Appliquer les migrations
6. Créer le superutilisateur
7. Déployer l'application

**Cela peut prendre 3-5 minutes.**

## 📝 Checklist Avant de Créer le Blueprint

Assurez-vous que ces fichiers sont dans votre repository GitHub :

- [x] `render.yaml` (à la racine)
- [x] `create_superuser.py` (à la racine)
- [x] `requirements.txt` (avec toutes les dépendances)
- [x] `appointments/settings.py` (configuré pour la production)

Si vous n'avez pas encore poussé ces fichiers :

```bash
git add render.yaml create_superuser.py requirements.txt
git commit -m "Configuration complète pour Render Blueprint"
git push origin main
```

## 🎯 Ce Qui Sera Créé Automatiquement

Une fois le Blueprint créé, vous aurez :

1. **Web Service "django-appointment"**
   - URL : https://maw3idi.onrender.com
   - Build Command : configuré automatiquement
   - Start Command : gunicorn
   - Variables d'environnement : configurées

2. **Background Worker "django-appointment-worker"**
   - Pour Django Q (envoi d'emails asynchrones)
   - Variables d'environnement : partagées avec le Web Service

3. **PostgreSQL Database "django-appointment-db"**
   - Plan : Free
   - Variable `DATABASE_URL` : créée automatiquement

## ⚙️ Après la Création

Une fois le déploiement terminé :

1. **Vérifiez les logs** pour voir si tout s'est bien passé
2. **Accédez à votre application** : https://maw3idi.onrender.com
3. **Accédez à l'admin** : https://maw3idi.onrender.com/admin
   - Utilisateur : admin (ou celui que vous avez configuré)
   - Mot de passe : celui que vous avez mis dans `ADMIN_PASSWORD`

## 🐛 Si Vous Avez des Erreurs

Si le déploiement échoue :

1. **Vérifiez les logs** dans chaque service
2. **Vérifiez que toutes les variables d'environnement sont configurées**
3. **Vérifiez que `requirements.txt` contient toutes les dépendances**
4. **Vérifiez que `render.yaml` est correct**

## ✅ Résumé

1. Cliquez sur **"New Blueprint Instance"**
2. Sélectionnez votre repository GitHub
3. Configurez les variables d'environnement
4. Cliquez sur **"Apply"**
5. Attendez 3-5 minutes
6. Votre application sera en ligne ! 🎉

**C'est tout ! Render fera le reste automatiquement.**

