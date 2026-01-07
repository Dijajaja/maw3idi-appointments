# 📸 Guide pour Capturer les Pages du Site

## ⚠️ Problème : Pages Blanches

Si les captures sont blanches, c'est que **le serveur Django n'est pas démarré**.

## ✅ Solution : Démarrer le Serveur d'abord

### Étape 1 : Démarrer le Serveur Django

Ouvrez un **nouveau terminal** et exécutez :

```bash
cd C:\Users\PC\django-appointment
python manage.py runserver
```

Vous devriez voir :
```
Starting development server at http://127.0.0.1:8000/
```

**⚠️ IMPORTANT : Laissez ce terminal ouvert !**

### Étape 2 : Vérifier que le serveur fonctionne

Ouvrez votre navigateur et allez sur :
```
http://localhost:8000/fr/
```

Vous devriez voir la page d'accueil avec les services.

### Étape 3 : Capturer les pages

Dans un **autre terminal**, exécutez :

```bash
cd C:\Users\PC\django-appointment\docs\screenshots
python capture_toutes_pages.py
```

## 🔄 Alternative : Script Automatique

Le script peut démarrer le serveur automatiquement, mais c'est moins fiable.

## 📝 Notes

- Le serveur doit rester **démarré** pendant toute la capture
- Les pages blanches = serveur non démarré ou inaccessible
- Vérifiez toujours que `http://localhost:8000/fr/` fonctionne dans votre navigateur avant de capturer

## 🛠️ Dépannage

**Erreur "Connection refused"** :
→ Le serveur n'est pas démarré

**Pages blanches** :
→ Le serveur n'a pas fini de charger ou il y a une erreur

**Timeout** :
→ Le serveur met trop de temps à répondre, vérifiez qu'il fonctionne bien

