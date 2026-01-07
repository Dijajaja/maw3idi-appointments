# Initialiser l'application après le déploiement

## ✅ Le service est maintenant en ligne !

Votre application Django est déployée avec succès sur Render. Maintenant, il faut initialiser la base de données.

## Étapes d'initialisation

### 1. Appliquer les migrations

1. Allez sur https://dashboard.render.com
2. Cliquez sur votre service `django-appointment`
3. Allez dans l'onglet **"Shell"** (ou **"Console"**)
4. Exécutez la commande suivante :
   ```bash
   python manage.py migrate --noinput
   ```

Cela créera toutes les tables nécessaires dans la base de données PostgreSQL.

### 2. Créer un superutilisateur

Vous avez deux options :

#### Option A : Utiliser le script automatique (si vous avez configuré les variables d'environnement)

Si vous avez configuré `ADMIN_USERNAME`, `ADMIN_EMAIL`, et `ADMIN_PASSWORD` dans les variables d'environnement de Render, exécutez :

```bash
python create_superuser.py
```

#### Option B : Créer manuellement

Dans le Shell Render, exécutez :

```bash
python manage.py createsuperuser
```

Suivez les instructions pour créer votre compte administrateur.

### 3. Vérifier que tout fonctionne

1. Allez sur https://django-appointment-u96d.onrender.com
2. Vous devriez voir la page d'accueil de l'application
3. Allez sur `/admin/` pour accéder à l'interface d'administration Django
4. Connectez-vous avec le superutilisateur que vous avez créé

## Variables d'environnement à vérifier

Assurez-vous que les variables suivantes sont configurées dans Render (Settings > Environment) :

- ✅ `SECRET_KEY` (généré automatiquement)
- ✅ `DEBUG=False`
- ✅ `ALLOWED_HOSTS` (déjà configuré)
- ✅ `DATABASE_URL` (connecté automatiquement à la base de données)
- ⚠️ `EMAIL_HOST_USER` (si vous voulez envoyer des emails)
- ⚠️ `EMAIL_HOST_PASSWORD` (si vous voulez envoyer des emails)
- ⚠️ `ADMIN_USERNAME`, `ADMIN_EMAIL`, `ADMIN_PASSWORD` (pour créer automatiquement le superutilisateur)

## Résolution de problèmes

### Erreur 500

Si vous voyez une erreur 500 :
1. Vérifiez que les migrations ont été appliquées
2. Vérifiez les logs dans Render pour voir l'erreur exacte
3. Assurez-vous que toutes les variables d'environnement sont configurées

### Erreur de connexion à la base de données

Si vous avez des erreurs de connexion :
1. Vérifiez que la base de données est bien créée et en ligne
2. Vérifiez que `DATABASE_URL` est correctement configuré
3. Les logs de la base de données dans Render peuvent vous aider

## Félicitations ! 🎉

Votre application Django est maintenant déployée et fonctionnelle sur Render !

