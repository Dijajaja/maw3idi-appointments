# 📸 Captures d'Écran du Site Web

Ce dossier contient les scripts pour générer des captures d'écran automatiques des pages principales du site web.

## 🚀 Utilisation Rapide

### Étape 1 : Installer les dépendances

```bash
# Windows
install_dependencies.bat

# Ou manuellement
pip install playwright
playwright install chromium
```

### Étape 2 : Démarrer le serveur Django

Dans un terminal séparé :

```bash
cd C:\Users\PC\django-appointment
python manage.py runserver
```

### Étape 3 : Capturer les pages

```bash
# Windows
capturer_site.bat

# Ou manuellement
python capture_site.py
```

## 📋 Pages Capturées

Le script capture automatiquement les pages suivantes :

1. **Page d'accueil** (`01_page_accueil.png`)
   - URL: `/fr/`
   - Liste des services disponibles

2. **Page de connexion** (`02_page_connexion.png`)
   - URL: `/fr/login/`
   - Formulaire de connexion

3. **Page d'inscription** (`03_page_inscription.png`)
   - URL: `/fr/register/`
   - Formulaire d'inscription

4. **Page de contact** (`04_page_contact.png`)
   - URL: `/fr/contact/`
   - Formulaire de contact

5. **Page calendrier** (`05_page_calendrier.png`)
   - URL: `/fr/calendar/`
   - Vue calendrier (nécessite connexion)

## 🔧 Configuration

Vous pouvez modifier le script `capture_site.py` pour :

- Ajouter d'autres pages à capturer
- Modifier la résolution des captures (viewport)
- Changer l'URL du serveur
- Ajouter des délais d'attente

### Exemple d'ajout de page

```python
PAGES_TO_CAPTURE.append({
    "url": f"{FR_BASE_URL}/my-appointments/",
    "name": "06_mes_rendez_vous",
    "description": "Page mes rendez-vous"
})
```

## 📦 Dépendances

- **Playwright** : Bibliothèque pour automatiser les navigateurs
- **Python 3.7+** : Langage de programmation

## 🐛 Dépannage

### Erreur : "Playwright n'est pas installé"
```bash
pip install playwright
playwright install chromium
```

### Erreur : "Serveur Django non accessible"
- Vérifiez que le serveur est démarré : `python manage.py runserver`
- Vérifiez que le serveur écoute sur `http://localhost:8000`
- Vérifiez votre pare-feu

### Erreur : "Page ne se charge pas"
- Certaines pages nécessitent d'être connecté
- Vérifiez que les données de test sont présentes dans la base
- Augmentez le délai `WAIT_TIME` dans le script

## 📝 Notes

- Les captures sont en haute résolution (1920x1080, 2x device scale)
- Les captures sont en mode "full page" (page complète)
- Le format de sortie est PNG
- Les fichiers sont nommés avec un préfixe numérique pour l'ordre

## 📂 Structure

```
docs/screenshots/
├── README.md                    # Ce fichier
├── capture_site.py              # Script principal
├── capturer_site.bat            # Script Windows
├── install_dependencies.bat     # Installation dépendances
└── [images générées].png        # Captures d'écran
```

