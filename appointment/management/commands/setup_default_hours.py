# Path: appointment/management/commands/setup_default_hours.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
import datetime

from appointment.models import StaffMember, WorkingHours, DayOff, Config


class Command(BaseCommand):
    help = "Create default working hours (Mon–Fri 09:00–17:00, 30min slots) for Aissata and Abdoulaye and remove blocking day-offs."

    def add_arguments(self, parser):
        parser.add_argument('--start', default='09:00', help='Start time HH:MM (default: 09:00)')
        parser.add_argument('--end', default='17:00', help='End time HH:MM (default: 17:00)')
        parser.add_argument('--slot', default=30, type=int, help='Slot duration in minutes (default: 30)')
        parser.add_argument('--names', nargs='*', default=['Aissata', 'Abdoulaye'],
                            help='First names of staff members to configure (default: Aissata Abdoulaye)')

    @transaction.atomic
    def handle(self, *args, **options):
        # Parse times
        start_h, start_m = map(int, str(options['start']).split(':', 1))
        end_h, end_m = map(int, str(options['end']).split(':', 1))
        t_start = datetime.time(hour=start_h, minute=start_m, second=0)
        t_end = datetime.time(hour=end_h, minute=end_m, second=0)

        # Ensure global slot duration (Config) exists/is set
        cfg, _ = Config.objects.get_or_create(id=1)  # assumes a single row
        cfg.slot_duration = datetime.timedelta(minutes=int(options['slot']))
        # keep other fields as-is
        cfg.save()

        names = options['names']
        staff_qs = StaffMember.objects.filter(user__first_name__in=names)
        if not staff_qs.exists():
            self.stdout.write(self.style.WARNING("No StaffMember found with first_name in %s" % names))

        # Remove blocking day-offs in the future
        today = timezone.localdate()
        deleted = DayOff.objects.filter(end_date__gte=today).delete()[0]
        if deleted:
            self.stdout.write(self.style.SUCCESS(f"Removed {deleted} future day-off(s)."))

        created_total = 0
        for staff in staff_qs:
            created_for_staff = 0
            for dow in [1, 2, 3, 4, 5]:  # Monday..Friday per DAYS_OF_WEEK
                wh, created = WorkingHours.objects.update_or_create(
                    staff_member=staff, day_of_week=dow,
                    defaults={
                        'start_time': t_start,
                        'end_time': t_end,
                    }
                )
                if created:
                    created_for_staff += 1
            created_total += created_for_staff
            self.stdout.write(self.style.SUCCESS(
                f"{staff.get_staff_member_name()}: ensured Mon–Fri {t_start.strftime('%H:%M')}–{t_end.strftime('%H:%M')}."
            ))

        self.stdout.write(self.style.SUCCESS(
            f"Done. Slot duration set to {options['slot']} minutes. WorkingHours created/ensured for {staff_qs.count()} staff."
        ))


