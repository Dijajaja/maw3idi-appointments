#!/usr/bin/env python
"""
Commande Django pour importer les services depuis un fichier JSON vers PostgreSQL.

Usage:
    python manage.py import_services_to_postgres services_local.json

Cette commande permet d'importer les services créés localement (SQLite)
vers PostgreSQL sur Render.com.
"""
import os
import json
import django
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from datetime import timedelta
from decimal import Decimal

# Configuration de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appointments.settings')
django.setup()

from appointment.models import Service


class Command(BaseCommand):
    help = 'Importe les services depuis un fichier JSON vers PostgreSQL'

    def add_arguments(self, parser):
        parser.add_argument(
            'json_file',
            type=str,
            help='Chemin vers le fichier JSON contenant les services à importer'
        )
        parser.add_argument(
            '--skip-existing',
            action='store_true',
            help='Ignore les services qui existent déjà (basé sur le nom)',
        )
        parser.add_argument(
            '--update-existing',
            action='store_true',
            help='Met à jour les services existants au lieu de créer de nouveaux',
        )

    def handle(self, *args, **options):
        json_file = options['json_file']
        skip_existing = options['skip_existing']
        update_existing = options['update_existing']

        # Vérifier que le fichier existe
        if not os.path.exists(json_file):
            raise CommandError(f'Le fichier "{json_file}" n\'existe pas.')

        # Lire le fichier JSON
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise CommandError(f'Erreur lors de la lecture du fichier JSON: {e}')
        except Exception as e:
            raise CommandError(f'Erreur lors de l\'ouverture du fichier: {e}')

        # Vérifier que c'est bien une liste de services
        if not isinstance(data, list):
            raise CommandError('Le fichier JSON doit contenir une liste de services.')

        # Filtrer uniquement les services
        services_data = [item for item in data if item.get('model') == 'appointment.service']
        
        if not services_data:
            self.stdout.write(self.style.WARNING('Aucun service trouvé dans le fichier JSON.'))
            return

        self.stdout.write(f'📦 {len(services_data)} service(s) trouvé(s) dans le fichier JSON.')

        # Vérifier la base de données utilisée
        from django.conf import settings
        db_engine = settings.DATABASES['default']['ENGINE']
        if 'postgresql' not in db_engine.lower():
            self.stdout.write(self.style.WARNING(
                f'⚠️  ATTENTION: La base de données actuelle est {db_engine}, '
                f'pas PostgreSQL. Assurez-vous d\'avoir configuré DATABASE_URL.'
            ))

        # Importer les services
        imported_count = 0
        skipped_count = 0
        updated_count = 0
        error_count = 0

        with transaction.atomic():
            for service_data in services_data:
                fields = service_data.get('fields', {})
                pk = service_data.get('pk')
                
                name = fields.get('name')
                if not name:
                    self.stdout.write(self.style.ERROR(f'❌ Service sans nom ignoré (PK: {pk})'))
                    error_count += 1
                    continue

                try:
                    # Vérifier si le service existe déjà
                    existing_service = None
                    if update_existing or skip_existing:
                        try:
                            # Chercher par nom (sensible à la casse)
                            existing_service = Service.objects.get(name=name)
                        except Service.DoesNotExist:
                            pass
                        except Service.MultipleObjectsReturned:
                            # Si plusieurs services avec le même nom, prendre le premier
                            existing_service = Service.objects.filter(name=name).first()

                    if existing_service:
                        if skip_existing:
                            self.stdout.write(
                                self.style.WARNING(f'⏭️  Service "{name}" existe déjà, ignoré.')
                            )
                            skipped_count += 1
                            continue
                        elif update_existing:
                            # Mettre à jour le service existant
                            self._update_service(existing_service, fields)
                            self.stdout.write(
                                self.style.SUCCESS(f'✅ Service "{name}" mis à jour.')
                            )
                            updated_count += 1
                            continue
                        else:
                            # Créer un nouveau service avec un nom légèrement modifié
                            name = f"{name} (importé)"
                            self.stdout.write(
                                self.style.WARNING(
                                    f'⚠️  Service "{fields.get("name")}" existe déjà, '
                                    f'création avec le nom "{name}"'
                                )
                            )

                    # Créer un nouveau service
                    service = self._create_service(name, fields)
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ Service "{name}" créé avec succès.')
                    )
                    imported_count += 1

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'❌ Erreur lors de l\'import du service "{name}": {e}')
                    )
                    error_count += 1
                    import traceback
                    traceback.print_exc()

        # Résumé
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('📊 RÉSUMÉ DE L\'IMPORTATION'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(f'✅ Services importés: {imported_count}')
        if updated_count > 0:
            self.stdout.write(f'🔄 Services mis à jour: {updated_count}')
        if skipped_count > 0:
            self.stdout.write(f'⏭️  Services ignorés: {skipped_count}')
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f'❌ Erreurs: {error_count}'))
        self.stdout.write(self.style.SUCCESS('='*60))

    def _create_service(self, name, fields):
        """Crée un nouveau service à partir des données des champs."""
        # Convertir la durée depuis le format ISO (ex: "01:00:00")
        duration_str = fields.get('duration', '01:00:00')
        duration = self._parse_duration(duration_str)

        # Gérer background_color (peut être une fonction génératrice)
        background_color = fields.get('background_color')
        if not background_color:
            # Utiliser la fonction par défaut si disponible
            try:
                from appointment.models import generate_rgb_color
                background_color = generate_rgb_color()
            except:
                background_color = 'rgb(128, 128, 128)'  # Gris par défaut

        # Créer le service
        service = Service.objects.create(
            name=name,
            description=fields.get('description', ''),
            duration=duration,
            price=Decimal(str(fields.get('price', 0))),
            down_payment=Decimal(str(fields.get('down_payment', 0))),
            currency=fields.get('currency', 'MRU'),
            background_color=background_color,
            reschedule_limit=fields.get('reschedule_limit', 0),
            allow_rescheduling=fields.get('allow_rescheduling', False),
        )
        
        # Note: Les images ne peuvent pas être importées facilement car elles sont des fichiers
        # Si vous avez besoin d'importer les images, il faudrait les copier manuellement
        
        return service

    def _update_service(self, service, fields):
        """Met à jour un service existant."""
        # Convertir la durée
        duration_str = fields.get('duration', None)
        if duration_str:
            service.duration = self._parse_duration(duration_str)

        # Mettre à jour les autres champs
        if 'description' in fields:
            service.description = fields['description']
        if 'price' in fields:
            service.price = Decimal(str(fields['price']))
        if 'down_payment' in fields:
            service.down_payment = Decimal(str(fields['down_payment']))
        if 'currency' in fields:
            service.currency = fields['currency']
        if 'background_color' in fields:
            service.background_color = fields['background_color']
        if 'reschedule_limit' in fields:
            service.reschedule_limit = fields['reschedule_limit']
        if 'allow_rescheduling' in fields:
            service.allow_rescheduling = fields['allow_rescheduling']

        service.save()

    def _parse_duration(self, duration_str):
        """Convertit une chaîne de durée (HH:MM:SS ou format Django) en timedelta."""
        try:
            # Format Django: "1 00:00:00" ou "01:00:00"
            if ' ' in duration_str:
                # Format: "1 00:00:00" (jours heures:minutes:secondes)
                parts = duration_str.split(' ')
                days = int(parts[0])
                time_parts = parts[1].split(':')
                hours = int(time_parts[0])
                minutes = int(time_parts[1])
                seconds = int(time_parts[2]) if len(time_parts) > 2 else 0
                return timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
            else:
                # Format: "HH:MM:SS"
                time_parts = duration_str.split(':')
                if len(time_parts) >= 3:
                    hours = int(time_parts[0])
                    minutes = int(time_parts[1])
                    seconds = int(time_parts[2])
                    return timedelta(hours=hours, minutes=minutes, seconds=seconds)
                elif len(time_parts) == 2:
                    hours = int(time_parts[0])
                    minutes = int(time_parts[1])
                    return timedelta(hours=hours, minutes=minutes)
                else:
                    # Juste des minutes
                    return timedelta(minutes=int(duration_str))
        except (ValueError, IndexError) as e:
            # Valeur par défaut: 1 heure
            self.stdout.write(
                self.style.WARNING(
                    f'⚠️  Impossible de parser la durée "{duration_str}", utilisation de 1 heure par défaut.'
                )
            )
            return timedelta(hours=1)

