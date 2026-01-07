# views_payment.py
# Path: appointment/views_payment.py

"""
Payment views for appointment system
Author: Auto-generated
"""

from django.contrib import messages
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext as _
from django.conf import settings as django_settings

from appointment.models import PaymentInfo, Appointment
from appointment.utils.json_context import get_generic_context_with_extra
from appointment.logger_config import get_logger

logger = get_logger(__name__)


def select_payment_method(request, object_id, id_request):
    """
    Vue pour sélectionner la méthode de paiement (carte bancaire ou virement bancaire).
    """
    payment_info = get_object_or_404(PaymentInfo, id=object_id)
    # Vérifier que l'id_request correspond pour la sécurité
    if payment_info.get_id_request() != id_request:
        raise Http404("PaymentInfo not found")
    appointment = payment_info.appointment
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        
        if payment_method == 'bank_account':
            # Redirection vers la page de sélection des portefeuilles électroniques
            return redirect('appointment:select_digital_wallet', object_id=object_id, id_request=id_request)
        elif payment_method == 'bank_transfer':
            # Redirection vers la page de virement bancaire
            return redirect('appointment:bank_transfer', object_id=object_id, id_request=id_request)
        else:
            messages.error(request, _("Veuillez sélectionner une méthode de paiement."))
    
    # Obtenir les comptes bancaires configurés
    bank_accounts = getattr(django_settings, 'BANK_ACCOUNTS', {})
    payment_card_enabled = getattr(django_settings, 'PAYMENT_CARD_ENABLED', True)
    
    extra_context = {
        'payment_info': payment_info,
        'appointment': appointment,
        'amount': payment_info.get_amount_to_pay(),
        'currency': payment_info.get_currency(),
        'service_name': appointment.get_service_name(),
        'bank_accounts': bank_accounts,
        'payment_card_enabled': payment_card_enabled,
    }
    
    context = get_generic_context_with_extra(request, extra_context, admin=False)
    
    # Utiliser Black Dashboard si disponible
    import os
    from django.conf import settings
    base_dir = getattr(settings, 'BASE_DIR', None)
    if base_dir:
        assets_path = os.path.join(base_dir, 'appointment', 'static', 'assets', 'css', 'black-dashboard.css')
        use_black_dashboard = os.path.exists(assets_path)
    else:
        use_black_dashboard = False
    
    if use_black_dashboard:
        context['BASE_TEMPLATE'] = 'base_templates/black_dashboard_base.html'
    
    return render(request, 'appointment/select_payment_method.html', context)


def card_payment(request, object_id, id_request):
    """
    Vue pour le paiement par carte bancaire.
    """
    payment_info = get_object_or_404(PaymentInfo, id=object_id)
    # Vérifier que l'id_request correspond pour la sécurité
    if payment_info.get_id_request() != id_request:
        raise Http404("PaymentInfo not found")
    appointment = payment_info.appointment
    
    stripe_public_key = getattr(django_settings, 'STRIPE_PUBLIC_KEY', '')
    payment_card_enabled = getattr(django_settings, 'PAYMENT_CARD_ENABLED', True)
    
    if not payment_card_enabled:
        messages.error(request, _("Le paiement par carte bancaire n'est pas disponible pour le moment."))
        return redirect('appointment:select_payment_method', object_id=object_id, id_request=id_request)
    
    if request.method == 'POST':
        # Ici, vous intégreriez avec l'API de paiement (Stripe, etc.)
        # Pour l'instant, on simule un paiement réussi
        messages.success(request, _("Paiement effectué avec succès!"))
        appointment.paid = True
        appointment.save()
        return redirect('appointment:payment_success', appointment_id=appointment.id)
    
    extra_context = {
        'payment_info': payment_info,
        'appointment': appointment,
        'amount': payment_info.get_amount_to_pay(),
        'currency': payment_info.get_currency(),
        'service_name': appointment.get_service_name(),
        'stripe_public_key': stripe_public_key,
    }
    
    context = get_generic_context_with_extra(request, extra_context, admin=False)
    
    # Utiliser Black Dashboard si disponible
    import os
    from django.conf import settings
    base_dir = getattr(settings, 'BASE_DIR', None)
    if base_dir:
        assets_path = os.path.join(base_dir, 'appointment', 'static', 'assets', 'css', 'black-dashboard.css')
        use_black_dashboard = os.path.exists(assets_path)
    else:
        use_black_dashboard = False
    
    if use_black_dashboard:
        context['BASE_TEMPLATE'] = 'base_templates/black_dashboard_base.html'
    
    return render(request, 'appointment/card_payment.html', context)


def bank_transfer(request, object_id, id_request):
    """
    Vue pour afficher les informations de virement bancaire.
    """
    payment_info = get_object_or_404(PaymentInfo, id=object_id)
    # Vérifier que l'id_request correspond pour la sécurité
    if payment_info.get_id_request() != id_request:
        raise Http404("PaymentInfo not found")
    appointment = payment_info.appointment
    
    bank_accounts = getattr(django_settings, 'BANK_ACCOUNTS', {})
    
    extra_context = {
        'payment_info': payment_info,
        'appointment': appointment,
        'amount': payment_info.get_amount_to_pay(),
        'currency': payment_info.get_currency(),
        'service_name': appointment.get_service_name(),
        'bank_accounts': bank_accounts,
        'id_request': id_request,
    }
    
    context = get_generic_context_with_extra(request, extra_context, admin=False)
    
    # Utiliser Black Dashboard si disponible
    import os
    from django.conf import settings
    base_dir = getattr(settings, 'BASE_DIR', None)
    if base_dir:
        assets_path = os.path.join(base_dir, 'appointment', 'static', 'assets', 'css', 'black-dashboard.css')
        use_black_dashboard = os.path.exists(assets_path)
    else:
        use_black_dashboard = False
    
    if use_black_dashboard:
        context['BASE_TEMPLATE'] = 'base_templates/black_dashboard_base.html'
    
    return render(request, 'appointment/bank_transfer.html', context)


def select_digital_wallet(request, object_id, id_request):
    """
    Vue pour sélectionner le portefeuille électronique (Bankily, Masrvi, Click, Sedad, Amanty).
    """
    payment_info = get_object_or_404(PaymentInfo, id=object_id)
    # Vérifier que l'id_request correspond pour la sécurité
    if payment_info.get_id_request() != id_request:
        raise Http404("PaymentInfo not found")
    appointment = payment_info.appointment
    
    # Liste des portefeuilles électroniques disponibles
    digital_wallets = [
        {
            'code': 'bankily',
            'name': 'Bankily',
            'icon': 'fas fa-mobile-alt',
            'description': _('Portefeuille électronique Bankily'),
        },
        {
            'code': 'masrvi',
            'name': 'Masrvi',
            'icon': 'fas fa-wallet',
            'description': _('Portefeuille électronique Masrvi'),
        },
        {
            'code': 'click',
            'name': 'Click',
            'icon': 'fas fa-mouse-pointer',
            'description': _('Portefeuille électronique Click'),
        },
        {
            'code': 'sedad',
            'name': 'Sedad',
            'icon': 'fas fa-credit-card',
            'description': _('Portefeuille électronique Sedad'),
        },
        {
            'code': 'amanty',
            'name': 'Amanty',
            'icon': 'fas fa-coins',
            'description': _('Portefeuille électronique Amanty'),
        },
    ]
    
    if request.method == 'POST':
        wallet_code = request.POST.get('wallet')
        if wallet_code:
            # Si Bankily est sélectionné, rediriger vers la page de paiement Bankily
            if wallet_code == 'bankily':
                return redirect('appointment:bankily_payment', object_id=object_id, id_request=id_request)
            # Pour les autres portefeuilles, on peut simuler ou rediriger vers leurs APIs
            # Pour l'instant, on simule un paiement réussi
            messages.success(request, _("Paiement effectué avec succès via {}!").format(
                next((w['name'] for w in digital_wallets if w['code'] == wallet_code), wallet_code)
            ))
            appointment.paid = True
            appointment.save()
            return redirect('appointment:payment_success', appointment_id=appointment.id)
        else:
            messages.error(request, _("Veuillez sélectionner un portefeuille électronique."))
    
    extra_context = {
        'payment_info': payment_info,
        'appointment': appointment,
        'amount': payment_info.get_amount_to_pay(),
        'currency': payment_info.get_currency(),
        'service_name': appointment.get_service_name(),
        'digital_wallets': digital_wallets,
        'id_request': id_request,
    }
    
    context = get_generic_context_with_extra(request, extra_context, admin=False)
    
    # Utiliser Black Dashboard si disponible
    import os
    from django.conf import settings
    base_dir = getattr(settings, 'BASE_DIR', None)
    if base_dir:
        assets_path = os.path.join(base_dir, 'appointment', 'static', 'assets', 'css', 'black-dashboard.css')
        use_black_dashboard = os.path.exists(assets_path)
    else:
        use_black_dashboard = False
    
    if use_black_dashboard:
        context['BASE_TEMPLATE'] = 'base_templates/black_dashboard_base.html'
    
    return render(request, 'appointment/select_digital_wallet.html', context)


def bankily_payment(request, object_id, id_request):
    """
    Vue pour le paiement via Bankily.
    L'utilisateur doit entrer son numéro de compte Bankily et un code à 5 chiffres.
    """
    payment_info = get_object_or_404(PaymentInfo, id=object_id)
    # Vérifier que l'id_request correspond pour la sécurité
    if payment_info.get_id_request() != id_request:
        raise Http404("PaymentInfo not found")
    appointment = payment_info.appointment
    
    # Code de paiement fixe à 5 chiffres
    payment_code = '58463'
    
    if request.method == 'POST':
        account_number = request.POST.get('account_number', '').strip()
        entered_code = request.POST.get('payment_code', '').strip()
        
        # Validation
        if not account_number:
            messages.error(request, _("Veuillez entrer votre numéro de compte Bankily."))
        elif len(account_number) < 8:
            messages.error(request, _("Le numéro de compte Bankily doit contenir au moins 8 chiffres."))
        elif entered_code != payment_code:
            messages.error(request, _("Le code de paiement est incorrect. Veuillez réessayer."))
        else:
            # Ici, vous intégreriez avec l'API Bankily pour valider et traiter le paiement
            # Pour l'instant, on simule un paiement réussi
            
            # Marquer le rendez-vous comme payé
            appointment.paid = True
            appointment.save()
            
            messages.success(request, _("Paiement effectué avec succès via Bankily!"))
            return redirect('appointment:payment_success', appointment_id=appointment.id)
    
    extra_context = {
        'payment_info': payment_info,
        'appointment': appointment,
        'amount': payment_info.get_amount_to_pay(),
        'currency': payment_info.get_currency(),
        'service_name': appointment.get_service_name(),
        'payment_code': payment_code,
        'id_request': id_request,
    }
    
    context = get_generic_context_with_extra(request, extra_context, admin=False)
    
    # Utiliser Black Dashboard si disponible
    import os
    from django.conf import settings
    base_dir = getattr(settings, 'BASE_DIR', None)
    if base_dir:
        assets_path = os.path.join(base_dir, 'appointment', 'static', 'assets', 'css', 'black-dashboard.css')
        use_black_dashboard = os.path.exists(assets_path)
    else:
        use_black_dashboard = False
    
    if use_black_dashboard:
        context['BASE_TEMPLATE'] = 'base_templates/black_dashboard_base.html'
    
    return render(request, 'appointment/bankily_payment.html', context)


def payment_success(request, appointment_id):
    """
    Vue de confirmation après paiement réussi.
    """
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    extra_context = {
        'appointment': appointment,
    }
    
    context = get_generic_context_with_extra(request, extra_context, admin=False)
    
    # Utiliser Black Dashboard si disponible
    import os
    from django.conf import settings
    base_dir = getattr(settings, 'BASE_DIR', None)
    if base_dir:
        assets_path = os.path.join(base_dir, 'appointment', 'static', 'assets', 'css', 'black-dashboard.css')
        use_black_dashboard = os.path.exists(assets_path)
    else:
        use_black_dashboard = False
    
    if use_black_dashboard:
        context['BASE_TEMPLATE'] = 'base_templates/black_dashboard_base.html'
    
    return render(request, 'appointment/payment_success.html', context)

