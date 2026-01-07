#!/bin/bash
# Script de démarrage pour Render
# Applique les migrations automatiquement au démarrage

# Ne pas arrêter le script si une commande échoue (sauf pour gunicorn)
set +e

echo "🔍 Vérification de la configuration de la base de données..."
python -c "import os; db_url = os.getenv('DATABASE_URL', ''); print(f'DATABASE_URL: {\"défini (longueur: {len(db_url)})\" if db_url else \"❌ NON DÉFINI\"}'); print(f'SKIP_DB_CONNECTION: {os.getenv(\"SKIP_DB_CONNECTION\", \"non défini\")}')"

echo "🔄 Vérification de la base de données utilisée AVANT les migrations..."
DB_CHECK_OUTPUT=$(python -c "
import os
import sys
print('🔍 Vérification de DATABASE_URL...', file=sys.stderr)
db_url = os.getenv('DATABASE_URL', '')
print(f'DATABASE_URL: {\"défini\" if db_url else \"❌ NON DÉFINI\"}', file=sys.stderr)
print(f'Longueur: {len(db_url)}', file=sys.stderr)

print('🔍 Chargement de Django...', file=sys.stderr)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appointments.settings')
import django
django.setup()

print('🔍 Vérification de la configuration de la base de données...', file=sys.stderr)
from django.db import connection
engine = connection.settings_dict['ENGINE']
db_name = connection.settings_dict.get('NAME', 'N/A')
print(f'📊 Base de données: {engine}')
print(f'📊 Nom de la base: {db_name}')
if 'sqlite' in engine.lower():
    print('❌ ERREUR: Django utilise SQLite au lieu de PostgreSQL!', file=sys.stderr)
    print(f'❌ DATABASE_URL: {db_url[:100] if db_url else \"NON DÉFINI\"}...', file=sys.stderr)
    print('❌ Test d\'import de psycopg (psycopg 3) ou psycopg2...', file=sys.stderr)
    try:
        import psycopg
        print('✅ psycopg 3 peut être importé!', file=sys.stderr)
    except ImportError:
        try:
            import psycopg2
            print('✅ psycopg2 peut être importé!', file=sys.stderr)
        except Exception as e:
            print(f'❌ psycopg (psycopg 3) et psycopg2 ne peuvent PAS être importés: {e}', file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
    sys.exit(1)
else:
    print('✅ Django utilise PostgreSQL', file=sys.stderr)
" 2>&1)

DB_CHECK_EXIT=$?
echo "$DB_CHECK_OUTPUT"

if [ $DB_CHECK_EXIT -ne 0 ]; then
    echo "❌ ERREUR CRITIQUE: Django utilise SQLite au lieu de PostgreSQL!"
    echo "❌ Le script s'arrête pour éviter d'appliquer les migrations sur SQLite"
    exit 1
fi

# Si on arrive ici, PostgreSQL est utilisé
set -e  # Maintenant, arrêter le script en cas d'erreur

echo "🔄 Application des migrations..."
echo "📋 Liste des migrations à appliquer:"
python manage.py showmigrations --list || echo "⚠️  Impossible de lister les migrations"

echo "🔄 Application de toutes les migrations (y compris appointment)..."
python manage.py migrate --noinput --verbosity 2
# S'assurer que les migrations de appointment sont appliquées
python manage.py migrate appointment --noinput --verbosity 2 || echo "⚠️  Les migrations de appointment sont peut-être déjà appliquées"

echo "✅ Migrations appliquées avec succès"
echo "📋 Vérification des migrations appliquées:"
python manage.py showmigrations --list | grep -E "appointment|\[X\]|\[ \]" || echo "⚠️  Impossible de vérifier les migrations"

set +e  # Permettre les erreurs pour le superutilisateur
echo "👤 Création du superutilisateur (si configuré)..."
python create_superuser.py || echo "ℹ️  Superutilisateur non créé (variables d'environnement non configurées ou déjà existant)"
set -e  # Revenir à l'arrêt en cas d'erreur

echo "🚀 Démarrage de Gunicorn..."
# Utiliser set -e seulement pour gunicorn pour qu'il s'arrête en cas d'erreur
set -e
exec gunicorn appointments.wsgi:application --bind 0.0.0.0:$PORT

