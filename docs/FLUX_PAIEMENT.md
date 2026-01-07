# Flux de Paiement - Explication Détaillée

## 📋 Vue d'ensemble du flux

Voici comment fonctionne le processus de paiement après une réservation :

```
1. Sélection du service
   ↓
2. Choix de la date/heure (appointment_request)
   ↓
3. Remplissage des informations client (appointment_client_information)
   ↓
4. Soumission du formulaire
   ↓
5. Création du rendez-vous (Appointment)
   ↓
6. [PAIEMENT ICI] Redirection vers la page de paiement
   ↓
7. Sélection de la méthode de paiement
   ↓
8. Paiement (carte ou virement)
   ↓
9. Confirmation de paiement
```

## 🔍 Détails du flux

### Étape 1-3 : Réservation normale
L'utilisateur :
- Sélectionne un service
- Choisit une date/heure
- Remplit ses informations personnelles

### Étape 4 : Soumission du formulaire
Quand l'utilisateur clique sur "Soumettre" dans `appointment_client_information.html`, le formulaire POST est envoyé à la vue `appointment_client_information`.

**Fichier :** `appointment/views.py`, ligne 446-478

```python
if request.method == 'POST':
    appointment_form = AppointmentForm(request.POST)
    client_data_form = ClientDataForm(request.POST)
    
    if appointment_form.is_valid() and client_data_form.is_valid():
        # ... validation et préparation des données ...
        response = create_appointment(request, ar, client_data, appointment_data)
        return response
```

### Étape 5 : Création du rendez-vous
La fonction `create_appointment` est appelée :

**Fichier :** `appointment/views.py`, ligne 430-434

```python
def create_appointment(request, appointment_request_obj, client_data, appointment_data):
    """This function creates a new appointment and redirects to the payment page or the thank-you page."""
    appointment = create_and_save_appointment(appointment_request_obj, client_data, appointment_data, request)
    notify_admin_about_appointment(appointment, appointment.client.first_name)
    return redirect_to_payment_or_thank_you_page(appointment)
```

### Étape 6 : 🎯 **REDIRECTION VERS LE PAIEMENT**

**Fichier :** `appointment/views.py`, ligne 418-427

```python
def redirect_to_payment_or_thank_you_page(appointment):
    """This function redirects to the payment page or the thank-you page based on the configuration."""
    if (APPOINTMENT_PAYMENT_URL is not None and APPOINTMENT_PAYMENT_URL != '') and appointment.service_is_paid():
        logger.info("Creating payment info and get payment url")
        payment_url = create_payment_info_and_get_url(appointment)
        return HttpResponseRedirect(payment_url)
    else:
        logger.info("Redirecting to the thank-you page")
        thank_you_url = reverse('appointment:default_thank_you', args=[appointment.id])
        return HttpResponseRedirect(thank_you_url)
```

**Conditions pour la redirection vers le paiement :**
1. ✅ `APPOINTMENT_PAYMENT_URL` doit être configuré (actuellement = `'appointment:select_payment_method'`)
2. ✅ Le service doit être payant (`appointment.service_is_paid()` retourne `True`)

**Si ces conditions sont remplies :**
- Un objet `PaymentInfo` est créé
- L'URL de paiement est générée
- L'utilisateur est redirigé vers `/payment/<object_id>/<id_request>/`

**Fichier :** `appointment/utils/db_helpers.py`, ligne 363-386

### Étape 7 : Sélection de la méthode de paiement

**URL :** `/payment/<object_id>/<id_request>/`

**Vue :** `select_payment_method` dans `appointment/views_payment.py`

L'utilisateur choisit entre :
- 💳 Paiement par carte bancaire
- 🏦 Virement bancaire

### Étape 8 : Paiement

#### Option A : Paiement par carte
**URL :** `/payment/card/<object_id>/<id_request>/`
**Vue :** `card_payment`

#### Option B : Virement bancaire
**URL :** `/payment/bank-transfer/<object_id>/<id_request>/`
**Vue :** `bank_transfer`

### Étape 9 : Confirmation
**URL :** `/payment/success/<appointment_id>/`
**Vue :** `payment_success`

## 🔧 Vérification du flux

### Pour tester que le paiement est déclenché :

1. **Vérifiez que le service est payant :**
   - Dans l'administration Django, allez dans "Services"
   - Le service doit avoir un prix > 0

2. **Vérifiez la configuration :**
   ```python
   # Dans appointments/settings.py
   APPOINTMENT_PAYMENT_URL = 'appointment:select_payment_method'
   ```

3. **Testez le flux complet :**
   - Créez un rendez-vous pour un service payant
   - Après avoir rempli les informations client et soumis
   - Vous devriez être automatiquement redirigé vers `/payment/<object_id>/<id_request>/`

## 📍 Localisation dans le code

| Étape | Fichier | Fonction/Ligne |
|-------|---------|----------------|
| Soumission formulaire | `appointment/views.py` | `appointment_client_information()` ligne 446 |
| Création rendez-vous | `appointment/views.py` | `create_appointment()` ligne 430 |
| **Redirection paiement** | `appointment/views.py` | `redirect_to_payment_or_thank_you_page()` ligne 418 |
| Création PaymentInfo | `appointment/utils/db_helpers.py` | `create_payment_info_and_get_url()` ligne 363 |
| Sélection méthode | `appointment/views_payment.py` | `select_payment_method()` |
| Paiement carte | `appointment/views_payment.py` | `card_payment()` |
| Virement | `appointment/views_payment.py` | `bank_transfer()` |

## ⚠️ Points importants

1. **Le paiement se déclenche automatiquement** après la création du rendez-vous si :
   - Le service est payant (prix > 0)
   - `APPOINTMENT_PAYMENT_URL` est configuré

2. **Si le service est gratuit** (prix = 0) :
   - L'utilisateur est redirigé directement vers la page de remerciement
   - Pas de page de paiement

3. **Si `APPOINTMENT_PAYMENT_URL` n'est pas configuré** :
   - L'utilisateur est redirigé vers la page de remerciement
   - Pas de page de paiement

## 🐛 Dépannage

**Problème :** Pas de redirection vers le paiement après réservation

**Solutions :**
1. Vérifiez que le service a un prix > 0
2. Vérifiez que `APPOINTMENT_PAYMENT_URL` est configuré dans `settings.py`
3. Vérifiez les logs Django pour voir quelle route est prise
4. Vérifiez que l'URL `/payment/...` est accessible (testez manuellement)

