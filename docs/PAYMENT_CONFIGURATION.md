# Configuration des Paiements - Mauritanie

Ce document explique comment configurer le système de paiement pour les rendez-vous en Mauritanie, incluant les cartes bancaires et les virements bancaires.

## Vue d'ensemble

Le système de paiement supporte deux méthodes principales :
1. **Paiement par carte bancaire** (Visa, Mastercard)
2. **Virement bancaire** vers les comptes bancaires configurés

## Configuration dans settings.py

### URL de paiement

L'URL de paiement est déjà configurée dans `appointments/settings.py` :

```python
APPOINTMENT_PAYMENT_URL = 'appointment:select_payment_method'
```

### Comptes bancaires

Les comptes bancaires sont configurés dans le dictionnaire `BANK_ACCOUNTS`. Par défaut, les banques suivantes sont préconfigurées :

- **BAMIS** (Banque Arabe Africaine en Mauritanie)
- **BPM** (Banque Populaire de Mauritanie)
- **Chinguitel Cash** (Paiement mobile)

### Variables d'environnement

Pour configurer vos comptes bancaires, créez un fichier `.env` à la racine du projet avec les variables suivantes :

```env
# Compte BAMIS
BANK_BAMIS_ACCOUNT=000000000000
BANK_BAMIS_IBAN=MR00XXXXXXXXXXXXXXXXXXXXXXXXX
BANK_BAMIS_SWIFT=XXXXXXXX

# Compte BPM
BANK_BPM_ACCOUNT=000000000000
BANK_BPM_IBAN=MR00XXXXXXXXXXXXXXXXXXXXXXXXX
BANK_BPM_SWIFT=XXXXXXXX

# Chinguitel Cash
CHINGUITEL_CASH_NUMBER=+222XXXXXXXX

# Configuration des cartes bancaires
PAYMENT_CARD_ENABLED=True
STRIPE_PUBLIC_KEY=pk_test_xxxxxxxxxxxxx
STRIPE_SECRET_KEY=sk_test_xxxxxxxxxxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxx
```

### Modification des comptes bancaires

Pour ajouter ou modifier des comptes bancaires, éditez le dictionnaire `BANK_ACCOUNTS` dans `appointments/settings.py` :

```python
BANK_ACCOUNTS = {
    'VOTRE_BANQUE': {
        'name': 'Nom de votre banque',
        'account_number': os.getenv('BANK_VOTRE_BANQUE_ACCOUNT', ''),
        'iban': os.getenv('BANK_VOTRE_BANQUE_IBAN', ''),
        'swift': os.getenv('BANK_VOTRE_BANQUE_SWIFT', ''),
    },
    # ... autres banques
}
```

## Fonctionnement du système

### 1. Sélection de la méthode de paiement

Après la création d'un rendez-vous, si le service est payant, l'utilisateur est redirigé vers la page de sélection de méthode de paiement (`/payment/<object_id>/<id_request>/`).

### 2. Paiement par carte bancaire

Si l'utilisateur choisit le paiement par carte :
- Il est redirigé vers `/payment/card/<object_id>/<id_request>/`
- Un formulaire de paiement sécurisé s'affiche
- Actuellement, le paiement est simulé (à intégrer avec Stripe ou une autre solution)

**Note** : Pour activer le paiement par carte réel, vous devez :
1. Obtenir des clés API Stripe ou d'une autre solution de paiement
2. Configurer les clés dans votre fichier `.env`
3. Intégrer l'API de paiement dans la vue `card_payment`

### 3. Virement bancaire

Si l'utilisateur choisit le virement bancaire :
- Il est redirigé vers `/payment/bank-transfer/<object_id>/<id_request>/`
- Les informations des comptes bancaires configurés s'affichent
- Un code de référence unique est généré pour identifier le paiement
- L'utilisateur peut copier facilement les informations bancaires

### 4. Confirmation de paiement

Après un paiement réussi (actuellement simulé pour les cartes), l'utilisateur est redirigé vers `/payment/success/<appointment_id>/`.

Pour les virements bancaires, le paiement doit être marqué manuellement comme payé dans l'interface d'administration une fois le virement confirmé.

## Intégration avec Stripe (Optionnel)

Pour intégrer Stripe pour les paiements par carte :

1. Installez Stripe :
```bash
pip install stripe
```

2. Ajoutez vos clés dans le fichier `.env` :
```env
STRIPE_PUBLIC_KEY=pk_live_xxxxxxxxxxxxx
STRIPE_SECRET_KEY=sk_live_xxxxxxxxxxxxx
```

3. Modifiez la vue `card_payment` dans `appointment/views_payment.py` pour intégrer l'API Stripe.

## Autres solutions de paiement

Vous pouvez intégrer d'autres solutions de paiement courantes en Mauritanie :
- **Orange Money**
- **Mauritel Money**
- **Autres solutions de paiement mobile**

Pour cela, créez de nouvelles vues similaires à `card_payment` et ajoutez-les au template de sélection de méthode de paiement.

## Marquage manuel des paiements par virement

Pour marquer un rendez-vous comme payé après un virement bancaire :

1. Connectez-vous à l'interface d'administration Django
2. Allez dans "Appointments" > "Appointments"
3. Trouvez le rendez-vous concerné
4. Cochez la case "Paid" et sauvegardez

Vous pouvez également ajouter une fonctionnalité pour permettre aux utilisateurs de télécharger une preuve de virement qui sera vérifiée par un administrateur.

## Sécurité

- Tous les paiements sont traités de manière sécurisée
- Les informations bancaires sont stockées dans des variables d'environnement (jamais dans le code)
- Les codes de référence uniques permettent de traçabilité
- Le système est prêt pour l'intégration avec des APIs de paiement sécurisées (HTTPS requis)

## Support

Pour toute question ou problème avec la configuration des paiements, consultez la documentation de votre solution de paiement ou contactez le support technique.

