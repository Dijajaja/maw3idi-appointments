#!/usr/bin/env bash
# Script de build pour Render
# Ce script installe les dépendances, collecte les fichiers statiques,
# applique les migrations et crée un superutilisateur si nécessaire

set -o errexit

echo "📦 Installation des dépendances..."
pip install -r requirements.txt

echo "📁 Collecte des fichiers statiques..."
python manage.py collectstatic --noinput

echo "🔄 Application des migrations..."
python manage.py migrate --noinput

echo "👤 Création du superutilisateur (si nécessaire)..."
python create_superuser.py

echo "✅ Build terminé avec succès!"

