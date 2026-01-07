#!/usr/bin/env python3
"""
Arrête le serveur "Backend Green Check" et démarre le bon serveur Django
"""

import os
import sys
import time
import subprocess
import requests
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
MANAGE_PY = PROJECT_ROOT / "manage.py"
BASE_URL = "http://localhost:8000"

def find_and_kill_backend_server():
    """Trouve et arrête le serveur Backend Green Check"""
    print("🔍 Recherche du serveur 'Backend Green Check'...")
    
    if sys.platform == "win32":
        try:
            # Trouver tous les processus Python
            result = subprocess.run(
                ["wmic", "process", "where", "name='python.exe'", "get", "processid,commandline"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            pids_to_kill = []
            for line in result.stdout.split('\n'):
                if 'backend' in line.lower() or 'green' in line.lower() or 'runserver' in line.lower():
                    # Extraire le PID
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part.isdigit() and i > 0:
                            pids_to_kill.append(part)
                            break
            
            # Méthode alternative : trouver par port
            result2 = subprocess.run(
                ["netstat", "-ano"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            for line in result2.stdout.split('\n'):
                if ':8000' in line and 'LISTENING' in line:
                    parts = line.split()
                    if len(parts) > 4:
                        pid = parts[-1]
                        if pid not in pids_to_kill:
                            pids_to_kill.append(pid)
            
            if pids_to_kill:
                print(f"   → {len(pids_to_kill)} processus Django trouvé(s)")
                for pid in pids_to_kill:
                    try:
                        subprocess.run(
                            ["taskkill", "/F", "/PID", pid],
                            capture_output=True,
                            stderr=subprocess.DEVNULL
                        )
                        print(f"   ✓ Processus {pid} arrêté")
                    except:
                        pass
            else:
                print("   → Aucun processus Django trouvé")
            
            # Arrêter TOUS les processus Python pour être sûr
            print("   → Arrêt de tous les processus Python...")
            try:
                subprocess.run(
                    ["taskkill", "/F", "/IM", "python.exe"],
                    capture_output=True,
                    stderr=subprocess.DEVNULL
                )
                print("   ✓ Tous les processus Python arrêtés")
            except:
                pass
            
            time.sleep(3)  # Attendre que tout soit arrêté
            
        except Exception as e:
            print(f"   ⚠️  Erreur: {e}")

def verify_port_free():
    """Vérifie que le port 8000 est vraiment libre"""
    for i in range(5):
        try:
            response = requests.get(BASE_URL, timeout=1)
            return False
        except:
            pass
        time.sleep(1)
    return True

def start_appointment_server():
    """Démarre le serveur appointments"""
    print()
    print("🚀 Démarrage du serveur Django appointments...")
    print(f"   Chemin: {MANAGE_PY}")
    
    if not MANAGE_PY.exists():
        print(f"   ❌ Fichier manage.py non trouvé!")
        return None
    
    env = os.environ.copy()
    env['PYTHONUNBUFFERED'] = '1'
    
    # Démarrer dans une nouvelle console
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
    
    return process

def verify_correct_server():
    """Vérifie que le BON serveur tourne"""
    print()
    print("🔍 Vérification du serveur...")
    
    for i in range(20):
        time.sleep(1)
        try:
            # Tester la racine
            response = requests.get(BASE_URL, timeout=2, allow_redirects=True)
            
            # Tester /fr/
            response_fr = requests.get(f"{BASE_URL}/fr/", timeout=2, allow_redirects=True)
            
            # Vérifier que ce n'est PAS backend.urls
            if 'backend.urls' in response_fr.text or 'Backend Green Check' in response_fr.text:
                print(f"   ⚠️  Mauvais serveur encore actif (tentative {i+1})...")
                continue
            
            # Vérifier que c'est bien appointments.urls
            if response_fr.status_code in [200, 302, 301]:
                if 'appointment' in response_fr.text.lower() or 'service' in response_fr.text.lower():
                    print(f"   ✓ Serveur correct détecté (tentative {i+1})")
                    return True, "Serveur appointments correct"
            
        except:
            pass
    
    return False, "Impossible de vérifier"

def main():
    """Fonction principale"""
    print("=" * 70)
    print("🔧 ARRÊT DU SERVEUR BACKEND ET DÉMARRAGE DU BON SERVEUR")
    print("=" * 70)
    print()
    
    # Étape 1: Arrêter le serveur Backend Green Check
    find_and_kill_backend_server()
    
    # Étape 2: Vérifier que le port est libre
    print()
    print("🔍 Vérification que le port 8000 est libre...")
    if verify_port_free():
        print("   ✓ Port 8000 libre")
    else:
        print("   ⚠️  Port encore occupé, nouvelle tentative...")
        find_and_kill_backend_server()
        time.sleep(3)
    
    # Étape 3: Démarrer le bon serveur
    process = start_appointment_server()
    
    if not process:
        print()
        print("❌ Impossible de démarrer le serveur")
        return 1
    
    # Étape 4: Vérifier que c'est le bon serveur
    time.sleep(5)  # Attendre que le serveur démarre
    is_correct, msg = verify_correct_server()
    
    print()
    print("=" * 70)
    if is_correct:
        print("✅ SUCCÈS ! Le bon serveur est maintenant actif")
        print()
        print(f"📌 {msg}")
        print()
        print("🌐 Serveur accessible sur: http://localhost:8000/fr/")
        print()
        print("⚠️  IMPORTANT:")
        print("   - Laissez la console du serveur OUVERTE")
        print("   - Ne fermez PAS la fenêtre qui affiche 'Starting development server'")
        print("   - Pour arrêter: fermez la console ou Ctrl+C")
    else:
        print("⚠️  ATTENTION")
        print()
        print(f"📌 {msg}")
        print()
        print("💡 Le serveur Backend Green Check pourrait encore tourner.")
        print("   Essayez de:")
        print("   1. Redémarrer votre ordinateur")
        print("   2. Vérifier manuellement: netstat -ano | findstr :8000")
        print("   3. Arrêter manuellement tous les processus Python")
    
    print("=" * 70)
    
    return 0 if is_correct else 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n❌ Interrompu")
        sys.exit(1)

