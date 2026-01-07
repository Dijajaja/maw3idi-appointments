#!/usr/bin/env python3
"""
Capture TOUTES les pages avec vérification stricte
Arrête Green Check et capture uniquement les pages du bon serveur
"""

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

# Toutes les pages à capturer
PAGES_PUBLIQUES = [
    ("/", "01_page_accueil", "Page d'accueil"),
    ("/login/", "02_page_connexion", "Page de connexion"),
    ("/register/", "03_page_inscription", "Page d'inscription"),
    ("/contact/", "04_page_contact", "Page de contact"),
    ("/appointment-request/", "05_nouveau_rendez_vous", "Nouveau rendez-vous"),
]

PAGES_AUTH = [
    ("/appointments/", "06_mes_rendez_vous", "Mes rendez-vous"),
    ("/calendar/", "07_calendrier", "Calendrier"),
    ("/client-information/", "08_modifier_profil", "Modifier profil"),
    ("/change-password/", "09_changer_mot_de_passe", "Changer mot de passe"),
]

PAGES_ADMIN = [
    ("/admin/appointment/appointment/", "10_admin_rendez_vous", "Admin rendez-vous"),
    ("/admin/appointment/service/", "11_admin_liste_services", "Admin services"),
    ("/admin/appointment/service/add/", "12_admin_ajouter_service", "Ajouter service"),
    ("/admin/appointment/staffmember/", "13_admin_profil", "Admin staff"),
    ("/admin/appointment/staffmember/add/", "14_admin_ajouter_staff", "Ajouter staff"),
    ("/admin/", "15_tableau_de_bord_admin", "Dashboard admin"),
]

def kill_all_servers():
    """Arrête TOUS les serveurs Django agressivement"""
    print("🛑 Arrêt de TOUS les serveurs Django...")
    
    if sys.platform == "win32":
        try:
            # Par port
            result = subprocess.run(
                ["netstat", "-ano"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            pids = []
            for line in result.stdout.split('\n'):
                if ':8000' in line and 'LISTENING' in line:
                    parts = line.split()
                    if len(parts) > 4:
                        pids.append(parts[-1])
            
            for pid in pids:
                try:
                    subprocess.run(
                        ["taskkill", "/F", "/PID", pid],
                        capture_output=True,
                        stderr=subprocess.DEVNULL
                    )
                except:
                    pass
            
            # Tous les Python
            subprocess.run(
                ["taskkill", "/F", "/IM", "python.exe"],
                capture_output=True,
                stderr=subprocess.DEVNULL
            )
        except:
            pass
        
        time.sleep(3)

def verify_correct_server_strict():
    """Vérifie STRICTEMENT que c'est le bon serveur"""
    try:
        response = requests.get(BASE_URL, timeout=3, allow_redirects=True)
        
        # Vérifications strictes
        if 'Backend Green Check' in response.text:
            return False, "Serveur Green Check détecté"
        
        if 'backend.urls' in response.text:
            return False, "backend.urls détecté"
        
        if response.status_code == 404:
            if 'backend.urls' in response.text:
                return False, "404 avec backend.urls"
            return False, "Page 404"
        
        # Vérifier que c'est bien notre app
        if 'appointment' not in response.text.lower() and 'service' not in response.text.lower():
            return False, "Contenu non reconnu"
        
        return True, "Serveur correct"
        
    except Exception as e:
        return False, f"Erreur: {str(e)[:40]}"

def start_correct_server():
    """Démarre le bon serveur"""
    print("🚀 Démarrage du serveur appointments...")
    
    env = os.environ.copy()
    env['PYTHONUNBUFFERED'] = '1'
    
    if sys.platform == "win32":
        process = subprocess.Popen(
            [sys.executable, str(MANAGE_PY), "runserver"],
            creationflags=subprocess.CREATE_NEW_CONSOLE,
            env=env
        )
    else:
        process = subprocess.Popen(
            [sys.executable, str(MANAGE_PY), "runserver"],
            env=env
        )
    
    # Attendre et vérifier
    for i in range(30):
        time.sleep(1)
        is_correct, msg = verify_correct_server_strict()
        if is_correct:
            print(f"✓ Serveur correct démarré (tentative {i+1})")
            time.sleep(2)
            return process
        elif i % 5 == 0:
            print(f"   En attente... ({msg})")
    
    return process

def capture_page(page, url, name, desc):
    """Capture une page avec vérification"""
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_load_state("networkidle", timeout=15000)
        time.sleep(3)
        
        # Vérifier le contenu
        page_text = page.inner_text("body")
        
        # Vérifier que ce n'est PAS Green Check
        if 'Backend Green Check' in page_text or 'backend.urls' in page_text:
            return False, "Page Green Check détectée"
        
        # Vérifier qu'il y a du contenu
        if len(page_text) < 50:
            return False, "Contenu minimal"
        
        # Capturer
        screenshot_path = SCREENSHOT_DIR / f"{name}.png"
        page.screenshot(path=str(screenshot_path), full_page=True)
        
        size_kb = screenshot_path.stat().st_size / 1024
        if size_kb < 50:
            screenshot_path.unlink()
            return False, f"Image suspecte ({size_kb:.1f} KB)"
        
        return True, f"{size_kb:.1f} KB"
        
    except Exception as e:
        return False, str(e)[:40]

def capture_all():
    """Capture toutes les pages"""
    if not PLAYWRIGHT_AVAILABLE:
        print("❌ Playwright non installé")
        return False
    
    SCREENSHOT_DIR.mkdir(exist_ok=True)
    
    print("=" * 70)
    print("📸 CAPTURE DE TOUTES LES PAGES AVEC VÉRIFICATION")
    print("=" * 70)
    print()
    
    # Arrêter tous les serveurs
    kill_all_servers()
    time.sleep(2)
    
    # Vérifier le serveur
    is_correct, msg = verify_correct_server_strict()
    
    server_process = None
    if not is_correct:
        print(f"❌ {msg}")
        print("   Démarrage du bon serveur...\n")
        server_process = start_correct_server()
        time.sleep(5)
        
        is_correct, msg = verify_correct_server_strict()
        if not is_correct:
            print(f"❌ {msg}")
            return False
    else:
        print(f"✓ {msg}\n")
    
    # Capturer
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            device_scale_factor=2
        )
        page = context.new_page()
        page.set_default_timeout(30000)
        
        total_captured = 0
        total_skipped = 0
        
        # Pages publiques
        print("─" * 70)
        print("📄 PAGES PUBLIQUES")
        print("─" * 70)
        for path, name, desc in PAGES_PUBLIQUES:
            url = BASE_URL + path
            print(f"📸 {desc}...", end=" ", flush=True)
            success, result = capture_page(page, url, name, desc)
            if success:
                print(f"✓ ({result})")
                total_captured += 1
            else:
                print(f"⚠️  SKIP - {result}")
                total_skipped += 1
            print()
        
        # Pages authentifiées
        print("─" * 70)
        print("🔐 PAGES AUTHENTIFIÉES")
        print("─" * 70)
        for path, name, desc in PAGES_AUTH:
            url = BASE_URL + path
            print(f"📸 {desc}...", end=" ", flush=True)
            success, result = capture_page(page, url, name, desc)
            if success:
                print(f"✓ ({result})")
                total_captured += 1
            else:
                print(f"⚠️  SKIP - {result}")
                total_skipped += 1
            print()
        
        # Pages admin
        print("─" * 70)
        print("👑 PAGES ADMINISTRATION")
        print("─" * 70)
        for path, name, desc in PAGES_ADMIN:
            url = BASE_URL + path
            print(f"📸 {desc}...", end=" ", flush=True)
            success, result = capture_page(page, url, name, desc)
            if success:
                print(f"✓ ({result})")
                total_captured += 1
            else:
                print(f"⚠️  SKIP - {result}")
                total_skipped += 1
            print()
        
        browser.close()
        
        print("=" * 70)
        print(f"✅ {total_captured} pages capturées")
        if total_skipped > 0:
            print(f"⚠️  {total_skipped} pages ignorées (Green Check ou contenu vide)")
        print(f"📂 {SCREENSHOT_DIR}")
        print("=" * 70)
        
        if server_process:
            print("\n🛑 Le serveur continuera de tourner dans sa console")
            print("   Fermez la console pour l'arrêter")
        
        return total_captured > 0

if __name__ == "__main__":
    try:
        success = capture_all()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Interrompu")
        sys.exit(1)

