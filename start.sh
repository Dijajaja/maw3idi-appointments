#!/bin/bash
# Script de démarrage pour Render
# Applique les migrations automatiquement au démarrage

# Ne pas arrêter le script si une commande échoue (sauf pour gunicorn)
set +e

echo "🔄 Application des migrations..."
echo "📋 Liste des migrations à appliquer:"
python manage.py showmigrations --list || echo "⚠️  Impossible de lister les migrations"

echo "🔄 Application de toutes les migrations..."
python manage.py migrate --noinput --verbosity 2
MIGRATE_EXIT=$?

if [ $MIGRATE_EXIT -ne 0 ]; then
    echo "⚠️  Erreur lors de l'application des migrations (code: $MIGRATE_EXIT)"
    echo "ℹ️  Tentative de connexion à la base de données..."
    python -c "import django; django.setup(); from django.db import connection; connection.ensure_connection()" || echo "❌ Impossible de se connecter à la base de données"
else
    echo "✅ Migrations appliquées avec succès"
    echo "📋 Vérification des migrations appliquées:"
    python manage.py showmigrations --list | grep -E "\[X\]|\[ \]" || echo "⚠️  Impossible de vérifier les migrations"
fi

echo "👤 Création du superutilisateur (si configuré)..."
python create_superuser.py || echo "ℹ️  Superutilisateur non créé (variables d'environnement non configurées ou déjà existant)"

echo "🚀 Démarrage de Gunicorn..."
# Utiliser set -e seulement pour gunicorn pour qu'il s'arrête en cas d'erreur
set -e
exec gunicorn appointments.wsgi:application --bind 0.0.0.0:$PORT

