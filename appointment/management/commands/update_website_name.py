"""
Commande Django pour mettre à jour le nom du site web dans la base de données.
Usage: python manage.py update_website_name "DIARY@"
"""
from django.core.management.base import BaseCommand
from appointment.models import Config


class Command(BaseCommand):
    help = 'Met à jour le nom du site web dans la configuration'

    def add_arguments(self, parser):
        parser.add_argument(
            'website_name',
            type=str,
            nargs='?',
            default='DIARY@',
            help='Le nouveau nom du site web (par défaut: DIARY@)'
        )

    def handle(self, *args, **options):
        website_name = options['website_name']
        
        # Récupérer ou créer le Config
        config, created = Config.objects.get_or_create(pk=1)
        
        # Mettre à jour le nom du site
        old_name = config.website_name or "non défini"
        config.website_name = website_name
        config.save()
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Configuration creee avec le nom du site: "{website_name}"'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Nom du site mis a jour de "{old_name}" vers "{website_name}"'
                )
            )

