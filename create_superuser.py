#!/usr/bin/env python
"""
Script pour créer un superutilisateur automatiquement lors du déploiement.
À utiliser uniquement si vous n'avez pas accès au Shell Render.
"""
import os
import sys

try:
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appointments.settings')
    django.setup()

    from django.contrib.auth import get_user_model

    User = get_user_model()

    # Récupérer les informations depuis les variables d'environnement
    admin_username = os.getenv('ADMIN_USERNAME', 'admin')
    admin_email = os.getenv('ADMIN_EMAIL', 'admin@example.com')
    admin_password = os.getenv('ADMIN_PASSWORD', 'changeme123')

    # Vérifier que les variables sont configurées
    if not admin_password or admin_password == 'changeme123':
        print("⚠️  ADMIN_PASSWORD n'est pas configuré. Superutilisateur non créé.")
        sys.exit(0)

    # Créer le superutilisateur s'il n'existe pas
    if not User.objects.filter(username=admin_username).exists():
        User.objects.create_superuser(
            username=admin_username,
            email=admin_email,
            password=admin_password
        )
        print(f"✅ Superutilisateur '{admin_username}' créé avec succès!")
    else:
        print(f"ℹ️  Le superutilisateur '{admin_username}' existe déjà.")
except Exception as e:
    print(f"⚠️  Erreur lors de la création du superutilisateur: {e}")
    print("ℹ️  Le superutilisateur peut être créé manuellement plus tard.")
    # Ne pas faire échouer le déploiement si la création du superutilisateur échoue
    sys.exit(0)

