#!/usr/bin/env python3
"""Génère directement les captures - démarre le serveur si nécessaire"""

import os
import sys
import time
import subprocess
import requests
from pathlib import Path
from threading import Thread

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

SCREENSHOT_DIR = Path(__file__).parent
BASE_URL = "http://localhost:8000/fr"
MANAGE_PY = Path(__file__).parent.parent.parent / "manage.py"

def check_server():
    """Vérifie si le serveur est actif"""
    try:
        response = requests.get(BASE_URL, timeout=2)
        return response.status_code in [200, 302, 301]
    except:
        return False

def start_server():
    """Démarre le serveur Django en arrière-plan"""
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
    
    # Attendre que le serveur démarre
    for i in range(30):
        time.sleep(1)
        if check_server():
            print("✓ Serveur démarré\n")
            return process
        if process.poll() is not None:
            print("❌ Le serveur n'a pas pu démarrer")
            return None
    
    print("⚠️  Timeout en attendant le serveur")
    return process

def capture_all():
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
        return False
    
    print("=" * 60)
    print("📸 CAPTURE DES PAGES DU SITE WEB")
    print("=" * 60)
    print()
    
    # Vérifier/ démarrer le serveur
    server_process = None
    if not check_server():
        server_process = start_server()
        if server_process is None:
            print("❌ Impossible de démarrer le serveur Django")
            return False
    else:
        print("✓ Serveur Django déjà actif\n")
    
    # Prendre les captures
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
                print(f"📸 {desc}...", end=" ", flush=True)
                url = BASE_URL + path
                page.goto(url, wait_until="networkidle", timeout=15000)
                time.sleep(1.5)  # Attendre que tout soit chargé
                
                screenshot_path = SCREENSHOT_DIR / f"{name}.png"
                page.screenshot(path=str(screenshot_path), full_page=True)
                
                size_kb = screenshot_path.stat().st_size / 1024
                print(f"✓ ({size_kb:.1f} KB)")
                captured += 1
                
            except Exception as e:
                print(f"✗ Erreur: {str(e)[:50]}")
        
        browser.close()
        
        print()
        print("=" * 60)
        print(f"✅ {captured}/{len(pages)} pages capturées avec succès!")
        print(f"📂 Emplacement: {SCREENSHOT_DIR}")
        print("=" * 60)
        
        # Arrêter le serveur si on l'a démarré
        if server_process:
            print("\n🛑 Arrêt du serveur Django...")
            try:
                server_process.terminate()
                time.sleep(2)
            except:
                pass
        
        return captured == len(pages)

if __name__ == "__main__":
    try:
        success = capture_all()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Interrompu par l'utilisateur")
        sys.exit(1)

