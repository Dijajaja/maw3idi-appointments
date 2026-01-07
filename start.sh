#!/bin/bash
# Script de démarrage pour Render
# Applique les migrations automatiquement au démarrage

set -e

echo "🔄 Application des migrations..."
python manage.py migrate --noinput || echo "⚠️  Erreur lors de l'application des migrations (peut être normal si déjà appliquées)"

echo "🚀 Démarrage de Gunicorn..."
exec gunicorn appointments.wsgi:application --bind 0.0.0.0:$PORT

