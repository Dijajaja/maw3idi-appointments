# 📍 Où Trouver le Build Command dans Render

## 🔍 Emplacements Possibles

### Option 1 : Dans l'onglet "Settings"

1. **Ouvrez votre service "maw3idi"** dans le dashboard Render
2. Regardez les **onglets en haut** :
   - Logs
   - Metrics
   - **Settings** ← Cliquez ici
   - Events
   - etc.

3. Dans **Settings**, faites défiler vers le bas jusqu'à trouver :
   - **Build & Deploy** (section)
   - **Build Command** (champ de texte)

### Option 2 : Dans l'onglet "Environment"

Parfois le Build Command est dans :
1. Onglet **"Environment"** (au lieu de Settings)
2. Section **"Build & Deploy"**

### Option 3 : Si vous ne trouvez toujours pas

Le Build Command peut être configuré différemment selon comment vous avez créé le service.

## ✅ Solution Alternative : Utiliser render.yaml

Si vous ne trouvez pas le Build Command, la **meilleure solution** est d'utiliser le fichier `render.yaml` que nous avons créé.

### Étape 1 : Vérifier que render.yaml est dans votre repository

Le fichier `render.yaml` doit être à la racine de votre projet GitHub.

### Étape 2 : Supprimer et Recréer le Service avec Blueprint

1. **Supprimez** votre service actuel "maw3idi" dans Render
2. Cliquez sur **"New +"** → **"Blueprint"**
3. Connectez votre repository GitHub
4. Render détectera automatiquement `render.yaml`
5. Il créera automatiquement :
   - Le Web Service avec la bonne configuration
   - Le Worker Django Q
   - La base de données PostgreSQL
   - Toutes les variables d'environnement

C'est **beaucoup plus simple** et évite les problèmes de configuration manuelle !

## 🎯 Solution Rapide : Modifier render.yaml

Si vous préférez garder votre service actuel, modifiez le fichier `render.yaml` :

```yaml
services:
  - type: web
    name: django-appointment
    env: python
    buildCommand: pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate --noinput && python create_superuser.py
    startCommand: gunicorn appointments.wsgi:application --bind 0.0.0.0:$PORT
    # ... reste de la config
```

Puis poussez sur GitHub et Render redéploiera automatiquement.

## 📸 À Quoi Ressemble l'Interface Render

Dans le dashboard Render, quand vous ouvrez un service, vous devriez voir :

```
┌─────────────────────────────────────────┐
│  maw3idi                                │
├─────────────────────────────────────────┤
│ [Logs] [Metrics] [Settings] [Events]    │ ← Onglets
├─────────────────────────────────────────┤
│                                         │
│  Settings                               │
│                                         │
│  Service Details                        │
│  Name: maw3idi                          │
│  ...                                    │
│                                         │
│  Build & Deploy                         │ ← Section
│  Build Command:                         │ ← Ici !
│  [___________________________]          │
│                                         │
│  Start Command:                         │
│  [___________________________]          │
│                                         │
└─────────────────────────────────────────┘
```

## 🚀 Solution la Plus Simple (Recommandée)

**Utilisez Blueprint avec render.yaml :**

1. **Supprimez** le service actuel
2. **"New +"** → **"Blueprint"**
3. Sélectionnez votre repository
4. Render fera tout automatiquement !

C'est la méthode la plus fiable et la plus simple.

## 💡 Si Rien Ne Fonctionne

Si vous ne trouvez vraiment pas le Build Command, dites-moi :
- Quel onglet vous voyez dans votre service Render
- Quelle version de l'interface Render vous utilisez
- Si vous voyez "Environment Variables" quelque part

Je vous guiderai plus précisément !

