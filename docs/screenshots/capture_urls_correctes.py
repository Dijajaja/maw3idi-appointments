#!/usr/bin/env python3
"""
Capture avec les VRAIES URLs du projet Django
Basé sur appointment/urls.py
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

# URLs CORRECTES basées sur appointment/urls.py
ALL_PAGES = [
    # Pages publiques
    ("/", "01_page_accueil", "Page d'accueil"),
    ("/login/", "02_page_connexion", "Page de connexion"),
    ("/register/", "03_page_inscription", "Page d'inscription"),
    ("/contact/", "04_page_contact", "Page de contact"),
    ("/new-appointment/", "05_nouveau_rendez_vous", "Nouveau rendez-vous"),
    
    # Pages authentifiées
    ("/my-appointments/", "06_mes_rendez_vous", "Mes rendez-vous"),
    ("/calendar/", "07_calendrier", "Calendrier"),
    ("/update-user-info-simple/", "08_modifier_profil", "Modifier profil"),
    ("/change-password-simple/", "09_changer_mot_de_passe", "Changer mot de passe"),
    
    # Pages admin (app-admin/)
    ("/app-admin/appointments/", "10_admin_rendez_vous", "Admin rendez-vous"),
    ("/app-admin/service-list/", "11_admin_liste_services", "Admin services"),
    ("/app-admin/add-service/", "12_admin_ajouter_service", "Ajouter service"),
    ("/app-admin/user-profile/", "13_admin_profil", "Admin profil"),
    ("/app-admin/add-staff-member/", "14_admin_ajouter_staff", "Ajouter staff"),
    ("/admin-dashboard/", "15_tableau_de_bord_admin", "Dashboard admin"),
]

def kill_all_servers():
    """Arrête TOUS les serveurs"""
    print("🛑 Arrêt de TOUS les serveurs...")
    
    if sys.platform == "win32":
        try:
            subprocess.run(
                ["taskkill", "/F", "/IM", "python.exe"],
                capture_output=True,
                stderr=subprocess.DEVNULL
            )
            time.sleep(3)
        except:
            pass

def verify_server():
    """Vérifie le serveur"""
    try:
        response = requests.get(BASE_URL, timeout=2, allow_redirects=True)
        
        if 'Backend Green Check' in response.text:
            return False, "Green Check détecté"
        if 'backend.urls' in response.text:
            return False, "backend.urls détecté"
        
        return True, "OK"
    except:
        return False, "Serveur non accessible"

def is_green_check_page(page_content):
    """Vérifie si c'est une page Green Check"""
    indicators = ['Backend Green Check', 'backend.urls', 'Using the URLconf defined in backend']
    content_lower = page_content.lower()
    return any(ind.lower() in content_lower for ind in indicators)

def capture_all_correct():
    """Capture toutes les pages avec les bonnes URLs"""
    if not PLAYWRIGHT_AVAILABLE:
        print("❌ Playwright non installé")
        return False
    
    SCREENSHOT_DIR.mkdir(exist_ok=True)
    
    print("=" * 70)
    print("📸 CAPTURE AVEC URLs CORRECTES")
    print("=" * 70)
    print()
    
    # Arrêter tous les serveurs
    kill_all_servers()
    time.sleep(2)
    
    # Vérifier le serveur
    is_ok, msg = verify_server()
    if not is_ok:
        print(f"❌ {msg}")
        print("   Démarrage du serveur...")
        
        env = os.environ.copy()
        env['PYTHONUNBUFFERED'] = '1'
        
        if sys.platform == "win32":
            subprocess.Popen(
                [sys.executable, str(MANAGE_PY), "runserver"],
                creationflags=subprocess.CREATE_NEW_CONSOLE,
                env=env
            )
        else:
            subprocess.Popen(
                [sys.executable, str(MANAGE_PY), "runserver"],
                env=env
            )
        
        print("   Attente du démarrage...")
        for i in range(20):
            time.sleep(1)
            is_ok, msg = verify_server()
            if is_ok:
                print(f"✓ Serveur prêt (tentative {i+1})")
                break
    else:
        print(f"✓ {msg}\n")
    
    time.sleep(3)
    
    # Capturer
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            device_scale_factor=2
        )
        page = context.new_page()
        page.set_default_timeout(30000)
        
        captured = 0
        skipped = 0
        
        print("─" * 70)
        print("📄 CAPTURE DES PAGES")
        print("─" * 70)
        print()
        
        for path, name, desc in ALL_PAGES:
            url = BASE_URL + path
            print(f"📸 {desc} ({path})...", end=" ", flush=True)
            
            try:
                # Charger la page
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
                page.wait_for_load_state("networkidle", timeout=15000)
                time.sleep(3)
                
                # Vérifier le statut
                response = page.evaluate("() => document.body.innerText")
                
                # Vérifier Green Check
                if is_green_check_page(response):
                    print("❌ GREEN CHECK - IGNORÉ")
                    skipped += 1
                    continue
                
                # Vérifier 404
                if 'not found' in response.lower() or '404' in response.lower():
                    if len(response) < 200:  # Vraie page 404
                        print("❌ 404 NOT FOUND")
                        skipped += 1
                        continue
                
                # Vérifier contenu minimal
                if len(response) < 50:
                    print("⚠️  Contenu minimal - IGNORÉ")
                    skipped += 1
                    continue
                
                # Capturer
                screenshot_path = SCREENSHOT_DIR / f"{name}.png"
                page.screenshot(path=str(screenshot_path), full_page=True)
                
                size_kb = screenshot_path.stat().st_size / 1024
                
                if size_kb < 50:
                    print(f"⚠️  Image suspecte ({size_kb:.1f} KB) - SUPPRIMÉE")
                    screenshot_path.unlink()
                    skipped += 1
                    continue
                
                print(f"✓ ({size_kb:.1f} KB)")
                captured += 1
                
            except Exception as e:
                error_msg = str(e)[:40]
                print(f"✗ {error_msg}")
                skipped += 1
            
            print()
        
        browser.close()
        
        print("=" * 70)
        print(f"✅ RÉSULTAT")
        print("=" * 70)
        print(f"✓ {captured} pages capturées")
        if skipped > 0:
            print(f"⚠️  {skipped} pages ignorées")
        print(f"📂 {SCREENSHOT_DIR}")
        print("=" * 70)
        
        return captured > 0

if __name__ == "__main__":
    try:
        success = capture_all_correct()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Interrompu")
        sys.exit(1)
