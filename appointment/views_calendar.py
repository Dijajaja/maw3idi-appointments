# views_calendar.py
# Path: appointment/views_calendar.py

"""
Vues pour le calendrier dynamique mensuel
"""

from datetime import date, timedelta
import calendar as cal
from django.shortcuts import render
from django.utils import timezone
from django.utils.translation import gettext as _
from django.db.models import Q

from appointment.decorators import require_user_authenticated
from appointment.models import Appointment, AppointmentRequest
from appointment.utils.json_context import get_generic_context_with_extra, json_response
from appointment.utils.db_helpers import get_website_name
from .decorators import require_ajax


@require_user_authenticated
def calendar_view(request, year=None, month=None):
    """Vue calendrier mensuel avec les rendez-vous."""
    today = timezone.now().date()
    
    # Utiliser l'année et le mois de la requête ou ceux d'aujourd'hui
    if year and month:
        try:
            current_date = date(int(year), int(month), 1)
        except (ValueError, TypeError):
            current_date = today.replace(day=1)
    else:
        current_date = today.replace(day=1)
    
    # Récupérer les rendez-vous du mois
    if request.user.is_superuser or request.user.is_staff:
        appointments = Appointment.objects.filter(
            appointment_request__date__year=current_date.year,
            appointment_request__date__month=current_date.month
        ).select_related('appointment_request', 'client', 'appointment_request__service')
    else:
        appointments = Appointment.objects.filter(
            client=request.user,
            appointment_request__date__year=current_date.year,
            appointment_request__date__month=current_date.month
        ).select_related('appointment_request', 'appointment_request__service')
    
    # Créer un dictionnaire des rendez-vous par jour
    appointments_by_date = {}
    for appointment in appointments:
        appt_date = appointment.appointment_request.date
        if appt_date not in appointments_by_date:
            appointments_by_date[appt_date] = []
        appointments_by_date[appt_date].append({
            'id': appointment.id,
            'service': appointment.appointment_request.service.name,
            'time': appointment.appointment_request.start_time.strftime('%H:%M'),
            'client': appointment.get_client_name() if hasattr(appointment, 'get_client_name') else str(appointment.client),
        })
    
    # Générer le calendrier
    cal_data = cal.monthcalendar(current_date.year, current_date.month)
    
    # Préparer les données pour le template
    calendar_days = []
    for week in cal_data:
        week_days = []
        for day in week:
            if day == 0:
                week_days.append(None)
            else:
                day_date = date(current_date.year, current_date.month, day)
                day_appointments = appointments_by_date.get(day_date, [])
                week_days.append({
                    'day': day,
                    'date': day_date,
                    'is_today': day_date == today,
                    'is_past': day_date < today,
                    'appointments': day_appointments,
                    'count': len(day_appointments)
                })
        calendar_days.append(week_days)
    
    # Mois précédent et suivant
    if current_date.month == 1:
        prev_month = current_date.replace(year=current_date.year - 1, month=12)
    else:
        prev_month = current_date.replace(month=current_date.month - 1)
    
    if current_date.month == 12:
        next_month = current_date.replace(year=current_date.year + 1, month=1)
    else:
        next_month = current_date.replace(month=current_date.month + 1)
    
    month_names = [
        _('Janvier'), _('Février'), _('Mars'), _('Avril'), _('Mai'), _('Juin'),
        _('Juillet'), _('Août'), _('Septembre'), _('Octobre'), _('Novembre'), _('Décembre')
    ]
    
    website_name = get_website_name()
    context = get_generic_context_with_extra(request, {
        'calendar_days': calendar_days,
        'current_date': current_date,
        'current_month_name': month_names[current_date.month - 1],
        'current_year': current_date.year,
        'prev_month': prev_month,
        'next_month': next_month,
        'today': today,
        'total_appointments': len(appointments),
        'website_name': website_name,
        'page_title': f"{_('Calendrier')} - {current_date.strftime('%B %Y')} - {website_name}",
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
        template_name = 'appointment/calendar.html'
    else:
        template_name = 'appointment/calendar.html'
    
    return render(request, template_name, context)


@require_ajax
def get_calendar_appointments_ajax(request):
    """AJAX endpoint pour récupérer les rendez-vous d'un mois."""
    year = request.GET.get('year')
    month = request.GET.get('month')
    
    if not year or not month:
        return json_response("L'année et le mois sont requis", success=False, status=400)
    
    try:
        current_date = date(int(year), int(month), 1)
    except (ValueError, TypeError):
        return json_response("Date invalide", success=False, status=400)
    
    # Récupérer les rendez-vous
    if request.user.is_superuser or request.user.is_staff:
        appointments = Appointment.objects.filter(
            appointment_request__date__year=current_date.year,
            appointment_request__date__month=current_date.month
        )
    else:
        appointments = Appointment.objects.filter(
            client=request.user,
            appointment_request__date__year=current_date.year,
            appointment_request__date__month=current_date.month
        )
    
    # Formater les données
    appointments_data = {}
    for appointment in appointments:
        appt_date = appointment.appointment_request.date.isoformat()
        if appt_date not in appointments_data:
            appointments_data[appt_date] = []
        appointments_data[appt_date].append({
            'id': appointment.id,
            'service': appointment.appointment_request.service.name,
            'time': appointment.appointment_request.start_time.strftime('%H:%M'),
        })
    
    return json_response("Rendez-vous récupérés", custom_data={'appointments': appointments_data})

