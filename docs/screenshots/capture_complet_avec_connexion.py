#!/usr/bin/env python3
"""
Capture complète : pages publiques + authentifiées + contact + services
Avec connexion automatique pour les pages authentifiées
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

# Pages publiques
PAGES_PUBLIQUES = [
    ("/", "01_page_accueil", "Page d'accueil (Services)"),
    ("/login/", "02_page_connexion", "Page de connexion"),
    ("/register/", "03_page_inscription", "Page d'inscription"),
    ("/contact/", "04_page_contact", "Page de contact"),
    ("/new-appointment/", "05_nouveau_rendez_vous", "Nouveau rendez-vous"),
]

# Pages authentifiées
PAGES_AUTH = [
    ("/my-appointments/", "06_mes_rendez_vous", "Mes rendez-vous"),
    ("/calendar/", "07_calendrier", "Calendrier"),
    ("/update-user-info-simple/", "08_modifier_profil", "Modifier profil"),
    ("/change-password-simple/", "09_changer_mot_de_passe", "Changer mot de passe"),
]

def kill_all_servers():
    """Arrête TOUS les serveurs"""
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
        if 'Backend Green Check' in response.text or 'backend.urls' in response.text:
            return False, "Mauvais serveur"
        return True, "OK"
    except:
        return False, "Serveur non accessible"

def login_user(page, username, password):
    """Connecte un utilisateur"""
    try:
        print(f"   → Connexion...", end=" ", flush=True)
        
        page.goto(f"{BASE_URL}/login/", wait_until="domcontentloaded", timeout=30000)
        time.sleep(2)
        
        # Chercher les champs de connexion
        username_input = page.query_selector('input[name="username"], input[type="text"], input[id*="username"], input[id*="login"]')
        password_input = page.query_selector('input[name="password"], input[type="password"]')
        
        if username_input and password_input:
            username_input.fill(username)
            password_input.fill(password)
            
            # Chercher le bouton de soumission
            submit_button = page.query_selector('button[type="submit"], input[type="submit"], button:has-text("Connexion"), button:has-text("Login")')
            if submit_button:
                submit_button.click()
            else:
                # Essayer avec Enter
                password_input.press("Enter")
            
            page.wait_for_load_state("networkidle", timeout=10000)
            time.sleep(2)
            
            current_url = page.url
            if 'login' not in current_url.lower():
                print("✓ Connecté")
                return True
            else:
                print("✗ Échec")
                return False
        else:
            print("✗ Champs non trouvés")
            return False
            
    except Exception as e:
        print(f"✗ Erreur: {str(e)[:30]}")
        return False

def get_first_service_id(page):
    """Récupère l'ID du premier service depuis la page d'accueil"""
    try:
        page.goto(BASE_URL, wait_until="domcontentloaded", timeout=30000)
        time.sleep(2)
        
        # Chercher les liens vers les services
        service_links = page.query_selector_all('a[href*="/request/"], a[href*="service"]')
        for link in service_links:
            href = link.get_attribute('href')
            if href and '/request/' in href:
                # Extraire l'ID du service
                parts = href.split('/request/')
                if len(parts) > 1:
                    service_id = parts[1].split('/')[0]
                    if service_id.isdigit():
                        return int(service_id)
        
        # Alternative : chercher dans les données
        service_elements = page.query_selector_all('[data-service-id], [id*="service"]')
        for elem in service_elements:
            service_id = elem.get_attribute('data-service-id') or elem.get_attribute('id')
            if service_id and service_id.isdigit():
                return int(service_id)
        
        return None
    except:
        return None

def capture_all():
    """Capture toutes les pages"""
    if not PLAYWRIGHT_AVAILABLE:
        print("❌ Playwright non installé")
        return False
    
    SCREENSHOT_DIR.mkdir(exist_ok=True)
    
    print("=" * 70)
    print("📸 CAPTURE COMPLÈTE AVEC CONNEXION")
    print("=" * 70)
    print()
    
    # Demander les identifiants
    print("🔐 Identifiants de connexion (pour pages authentifiées)")
    username = input("   Nom d'utilisateur [admin]: ").strip() or "admin"
    password = input("   Mot de passe: ").strip()
    
    use_login = bool(password)
    if not use_login:
        print("   ⚠️  Pas de mot de passe, pages authentifiées ignorées")
    
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
        
        # Pages publiques
        print("─" * 70)
        print("📄 PAGES PUBLIQUES")
        print("─" * 70)
        print()
        
        for path, name, desc in PAGES_PUBLIQUES:
            url = BASE_URL + path
            print(f"📸 {desc} ({path})...", end=" ", flush=True)
            
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
                page.wait_for_load_state("networkidle", timeout=15000)
                time.sleep(3)
                
                screenshot_path = SCREENSHOT_DIR / f"{name}.png"
                page.screenshot(path=str(screenshot_path), full_page=True)
                
                size_kb = screenshot_path.stat().st_size / 1024
                print(f"✓ ({size_kb:.1f} KB)")
                captured += 1
                
            except Exception as e:
                print(f"✗ {str(e)[:40]}")
                skipped += 1
            
            print()
        
        # Pages authentifiées
        if use_login:
            print("─" * 70)
            print("🔐 PAGES AUTHENTIFIÉES")
            print("─" * 70)
            print()
            
            if login_user(page, username, password):
                print()
                
                for path, name, desc in PAGES_AUTH:
                    url = BASE_URL + path
                    print(f"📸 {desc} ({path})...", end=" ", flush=True)
                    
                    try:
                        page.goto(url, wait_until="domcontentloaded", timeout=30000)
                        page.wait_for_load_state("networkidle", timeout=15000)
                        time.sleep(3)
                        
                        screenshot_path = SCREENSHOT_DIR / f"{name}.png"
                        page.screenshot(path=str(screenshot_path), full_page=True)
                        
                        size_kb = screenshot_path.stat().st_size / 1024
                        
                        if size_kb < 50:
                            print(f"⚠️  Petite image ({size_kb:.1f} KB)")
                        else:
                            print(f"✓ ({size_kb:.1f} KB)")
                        
                        captured += 1
                        
                    except Exception as e:
                        print(f"✗ {str(e)[:40]}")
                        skipped += 1
                    
                    print()
            else:
                print("   ⚠️  Connexion échouée, pages authentifiées ignorées")
                skipped += len(PAGES_AUTH)
        else:
            skipped += len(PAGES_AUTH)
        
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
        success = capture_all()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Interrompu")
        sys.exit(1)

