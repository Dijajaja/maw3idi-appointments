# forms.py
# Path: appointment/forms.py

"""
Author: Adams Pierre David
Since: 1.0.0
"""

from django import forms
from django.utils.translation import gettext as _
from phonenumber_field.formfields import SplitPhoneNumberField

from .models import (
    Appointment, AppointmentRequest, AppointmentRescheduleHistory, DayOff, Service, StaffMember,
    WorkingHours
)
from .utils.db_helpers import get_user_model
from .utils.validators import not_in_the_past


class SlotForm(forms.Form):
    selected_date = forms.DateField(validators=[not_in_the_past])
    staff_member = forms.ModelChoiceField(
            StaffMember.objects.all(),
            error_messages={'invalid_choice': _('Staff member does not exist')}
    )


class AppointmentRequestForm(forms.ModelForm):
    class Meta:
        model = AppointmentRequest
        fields = ('date', 'start_time', 'end_time', 'service', 'staff_member')


class ReschedulingForm(forms.ModelForm):
    class Meta:
        model = AppointmentRescheduleHistory
        fields = ['reason_for_rescheduling']
        widgets = {
            'reason_for_rescheduling': forms.Textarea(attrs={'rows': 4, 'placeholder': _('Raison du report...')}),
        }


class AppointmentForm(forms.ModelForm):
    phone = SplitPhoneNumberField()

    class Meta:
        model = Appointment
        fields = ('phone', 'want_reminder', 'address', 'additional_info')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['phone'].widget.attrs.update(
                {
                    'placeholder': _('+222 XX XXX XX XX')
                })
        self.fields['additional_info'].widget.attrs.update(
                {
                    'rows': 2,
                    'class': 'form-control',
                })
        self.fields['address'].widget.attrs.update(
                {
                    'rows': 2,
                    'class': 'form-control',
                    'placeholder': _('Adresse complète : rue, ville, code postal'),
                    'required': 'true'
                })
        self.fields['additional_info'].widget.attrs.update(
                {
                    'class': 'form-control',
                    'placeholder': _('Informations supplémentaires (optionnel)')
                })


class ClientDataForm(forms.Form):
    name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Prénom Nom')}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': _('votre.email@exemple.com')}))


class PersonalInformationForm(forms.Form):
    # first_name, last_name, email
    first_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Prénom')}))
    last_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Nom')}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': _('votre.email@exemple.com')}))

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # pop the user from the kwargs
        super().__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if self.user:
            if self.user.email == email:
                return email
            queryset = get_user_model().objects.exclude(pk=self.user.pk)
        else:
            queryset = get_user_model().objects.all()

        if queryset.filter(email=email).exists():
            raise forms.ValidationError(_("This email is already taken."))

        return email


class ContactForm(forms.Form):
    """Formulaire de contact simple."""
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Votre nom')
        }),
        label=_('Nom')
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': _('votre.email@exemple.com')
        }),
        label=_('Email')
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': _('Votre message...')
        }),
        label=_('Message')
    )


class UserRegistrationForm(forms.Form):
    """Formulaire d'inscription utilisateur avec email, téléphone et mot de passe."""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': _('votre.email@exemple.com'),
            'autocomplete': 'email'
        }),
        label=_('Email'),
        help_text=_("Nous utiliserons cet email pour vous contacter")
    )
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('+222 XX XXX XX XX'),
            'type': 'tel',
            'autocomplete': 'tel'
        }),
        label=_('Numéro de téléphone'),
        help_text=_("Format: +222 XX XXX XX XX")
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Mot de passe'),
            'autocomplete': 'new-password'
        }),
        label=_('Mot de passe'),
        min_length=8,
        help_text=_("Au moins 8 caractères")
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Confirmer le mot de passe'),
            'autocomplete': 'new-password'
        }),
        label=_('Confirmer le mot de passe')
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        CLIENT_MODEL = get_user_model()
        if CLIENT_MODEL.objects.filter(email=email).exists():
            raise forms.ValidationError(_("Cet email est déjà utilisé. Veuillez vous connecter."))
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_("Les mots de passe ne correspondent pas."))
        return password2

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        # Validation basique du numéro de téléphone
        if phone and len(phone.replace('+', '').replace(' ', '').replace('-', '')) < 8:
            raise forms.ValidationError(_("Veuillez entrer un numéro de téléphone valide."))
        return phone


class StaffAppointmentInformationForm(forms.ModelForm):
    class Meta:
        model = StaffMember
        fields = ['services_offered', 'slot_duration', 'lead_time', 'finish_time',
                  'appointment_buffer_time', 'work_on_saturday', 'work_on_sunday']
        widgets = {
            'service_offered': forms.Select(attrs={'class': 'form-control'}),
            'slot_duration': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': _('Exemple : 30, 60, 90, 120... (en minutes)')
            }),
            'lead_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'placeholder': _('Exemple : 08:00:00, 09:00:00... (format 24h)')
            }),
            'finish_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'placeholder': _('Exemple : 17:00:00, 18:00:00... (format 24h)')
            }),
            'appointment_buffer_time': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': _('Exemple : 15, 30, 45, 60... (en minutes)')
            }),
            'work_on_saturday': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'work_on_sunday': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class StaffMemberForm(forms.ModelForm):
    class Meta:
        model = StaffMember
        fields = ['user', 'services_offered', 'slot_duration', 'lead_time', 'finish_time',
                  'appointment_buffer_time', 'work_on_saturday', 'work_on_sunday']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
            'service_offered': forms.Select(attrs={'class': 'form-control'}),
            'slot_duration': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': _('Exemple : 30, 60, 90, 120... (en minutes)')
            }),
            'lead_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'placeholder': _('Exemple : 08:00:00, 09:00:00... (format 24h)')
            }),
            'finish_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'placeholder': _('Exemple : 17:00:00, 18:00:00... (format 24h)')
            }),
            'appointment_buffer_time': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': _('Exemple : 15, 30, 45, 60... (en minutes)')
            }),
            'work_on_saturday': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'work_on_sunday': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super(StaffMemberForm, self).__init__(*args, **kwargs)
        # Exclude users who are already staff members
        existing_staff_user_ids = StaffMember.objects.values_list('user', flat=True)
        # Filter queryset for user field to include only superusers or users not already staff members
        self.fields['user'].queryset = get_user_model().objects.filter(
                is_superuser=True
        ).exclude(id__in=existing_staff_user_ids) | get_user_model().objects.exclude(
                id__in=existing_staff_user_ids
        )


class StaffDaysOffForm(forms.ModelForm):
    class Meta:
        model = DayOff
        fields = ['start_date', 'end_date', 'description']
        widgets = {
            'start_date': forms.DateInput(attrs={'class': 'datepicker'}),
            'end_date': forms.DateInput(attrs={'class': 'datepicker'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data


class StaffWorkingHoursForm(forms.ModelForm):
    class Meta:
        model = WorkingHours
        fields = ['day_of_week', 'start_time', 'end_time']


class ServiceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ServiceForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['background_color'].widget.attrs['value'] = self.instance.background_color

    class Meta:
        model = Service
        fields = ['name', 'description', 'duration', 'price', 'down_payment', 'image', 'currency', 'background_color']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Exemple : Première consultation')
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': _("Exemple : Aperçu des besoins du client.")
            }),
            'duration': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('HH:MM:SS, (exemple : 00:15:00 pour 15 minutes)')
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': _('Exemple : 100.00 (0 pour gratuit)')
            }),
            'down_payment': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': _('Exemple : 50.00 (0 pour gratuit)')
            }),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'currency': forms.Select(choices=[('MRU', 'MRU'), ('EUR', 'EUR'), ('GBP', 'GBP'), ('USD', 'USD')],
                                     attrs={'class': 'form-control'}),
            'background_color': forms.TextInput(attrs={'class': 'form-control', 'type': 'color', 'value': '#000000'}),
        }
