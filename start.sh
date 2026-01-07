#!/bin/bash
# Script de démarrage pour Render
# Applique les migrations automatiquement au démarrage

# Ne pas arrêter le script si une commande échoue (sauf pour gunicorn)
set +e

echo "🔄 Application des migrations..."
python manage.py migrate --noinput
if [ $? -ne 0 ]; then
    echo "⚠️  Erreur lors de l'application des migrations"
    echo "ℹ️  Tentative de connexion à la base de données..."
    python -c "import django; django.setup(); from django.db import connection; connection.ensure_connection()" || echo "❌ Impossible de se connecter à la base de données"
fi

echo "👤 Création du superutilisateur (si configuré)..."
python create_superuser.py || echo "ℹ️  Superutilisateur non créé (variables d'environnement non configurées ou déjà existant)"

echo "🚀 Démarrage de Gunicorn..."
# Utiliser set -e seulement pour gunicorn pour qu'il s'arrête en cas d'erreur
set -e
exec gunicorn appointments.wsgi:application --bind 0.0.0.0:$PORT

