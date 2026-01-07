#!/usr/bin/env python3
"""Capture avec vérification que le contenu est bien chargé"""

import os
import sys
import time
import subprocess
import requests
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

SCREENSHOT_DIR = Path(__file__).parent
BASE_URL = "http://localhost:8000/fr"
MANAGE_PY = Path(__file__).parent.parent.parent / "manage.py"

PAGES_PUBLIQUES = [
    ("/", "01_page_accueil", "Page d'accueil"),
    ("/login/", "02_page_connexion", "Page de connexion"),
    ("/register/", "03_page_inscription", "Page d'inscription"),
    ("/contact/", "04_page_contact", "Page de contact"),
]

def check_server():
    """Vérifie vraiment que le serveur fonctionne"""
    try:
        response = requests.get(BASE_URL, timeout=5)
        print(f"   Status code: {response.status_code}")
        if response.status_code == 200:
            print(f"   Taille réponse: {len(response.content)} bytes")
        return response.status_code in [200, 302, 301]
    except Exception as e:
        print(f"   Erreur: {e}")
        return False

def capture_with_verification():
    """Capture avec vérification du contenu"""
    if not PLAYWRIGHT_AVAILABLE:
        print("❌ Playwright n'est pas installé")
        return False
    
    print("=" * 70)
    print("📸 CAPTURE AVEC VÉRIFICATION DU CONTENU")
    print("=" * 70)
    print()
    
    # Vérifier le serveur
    print("🔍 Vérification du serveur Django...")
    if not check_server():
        print("❌ Le serveur Django n'est pas accessible!")
        print(f"   URL testée: {BASE_URL}")
        print("\n💡 Assurez-vous que le serveur est démarré:")
        print("   python manage.py runserver")
        return False
    
    print("✓ Serveur accessible\n")
    
    SCREENSHOT_DIR.mkdir(exist_ok=True)
    
    with sync_playwright() as p:
        # Utiliser headless=False pour voir ce qui se passe
        print("🌐 Lancement du navigateur (mode visible)...")
        browser = p.chromium.launch(headless=False, slow_mo=500)
        
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            device_scale_factor=1
        )
        
        page = context.new_page()
        page.set_default_timeout(30000)  # 30 secondes
        
        captured = 0
        
        for path, name, desc in PAGES_PUBLIQUES:
            try:
                url = BASE_URL + path
                print(f"\n📸 {desc}")
                print(f"   URL: {url}")
                
                # Naviguer
                print("   → Navigation...")
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
                
                # Attendre que le body soit présent
                print("   → Attente du contenu...")
                page.wait_for_selector("body", timeout=10000)
                
                # Attendre que la page soit complètement chargée
                print("   → Attente du chargement complet...")
                page.wait_for_load_state("networkidle", timeout=15000)
                
                # Attendre encore un peu pour le CSS/JS
                print("   → Attente du rendu final...")
                time.sleep(4)
                
                # Vérifier qu'il y a du contenu
                body_text = page.inner_text("body")
                if len(body_text) < 50:
                    print(f"   ⚠️  Contenu minimal détecté ({len(body_text)} caractères)")
                
                # Capturer
                screenshot_path = SCREENSHOT_DIR / f"{name}.png"
                print(f"   → Capture en cours...")
                page.screenshot(path=str(screenshot_path), full_page=True)
                
                size_kb = screenshot_path.stat().st_size / 1024
                print(f"   ✓ Capturé: {size_kb:.1f} KB")
                
                # Vérifier la taille
                if size_kb < 20:
                    print(f"   ⚠️  ATTENTION: Image très petite ({size_kb:.1f} KB)")
                else:
                    captured += 1
                    
            except Exception as e:
                print(f"   ✗ Erreur: {str(e)[:100]}")
        
        # Garder le navigateur ouvert 5 secondes pour inspection
        print("\n⏸️  Navigateur ouvert 5 secondes pour inspection...")
        time.sleep(5)
        
        browser.close()
        
        print("\n" + "=" * 70)
        print(f"✅ {captured}/{len(PAGES_PUBLIQUES)} pages capturées")
        print(f"📂 {SCREENSHOT_DIR}")
        print("=" * 70)
        
        return captured > 0

if __name__ == "__main__":
    capture_with_verification()

