#!/usr/bin/env python
"""
Script pour importer les services locaux vers PostgreSQL sur Render.

Ce script se connecte directement à PostgreSQL sur Render et importe les services.

Usage:
    python importer_services_local.py

Important: Vous devez d'abord configurer le DATABASE_URL de Render dans ce script
ou dans votre fichier .env
"""
import os
import sys
import django

# Configurer le DATABASE_URL de Render ici
# Récupérez-le depuis votre dashboard Render : 
# Database > Internal Database URL
RENDER_DATABASE_URL = os.getenv(
    'RENDER_DATABASE_URL',
    'postgresql://django_appointment_db_user:XYqooihaTyg4IjL823EWb1qnyj9WvXZr@dpg-d5eqgcsjebjc73e0ig5g-a/django_appointment_db'
)

# Forcer l'utilisation de PostgreSQL sur Render
os.environ['DATABASE_URL'] = RENDER_DATABASE_URL
os.environ['SKIP_DB_CONNECTION'] = '0'  # Permettre la connexion

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appointments.settings')

print("🔍 Configuration de Django...")
django.setup()

print("✅ Django configuré avec succès!")
print(f"📊 Base de données: {os.environ.get('DATABASE_URL', 'Non défini')[:50]}...")

# Vérifier la connexion à la base de données
from django.db import connection
try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        print("✅ Connexion à PostgreSQL réussie!")
except Exception as e:
    print(f"❌ Erreur de connexion à PostgreSQL: {e}")
    print("Vérifiez que DATABASE_URL est correct.")
    sys.exit(1)

# Importer la commande
from appointment.management.commands.import_services_to_postgres import Command
from io import StringIO

print("\n" + "="*60)
print("📦 IMPORTATION DES SERVICES")
print("="*60 + "\n")

# Vérifier que le fichier existe
json_file = 'services_local.json'
if not os.path.exists(json_file):
    print(f"❌ Le fichier {json_file} n'existe pas!")
    print("Assurez-vous que le fichier est dans le même répertoire que ce script.")
    sys.exit(1)

# Exécuter la commande d'import
command = Command()
command.stdout = StringIO()
command.stderr = StringIO()

try:
    command.handle(
        json_file,
        skip_existing=True  # Ignorer les services existants pour éviter les doublons
    )
    
    output = command.stdout.getvalue()
    if output:
        print(output)
    
    stderr_output = command.stderr.getvalue()
    if stderr_output:
        print(stderr_output, file=sys.stderr)
    
    print("\n" + "="*60)
    print("✅ IMPORTATION TERMINÉE!")
    print("="*60)
    print("\nVérifiez votre site Render pour voir les services importés:")
    print("https://django-appointment-u96d.onrender.com/")
    
except Exception as e:
    print(f"\n❌ Erreur lors de l'importation: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

