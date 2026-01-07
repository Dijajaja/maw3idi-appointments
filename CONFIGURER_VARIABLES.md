# 📝 Guide pour Configurer les Variables d'Environnement Render

## 🔑 Variables à Configurer

### 1. EMAIL_HOST_USER
**Votre adresse email Gmail**

Exemple :
```
EMAIL_HOST_USER=monemail@gmail.com
```

**Remplacez** `monemail@gmail.com` par votre vraie adresse Gmail.

---

### 2. EMAIL_HOST_PASSWORD
**Mot de passe d'application Gmail** (⚠️ PAS votre mot de passe Gmail normal !)

#### Comment Obtenir un Mot de Passe d'Application Gmail :

1. **Allez sur** : https://myaccount.google.com/apppasswords
   - Ou : Google Account → Sécurité → Validation en deux étapes → Mots de passe des applications

2. **Activez la validation en deux étapes** (si ce n'est pas déjà fait) :
   - C'est obligatoire pour créer un mot de passe d'application
   - Allez dans : https://myaccount.google.com/security
   - Activez "Validation en deux étapes"

3. **Créez un mot de passe d'application** :
   - Allez sur : https://myaccount.google.com/apppasswords
   - Sélectionnez "Autre (nom personnalisé)"
   - Tapez : "Render Django Appointment"
   - Cliquez sur "Générer"
   - **Copiez le mot de passe** (16 caractères, espaces ou sans espaces)

4. **Utilisez ce mot de passe** dans Render :
   ```
   EMAIL_HOST_PASSWORD=abcd efgh ijkl mnop
   ```
   (Vous pouvez mettre avec ou sans espaces, les deux fonctionnent)

**⚠️ Important :** 
- Ne partagez JAMAIS ce mot de passe
- Ne l'utilisez que pour cette application
- Si vous le perdez, créez-en un nouveau

---

### 3. ADMIN_EMAIL
**Email de l'administrateur** (celui qui recevra les notifications d'erreur)

Exemple :
```
ADMIN_EMAIL=admin@example.com
```

**Ou utilisez votre email personnel :**
```
ADMIN_EMAIL=monemail@gmail.com
```

---

### 4. ADMIN_USERNAME
**Nom d'utilisateur pour se connecter à l'admin Django**

Exemple :
```
ADMIN_USERNAME=admin
```

**Vous pouvez choisir n'importe quel nom :**
```
ADMIN_USERNAME=superadmin
ADMIN_USERNAME=maw3idi_admin
```

---

### 5. ADMIN_PASSWORD
**Mot de passe pour se connecter à l'admin Django**

⚠️ **Choisissez un mot de passe fort et sécurisé !**

Exemple :
```
ADMIN_PASSWORD=MonMotDePasseSecurise123!
```

**Recommandations pour un mot de passe fort :**
- Au moins 12 caractères
- Mélangez majuscules, minuscules, chiffres et symboles
- Ne réutilisez pas un mot de passe que vous utilisez ailleurs

**Exemples de bons mots de passe :**
```
ADMIN_PASSWORD=Maw3idi@2024!Secure
ADMIN_PASSWORD=Admin123!@#Secure
ADMIN_PASSWORD=SuperAdmin2024!Maw3idi
```

---

## 📋 Exemple Complet

Voici un exemple avec des valeurs fictives (remplacez par les vôtres) :

```
EMAIL_HOST_USER=jean.dupont@gmail.com
EMAIL_HOST_PASSWORD=abcd efgh ijkl mnop
ADMIN_EMAIL=jean.dupont@gmail.com
ADMIN_USERNAME=admin
ADMIN_PASSWORD=Maw3idi@2024!Secure
```

---

## ✅ Checklist

- [ ] J'ai activé la validation en deux étapes sur mon compte Gmail
- [ ] J'ai créé un mot de passe d'application Gmail
- [ ] J'ai copié le mot de passe d'application (16 caractères)
- [ ] J'ai choisi un mot de passe admin fort et sécurisé
- [ ] J'ai rempli toutes les variables dans Render

---

## 🚨 Sécurité

**Ne partagez JAMAIS :**
- ❌ Votre mot de passe Gmail normal
- ❌ Votre mot de passe d'application
- ❌ Votre mot de passe admin
- ❌ Ces variables d'environnement

**Ces informations sont sensibles et doivent rester secrètes !**

---

## 💡 Astuce

Si vous avez des problèmes avec Gmail :
- Vérifiez que la validation en deux étapes est activée
- Vérifiez que vous utilisez bien un "mot de passe d'application", pas votre mot de passe normal
- Le mot de passe d'application doit avoir 16 caractères

**Bon remplissage ! 🔒**

