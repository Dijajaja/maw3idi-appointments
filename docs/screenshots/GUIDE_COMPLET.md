# 📸 Guide Complet pour les Captures d'Écran

## ❌ Problème Actuel

Vous voyez des pages **blanches ou des erreurs 404** parce qu'un **mauvais serveur Django** tourne sur le port 8000.

L'erreur indique : `Using the URLconf defined in backend.urls` au lieu de `appointments.urls`.

## ✅ Solution Étape par Étape

### Étape 1 : Arrêter TOUS les serveurs Django

Ouvrez PowerShell en **administrateur** et exécutez :

```powershell
# Trouver tous les processus qui utilisent le port 8000
netstat -ano | findstr :8000

# Arrêter tous les processus Python (attention, cela arrêtera TOUS les Python)
Get-Process python | Stop-Process -Force
```

**OU** plus sélectif :

```powershell
# Trouver le PID du processus sur le port 8000
$port = netstat -ano | findstr :8000 | findstr LISTENING
$pid = ($port -split '\s+')[-1]
taskkill /F /PID $pid
```

### Étape 2 : Vérifier que le port est libre

```powershell
netstat -ano | findstr :8000
```

Si rien ne s'affiche, c'est bon ! ✅

### Étape 3 : Démarrer le BON serveur Django

Ouvrez un **nouveau terminal** et exécutez :

```powershell
cd C:\Users\PC\django-appointment
python manage.py runserver
```

Vous devriez voir :
```
Starting development server at http://127.0.0.1:8000/
```

**⚠️ LAISSEZ CE TERMINAL OUVERT !**

### Étape 4 : Vérifier que ça fonctionne

1. Ouvrez votre **navigateur web**
2. Allez sur : `http://localhost:8000/fr/`
3. Vous devriez voir la **page d'accueil avec les services**

Si vous voyez encore une erreur 404, il y a encore un problème.

### Étape 5 : Capturer les pages

Dans un **autre terminal** :

```powershell
cd C:\Users\PC\django-appointment\docs\screenshots
python capture_toutes_pages.py
```

## 👀 Comment Voir les Images Existantes

### Méthode 1 : Explorateur Windows

1. Ouvrez l'**Explorateur de fichiers**
2. Allez dans : `C:\Users\PC\django-appointment\docs\screenshots`
3. Double-cliquez sur n'importe quel fichier `.png`

### Méthode 2 : Ouvrir le dossier directement

Dans PowerShell :
```powershell
cd C:\Users\PC\django-appointment\docs\screenshots
explorer .
```

### Méthode 3 : Page HTML

Double-cliquez sur `voir_images.html` dans le dossier screenshots.

## 🐛 Dépannage

**Erreur "backend.urls"** :
→ Un autre projet Django tourne. Arrêtez-le avec les commandes ci-dessus.

**Pages blanches** :
→ Le serveur n'a pas fini de charger. Attendez 5-10 secondes après le démarrage.

**Timeout** :
→ Le serveur ne répond pas. Vérifiez qu'il tourne bien.

## 📝 Note Importante

Les captures actuelles sont probablement des pages 404 ou blanches parce que le mauvais serveur tournait. **Refaites les captures** après avoir suivi les étapes ci-dessus !

