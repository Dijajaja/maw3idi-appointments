# Déboguer l'erreur 500

## Problème
Le site est en ligne mais affiche une erreur 500 (Server Error).

## Solutions

### 1. Vérifier les logs Render

Les logs Render contiennent l'erreur exacte. Pour les voir :

1. Allez sur https://dashboard.render.com
2. Cliquez sur votre service `django-appointment`
3. Allez dans l'onglet **"Logs"**
4. Cherchez les erreurs récentes (en rouge)

### 2. Activer DEBUG temporairement (pour voir l'erreur)

⚠️ **ATTENTION** : Ne laissez jamais DEBUG=True en production pour des raisons de sécurité !

Pour voir l'erreur exacte, activez DEBUG temporairement :

1. Allez dans **Settings** > **Environment** de votre service
2. Trouvez la variable `DEBUG`
3. Changez sa valeur de `False` à `True`
4. Sauvegardez et attendez le redéploiement
5. Rechargez la page - vous verrez maintenant l'erreur détaillée
6. **IMPORTANT** : Remettez `DEBUG=False` après avoir identifié le problème

### 3. Causes courantes d'erreur 500

#### A. Migrations non appliquées
**Symptôme** : Erreur liée aux tables manquantes dans les logs

**Solution** : Le script `start.sh` devrait appliquer les migrations automatiquement. Vérifiez les logs pour voir si les migrations ont été appliquées.

#### B. Problème de connexion à la base de données
**Symptôme** : Erreur de connexion PostgreSQL dans les logs

**Solution** : 
- Vérifiez que la base de données est en ligne dans Render
- Vérifiez que `DATABASE_URL` est correctement configuré
- Les logs de la base de données peuvent aider

#### C. Variables d'environnement manquantes
**Symptôme** : Erreur `ImproperlyConfigured` dans les logs

**Solution** : Vérifiez que toutes les variables d'environnement nécessaires sont configurées.

#### D. Problème avec les fichiers statiques
**Symptôme** : Erreur liée aux fichiers statiques

**Solution** : Vérifiez que `collectstatic` a été exécuté (il devrait l'être dans le buildCommand).

### 4. Vérifier que le script start.sh s'exécute

Dans les logs, vous devriez voir :
```
🔄 Application des migrations...
👤 Création du superutilisateur (si configuré)...
🚀 Démarrage de Gunicorn...
```

Si vous ne voyez pas ces messages, le script ne s'exécute pas correctement.

### 5. Tester la connexion à la base de données

Le script amélioré teste maintenant la connexion à la base de données. Vérifiez les logs pour voir si la connexion réussit.

## Prochaines étapes

1. **Vérifiez les logs Render** pour voir l'erreur exacte
2. **Activez DEBUG temporairement** si nécessaire pour voir l'erreur détaillée
3. **Partagez l'erreur** avec moi pour que je puisse vous aider à la résoudre

## Important

- ⚠️ Ne laissez jamais `DEBUG=True` en production
- 🔒 Les logs peuvent contenir des informations sensibles
- 📝 Notez l'erreur exacte avant de désactiver DEBUG

