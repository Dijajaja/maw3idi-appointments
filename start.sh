#!/bin/bash
# Script de démarrage pour Render
# Applique les migrations automatiquement au démarrage

# Ne pas arrêter le script si une commande échoue (sauf pour gunicorn)
set +e

echo "🔍 Vérification de la configuration de la base de données..."
python -c "import os; db_url = os.getenv('DATABASE_URL', ''); print(f'DATABASE_URL: {\"défini (longueur: {len(db_url)})\" if db_url else \"❌ NON DÉFINI\"}'); print(f'SKIP_DB_CONNECTION: {os.getenv(\"SKIP_DB_CONNECTION\", \"non défini\")}')"

echo "🔄 Application des migrations..."
echo "📋 Liste des migrations à appliquer:"
python manage.py showmigrations --list || echo "⚠️  Impossible de lister les migrations"

echo "🔄 Vérification de la base de données utilisée AVANT les migrations..."
python -c "
import os
import sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appointments.settings')
import django
django.setup()
from django.db import connection
engine = connection.settings_dict['ENGINE']
db_name = connection.settings_dict.get('NAME', 'N/A')
print(f'📊 Base de données: {engine}', file=sys.stderr)
print(f'📊 Nom de la base: {db_name}', file=sys.stderr)
if 'sqlite' in engine.lower():
    print('❌ ERREUR: Django utilise SQLite au lieu de PostgreSQL!', file=sys.stderr)
    print(f'❌ DATABASE_URL: {os.getenv(\"DATABASE_URL\", \"NON DÉFINI\")[:50]}...', file=sys.stderr)
    sys.exit(1)
else:
    print('✅ Django utilise PostgreSQL', file=sys.stderr)
"

echo "🔄 Application de toutes les migrations (y compris appointment)..."
python manage.py migrate appointment --noinput --verbosity 2 || echo "⚠️  Erreur lors de l'application des migrations appointment"
python manage.py migrate --noinput --verbosity 2
MIGRATE_EXIT=$?

if [ $MIGRATE_EXIT -ne 0 ]; then
    echo "⚠️  Erreur lors de l'application des migrations (code: $MIGRATE_EXIT)"
    echo "ℹ️  Tentative de connexion à la base de données..."
    python -c "import django; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appointments.settings'); django.setup(); from django.db import connection; connection.ensure_connection(); print(f'✅ Connexion réussie à: {connection.settings_dict[\"ENGINE\"]}')" || echo "❌ Impossible de se connecter à la base de données"
else
    echo "✅ Migrations appliquées avec succès"
    echo "📋 Vérification des migrations appliquées:"
    python manage.py showmigrations --list | grep -E "appointment|\[X\]|\[ \]" || echo "⚠️  Impossible de vérifier les migrations"
fi

echo "👤 Création du superutilisateur (si configuré)..."
python create_superuser.py || echo "ℹ️  Superutilisateur non créé (variables d'environnement non configurées ou déjà existant)"

echo "🚀 Démarrage de Gunicorn..."
# Utiliser set -e seulement pour gunicorn pour qu'il s'arrête en cas d'erreur
set -e
exec gunicorn appointments.wsgi:application --bind 0.0.0.0:$PORT

