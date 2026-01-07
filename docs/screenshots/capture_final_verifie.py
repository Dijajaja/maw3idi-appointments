#!/usr/bin/env python3
"""
Capture FINALE avec vérification STRICTE de chaque page
Ignore automatiquement les pages Green Check
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

# Toutes les pages
ALL_PAGES = [
    # Publiques
    ("/", "01_page_accueil", "Page d'accueil"),
    ("/login/", "02_page_connexion", "Page de connexion"),
    ("/register/", "03_page_inscription", "Page d'inscription"),
    ("/contact/", "04_page_contact", "Page de contact"),
    ("/appointment-request/", "05_nouveau_rendez_vous", "Nouveau rendez-vous"),
    # Authentifiées
    ("/appointments/", "06_mes_rendez_vous", "Mes rendez-vous"),
    ("/calendar/", "07_calendrier", "Calendrier"),
    ("/client-information/", "08_modifier_profil", "Modifier profil"),
    ("/change-password/", "09_changer_mot_de_passe", "Changer mot de passe"),
    # Admin
    ("/admin/appointment/appointment/", "10_admin_rendez_vous", "Admin rendez-vous"),
    ("/admin/appointment/service/", "11_admin_liste_services", "Admin services"),
    ("/admin/appointment/service/add/", "12_admin_ajouter_service", "Ajouter service"),
    ("/admin/appointment/staffmember/", "13_admin_profil", "Admin staff"),
    ("/admin/appointment/staffmember/add/", "14_admin_ajouter_staff", "Ajouter staff"),
    ("/admin/", "15_tableau_de_bord_admin", "Dashboard admin"),
]

def kill_all_servers():
    """Arrête TOUS les serveurs"""
    print("🛑 Arrêt de TOUS les serveurs...")
    
    if sys.platform == "win32":
        try:
            # Tous les Python
            subprocess.run(
                ["taskkill", "/F", "/IM", "python.exe"],
                capture_output=True,
                stderr=subprocess.DEVNULL
            )
            time.sleep(3)
        except:
            pass

def verify_server_before_capture():
    """Vérifie le serveur avant de capturer"""
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
    """Vérifie si le contenu est une page Green Check"""
    green_check_indicators = [
        'Backend Green Check',
        'backend.urls',
        'Using the URLconf defined in backend',
        'Green Check',
    ]
    
    content_lower = page_content.lower()
    for indicator in green_check_indicators:
        if indicator.lower() in content_lower:
            return True
    
    return False

def capture_with_strict_check():
    """Capture avec vérification stricte de chaque page"""
    if not PLAYWRIGHT_AVAILABLE:
        print("❌ Playwright non installé")
        return False
    
    SCREENSHOT_DIR.mkdir(exist_ok=True)
    
    print("=" * 70)
    print("📸 CAPTURE FINALE AVEC VÉRIFICATION STRICTE")
    print("=" * 70)
    print()
    
    # Arrêter tous les serveurs
    kill_all_servers()
    time.sleep(2)
    
    # Vérifier le serveur
    is_ok, msg = verify_server_before_capture()
    if not is_ok:
        print(f"❌ {msg}")
        print("   Démarrage du bon serveur...")
        
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
            is_ok, msg = verify_server_before_capture()
            if is_ok:
                print(f"✓ Serveur prêt (tentative {i+1})")
                break
        else:
            print("⚠️  Serveur démarré mais vérification incomplète")
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
        skipped_green_check = 0
        skipped_other = 0
        
        print("─" * 70)
        print("📄 CAPTURE DES PAGES")
        print("─" * 70)
        print()
        
        for path, name, desc in ALL_PAGES:
            url = BASE_URL + path
            print(f"📸 {desc}...", end=" ", flush=True)
            
            try:
                # Charger la page
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
                page.wait_for_load_state("networkidle", timeout=15000)
                time.sleep(3)
                
                # Récupérer le contenu
                page_html = page.content()
                page_text = page.inner_text("body")
                
                # VÉRIFICATION STRICTE : Green Check ?
                if is_green_check_page(page_html) or is_green_check_page(page_text):
                    print("❌ GREEN CHECK DÉTECTÉ - IGNORÉ")
                    skipped_green_check += 1
                    continue
                
                # Vérifier le contenu minimal
                if len(page_text) < 50:
                    print("⚠️  Contenu minimal - IGNORÉ")
                    skipped_other += 1
                    continue
                
                # Capturer
                screenshot_path = SCREENSHOT_DIR / f"{name}.png"
                page.screenshot(path=str(screenshot_path), full_page=True)
                
                size_kb = screenshot_path.stat().st_size / 1024
                
                # Vérifier la taille
                if size_kb < 50:
                    print(f"⚠️  Image suspecte ({size_kb:.1f} KB) - SUPPRIMÉE")
                    screenshot_path.unlink()
                    skipped_other += 1
                    continue
                
                # Double vérification : relire l'image et vérifier qu'elle n'est pas blanche
                # (on peut ajouter une vérification d'image si nécessaire)
                
                print(f"✓ ({size_kb:.1f} KB)")
                captured += 1
                
            except Exception as e:
                error_msg = str(e)[:40]
                print(f"✗ {error_msg}")
                skipped_other += 1
            
            print()
        
        browser.close()
        
        print("=" * 70)
        print(f"✅ RÉSULTAT FINAL")
        print("=" * 70)
        print(f"✓ {captured} pages capturées avec succès")
        if skipped_green_check > 0:
            print(f"❌ {skipped_green_check} pages ignorées (Green Check détecté)")
        if skipped_other > 0:
            print(f"⚠️  {skipped_other} pages ignorées (autre raison)")
        print(f"📂 {SCREENSHOT_DIR}")
        print("=" * 70)
        
        if skipped_green_check > 0:
            print()
            print("⚠️  ATTENTION: Des pages Green Check ont été détectées !")
            print("   Le serveur Backend Green Check tourne encore.")
            print("   Arrêtez-le manuellement avant de régénérer le rapport.")
        
        return captured > 0

if __name__ == "__main__":
    try:
        success = capture_with_strict_check()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Interrompu")
        sys.exit(1)

