# Guide d'intégration du template Black Dashboard

## ✅ Ce qui a été fait

1. ✅ Template de base Django créé : `appointment/templates/base_templates/black_dashboard_base.html`
2. ✅ Page index adaptée pour utiliser Black Dashboard
3. ✅ Styles CSS adaptés pour le thème sombre de Black Dashboard

## 📋 Étape 1 : Déplacer les assets (IMPORTANT)

Le template Black Dashboard que vous avez téléchargé contient un dossier `assets/` avec :
- `css/` - fichiers CSS (black-dashboard.css, nucleo-icons.css, etc.)
- `js/` - fichiers JavaScript (black-dashboard.js, demos.js, etc.)
- `img/` - images (logos, icônes, etc.)
- `demo/` - fichiers de démonstration

**Action requise :**
1. Trouvez le dossier `assets/` dans le template décompressé (généralement dans le dossier racine du template)
2. Copiez-le dans `appointment/static/`
3. La structure finale devrait être :
   ```
   appointment/static/
   ├── assets/
   │   ├── css/
   │   │   ├── black-dashboard.css
   │   │   ├── nucleo-icons.css
   │   │   └── ...
   │   ├── js/
   │   │   ├── black-dashboard.min.js
   │   │   ├── demos.js
   │   │   └── ...
   │   ├── img/
   │   │   ├── favicon.png
   │   │   ├── apple-icon.png
   │   │   └── ...
   │   └── demo/
   │       └── demo.css
   ├── css/ (vos fichiers CSS existants)
   ├── js/ (vos fichiers JS existants)
   └── examples/ (vos fichiers HTML d'exemple)
   ```

## 🔍 Étape 2 : Vérification

Après avoir déplacé les assets, vérifiez que les fichiers suivants existent :
```bash
# Dans PowerShell
Test-Path "appointment\static\assets\css\black-dashboard.css"
Test-Path "appointment\static\assets\css\nucleo-icons.css"
Test-Path "appointment\static\assets\js\black-dashboard.min.js"
Test-Path "appointment\static\assets\js\demos.js"
```

Tous doivent retourner `True`.

## 🚀 Étape 3 : Tester

1. Démarrez le serveur Django :
   ```bash
   python manage.py runserver
   ```

2. Accédez à la page d'accueil :
   ```
   http://127.0.0.1:8000/fr/
   ```

3. Vous devriez voir la page avec le design Black Dashboard (fond sombre, sidebar, etc.)

## 🎨 Personnalisation

### Changer le template par défaut

Dans `appointments/settings.py`, ajoutez :
```python
APPOINTMENT_BASE_TEMPLATE = 'base_templates/black_dashboard_base.html'
```

### Personnaliser le menu sidebar

Modifiez le bloc `{% block sidebar_menu %}` dans `black_dashboard_base.html` ou dans vos templates enfants.

### Changer la couleur du sidebar

Dans le template, modifiez :
```html
<div class="sidebar" data-color="blue">  <!-- ou green, orange, red, black -->
```

## ⚠️ Notes importantes

- Si les assets ne sont pas trouvés, vous verrez des erreurs 404 dans la console du navigateur
- Assurez-vous que `python manage.py collectstatic` a été exécuté en production
- Les fichiers JavaScript du template utilisent jQuery et Bootstrap 4

## 🔧 Script de vérification

Un script PowerShell a été créé pour vérifier l'installation des assets :
```powershell
.\check_black_dashboard_assets.ps1
```

Ce script vérifie que tous les fichiers nécessaires sont présents.

## 📝 Fonctionnalités automatiques

Le système détecte automatiquement si les assets Black Dashboard sont installés :
- ✅ Si les assets sont présents → Utilise le template Black Dashboard
- ❌ Si les assets sont absents → Utilise le template par défaut

Aucune configuration supplémentaire n'est nécessaire !

