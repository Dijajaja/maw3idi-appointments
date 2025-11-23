# Path: appointment/management/commands/setup_all_staff_hours.py

"""
Commande Django pour configurer automatiquement des horaires de travail pour tous les staff members.
Usage: python manage.py setup_all_staff_hours
       python manage.py setup_all_staff_hours --start 09:00 --end 17:00 --days 0
       (0=Dimanche, 1=Lundi, 2=Mardi, 3=Mercredi, 4=Jeudi, 5=Vendredi, 6=Samedi)
"""

from django.core.management.base import BaseCommand
from django.db import transaction
import datetime

from appointment.models import StaffMember, WorkingHours, Config


class Command(BaseCommand):
    help = 'Configure des horaires de travail par défaut pour tous les staff members qui n\'en ont pas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--start',
            default='09:00',
            help='Heure de début au format HH:MM (par défaut: 09:00)'
        )
        parser.add_argument(
            '--end',
            default='17:00',
            help='Heure de fin au format HH:MM (par défaut: 17:00)'
        )
        parser.add_argument(
            '--days',
            default='0',
            help='Jours de la semaine (0=Dimanche, 1=Lundi, ..., 6=Samedi). Par défaut: 0 (Dimanche uniquement)'
        )
        parser.add_argument(
            '--all-staff',
            action='store_true',
            help='Configurer pour tous les staff members, même ceux qui ont déjà des horaires'
        )
        parser.add_argument(
            '--slot-duration',
            type=int,
            default=30,
            help='Durée des créneaux en minutes (par défaut: 30)'
        )

    @transaction.atomic
    def handle(self, *args, **options):
        # Parser les heures
        try:
            start_h, start_m = map(int, str(options['start']).split(':'))
            end_h, end_m = map(int, str(options['end']).split(':'))
            t_start = datetime.time(hour=start_h, minute=start_m)
            t_end = datetime.time(hour=end_h, minute=end_m)
        except ValueError:
            self.stdout.write(
                self.style.ERROR('Format d\'heure invalide. Utilisez HH:MM (ex: 09:00)')
            )
            return

        # Parser les jours de la semaine
        try:
            days_list = [int(d.strip()) for d in str(options['days']).split(',')]
            # Vérifier que les jours sont valides (0-6)
            if not all(0 <= d <= 6 for d in days_list):
                raise ValueError('Les jours doivent être entre 0 (Dimanche) et 6 (Samedi)')
        except ValueError as e:
            self.stdout.write(
                self.style.ERROR(f'Format de jours invalide: {e}')
            )
            return

        # Configurer la durée des créneaux dans Config
        cfg, created = Config.objects.get_or_create(id=1)
        cfg.slot_duration = options['slot_duration']  # En minutes (entier)
        cfg.save()
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Configuration créée avec durée de créneau: {options["slot_duration"]} minutes')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Durée de créneau mise à jour: {options["slot_duration"]} minutes')
            )

        # Récupérer tous les staff members
        all_staff = StaffMember.objects.all()
        
        if not all_staff.exists():
            self.stdout.write(
                self.style.WARNING('Aucun staff member trouvé dans la base de données')
            )
            return

        self.stdout.write(f'\nTraitement de {all_staff.count()} staff member(s)...\n')

        total_created = 0
        total_updated = 0
        staff_processed = 0

        for staff in all_staff:
            # Vérifier si le staff member a déjà des horaires
            existing_hours = WorkingHours.objects.filter(staff_member=staff).count()
            
            if existing_hours > 0 and not options['all_staff']:
                self.stdout.write(
                    self.style.WARNING(
                        f'  >> {staff.get_staff_member_name()}: {existing_hours} horaire(s) deja configure(s), ignore'
                    )
                )
                continue

            staff_created = 0
            staff_updated = 0

            # Créer ou mettre à jour les horaires pour chaque jour spécifié
            for day_of_week in days_list:
                wh, created = WorkingHours.objects.update_or_create(
                    staff_member=staff,
                    day_of_week=day_of_week,
                    defaults={
                        'start_time': t_start,
                        'end_time': t_end,
                    }
                )
                if created:
                    staff_created += 1
                else:
                    staff_updated += 1

            total_created += staff_created
            total_updated += staff_updated
            staff_processed += 1

            # Afficher le résultat pour ce staff member
            day_names = {
                0: 'Dim', 1: 'Lun', 2: 'Mar', 3: 'Mer', 4: 'Jeu', 5: 'Ven', 6: 'Sam'
            }
            days_str = ', '.join([day_names.get(d, str(d)) for d in days_list])
            
            if staff_created > 0 or staff_updated > 0:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'  [OK] {staff.get_staff_member_name()}: '
                        f'{staff_created} cree(s), {staff_updated} mis a jour - '
                        f'{days_str} {t_start.strftime("%H:%M")}-{t_end.strftime("%H:%M")}'
                    )
                )

        # Résumé final
        self.stdout.write('\n' + '='*60)
        self.stdout.write(
            self.style.SUCCESS(
                f'\n[TERMINE]\n'
                f'   Staff members traites: {staff_processed}/{all_staff.count()}\n'
                f'   Horaires crees: {total_created}\n'
                f'   Horaires mis a jour: {total_updated}\n'
                f'   Heures: {t_start.strftime("%H:%M")} - {t_end.strftime("%H:%M")}\n'
                f'   Jours: {options["days"]}\n'
                f'   Duree de creneau: {options["slot_duration"]} minutes'
            )
        )

