# views.py
# Path: appointment/views.py

"""
Author: Adams Pierre David
Since: 1.0.0
"""

from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash, authenticate
from django.contrib.auth.forms import SetPasswordForm, PasswordChangeForm, AuthenticationForm
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone, translation
from django.utils.encoding import force_str
from django.utils.formats import date_format
from django.utils.http import urlsafe_base64_decode
from django.utils.timezone import get_current_timezone_name
from django.utils.translation import gettext as _

from appointment.forms import AppointmentForm, AppointmentRequestForm, ClientDataForm, SlotForm
from appointment.logger_config import get_logger
from appointment.models import (
    Appointment, AppointmentRequest, AppointmentRescheduleHistory, Config, DayOff, EmailVerificationCode,
    PasswordResetToken, Service,
    StaffMember
)
from appointment.settings import check_q_cluster
from appointment.utils.db_helpers import (
    can_appointment_be_rescheduled, check_day_off_for_staff, create_and_save_appointment, create_new_user,
    create_payment_info_and_get_url, get_non_working_days_for_staff, get_user_by_email, get_user_model,
    get_website_name, get_weekday_num_from_date, is_working_day, staff_change_allowed_on_reschedule,
    username_in_user_model
)
from appointment.utils.email_ops import notify_admin_about_appointment, notify_admin_about_reschedule, \
    send_reschedule_confirmation_email, \
    send_thank_you_email
from appointment.utils.session import get_appointment_data_from_session, handle_existing_email
from appointment.utils.view_helpers import get_locale
from appointment.decorators import require_user_authenticated, require_superuser
from .decorators import require_ajax
from .email_sender.email_sender import has_required_email_settings
from .messages_ import passwd_error, passwd_set_successfully
from .services import get_appointments_and_slots, get_available_slots_for_staff
from .settings import (APPOINTMENT_PAYMENT_URL, APPOINTMENT_THANK_YOU_URL)
from .utils.date_time import DATE_FORMATS, convert_str_to_date
from .utils.error_codes import ErrorCode
from .utils.ics_utils import generate_ics_file
from .utils.json_context import get_generic_context, get_generic_context_with_extra, json_response
import json
import calendar

CLIENT_MODEL = get_user_model()

logger = get_logger(__name__)


@require_ajax
def get_available_slots_ajax(request):
    """This view function handles AJAX requests to get available slots for a selected date."""
    slot_form = SlotForm(request.GET)
    error_code = 0
    if not slot_form.is_valid():
        custom_data = {'error': True, 'available_slots': [], 'date_chosen': '', 'date_iso': ''}
        if 'selected_date' in slot_form.errors:
            error_code = ErrorCode.PAST_DATE
        elif 'staff_member' in slot_form.errors:
            error_code = ErrorCode.STAFF_ID_REQUIRED
        message = list(slot_form.errors.as_data().items())[0][1][0].messages[0]
        return json_response(message=message, custom_data=custom_data, success=False,
                             error_code=error_code)

    selected_date = slot_form.cleaned_data['selected_date']
    sm = slot_form.cleaned_data['staff_member']
    current_lang = translation.get_language()
    format_string = DATE_FORMATS.get(current_lang, "D, F j, Y")
    date_chosen = date_format(selected_date, format_string, use_l10n=True)
    custom_data = {
        'date_chosen': date_chosen,
        'date_iso': selected_date.isoformat()
    }

    days_off_exist = check_day_off_for_staff(staff_member=sm, date=selected_date)
    if days_off_exist:
        message = _("Jour de congé. Veuillez sélectionner une autre date !")
        custom_data['available_slots'] = []
        custom_data['date_iso'] = selected_date.isoformat()
        return json_response(message=message, custom_data=custom_data, success=False, error_code=ErrorCode.INVALID_DATE)
    
    weekday_num = get_weekday_num_from_date(selected_date)
    is_working_day_ = is_working_day(staff_member=sm, day=weekday_num)

    custom_data['staff_member'] = sm.get_staff_member_name()
    if not is_working_day_:
        message = _("Jour de congé. Veuillez sélectionner une autre date !")
        custom_data['available_slots'] = []
        return json_response(message=message, custom_data=custom_data, success=False, error_code=ErrorCode.INVALID_DATE)

    # Utiliser get_available_slots_for_staff qui prend en compte les heures de travail du staff member
    available_slots = get_available_slots_for_staff(selected_date, sm, weekday_num)
    custom_data['available_slots'] = available_slots
    return json_response(message=_("Créneaux disponibles récupérés avec succès"), custom_data=custom_data, success=True)


@require_ajax
def get_next_available_date_ajax(request, service_id):
    """This view function handles AJAX requests to get the next available date for a service."""
    service = get_object_or_404(Service, pk=service_id)
    staff_member_id = request.GET.get('staff_member')
    
    if not staff_member_id or staff_member_id == 'none':
        return json_response(_("Aucun membre du personnel sélectionné"), success=False, 
                           error_code=ErrorCode.STAFF_ID_REQUIRED)
    
    try:
        staff_member = StaffMember.objects.get(pk=staff_member_id)
    except StaffMember.DoesNotExist:
        return json_response(_("Membre du personnel introuvable"), success=False, 
                           error_code=ErrorCode.STAFF_ID_REQUIRED)
    
    today = timezone.now().date()
    current_date = today
    max_days = 365
    
    for _ in range(max_days):
        weekday_num = get_weekday_num_from_date(current_date)
        if is_working_day(staff_member=staff_member, day=weekday_num):
            if not check_day_off_for_staff(staff_member=staff_member, date=current_date):
                appointments, available_slots = get_appointments_and_slots(current_date, staff_member)
                if available_slots:
                    return json_response(_("Prochaine date disponible trouvée"), 
                                       custom_data={'next_available_date': current_date.isoformat()}, 
                                       success=True)
        current_date += timedelta(days=1)
    
    return json_response(_("Aucune date disponible trouvée dans les 365 prochains jours"), success=False)


@require_ajax
def get_non_working_days_ajax(request):
    """AJAX endpoint pour récupérer les jours non travaillés d'un membre du personnel."""
    staff_member_id = request.GET.get('staff_member')
    
    if not staff_member_id or staff_member_id == 'none':
        return json_response(_("Aucun membre du personnel sélectionné"), success=False,
                           error_code=ErrorCode.STAFF_ID_REQUIRED)
    
    non_working_days = get_non_working_days_for_staff(staff_member_id)
    return json_response(_("Jours non travaillés récupérés avec succès"), 
                        custom_data={'non_working_days': non_working_days}, success=True)


def appointment_request(request, service_id=None, staff_member_id=None):
    """This view function handles requests to book an appointment for a service."""
    service = get_object_or_404(Service, pk=service_id) if service_id else None
    staff_member = get_object_or_404(StaffMember, pk=staff_member_id) if staff_member_id else None
    
    # Stocker le service_id dans la session pour pouvoir le récupérer plus tard
    if service:
        request.session['current_service_id'] = service.id
        request.session.modified = True  # S'assurer que la session est sauvegardée
        logger.info(f"Service ID stocké dans la session: {service.id}")
        logger.info(f"Session actuelle - current_service_id: {request.session.get('current_service_id')}")
    
    all_staff_members = StaffMember.objects.all()
    label = _("Sélectionnez un membre du personnel")
    
    # Variables nécessaires pour le template
    from appointment.utils.db_helpers import get_website_name
    from django.utils import timezone as django_timezone
    from django.conf import settings as django_settings
    
    # Récupérer le timezone depuis les settings Django
    timezoneTxt = getattr(django_settings, 'TIME_ZONE', 'UTC')
    date_chosen = ""  # Sera rempli par JavaScript quand une date est sélectionnée
    ar_id_request = ""  # Vide pour une nouvelle réservation
    rescheduled_date = None  # Pas de reprogrammation pour une nouvelle réservation
    website_name = get_website_name()
    
    extra_context = {
        'service': service,
        'all_staff_members': all_staff_members,
        'staff_member': staff_member,
        'label': label,
        'timezoneTxt': timezoneTxt,
        'date_chosen': date_chosen,
        'ar_id_request': ar_id_request,
        'rescheduled_date': rescheduled_date,
        'page_header': None,  # Utilisera service.name par défaut
        'page_description': _("Consultez nos disponibilités et réservez la date et l'heure qui vous conviennent"),
        'website_name': website_name,
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
        assets_path = os.path.join('appointment', 'static', 'assets', 'css', 'black-dashboard.css')
        use_black_dashboard = os.path.exists(assets_path)
    
    if use_black_dashboard:
        context['BASE_TEMPLATE'] = 'base_templates/black_dashboard_base.html'
    
    return render(request, 'appointment/appointments.html', context=context)


def appointment_request_submit(request):
    """This view function handles the submission of the appointment request form."""
    service = None  # Initialiser la variable service
    
    if request.method == 'POST':
        # Récupérer le service_id depuis POST en premier
        service_id = request.POST.get('service')
        logger.info(f"=== SOUMISSION DU FORMULAIRE ===")
        logger.info(f"Service ID depuis POST: {service_id}")
        logger.info(f"Données POST: {dict(request.POST)}")
        
        # Essayer de récupérer le service avant la validation du formulaire
        if service_id:
            try:
                service = Service.objects.get(pk=service_id)
                logger.info(f"✓ Service trouvé: {service.name} (ID: {service.id})")
            except (Service.DoesNotExist, ValueError) as e:
                logger.error(f"✗ Service avec l'ID {service_id} non trouvé: {e}")
                messages.error(request, _("Le service sélectionné n'existe pas ou n'est plus disponible."))
        else:
            logger.error("✗ Aucun service_id trouvé dans les données POST")
            
            # Essayer de récupérer depuis la session en premier (plus fiable)
            service_id_from_session = request.session.get('current_service_id')
            if service_id_from_session:
                logger.info(f"Tentative de récupération du service depuis la session: {service_id_from_session}")
                try:
                    service = Service.objects.get(pk=service_id_from_session)
                    logger.info(f"✓ Service récupéré depuis la session: {service.name} (ID: {service.id})")
                except (Service.DoesNotExist, ValueError) as e:
                    logger.error(f"✗ Service avec ID {service_id_from_session} non trouvé depuis la session: {e}")
            
            # Si pas trouvé dans la session, essayer depuis l'URL de référence
            if not service:
                referer = request.META.get('HTTP_REFERER', '')
                logger.info(f"URL de référence: {referer}")
                if referer:
                    # Extraire service_id depuis l'URL de référence si possible
                    import re
                    # Chercher /request/123/ ou /request/123 ou /fr/request/123/
                    match = re.search(r'(?:/fr)?/request/(\d+)/?', referer)
                    if match:
                        service_id = match.group(1)
                        logger.info(f"Service ID extrait de l'URL de référence: {service_id}")
                        try:
                            service = Service.objects.get(pk=service_id)
                            logger.info(f"✓ Service récupéré depuis l'URL de référence: {service.name} (ID: {service.id})")
                            # Stocker dans la session pour la prochaine fois
                            request.session['current_service_id'] = service.id
                        except (Service.DoesNotExist, ValueError) as e:
                            logger.error(f"✗ Service avec ID {service_id} non trouvé depuis l'URL de référence: {e}")
                    else:
                        logger.warning("Aucun service_id trouvé dans l'URL de référence")
        
        form = AppointmentRequestForm(request.POST)
        if form.is_valid():
            staff_member = form.cleaned_data['staff_member']
            # StaffMember est déjà importé en haut du fichier (ligne 30)
            staff_exists = StaffMember.objects.filter(id=staff_member.id).exists()
            if not staff_exists:
                messages.error(request, _("Le membre du personnel sélectionné n'existe pas."))
            else:
                logger.info(f"✓ Formulaire valide - date: {form.cleaned_data['date']} start_time: {form.cleaned_data['start_time']} end_time: "
                          f"{form.cleaned_data['end_time']} service: {form.cleaned_data['service']} staff: {staff_member}")
                ar = form.save()
                request.session[f'appointment_completed_{ar.id_request}'] = False
                return redirect('appointment:appointment_client_information', appointment_request_id=ar.id,
                                id_request=ar.id_request)
        else:
            logger.error(f"✗ Erreurs de formulaire: {form.errors}")
            logger.error(f"Données POST complètes: {dict(request.POST)}")
            
            # Afficher les erreurs spécifiques pour chaque champ
            for field, errors in form.errors.items():
                logger.error(f"  - Champ '{field}': {errors}")
            
            # Si le service n'a pas été récupéré avant, essayer de le récupérer depuis plusieurs sources
            if not service:
                # 1. Essayer depuis POST brut
                service_id_from_post = request.POST.get('service')
                logger.info(f"Tentative de récupération du service depuis POST brut: {service_id_from_post}")
                if service_id_from_post:
                    try:
                        service = Service.objects.get(pk=service_id_from_post)
                        logger.info(f"✓ Service récupéré depuis POST brut après erreur de formulaire: {service.name} (ID: {service.id})")
                    except (Service.DoesNotExist, ValueError) as e:
                        logger.error(f"✗ Service avec ID {service_id_from_post} non trouvé depuis POST brut: {e}")
                
                # 2. Si toujours pas trouvé, essayer depuis la session
                if not service:
                    service_id_from_session = request.session.get('current_service_id')
                    if service_id_from_session:
                        logger.info(f"Tentative de récupération du service depuis la session (après erreur): {service_id_from_session}")
                        try:
                            service = Service.objects.get(pk=service_id_from_session)
                            logger.info(f"✓ Service récupéré depuis la session après erreur: {service.name} (ID: {service.id})")
                        except (Service.DoesNotExist, ValueError) as e:
                            logger.error(f"✗ Service avec ID {service_id_from_session} non trouvé depuis la session: {e}")
                
                # 3. Si toujours pas trouvé, essayer depuis l'URL de référence
                if not service:
                    referer = request.META.get('HTTP_REFERER', '')
                    if referer:
                        import re
                        match = re.search(r'(?:/fr)?/request/(\d+)/?', referer)
                        if match:
                            service_id = match.group(1)
                            try:
                                service = Service.objects.get(pk=service_id)
                                logger.info(f"✓ Service récupéré depuis l'URL de référence après erreur: {service.name} (ID: {service.id})")
                                request.session['current_service_id'] = service.id
                            except (Service.DoesNotExist, ValueError) as e:
                                logger.error(f"✗ Service avec ID {service_id} non trouvé depuis l'URL de référence: {e}")
                
                if not service:
                    logger.error("✗ Service non trouvé après toutes les tentatives (POST, session, URL de référence)")
            
            # Créer un message d'erreur plus détaillé
            error_details = []
            for field, errors in form.errors.items():
                error_details.append(f"{field}: {', '.join(errors)}")
            
            if error_details:
                detailed_message = _('Il y a eu une erreur dans votre soumission. ') + ' ' + ' | '.join(error_details)
                messages.error(request, detailed_message)
            else:
                messages.error(request, _('Il y a eu une erreur dans votre soumission. Veuillez vérifier le formulaire et réessayer.'))
    else:
        form = AppointmentRequestForm()

    # Dernière tentative de récupération du service si toujours pas trouvé
    if not service:
        logger.warning("⚠️ Service toujours non trouvé, dernière tentative de récupération...")
        logger.info(f"Contenu de la session: {dict(request.session)}")
        # Essayer depuis la session
        service_id_from_session = request.session.get('current_service_id')
        logger.info(f"Service ID depuis la session: {service_id_from_session}")
        if service_id_from_session:
            logger.info(f"Dernière tentative: récupération depuis la session: {service_id_from_session}")
            try:
                service = Service.objects.get(pk=service_id_from_session)
                logger.info(f"✓ Service récupéré depuis la session (dernière tentative): {service.name} (ID: {service.id})")
            except (Service.DoesNotExist, ValueError) as e:
                logger.error(f"✗ Service avec ID {service_id_from_session} non trouvé depuis la session: {e}")
        
        # Si toujours pas trouvé, essayer depuis l'URL de référence
        if not service:
            referer = request.META.get('HTTP_REFERER', '')
            if referer:
                import re
                match = re.search(r'(?:/fr)?/request/(\d+)/?', referer)
                if match:
                    service_id = match.group(1)
                    try:
                        service = Service.objects.get(pk=service_id)
                        logger.info(f"✓ Service récupéré depuis l'URL de référence (dernière tentative): {service.name} (ID: {service.id})")
                        request.session['current_service_id'] = service.id
                    except (Service.DoesNotExist, ValueError) as e:
                        logger.error(f"✗ Service avec ID {service_id} non trouvé depuis l'URL de référence: {e}")
    
    # Préparer le contexte avec le service si disponible
    extra_context = {'form': form}
    if service:
        extra_context['service'] = service
        # Récupérer aussi les staff members pour le template
        # StaffMember est déjà importé en haut du fichier (ligne 30)
        extra_context['all_staff_members'] = StaffMember.objects.all()
        extra_context['label'] = _("Sélectionnez un membre du personnel")
        logger.info(f"✓ Service passé au contexte: {service.name} (ID: {service.id})")
    else:
        logger.error("❌ Service NON passé au contexte - le calendrier ne sera pas affiché")
        # Ne pas rediriger si on est en POST avec des erreurs de formulaire - on veut afficher les erreurs
        # Rediriger seulement si c'est une requête GET sans service
        if request.method == 'GET':
            messages.error(request, _("Impossible de charger la page de réservation. Veuillez sélectionner un service depuis la page d'accueil."))
            # redirect est déjà importé en haut du fichier (ligne 16)
            return redirect('appointment:index')
        else:
            # En POST, on garde le contexte même sans service pour afficher les erreurs
            logger.error("Mode POST sans service - affichage des erreurs de formulaire (mais le calendrier ne sera pas affiché)")
    
    context = get_generic_context_with_extra(request, extra_context, admin=False)
    
    # Utiliser Black Dashboard si disponible
    import os
    from django.conf import settings
    base_dir = getattr(settings, 'BASE_DIR', None)
    if base_dir:
        assets_path = os.path.join(base_dir, 'appointment', 'static', 'assets', 'css', 'black-dashboard.css')
        use_black_dashboard = os.path.exists(assets_path)
    else:
        assets_path = os.path.join('appointment', 'static', 'assets', 'css', 'black-dashboard.css')
        use_black_dashboard = os.path.exists(assets_path)
    
    if use_black_dashboard:
        context['BASE_TEMPLATE'] = 'base_templates/black_dashboard_base.html'
    
    return render(request, 'appointment/appointments.html', context=context)


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


def create_appointment(request, appointment_request_obj, client_data, appointment_data):
    """This function creates a new appointment and redirects to the payment page or the thank-you page."""
    appointment = create_and_save_appointment(appointment_request_obj, client_data, appointment_data, request)
    notify_admin_about_appointment(appointment, appointment.client.first_name)
    return redirect_to_payment_or_thank_you_page(appointment)


def appointment_client_information(request, appointment_request_id, id_request):
    """This view function handles client information submission for an appointment."""
    ar = get_object_or_404(AppointmentRequest, pk=appointment_request_id, id_request=id_request)
    has_required_email_reminder_config = has_required_email_settings()
    
    if request.session.get(f'appointment_submitted_{id_request}', False):
        context = get_generic_context_with_extra(request, {'service_id': ar.service_id}, admin=False)
        return render(request, 'error_pages/304_already_submitted.html', context=context)

    if request.method == 'POST':
        appointment_form = AppointmentForm(request.POST)
        client_data_form = ClientDataForm(request.POST)

        if appointment_form.is_valid() and client_data_form.is_valid():
            appointment_data = appointment_form.cleaned_data
            client_data = client_data_form.cleaned_data
            payment_type = request.POST.get('payment_type')
            ar.payment_type = payment_type
            ar.save()

            # Si l'utilisateur est connecté et utilise son propre email, utiliser directement son compte
            if request.user.is_authenticated and request.user.email.lower() == client_data['email'].lower():
                logger.info(f"User is authenticated and using own email: {client_data['email']}, using existing account")
                # Mettre à jour les données client avec celles de l'utilisateur connecté
                client_data = {
                    'email': request.user.email,
                    'first_name': request.user.first_name,
                    'last_name': request.user.last_name
                }
                response = create_appointment(request, ar, client_data, appointment_data)
                request.session.setdefault(f'appointment_submitted_{id_request}', True)
                return response

            is_email_in_db = CLIENT_MODEL.objects.filter(email__exact=client_data['email']).exists()
            if is_email_in_db:
                return handle_existing_email(request, client_data, appointment_data, appointment_request_id, id_request)

            logger.info(f"Creating a new user: {client_data}")
            user = create_new_user(client_data)
            messages.success(request, _("Un compte a été créé pour vous."))

            response = create_appointment(request, ar, client_data, appointment_data)
            request.session.setdefault(f'appointment_submitted_{id_request}', True)
            return response
    else:
        appointment_form = AppointmentForm()
        client_data_form = ClientDataForm()

    extra_context = {
        'ar': ar,
        'APPOINTMENT_PAYMENT_URL': APPOINTMENT_PAYMENT_URL,
        'form': appointment_form,
        'client_data_form': client_data_form,
        'service_name': ar.service.name,
        'has_required_email_reminder_config': has_required_email_reminder_config,
    }
    context = get_generic_context_with_extra(request, extra_context, admin=False)
    
    # Utiliser Black Dashboard si disponible (comme les autres pages)
    import os
    from django.conf import settings
    base_dir = getattr(settings, 'BASE_DIR', None)
    if base_dir:
        assets_path = os.path.join(base_dir, 'appointment', 'static', 'assets', 'css', 'black-dashboard.css')
        use_black_dashboard = os.path.exists(assets_path)
    else:
        assets_path = os.path.join('appointment', 'static', 'assets', 'css', 'black-dashboard.css')
        use_black_dashboard = os.path.exists(assets_path)
    
    if use_black_dashboard:
        context['BASE_TEMPLATE'] = 'base_templates/black_dashboard_base.html'
    
    return render(request, 'appointment/appointment_client_information.html', context=context)


def verify_user_and_login(request, user, code):
    """This function verifies the user's email and logs the user in."""
    verification_code = EmailVerificationCode.objects.filter(user=user, code=code).first()
    if verification_code and verification_code.still_valid():
        verification_code.delete()
        login(request, user)
        return True
    return False


def enter_verification_code(request, appointment_request_id, id_request):
    """This view function handles the submission of the email verification code."""
    ar = get_object_or_404(AppointmentRequest, pk=appointment_request_id, id_request=id_request)
    
    if request.method == 'POST':
        code = request.POST.get('verification_code')
        user = get_user_by_email(request.session.get('email_to_verify'))
        
        if user and verify_user_and_login(request, user, code):
            appointment_data = get_appointment_data_from_session(request)
            client_data = {'email': user.email, 'first_name': user.first_name, 'last_name': user.last_name}
            response = create_appointment(request, ar, client_data, appointment_data)
            return response
        else:
            messages.error(request, _("Code de vérification invalide ou expiré."))
    
    context = get_generic_context_with_extra(request, {'ar': ar}, admin=False)
    
    # Utiliser Black Dashboard si disponible (comme les autres pages)
    import os
    from django.conf import settings
    base_dir = getattr(settings, 'BASE_DIR', None)
    if base_dir:
        assets_path = os.path.join(base_dir, 'appointment', 'static', 'assets', 'css', 'black-dashboard.css')
        use_black_dashboard = os.path.exists(assets_path)
    else:
        assets_path = os.path.join('appointment', 'static', 'assets', 'css', 'black-dashboard.css')
        use_black_dashboard = os.path.exists(assets_path)
    
    if use_black_dashboard:
        context['BASE_TEMPLATE'] = 'base_templates/black_dashboard_base.html'
    
    return render(request, 'appointment/enter_verification_code.html', context)


def default_thank_you(request, appointment_id):
    """This view function handles the default 'thank you' page."""
    appointment = get_object_or_404(Appointment, pk=appointment_id)
    ar = appointment.appointment_request
    email = appointment.client.email
    appointment_details = {
        _('Service'): appointment.get_service_name(),
        _('Appointment Date'): appointment.get_appointment_date(),
        _('Appointment Time'): appointment.appointment_request.start_time,
        _('Duration'): appointment.get_service_duration()
    }
    account_details = {
        _('Email address'): email,
    }
    if username_in_user_model():
        account_details[_('Username')] = appointment.client.username

    if appointment.client.has_usable_password():
        account_details = None

    send_thank_you_email(ar=ar, user=appointment.client, email=email, appointment_details=appointment_details,
                         account_details=account_details, request=request)
    extra_context = {
        'appointment': appointment,
    }
    context = get_generic_context_with_extra(request, extra_context, admin=False)
    return render(request, 'appointment/default_thank_you.html', context=context)


def set_passwd(request, uidb64, token):
    """This view function handles password reset."""
    extra = {
        'page_title': _("Erreur"),
        'page_message': passwd_error,
        'page_description': _("Veuillez réessayer de réinitialiser votre mot de passe ou contacter le support."),
    }
    context_ = get_generic_context_with_extra(request, extra, admin=False)
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = get_user_model().objects.get(pk=uid)
        token_verification = PasswordResetToken.verify_token(user, token)
        if token_verification is not None:
            if request.method == 'POST':
                form = SetPasswordForm(user, request.POST)
                if form.is_valid():
                    form.save()
                    messages.success(request, passwd_set_successfully)
                    login(request, user)
                    return redirect('appointment:index')
            else:
                form = SetPasswordForm(user)
            context_ = get_generic_context_with_extra(request, {'form': form}, admin=False)
            return render(request, 'appointment/set_password.html', context_)
        else:
            return render(request, 'error_pages/404_not_found.html', context_, status=404)
    except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
        return render(request, 'error_pages/404_not_found.html', context_, status=404)


def prepare_reschedule_appointment(request, id_request):
    """This view function prepares the reschedule appointment page."""
    from appointment.utils.view_helpers import is_ajax
    
    try:
        ar = AppointmentRequest.objects.get(id_request=id_request)
    except AppointmentRequest.DoesNotExist:
        # Si l'id_request n'est pas trouvé, essayer de voir s'il correspond à un Appointment
        # pour suggérer une solution
        try:
            appointment = Appointment.objects.get(id_request=id_request)
            error_msg = _("Le lien de reprogrammation est invalide. Veuillez utiliser le lien de reprogrammation depuis la page 'Mes rendez-vous'.")
            if is_ajax(request):
                return json_response(error_msg, status=404, success=False)
            messages.error(request, error_msg)
            if request.user.is_authenticated:
                return redirect('appointment:my_appointments')
            return redirect('appointment:index')
        except Appointment.DoesNotExist:
            error_msg = _("Le rendez-vous demandé n'existe pas ou a été supprimé.")
            if is_ajax(request):
                return json_response(error_msg, status=404, success=False)
            messages.error(request, error_msg)
            if request.user.is_authenticated:
                return redirect('appointment:my_appointments')
            return redirect('appointment:index')
    
    # Vérifier que l'utilisateur est authentifié et peut reprogrammer ce rendez-vous
    if not request.user.is_authenticated:
        error_msg = _("Vous devez être connecté pour reprogrammer un rendez-vous.")
        if is_ajax(request):
            return json_response(error_msg, status=401, success=False, error_code=ErrorCode.NOT_AUTHORIZED)
        messages.error(request, error_msg)
        return redirect('appointment:login')
    
    # Vérifier que l'utilisateur peut reprogrammer ce rendez-vous (c'est son propre rendez-vous ou il est staff/superuser)
    try:
        appointment = Appointment.objects.get(appointment_request=ar)
        if appointment.client != request.user and not (request.user.is_staff or request.user.is_superuser):
            error_msg = _("Vous n'êtes pas autorisé à reprogrammer ce rendez-vous.")
            if is_ajax(request):
                return json_response(error_msg, status=403, success=False, error_code=ErrorCode.NOT_AUTHORIZED)
            messages.error(request, error_msg)
            return redirect('appointment:my_appointments')
    except Appointment.DoesNotExist:
        # Si l'appointment n'existe pas encore, c'est peut-être normal (en cours de création)
        pass
    
    if not can_appointment_be_rescheduled(ar):
        error_msg = _("Ce rendez-vous ne peut plus être reprogrammé.")
        if is_ajax(request):
            return json_response(error_msg, status=403, success=False)
        messages.error(request, error_msg)
        return redirect('appointment:index')
    
    reschedule_history = AppointmentRescheduleHistory.objects.filter(
        appointment_request=ar,
        reschedule_status='pending'
    ).first()
    
    if reschedule_history:
        rescheduled_date = reschedule_history.date
        rescheduled_start_time = reschedule_history.start_time
        rescheduled_end_time = reschedule_history.end_time
        rescheduled_staff_member = reschedule_history.staff_member
    else:
        rescheduled_date = None
        rescheduled_start_time = None
        rescheduled_end_time = None
        rescheduled_staff_member = None
    
    all_staff_members = StaffMember.objects.all()
    label = _("Sélectionnez un membre du personnel")
    
    extra_context = {
        'service': ar.service,
        'all_staff_members': all_staff_members,
        'staff_member': rescheduled_staff_member or ar.staff_member,
        'label': label,
        'rescheduled_date': rescheduled_date,
        'rescheduled_start_time': rescheduled_start_time,
        'rescheduled_end_time': rescheduled_end_time,
        'id_request': id_request,
        'ar': ar,
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
        assets_path = os.path.join('appointment', 'static', 'assets', 'css', 'black-dashboard.css')
        use_black_dashboard = os.path.exists(assets_path)
    
    if use_black_dashboard:
        context['BASE_TEMPLATE'] = 'base_templates/black_dashboard_base.html'
    
    return render(request, 'appointment/appointments.html', context=context)


def reschedule_appointment_submit(request):
    """This view function handles the submission of the reschedule appointment form."""
    id_request = request.POST.get('id_request')
    ar = get_object_or_404(AppointmentRequest, id_request=id_request)
    
    if not can_appointment_be_rescheduled(ar):
        messages.error(request, _("Ce rendez-vous ne peut plus être reprogrammé."))
        return redirect('appointment:index')
    
    form = AppointmentRequestForm(request.POST)
    if form.is_valid():
        reschedule_history, created = AppointmentRescheduleHistory.objects.get_or_create(
            appointment_request=ar,
            reschedule_status='pending',
            defaults={
                'date': form.cleaned_data['date'],
                'start_time': form.cleaned_data['start_time'],
                'end_time': form.cleaned_data['end_time'],
                'staff_member': form.cleaned_data['staff_member'],
            }
        )
        
        if not created:
            reschedule_history.date = form.cleaned_data['date']
            reschedule_history.start_time = form.cleaned_data['start_time']
            reschedule_history.end_time = form.cleaned_data['end_time']
            reschedule_history.staff_member = form.cleaned_data['staff_member']
            reschedule_history.save()
        
        return redirect('appointment:confirm_reschedule', id_request=id_request)
    else:
        messages.error(request, _("Erreur dans le formulaire. Veuillez réessayer."))
        return redirect('appointment:prepare_reschedule_appointment', id_request=id_request)


def confirm_reschedule(request, id_request):
    """This view function confirms the reschedule of an appointment."""
    ar = get_object_or_404(AppointmentRequest, id_request=id_request)
    reschedule_history = get_object_or_404(AppointmentRescheduleHistory, 
                                          appointment_request=ar, 
                                          reschedule_status='pending')
    
    previous_details = {
        'date': ar.date,
        'start_time': ar.start_time,
        'end_time': ar.end_time,
        'staff_member': ar.staff_member,
    }

    ar.date = reschedule_history.date
    ar.start_time = reschedule_history.start_time
    ar.end_time = reschedule_history.end_time
    ar.staff_member = reschedule_history.staff_member
    ar.save(update_fields=['date', 'start_time', 'end_time', 'staff_member'])

    reschedule_history.date = previous_details['date']
    reschedule_history.start_time = previous_details['start_time']
    reschedule_history.end_time = previous_details['end_time']
    reschedule_history.staff_member = previous_details['staff_member']
    reschedule_history.reschedule_status = 'confirmed'
    reschedule_history.save(update_fields=['date', 'start_time', 'end_time', 'staff_member', 'reschedule_status'])

    messages.success(request, _("Rendez-vous reprogrammé avec succès"))
    client_name = Appointment.objects.get(appointment_request=ar).client.get_full_name()
    notify_admin_about_reschedule(reschedule_history, ar, client_name)
    return redirect('appointment:default_thank_you', appointment_id=ar.appointment.id)


def index(request):
    """Display the homepage with a list of available services."""
    services = Service.objects.all()
    website_name = get_website_name()
    page_title = f"{website_name} - {_('Services')}"
    page_description = _("Réservez un rendez-vous pour l'un de nos services à {wn}.").format(wn=website_name)
    
    import os
    from django.conf import settings
    
    base_dir = getattr(settings, 'BASE_DIR', None)
    if base_dir:
        assets_path = os.path.join(base_dir, 'appointment', 'static', 'assets', 'css', 'black-dashboard.css')
        use_black_dashboard = os.path.exists(assets_path)
    else:
        assets_path = os.path.join('appointment', 'static', 'assets', 'css', 'black-dashboard.css')
        use_black_dashboard = os.path.exists(assets_path)
    
    # Si l'utilisateur n'est pas connecté, afficher la page d'accueil publique
    if not request.user.is_authenticated:
        if use_black_dashboard:
            template_name = 'appointment/homepage.html'
            base_template = 'base_templates/black_dashboard_base.html'
        else:
            template_name = 'appointment/index.html'
            from appointment.settings import APPOINTMENT_BASE_TEMPLATE
            base_template = APPOINTMENT_BASE_TEMPLATE
    else:
        # Utilisateurs connectés : afficher la page des services avec sidebar
        if use_black_dashboard:
            template_name = 'appointment/index_black_dashboard.html'
            base_template = 'base_templates/black_dashboard_base.html'
        else:
            template_name = 'appointment/index.html'
            from appointment.settings import APPOINTMENT_BASE_TEMPLATE
            base_template = APPOINTMENT_BASE_TEMPLATE
    
    context = get_generic_context(request, admin=False)
    
    # Ajouter les URLs des réseaux sociaux depuis les settings
    from django.conf import settings
    social_media_urls = {
        'facebook_url': getattr(settings, 'SOCIAL_MEDIA_FACEBOOK_URL', 'https://www.facebook.com/'),
        'instagram_url': getattr(settings, 'SOCIAL_MEDIA_INSTAGRAM_URL', 'https://www.instagram.com/'),
        'linkedin_url': getattr(settings, 'SOCIAL_MEDIA_LINKEDIN_URL', 'https://www.linkedin.com/'),
    }
    
    context.update({
        'services': services,
        'website_name': website_name,
        'page_title': page_title,
        'page_description': page_description,
        'BASE_TEMPLATE': base_template,
        **social_media_urls,
    })
    
    return render(request, template_name, context)


@require_user_authenticated
def my_appointments(request):
    """Affiche la liste des rendez-vous de l'utilisateur connecté."""
    from appointment.utils.json_context import get_generic_context_with_extra
    from django.db.models import Q
    from appointment.utils.db_helpers import get_website_name
    
    # Récupérer les rendez-vous de l'utilisateur
    if request.user.is_superuser or request.user.is_staff:
        appointments = Appointment.objects.all().order_by('-appointment_request__date', '-appointment_request__start_time')
    else:
        appointments = Appointment.objects.filter(client=request.user).order_by('-appointment_request__date', '-appointment_request__start_time')
    
    # Filtres
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    date_filter = request.GET.get('date', '')
    
    if search_query:
        appointments = appointments.filter(
            Q(client__first_name__icontains=search_query) |
            Q(client__last_name__icontains=search_query) |
            Q(client__email__icontains=search_query) |
            Q(appointment_request__service__name__icontains=search_query)
        )
    
    if date_filter:
        appointments = appointments.filter(appointment_request__date=date_filter)
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(appointments, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    website_name = get_website_name()
    context = get_generic_context_with_extra(request, {
        'appointments': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'date_filter': date_filter,
        'website_name': website_name,
        'page_title': f"{_('Mes rendez-vous')} - {website_name}",
    }, admin=False)
    
    # Utiliser Black Dashboard si disponible
    import os
    from django.conf import settings
    base_dir = getattr(settings, 'BASE_DIR', None)
    if base_dir:
        assets_path = os.path.join(base_dir, 'appointment', 'static', 'assets', 'css', 'black-dashboard.css')
        use_black_dashboard = os.path.exists(assets_path)
    else:
        assets_path = os.path.join('appointment', 'static', 'assets', 'css', 'black-dashboard.css')
        use_black_dashboard = os.path.exists(assets_path)
    
    if use_black_dashboard:
        context['BASE_TEMPLATE'] = 'base_templates/black_dashboard_base.html'
        template_name = 'appointment/my_appointments.html'
    else:
        template_name = 'appointment/my_appointments.html'
    
    return render(request, template_name, context)


def new_appointment(request):
    """Page pour créer un nouveau rendez-vous - redirige vers la sélection de service."""
    from appointment.models import Service
    from appointment.utils.db_helpers import get_website_name
    from appointment.utils.json_context import get_generic_context
    
    services = Service.objects.all()
    website_name = get_website_name()
    
    context = get_generic_context(request, admin=False)
    context.update({
        'services': services,
        'website_name': website_name,
        'page_title': f"{_('Nouveau rendez-vous')} - {website_name}",
    })
    
    # Utiliser Black Dashboard si disponible
    import os
    from django.conf import settings
    base_dir = getattr(settings, 'BASE_DIR', None)
    if base_dir:
        assets_path = os.path.join(base_dir, 'appointment', 'static', 'assets', 'css', 'black-dashboard.css')
        use_black_dashboard = os.path.exists(assets_path)
    else:
        assets_path = os.path.join('appointment', 'static', 'assets', 'css', 'black-dashboard.css')
        use_black_dashboard = os.path.exists(assets_path)
    
    if use_black_dashboard:
        context['BASE_TEMPLATE'] = 'base_templates/black_dashboard_base.html'
        template_name = 'appointment/new_appointment.html'
    else:
        template_name = 'appointment/new_appointment.html'
    
    return render(request, template_name, context)


def user_login(request):
    """Vue de connexion pour les utilisateurs."""
    from appointment.utils.json_context import get_generic_context
    from appointment.utils.db_helpers import get_website_name
    
    # Si l'utilisateur est déjà connecté, rediriger
    if request.user.is_authenticated:
        return redirect('appointment:index')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
    else:
        form = AuthenticationForm()
    
    # Ajouter les classes CSS aux champs du formulaire (pour GET et POST)
    form.fields['username'].widget.attrs.update({
        'class': 'form-control',
        'placeholder': _("Nom d'utilisateur ou email"),
        'autocomplete': 'username'
    })
    form.fields['password'].widget.attrs.update({
        'class': 'form-control',
        'placeholder': _("Mot de passe"),
        'autocomplete': 'current-password'
    })
    
    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, _("Vous êtes maintenant connecté."))
                # Rediriger vers la page demandée ou le tableau de bord (mes rendez-vous)
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                # Rediriger vers le tableau de bord selon le type d'utilisateur
                if user.is_superuser:
                    return redirect('appointment:admin_dashboard')
                elif user.is_staff:
                    return redirect('appointment:get_user_appointments')
                else:
                    # Utilisateurs réguliers : rediriger vers leurs rendez-vous
                    return redirect('appointment:my_appointments')
            else:
                messages.error(request, _("Nom d'utilisateur ou mot de passe incorrect."))
        else:
            messages.error(request, _("Veuillez corriger les erreurs ci-dessous."))
    
    website_name = get_website_name()
    context = get_generic_context(request, admin=False)
    context.update({
        'form': form,
        'website_name': website_name,
        'page_title': f"{_('Connexion')} - {website_name}",
    })
    
    # Utiliser Black Dashboard si disponible
    import os
    from django.conf import settings
    base_dir = getattr(settings, 'BASE_DIR', None)
    if base_dir:
        assets_path = os.path.join(base_dir, 'appointment', 'static', 'assets', 'css', 'black-dashboard.css')
        use_black_dashboard = os.path.exists(assets_path)
    else:
        assets_path = os.path.join('appointment', 'static', 'assets', 'css', 'black-dashboard.css')
        use_black_dashboard = os.path.exists(assets_path)
    
    if use_black_dashboard:
        context['BASE_TEMPLATE'] = 'base_templates/black_dashboard_base.html'
        template_name = 'appointment/login.html'
    else:
        from appointment.settings import APPOINTMENT_BASE_TEMPLATE
        context['BASE_TEMPLATE'] = APPOINTMENT_BASE_TEMPLATE
        template_name = 'appointment/login.html'
    
    return render(request, template_name, context)


def user_register(request):
    """Vue d'inscription pour les utilisateurs."""
    from appointment.forms import UserRegistrationForm
    from appointment.utils.json_context import get_generic_context
    from appointment.utils.db_helpers import get_website_name
    
    # Si l'utilisateur est déjà connecté, rediriger
    if request.user.is_authenticated:
        return redirect('appointment:index')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            phone = form.cleaned_data.get('phone')
            password = form.cleaned_data.get('password1')
            
            try:
                # Créer l'utilisateur
                CLIENT_MODEL = get_user_model()
                
                # Vérifier si l'email existe déjà
                if CLIENT_MODEL.objects.filter(email=email).exists():
                    messages.error(request, _("Cet email est déjà utilisé."))
                    return redirect('appointment:user_register')
                
                # Créer l'utilisateur
                try:
                    # Vérifier si le modèle User a un champ username
                    CLIENT_MODEL._meta.get_field('username')
                    # Générer un username unique depuis l'email
                    username = email.split('@')[0]
                    counter = 1
                    while CLIENT_MODEL.objects.filter(username=username).exists():
                        username = f"{email.split('@')[0]}{counter}"
                        counter += 1
                    user = CLIENT_MODEL.objects.create_user(
                        username=username,
                        email=email,
                        password=password
                    )
                except:
                    # Pas de champ username, créer avec email uniquement
                    user = CLIENT_MODEL.objects.create_user(
                        email=email,
                        password=password
                    )
                
                # Connecter l'utilisateur automatiquement
                login(request, user)
                messages.success(request, _("Votre compte a été créé avec succès. Vous êtes maintenant connecté."))
                return redirect('appointment:index')
                
            except Exception as e:
                logger.error(f"Erreur lors de la création du compte: {e}")
                messages.error(request, _("Une erreur est survenue lors de la création de votre compte. Veuillez réessayer."))
    else:
        form = UserRegistrationForm()
    
    website_name = get_website_name()
    context = get_generic_context(request, admin=False)
    context.update({
        'form': form,
        'website_name': website_name,
        'page_title': f"{_('Inscription')} - {website_name}",
    })
    
    # Utiliser Black Dashboard si disponible
    import os
    from django.conf import settings
    base_dir = getattr(settings, 'BASE_DIR', None)
    if base_dir:
        assets_path = os.path.join(base_dir, 'appointment', 'static', 'assets', 'css', 'black-dashboard.css')
        use_black_dashboard = os.path.exists(assets_path)
    else:
        assets_path = os.path.join('appointment', 'static', 'assets', 'css', 'black-dashboard.css')
        use_black_dashboard = os.path.exists(assets_path)
    
    if use_black_dashboard:
        context['BASE_TEMPLATE'] = 'base_templates/black_dashboard_base.html'
        template_name = 'appointment/register.html'
    else:
        from appointment.settings import APPOINTMENT_BASE_TEMPLATE
        context['BASE_TEMPLATE'] = APPOINTMENT_BASE_TEMPLATE
        template_name = 'appointment/register.html'
    
    return render(request, template_name, context)


def custom_logout(request):
    """Vue de déconnexion personnalisée."""
    logout(request)
    messages.success(request, _("Vous avez été déconnecté avec succès."))
    return redirect('appointment:index')


@require_user_authenticated
@require_superuser
def admin_dashboard(request):
    """Dashboard administrateur avec statistiques."""
    from appointment.utils.json_context import get_generic_context_with_extra
    from django.db.models import Count, Q
    from datetime import datetime, timedelta
    from django.utils import timezone
    from appointment.utils.db_helpers import get_website_name
    
    now = timezone.now()
    today = now.date()
    this_month_start = today.replace(day=1)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
    
    # Statistiques
    total_appointments = Appointment.objects.count()
    total_services = Service.objects.count()
    total_staff = StaffMember.objects.count()
    
    # Rendez-vous ce mois
    appointments_this_month = Appointment.objects.filter(
        appointment_request__date__gte=this_month_start
    ).count()
    
    # Rendez-vous confirmés
    confirmed_appointments = Appointment.objects.filter(
        appointment_request__date__gte=today
    ).count()
    
    # Rendez-vous passés
    past_appointments = Appointment.objects.filter(
        appointment_request__date__lt=today
    ).count()
    
    # Rendez-vous par jour (7 derniers jours)
    appointments_by_day = []
    for i in range(7):
        date = today - timedelta(days=i)
        count = Appointment.objects.filter(appointment_request__date=date).count()
        appointments_by_day.append({
            'date': date.strftime('%Y-%m-%d'),
            'day': date.strftime('%a'),
            'count': count
        })
    appointments_by_day.reverse()
    appointments_by_day_json = json.dumps(appointments_by_day)
    
    # Services les plus populaires
    popular_services = Service.objects.annotate(
        appointment_count=Count('appointmentrequest__appointment')
    ).order_by('-appointment_count')[:5]
    
    website_name = get_website_name()
    context = get_generic_context_with_extra(request, {
        'total_appointments': total_appointments,
        'total_services': total_services,
        'total_staff': total_staff,
        'appointments_this_month': appointments_this_month,
        'confirmed_appointments': confirmed_appointments,
        'past_appointments': past_appointments,
        'appointments_by_day': appointments_by_day_json,
        'popular_services': popular_services,
        'website_name': website_name,
        'page_title': f"{_('Dashboard Admin')} - {website_name}",
    }, admin=True)
    
    # Utiliser Black Dashboard si disponible
    import os
    from django.conf import settings
    base_dir = getattr(settings, 'BASE_DIR', None)
    if base_dir:
        assets_path = os.path.join(base_dir, 'appointment', 'static', 'assets', 'css', 'black-dashboard.css')
        use_black_dashboard = os.path.exists(assets_path)
    else:
        assets_path = os.path.join('appointment', 'static', 'assets', 'css', 'black-dashboard.css')
        use_black_dashboard = os.path.exists(assets_path)
    
    if use_black_dashboard:
        context['BASE_TEMPLATE'] = 'base_templates/black_dashboard_base.html'
        template_name = 'appointment/admin_dashboard.html'
    else:
        template_name = 'appointment/admin_dashboard.html'
    
    return render(request, template_name, context)


@require_user_authenticated
def update_user_info_simple(request):
    """Vue simplifiée pour permettre aux utilisateurs réguliers de modifier leurs informations personnelles."""
    from appointment.forms import PersonalInformationForm
    from appointment.services import update_personal_info_service
    from appointment.utils.json_context import get_generic_context_with_extra
    
    if request.method == 'POST':
        user, is_valid, error_message = update_personal_info_service(request.user.id, request.POST, request.user)
        if is_valid:
            messages.success(request, _("Vos informations ont été mises à jour avec succès."))
            return redirect('appointment:user_profile')
        else:
            messages.error(request, error_message)
            return redirect('appointment:update_user_info_simple')
    
    form = PersonalInformationForm(initial={
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'email': request.user.email,
    }, user=request.user)
    
    # Utiliser Black Dashboard si disponible
    import os
    from django.conf import settings
    base_dir = getattr(settings, 'BASE_DIR', None)
    if base_dir:
        assets_path = os.path.join(base_dir, 'appointment', 'static', 'assets', 'css', 'black-dashboard.css')
        use_black_dashboard = os.path.exists(assets_path)
    else:
        assets_path = os.path.join('appointment', 'static', 'assets', 'css', 'black-dashboard.css')
        use_black_dashboard = os.path.exists(assets_path)
    
    if use_black_dashboard:
        base_template = 'base_templates/black_dashboard_base.html'
        template_name = 'appointment/update_user_info_simple.html'
    else:
        from appointment.settings import APPOINTMENT_BASE_TEMPLATE
        base_template = APPOINTMENT_BASE_TEMPLATE
        template_name = 'appointment/update_user_info_simple.html'
    
    context = get_generic_context_with_extra(request=request, extra={
        'form': form,
        'BASE_TEMPLATE': base_template,
    })
    
    return render(request, template_name, context)


@require_user_authenticated
def change_password_simple(request):
    """Vue simplifiée pour permettre aux utilisateurs réguliers de changer leur mot de passe."""
    from appointment.utils.json_context import get_generic_context_with_extra
    
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important pour maintenir la session
            messages.success(request, _("Votre mot de passe a été modifié avec succès."))
            return redirect('appointment:user_profile')
        else:
            messages.error(request, _("Veuillez corriger les erreurs ci-dessous."))
    else:
        form = PasswordChangeForm(request.user)
    
    # Utiliser Black Dashboard si disponible
    import os
    from django.conf import settings
    base_dir = getattr(settings, 'BASE_DIR', None)
    if base_dir:
        assets_path = os.path.join(base_dir, 'appointment', 'static', 'assets', 'css', 'black-dashboard.css')
        use_black_dashboard = os.path.exists(assets_path)
    else:
        assets_path = os.path.join('appointment', 'static', 'assets', 'css', 'black-dashboard.css')
        use_black_dashboard = os.path.exists(assets_path)
    
    if use_black_dashboard:
        base_template = 'base_templates/black_dashboard_base.html'
        template_name = 'appointment/change_password_simple.html'
    else:
        from appointment.settings import APPOINTMENT_BASE_TEMPLATE
        base_template = APPOINTMENT_BASE_TEMPLATE
        template_name = 'appointment/change_password_simple.html'
    
    context = get_generic_context_with_extra(request=request, extra={
        'form': form,
        'BASE_TEMPLATE': base_template,
    })
    
    return render(request, template_name, context)


def contact(request):
    """Vue pour gérer le formulaire de contact."""
    from appointment.forms import ContactForm
    from appointment.utils.json_context import get_generic_context
    from django.core.mail import send_mail
    from django.conf import settings
    
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']
            
            # Envoyer un email à l'administrateur
            try:
                subject = _("Nouveau message de contact de {name}").format(name=name)
                email_message = _("Nom: {name}\nEmail: {email}\n\nMessage:\n{message}").format(
                    name=name,
                    email=email,
                    message=message
                )
                
                # Envoyer à l'admin
                admin_email = getattr(settings, 'ADMIN_EMAIL', None) or getattr(settings, 'DEFAULT_FROM_EMAIL', None)
                if admin_email:
                    send_mail(
                        subject,
                        email_message,
                        getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com'),
                        [admin_email],
                        fail_silently=False,
                    )
                
                messages.success(request, _("Votre message a été envoyé avec succès. Nous vous répondrons dans les plus brefs délais."))
            except Exception as e:
                logger.error(f"Erreur lors de l'envoi de l'email de contact: {e}")
                messages.error(request, _("Une erreur est survenue lors de l'envoi de votre message. Veuillez réessayer plus tard."))
            
            return redirect('appointment:index')
    else:
        form = ContactForm()
    
    context = get_generic_context(request, admin=False)
    context['form'] = form
    
    # Utiliser Black Dashboard si disponible
    import os
    from django.conf import settings
    base_dir = getattr(settings, 'BASE_DIR', None)
    if base_dir:
        assets_path = os.path.join(base_dir, 'appointment', 'static', 'assets', 'css', 'black-dashboard.css')
        use_black_dashboard = os.path.exists(assets_path)
    else:
        assets_path = os.path.join('appointment', 'static', 'assets', 'css', 'black-dashboard.css')
        use_black_dashboard = os.path.exists(assets_path)
    
    if use_black_dashboard:
        context['BASE_TEMPLATE'] = 'base_templates/black_dashboard_base.html'
        template_name = 'appointment/homepage.html'
    else:
        from appointment.settings import APPOINTMENT_BASE_TEMPLATE
        context['BASE_TEMPLATE'] = APPOINTMENT_BASE_TEMPLATE
        template_name = 'appointment/homepage.html'
    
    return render(request, template_name, context)
