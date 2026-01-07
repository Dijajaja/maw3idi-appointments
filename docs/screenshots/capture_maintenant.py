#!/usr/bin/env python3
"""Script simple pour capturer les pages - exécute directement"""

import os
import sys
import time
from pathlib import Path

# Ajouter le répertoire parent au path pour importer Django
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    import django
    from django.conf import settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appointments.settings')
    django.setup()
    
    from django.test import Client
    from django.template.loader import render_to_string
    
    DJANGO_AVAILABLE = True
except:
    DJANGO_AVAILABLE = False

try:
    from PIL import Image, ImageDraw, ImageFont
    from io import BytesIO
    import requests
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

SCREENSHOT_DIR = Path(__file__).parent
BASE_URL = "http://localhost:8000/fr"

def capture_pages():
    """Capture toutes les pages"""
    SCREENSHOT_DIR.mkdir(exist_ok=True)
    
    pages = [
        ("/", "01_page_accueil", "Page d'accueil"),
        ("/login/", "02_page_connexion", "Page de connexion"),
        ("/register/", "03_page_inscription", "Page d'inscription"),
        ("/contact/", "04_page_contact", "Page de contact"),
    ]
    
    if not PLAYWRIGHT_AVAILABLE:
        print("❌ Playwright n'est pas installé.")
        print("Installation: pip install playwright && playwright install chromium")
        return False
    
    print("=" * 60)
    print("Capture des pages du site web")
    print("=" * 60)
    print()
    
    # Vérifier si le serveur est actif
    try:
        response = requests.get(BASE_URL, timeout=2)
        if response.status_code not in [200, 302]:
            print("❌ Le serveur Django ne semble pas être démarré.")
            print("Démarrez-le avec: python manage.py runserver")
            return False
    except:
        print("❌ Impossible de se connecter au serveur Django.")
        print("Assurez-vous que le serveur est démarré sur http://localhost:8000")
        return False
    
    print("✓ Serveur Django détecté\n")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            device_scale_factor=2
        )
        page = context.new_page()
        
        captured = 0
        
        for path, name, desc in pages:
            try:
                print(f"📸 {desc}...", end=" ")
                url = BASE_URL + path
                page.goto(url, wait_until="networkidle", timeout=10000)
                time.sleep(1)
                
                screenshot_path = SCREENSHOT_DIR / f"{name}.png"
                page.screenshot(path=str(screenshot_path), full_page=True)
                
                size_kb = screenshot_path.stat().st_size / 1024
                print(f"✓ ({size_kb:.1f} KB)")
                captured += 1
                
            except Exception as e:
                print(f"✗ Erreur: {e}")
        
        browser.close()
        
        print()
        print("=" * 60)
        print(f"✅ {captured}/{len(pages)} pages capturées")
        print(f"📂 Emplacement: {SCREENSHOT_DIR}")
        print("=" * 60)
        
        return captured == len(pages)

if __name__ == "__main__":
    capture_pages()

