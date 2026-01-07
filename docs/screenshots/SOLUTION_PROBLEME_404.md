# ⚠️ Problème : Pages 404 (Pages Blanches)

## 🔍 Diagnostic

Les captures montrent des erreurs **404 "Page not found"** avec ce message :
> "Using the URLconf defined in **backend.urls**"

Mais votre projet utilise **appointments.urls** !

Cela signifie qu'**un autre serveur Django tourne** sur le port 8000.

## ✅ Solution

### Étape 1 : Arrêter tous les serveurs Django

Dans PowerShell, exécutez :

```powershell
# Trouver tous les processus Python qui utilisent le port 8000
netstat -ano | findstr :8000

# Puis tuer les processus trouvés (remplacer PID par le numéro trouvé)
taskkill /PID [PID] /F
```

### Étape 2 : Vérifier que le port est libre

```powershell
netstat -ano | findstr :8000
```

Si rien n'apparaît, le port est libre.

### Étape 3 : Démarrer le BON serveur Django

Depuis le dossier du projet :

```powershell
cd C:\Users\PC\django-appointment
python manage.py runserver
```

Vous devriez voir :
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

**⚠️ IMPORTANT : Laissez ce terminal ouvert !**

### Étape 4 : Vérifier que ça fonctionne

Ouvrez votre navigateur sur : `http://localhost:8000/fr/`

Vous devriez voir la **page d'accueil avec les services**, PAS une erreur 404.

### Étape 5 : Relancer les captures

Dans un **autre terminal** :

```powershell
cd C:\Users\PC\django-appointment\docs\screenshots
python capture_toutes_pages.py
```

## 🔄 Alternative : Script Automatique

Un script amélioré va :
1. Vérifier quel serveur tourne
2. Arrêter les mauvais serveurs
3. Démarrer le bon serveur
4. Capturer les pages
5. Nettoyer après

Voulez-vous que je crée ce script ?

