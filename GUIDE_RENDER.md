# 🚀 Guide de Configuration Render.com - Étape par Étape

## ⚠️ Important : Configuration Correcte

Render a détecté Docker, mais nous allons utiliser la configuration Python/Django standard qui est plus simple.

## 📋 Configuration Étape par Étape

### 1. **Choisir le Type de Service**

**IMPORTANT :** Ne choisissez PAS "Docker" ! 

Au lieu de cela :
- **Language** : Sélectionnez **"Python 3"** (pas Docker)
- Ou utilisez le fichier `render.yaml` que nous avons créé

### 2. **Plan Gratuit (Sans Carte Bancaire)**

Vous pouvez choisir le plan **"Free"** ($0/mois) :
- ✅ **Pas besoin de carte bancaire** pour le plan Free
- ✅ 512 MB RAM (suffisant pour commencer)
- ⚠️ Le service se met en veille après 15 minutes d'inactivité
- ⚠️ Redémarre automatiquement au premier accès

**Pour éviter la mise en veille :** Utilisez un service de monitoring gratuit comme UptimeRobot.

### 3. **Configuration Manuelle (Si vous ne voulez pas utiliser render.yaml)**

Si vous configurez manuellement, voici les paramètres :

#### **Build Command :**
```bash
pip install -r requirements-prod.txt && python manage.py collectstatic --noinput
```

#### **Start Command :**
```bash
gunicorn appointments.wsgi:application --bind 0.0.0.0:$PORT
```

#### **Environment :**
- **Python 3** (pas Docker)

### 4. **Variables d'Environnement à Ajouter**

Cliquez sur "Add Environment Variable" et ajoutez :

```
SECRET_KEY=gefl9k5lp2b#6q0@p6nsbk3jbr3_9#tay*h(1c=@b)zgg98dwf
```

```
DEBUG=False
```

```
ALLOWED_HOSTS=maw3idi.onrender.com
```
*(Remplacez "maw3idi" par le nom que vous avez choisi)*

```
EMAIL_HOST_USER=votre-email@gmail.com
```

```
EMAIL_HOST_PASSWORD=votre-mot-de-passe-application-gmail
```
*(Pour Gmail, utilisez un "Mot de passe d'application", pas votre mot de passe normal)*

```
ADMIN_EMAIL=admin@example.com
```

```
USE_DJANGO_Q=True
```

```
APPOINTMENT_WEBSITE_NAME=Maw3idi
```

### 5. **Base de Données PostgreSQL**

**IMPORTANT :** Avant de déployer le Web Service, créez d'abord la base de données :

1. Dans le dashboard Render, cliquez sur **"New +"** → **"PostgreSQL"**
2. Choisissez le plan **"Free"** (gratuit)
3. Créez la base de données
4. Render créera automatiquement la variable `DATABASE_URL`
5. **Copiez cette variable** et ajoutez-la aux variables d'environnement de votre Web Service

### 6. **Déployer**

Une fois tout configuré, cliquez sur **"Create Web Service"** ou **"Save Changes"**.

## 🎯 Option Plus Simple : Utiliser render.yaml

Au lieu de configurer manuellement, vous pouvez :

1. **Annulez** la configuration actuelle
2. Dans le dashboard Render, cliquez sur **"New +"** → **"Blueprint"**
3. Connectez votre repository GitHub
4. Render détectera automatiquement `render.yaml`
5. Il créera automatiquement :
   - Le Web Service
   - Le Worker Django Q
   - La base de données PostgreSQL
   - Toutes les configurations nécessaires

C'est **beaucoup plus simple** ! 🎉

## 📝 Checklist Avant de Déployer

- [ ] Plan "Free" sélectionné (pas besoin de carte bancaire)
- [ ] Base de données PostgreSQL créée
- [ ] Variable `DATABASE_URL` ajoutée (automatique si vous créez la DB dans Render)
- [ ] Toutes les variables d'environnement ajoutées
- [ ] Build Command : `pip install -r requirements-prod.txt && python manage.py collectstatic --noinput`
- [ ] Start Command : `gunicorn appointments.wsgi:application --bind 0.0.0.0:$PORT`
- [ ] Language : **Python 3** (pas Docker)

## 🚀 Après le Déploiement

Une fois déployé, vous devrez initialiser la base de données :

1. Dans le dashboard Render, ouvrez votre Web Service
2. Cliquez sur l'onglet **"Shell"**
3. Exécutez :
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

## 💡 Astuce : Éviter la Mise en Veille (Plan Free)

Le plan Free met le service en veille après 15 minutes. Pour éviter cela :

1. Créez un compte gratuit sur https://uptimerobot.com
2. Ajoutez un monitor pour votre URL Render
3. UptimeRobot pingera votre site toutes les 5 minutes
4. Votre service restera actif !

## ❓ Questions Fréquentes

**Q : Dois-je payer ?**
R : Non, le plan Free est gratuit et ne nécessite pas de carte bancaire.

**Q : Pourquoi Render demande ma carte ?**
R : Seulement si vous choisissez un plan payant. Le plan Free ne nécessite pas de carte.

**Q : Mon service est lent au démarrage ?**
R : Normal avec le plan Free. Il se réveille après 15 minutes d'inactivité, le premier accès peut prendre 30-60 secondes.

**Bon déploiement ! 🎉**

