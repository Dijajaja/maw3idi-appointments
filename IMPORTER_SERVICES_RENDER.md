# 📦 Guide : Importer les Services Locaux vers PostgreSQL sur Render

Ce guide vous explique comment importer les services créés localement (SQLite) vers PostgreSQL sur Render.

## ✅ Ce qui a été fait

1. **Export des services locaux** : Les 5 services ont été exportés dans `services_local.json`
2. **Commande d'import créée** : Une commande Django `import_services_to_postgres` a été créée

## 📋 Fichiers créés

- `services_local.json` : Contient vos 5 services locaux
- `appointment/management/commands/import_services_to_postgres.py` : Commande pour importer les services

## 🚀 Méthode 1 : Import via le Shell Render (Recommandé)

### Étape 1 : Accéder au Shell Render

⚠️ **Note** : Le Shell Render n'est pas disponible sur les instances gratuites. Si vous avez une instance payante :

1. Allez sur votre service Render
2. Cliquez sur "Shell" dans le menu
3. Connectez-vous via SSH

### Étape 2 : Uploader le fichier JSON

```bash
# Dans votre terminal local
# Copiez le fichier vers Render (si vous avez accès SSH)
scp services_local.json render:/opt/render/project/src/
```

**OU** via Git (recommandé) :

1. Commitez le fichier `services_local.json` dans Git
2. Poussez vers votre repository
3. Render le récupèrera automatiquement

### Étape 3 : Exécuter la commande d'import

```bash
cd /opt/render/project/src
python manage.py import_services_to_postgres services_local.json
```

## 🔧 Méthode 2 : Import via Git (Sans Shell)

Puisque Render Free n'a pas de Shell, voici une méthode alternative :

### Étape 1 : Commiter le fichier JSON

```bash
git add services_local.json
git commit -m "Ajout des services locaux à importer"
git push origin main
```

### Étape 2 : Modifier le script de démarrage temporairement

Modifiez temporairement `start.sh` pour importer les services au démarrage (une seule fois) :

```bash
#!/bin/bash
# ... code existant ...

# Import automatique des services (une seule fois)
if [ -f "services_local.json" ] && [ ! -f ".services_imported" ]; then
    echo "📦 Import des services locaux..."
    python manage.py import_services_to_postgres services_local.json --skip-existing
    if [ $? -eq 0 ]; then
        touch .services_imported
        echo "✅ Services importés avec succès!"
    else
        echo "❌ Erreur lors de l'import des services"
    fi
fi

# ... reste du code ...
```

### Étape 3 : Déployer et retirer le code après import

1. Déployez avec Git
2. Attendez que les services soient importés
3. Retirez le code d'import de `start.sh`
4. Recommitez et redéployez

## 🛠️ Méthode 3 : Créer un script d'import manuel

### Créer un script Python simple

Créez un fichier `import_services.py` à la racine du projet :

```python
#!/usr/bin/env python
"""
Script pour importer les services localement vers PostgreSQL.
À exécuter une seule fois après avoir configuré DATABASE_URL pour Render.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appointments.settings')
django.setup()

# Importer la commande
from appointment.management.commands.import_services_to_postgres import Command
from io import StringIO

# Exécuter la commande
command = Command()
command.stdout = StringIO()

# Simuler les arguments
command.handle(
    'services_local.json',
    skip_existing=True
)

print(command.stdout.getvalue())
```

### Configurer DATABASE_URL localement

Dans votre fichier `.env` local, ajoutez temporairement le `DATABASE_URL` de Render :

```env
DATABASE_URL=postgresql://django_appointment_db_user:VOTRE_MOT_DE_PASSE@dpg-d5eqgcsjebjc73e0ig5g-a/django_appointment_db
```

### Exécuter le script

```bash
python import_services.py
```

## 📝 Options de la commande d'import

La commande `import_services_to_postgres` accepte plusieurs options :

```bash
# Import normal (crée de nouveaux services)
python manage.py import_services_to_postgres services_local.json

# Ignorer les services existants
python manage.py import_services_to_postgres services_local.json --skip-existing

# Mettre à jour les services existants
python manage.py import_services_to_postgres services_local.json --update-existing
```

## ⚠️ Notes importantes

1. **Images** : Les images des services ne seront pas importées automatiquement car elles sont des fichiers. Vous devrez les uploader manuellement via l'interface admin.

2. **IDs** : Les IDs des services peuvent changer lors de l'import (les nouveaux IDs seront assignés automatiquement).

3. **Relations** : Si vos services sont liés à d'autres objets (comme StaffMember), assurez-vous que ces objets existent aussi dans PostgreSQL.

4. **Vérification** : Après l'import, vérifiez sur votre site Render que les services apparaissent correctement.

## 🔍 Vérifier que les services sont importés

Après l'import, vérifiez :

1. Allez sur votre site : `https://django-appointment-u96d.onrender.com/`
2. Les services devraient apparaître sur la page d'accueil
3. Ou allez dans l'admin Django : `/admin/appointment/service/`

## ❓ Problèmes possibles

### Erreur : "No such file or directory"
- Vérifiez que `services_local.json` existe dans le répertoire du projet

### Erreur : "Connection refused" ou erreur PostgreSQL
- Vérifiez que `DATABASE_URL` est correctement configuré sur Render
- Vérifiez que la base de données PostgreSQL est accessible

### Les services n'apparaissent pas
- Vérifiez les logs Render pour voir s'il y a des erreurs
- Vérifiez que les migrations ont été appliquées
- Vérifiez que vous utilisez bien PostgreSQL (pas SQLite)

## 📞 Support

Si vous rencontrez des problèmes, consultez les logs Render ou créez une issue.

