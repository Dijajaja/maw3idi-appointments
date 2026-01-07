#!/usr/bin/env python3
"""Capture TOUTES les pages possibles du site"""

import os
import sys
import time
import subprocess
import requests
from pathlib import Path
from datetime import datetime

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

SCREENSHOT_DIR = Path(__file__).parent
BASE_URL = "http://localhost:8000/fr"
MANAGE_PY = Path(__file__).parent.parent.parent / "manage.py"

# Liste complète de toutes les pages à capturer
PAGES_PUBLIQUES = [
    ("/", "01_page_accueil", "Page d'accueil - Liste des services"),
    ("/login/", "02_page_connexion", "Page de connexion"),
    ("/register/", "03_page_inscription", "Page d'inscription"),
    ("/contact/", "04_page_contact", "Page de contact"),
    ("/new-appointment/", "05_nouveau_rendez_vous", "Page nouveau rendez-vous"),
]

PAGES_AUTHENTIFIEES = [
    ("/my-appointments/", "06_mes_rendez_vous", "Mes rendez-vous"),
    ("/calendar/", "07_calendrier", "Calendrier"),
    ("/update-user-info-simple/", "08_modifier_profil", "Modifier mon profil"),
    ("/change-password-simple/", "09_changer_mot_de_passe", "Changer mot de passe"),
]

PAGES_ADMIN = [
    ("/app-admin/appointments/", "10_admin_rendez_vous", "Admin - Liste des rendez-vous"),
    ("/app-admin/service-list/", "11_admin_liste_services", "Admin - Liste des services"),
    ("/app-admin/add-service/", "12_admin_ajouter_service", "Admin - Ajouter un service"),
    ("/app-admin/user-profile/", "13_admin_profil", "Admin - Profil utilisateur"),
    ("/app-admin/add-staff-member-info/", "14_admin_ajouter_staff", "Admin - Ajouter membre staff"),
    ("/admin-dashboard/", "15_tableau_de_bord_admin", "Tableau de bord admin"),
]

def check_server():
    """Vérifie si le serveur est actif"""
    try:
        response = requests.get(BASE_URL, timeout=2)
        return response.status_code in [200, 302, 301]
    except:
        return False

def start_server():
    """Démarre le serveur Django"""
    print("🔄 Démarrage du serveur Django...")
    env = os.environ.copy()
    env['PYTHONUNBUFFERED'] = '1'
    
    process = subprocess.Popen(
        [sys.executable, str(MANAGE_PY), "runserver"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
    )
    
    for i in range(30):
        time.sleep(1)
        if check_server():
            print("✓ Serveur démarré\n")
            return process
    
    return process

def capture_page(page, url, name, description, context=None):
    """Capture une page spécifique"""
    try:
        print(f"📸 {description}...", end=" ", flush=True)
        
        if context:
            page.goto(url, wait_until="networkidle", timeout=15000)
        else:
            page.goto(url, wait_until="networkidle", timeout=15000)
        
        time.sleep(2)  # Attendre que tout soit chargé
        
        screenshot_path = SCREENSHOT_DIR / f"{name}.png"
        page.screenshot(path=str(screenshot_path), full_page=True)
        
        size_kb = screenshot_path.stat().st_size / 1024
        print(f"✓ ({size_kb:.1f} KB)")
        return True
        
    except Exception as e:
        error_msg = str(e)[:50]
        print(f"✗ Erreur: {error_msg}")
        return False

def capture_all():
    """Capture toutes les pages"""
    SCREENSHOT_DIR.mkdir(exist_ok=True)
    
    if not PLAYWRIGHT_AVAILABLE:
        print("❌ Playwright n'est pas installé.")
        print("Installez-le avec: pip install playwright && playwright install chromium")
        return False
    
    print("=" * 70)
    print("📸 CAPTURE DE TOUTES LES PAGES DU SITE WEB")
    print("=" * 70)
    print()
    
    # Vérifier/démarrer le serveur
    server_process = None
    if not check_server():
        server_process = start_server()
        if server_process is None:
            print("❌ Impossible de démarrer le serveur Django")
            return False
    else:
        print("✓ Serveur Django déjà actif\n")
    
    total_captured = 0
    total_pages = len(PAGES_PUBLIQUES) + len(PAGES_AUTHENTIFIEES) + len(PAGES_ADMIN)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            device_scale_factor=2
        )
        page = context.new_page()
        
        # 1. Pages publiques
        print("─" * 70)
        print("📄 PAGES PUBLIQUES")
        print("─" * 70)
        for path, name, desc in PAGES_PUBLIQUES:
            url = BASE_URL + path
            if capture_page(page, url, name, desc):
                total_captured += 1
            print()
        
        # 2. Pages authentifiées (nécessitent connexion)
        print("─" * 70)
        print("🔐 PAGES AUTHENTIFIÉES")
        print("─" * 70)
        print("⚠️  Note: Ces pages nécessitent une connexion.")
        print("   Elles seront capturées mais peuvent être vides si non connecté.\n")
        
        for path, name, desc in PAGES_AUTHENTIFIEES:
            url = BASE_URL + path
            if capture_page(page, url, name, desc):
                total_captured += 1
            print()
        
        # 3. Pages admin
        print("─" * 70)
        print("👑 PAGES ADMINISTRATION")
        print("─" * 70)
        print("⚠️  Note: Ces pages nécessitent des droits admin.")
        print("   Elles seront capturées mais peuvent être vides si non connecté.\n")
        
        for path, name, desc in PAGES_ADMIN:
            url = BASE_URL + path
            if capture_page(page, url, name, desc):
                total_captured += 1
            print()
        
        browser.close()
        
        # Résumé
        print("=" * 70)
        print(f"✅ RÉSUMÉ: {total_captured}/{total_pages} pages capturées")
        print(f"📂 Emplacement: {SCREENSHOT_DIR}")
        print("=" * 70)
        
        # Arrêter le serveur si on l'a démarré
        if server_process:
            print("\n🛑 Arrêt du serveur Django...")
            try:
                server_process.terminate()
                time.sleep(2)
            except:
                pass
        
        return total_captured > 0

if __name__ == "__main__":
    try:
        success = capture_all()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Interrompu par l'utilisateur")
        sys.exit(1)

