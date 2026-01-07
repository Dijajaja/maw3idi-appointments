#!/usr/bin/env python3
"""
Script pour capturer les pages principales du site web
Génère des screenshots de toutes les pages importantes
"""

import os
import sys
import time
import subprocess
import requests
from pathlib import Path
from urllib.parse import urljoin

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

# Configuration
BASE_URL = "http://localhost:8000"
FR_BASE_URL = f"{BASE_URL}/fr"
SCREENSHOT_DIR = Path(__file__).parent
WAIT_TIME = 2  # Temps d'attente après chargement de page

# Liste des pages à capturer avec leurs noms
PAGES_TO_CAPTURE = [
    {
        "url": f"{FR_BASE_URL}/",
        "name": "01_page_accueil",
        "description": "Page d'accueil - Liste des services"
    },
    {
        "url": f"{FR_BASE_URL}/login/",
        "name": "02_page_connexion",
        "description": "Page de connexion"
    },
    {
        "url": f"{FR_BASE_URL}/register/",
        "name": "03_page_inscription",
        "description": "Page d'inscription"
    },
    {
        "url": f"{FR_BASE_URL}/contact/",
        "name": "04_page_contact",
        "description": "Page de contact"
    },
    {
        "url": f"{FR_BASE_URL}/calendar/",
        "name": "05_page_calendrier",
        "description": "Page calendrier (nécessite connexion)"
    },
]

def check_server_running(url):
    """Vérifie si le serveur Django est en cours d'exécution"""
    try:
        response = requests.get(url, timeout=2)
        return response.status_code in [200, 302, 301]
    except:
        return False

def start_django_server():
    """Démarre le serveur Django en arrière-plan"""
    print("⚠️  Le serveur Django n'est pas démarré.")
    print("Veuillez démarrer le serveur Django avec:")
    print("   python manage.py runserver")
    print("\nOu dans un autre terminal:")
    print("   cd C:\\Users\\PC\\django-appointment")
    print("   python manage.py runserver")
    return False

def capture_with_playwright():
    """Capture les pages avec Playwright (recommandé)"""
    print("=" * 60)
    print("Capture des pages avec Playwright")
    print("=" * 60)
    print()
    
    with sync_playwright() as p:
        # Lancer le navigateur
        print("Lancement du navigateur...")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            device_scale_factor=2  # Pour des captures haute résolution
        )
        page = context.new_page()
        
        captured_count = 0
        failed_pages = []
        
        for page_info in PAGES_TO_CAPTURE:
            url = page_info["url"]
            name = page_info["name"]
            description = page_info["description"]
            
            try:
                print(f"📸 Capture: {description}...", end=" ")
                
                # Naviguer vers la page
                page.goto(url, wait_until="networkidle", timeout=10000)
                
                # Attendre un peu pour que tout soit chargé
                time.sleep(WAIT_TIME)
                
                # Prendre la capture
                screenshot_path = SCREENSHOT_DIR / f"{name}.png"
                page.screenshot(path=str(screenshot_path), full_page=True)
                
                print(f"✓ ({screenshot_path.stat().st_size / 1024:.1f} KB)")
                captured_count += 1
                
            except Exception as e:
                print(f"✗ Erreur: {e}")
                failed_pages.append(name)
            
            print()
        
        browser.close()
        
        # Résumé
        print("=" * 60)
        print(f"Résumé: {captured_count}/{len(PAGES_TO_CAPTURE)} page(s) capturée(s)")
        if failed_pages:
            print(f"Pages en échec: {', '.join(failed_pages)}")
        print(f"Emplacement: {SCREENSHOT_DIR}")
        print("=" * 60)
        
        return captured_count == len(PAGES_TO_CAPTURE)

def capture_with_requests():
    """Méthode alternative simple (ne capture que le HTML, pas le rendu)"""
    print("⚠️  Playwright n'est pas disponible.")
    print("Installation recommandée: pip install playwright")
    print("Puis: playwright install chromium")
    print()
    print("Utilisation d'une méthode alternative limitée...")
    return False

def main():
    """Fonction principale"""
    # Créer le dossier s'il n'existe pas
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Vérifier si le serveur est en cours d'exécution
    print("Vérification du serveur Django...")
    if not check_server_running(BASE_URL):
        if not start_django_server():
            return 1
        print("\n⏳ Attente de 5 secondes pour le démarrage du serveur...")
        time.sleep(5)
        
        # Vérifier à nouveau
        if not check_server_running(BASE_URL):
            print("❌ Impossible de se connecter au serveur Django.")
            print("Assurez-vous que le serveur est démarré sur http://localhost:8000")
            return 1
    
    print("✓ Serveur Django détecté\n")
    
    # Choisir la méthode de capture
    if PLAYWRIGHT_AVAILABLE:
        success = capture_with_playwright()
        return 0 if success else 1
    else:
        capture_with_requests()
        print("\n❌ Playwright n'est pas installé.")
        print("Pour installer:")
        print("   pip install playwright")
        print("   playwright install chromium")
        return 1

if __name__ == "__main__":
    sys.exit(main())

