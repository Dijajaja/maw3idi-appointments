#!/usr/bin/env python3
"""Capture avec correction du problème de serveur"""

import os
import sys
import time
import subprocess
import requests
import signal
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

def kill_port_8000():
    """Tue tous les processus utilisant le port 8000"""
    try:
        if sys.platform == "win32":
            # Windows
            result = subprocess.run(
                ["netstat", "-ano"], 
                capture_output=True, 
                text=True
            )
            lines = result.stdout.split('\n')
            for line in lines:
                if ':8000' in line and 'LISTENING' in line:
                    parts = line.split()
                    if len(parts) > 4:
                        pid = parts[-1]
                        try:
                            subprocess.run(
                                ["taskkill", "/F", "/PID", pid],
                                capture_output=True
                            )
                            print(f"   ✓ Processus {pid} arrêté")
                        except:
                            pass
        else:
            # Linux/Mac
            subprocess.run(["lsof", "-ti:8000", "|", "xargs", "kill", "-9"], shell=True)
    except:
        pass

def check_correct_server():
    """Vérifie que le BON serveur tourne (celui avec appointments.urls)"""
    try:
        response = requests.get(BASE_URL, timeout=3, allow_redirects=True)
        
        # Vérifier que ce n'est pas une page 404
        if response.status_code == 404:
            # Vérifier si c'est une erreur backend.urls
            if 'backend.urls' in response.text:
                return False, "Mauvais serveur (backend.urls)"
            return False, "Page 404"
        
        # Vérifier que la page contient du contenu
        if len(response.text) < 500:
            return False, "Page trop petite"
        
        # Vérifier que c'est bien notre application
        if 'appointment' in response.text.lower() or 'service' in response.text.lower():
            return True, "Serveur correct"
        
        return True, "Serveur accessible"
    except Exception as e:
        return False, f"Erreur: {str(e)[:50]}"

def start_correct_server():
    """Démarre le bon serveur Django"""
    print("🔄 Arrêt des serveurs existants sur le port 8000...")
    kill_port_8000()
    time.sleep(2)
    
    print("🔄 Démarrage du serveur Django correct...")
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
    for i in range(40):
        time.sleep(1)
        is_correct, msg = check_correct_server()
        if is_correct:
            print(f"✓ Serveur démarré et correct ({msg})\n")
            time.sleep(1)
            return process
        elif i == 5:
            print(f"   En attente... ({msg})")
    
    print("⚠️  Serveur démarré mais pourrait être incorrect")
    return process

def capture_all():
    """Capture toutes les pages"""
    if not PLAYWRIGHT_AVAILABLE:
        print("❌ Playwright n'est pas installé")
        return False
    
    SCREENSHOT_DIR.mkdir(exist_ok=True)
    
    print("=" * 70)
    print("📸 CAPTURE AVEC VÉRIFICATION DU SERVEUR")
    print("=" * 70)
    print()
    
    # Vérifier le serveur
    print("🔍 Vérification du serveur...")
    is_correct, msg = check_correct_server()
    
    server_process = None
    if not is_correct:
        print(f"❌ {msg}")
        print("   Redémarrage du serveur...\n")
        server_process = start_correct_server()
        if not server_process:
            print("❌ Impossible de démarrer le serveur")
            return False
    else:
        print(f"✓ {msg}\n")
    
    # Capturer les pages
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            device_scale_factor=2
        )
        page = context.new_page()
        page.set_default_timeout(30000)
        
        captured = 0
        
        print("─" * 70)
        print("📄 CAPTURE DES PAGES")
        print("─" * 70)
        
        for path, name, desc in PAGES_PUBLIQUES:
            try:
                print(f"📸 {desc}...", end=" ", flush=True)
                url = BASE_URL + path
                
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
                page.wait_for_load_state("networkidle", timeout=15000)
                time.sleep(3)
                
                # Vérifier qu'il y a du contenu
                body_text = page.inner_text("body")
                if len(body_text) < 100:
                    print(f"⚠️  Contenu minimal ({len(body_text)} chars)")
                else:
                    screenshot_path = SCREENSHOT_DIR / f"{name}.png"
                    page.screenshot(path=str(screenshot_path), full_page=True)
                    size_kb = screenshot_path.stat().st_size / 1024
                    print(f"✓ ({size_kb:.1f} KB)")
                    captured += 1
                    
            except Exception as e:
                print(f"✗ {str(e)[:40]}")
            print()
        
        browser.close()
        
        print("=" * 70)
        print(f"✅ {captured}/{len(PAGES_PUBLIQUES)} pages capturées")
        print(f"📂 {SCREENSHOT_DIR}")
        print("=" * 70)
        
        if server_process:
            print("\n🛑 Arrêt du serveur...")
            try:
                server_process.terminate()
                time.sleep(2)
            except:
                pass
        
        return captured > 0

if __name__ == "__main__":
    try:
        success = capture_all()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Interrompu")
        sys.exit(1)

