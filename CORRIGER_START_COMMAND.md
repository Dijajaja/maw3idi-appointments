# Corriger la commande de démarrage dans Render

## Problème
Render essaie d'exécuter `gunicorn your_application.wsgi` au lieu de `gunicorn appointments.wsgi:application`.

## Solution

### Option 1 : Mettre à jour manuellement dans l'interface Render (RECOMMANDÉ)

1. Allez sur https://dashboard.render.com
2. Cliquez sur votre service `django-appointment`
3. Allez dans l'onglet **"Settings"** (Paramètres)
4. Trouvez la section **"Start Command"** (Commande de démarrage)
5. Remplacez la commande par :
   ```
   gunicorn appointments.wsgi:application --bind 0.0.0.0:$PORT
   ```
6. Cliquez sur **"Save Changes"** (Enregistrer les modifications)
7. Render redéploiera automatiquement avec la nouvelle commande

### Option 2 : Synchroniser le Blueprint

1. Allez sur votre Blueprint dans Render
2. Cliquez sur **"Manual sync"** (Synchronisation manuelle)
3. Cela devrait mettre à jour la configuration du service avec celle du `render.yaml`

### Option 3 : Supprimer et recréer le service via le Blueprint

⚠️ **ATTENTION** : Cette option supprimera le service actuel. Assurez-vous d'avoir sauvegardé toutes les données importantes.

1. Supprimez le service actuel dans Render
2. Recréez-le via le Blueprint en cliquant sur **"New Blueprint Instance"**
3. Cela créera un nouveau service avec la configuration correcte du `render.yaml`

## Vérification

Après avoir appliqué la correction, vérifiez les logs du déploiement. Vous devriez voir :
```
Running 'gunicorn appointments.wsgi:application --bind 0.0.0.0:$PORT'
```

Au lieu de :
```
Running 'gunicorn your_application.wsgi'
```

