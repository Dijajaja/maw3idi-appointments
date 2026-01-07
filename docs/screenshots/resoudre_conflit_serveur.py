#!/usr/bin/env python3
"""
Script pour résoudre le conflit de serveur Django
Arrête tous les serveurs sur le port 8000 et démarre le bon serveur
"""

import os
import sys
import time
import subprocess
import requests
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
MANAGE_PY = PROJECT_ROOT / "manage.py"
BASE_URL = "http://localhost:8000/fr"

def kill_all_python_servers():
    """Arrête tous les processus Python (serveurs Django)"""
    print("🛑 Arrêt de tous les serveurs Django...")
    
    if sys.platform == "win32":
        try:
            # Trouver les processus sur le port 8000
            result = subprocess.run(
                ["netstat", "-ano"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            pids_to_kill = []
            for line in result.stdout.split('\n'):
                if ':8000' in line and 'LISTENING' in line:
                    parts = line.split()
                    if len(parts) > 4:
                        pid = parts[-1]
                        pids_to_kill.append(pid)
            
            if pids_to_kill:
                print(f"   → {len(pids_to_kill)} processus trouvé(s) sur le port 8000")
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
                print("   → Aucun processus trouvé sur le port 8000")
            
            # Attendre un peu
            time.sleep(2)
            
            # Arrêter aussi tous les processus python.exe (plus agressif)
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
            
            time.sleep(2)
            
        except Exception as e:
            print(f"   ⚠️  Erreur: {e}")
    else:
        # Linux/Mac
        try:
            subprocess.run(["pkill", "-f", "manage.py runserver"], 
                         capture_output=True)
            subprocess.run(["lsof", "-ti:8000", "|", "xargs", "kill", "-9"], 
                         shell=True, capture_output=True)
        except:
            pass

def check_port_free():
    """Vérifie que le port 8000 est libre"""
    try:
        response = requests.get(BASE_URL, timeout=1)
        return False  # Port occupé
    except:
        return True  # Port libre

def start_correct_server():
    """Démarre le bon serveur Django"""
    print()
    print("🚀 Démarrage du serveur Django correct...")
    print(f"   Chemin: {MANAGE_PY}")
    
    if not MANAGE_PY.exists():
        print(f"   ❌ Fichier manage.py non trouvé: {MANAGE_PY}")
        return None
    
    env = os.environ.copy()
    env['PYTHONUNBUFFERED'] = '1'
    
    # Démarrer dans une nouvelle console Windows
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
    
    # Attendre que le serveur démarre
    print("   → Attente du démarrage...")
    for i in range(30):
        time.sleep(1)
        try:
            response = requests.get(BASE_URL, timeout=2)
            if response.status_code in [200, 302, 301]:
                # Vérifier que ce n'est pas backend.urls
                if 'backend.urls' not in response.text:
                    print(f"   ✓ Serveur démarré correctement (tentative {i+1})")
                    return process
                else:
                    print(f"   ⚠️  Mauvais serveur détecté (tentative {i+1})")
        except:
            pass
    
    print("   ⚠️  Serveur démarré mais vérification incomplète")
    return process

def verify_server():
    """Vérifie que le bon serveur tourne"""
    print()
    print("🔍 Vérification du serveur...")
    
    try:
        response = requests.get(BASE_URL, timeout=3, allow_redirects=True)
        
        if response.status_code == 404:
            if 'backend.urls' in response.text:
                return False, "❌ Mauvais serveur (backend.urls détecté)"
            return False, "❌ Page 404"
        
        if 'backend.urls' in response.text:
            return False, "❌ Mauvais serveur (backend.urls dans la réponse)"
        
        if len(response.text) < 500:
            return False, "❌ Réponse trop petite"
        
        # Vérifier que c'est bien notre application
        if 'appointment' in response.text.lower() or 'service' in response.text.lower():
            return True, "✓ Serveur correct (appointments.urls)"
        
        return True, "✓ Serveur accessible"
        
    except Exception as e:
        return False, f"❌ Erreur: {str(e)[:50]}"

def main():
    """Fonction principale"""
    print("=" * 70)
    print("🔧 RÉSOLUTION DU CONFLIT DE SERVEUR DJANGO")
    print("=" * 70)
    print()
    
    # Étape 1: Arrêter tous les serveurs
    kill_all_python_servers()
    
    # Étape 2: Vérifier que le port est libre
    print()
    print("🔍 Vérification que le port 8000 est libre...")
    if check_port_free():
        print("   ✓ Port 8000 libre")
    else:
        print("   ⚠️  Port 8000 encore occupé, nouvelle tentative...")
        time.sleep(2)
        kill_all_python_servers()
        time.sleep(2)
    
    # Étape 3: Démarrer le bon serveur
    process = start_correct_server()
    
    if not process:
        print()
        print("❌ Impossible de démarrer le serveur")
        return 1
    
    # Étape 4: Vérifier que le serveur est correct
    time.sleep(3)  # Attendre un peu plus
    is_correct, msg = verify_server()
    
    print()
    print("=" * 70)
    if is_correct:
        print("✅ SERVEUR CORRECT DÉMARRÉ !")
        print()
        print(f"📌 {msg}")
        print()
        print("🌐 Le serveur est accessible sur: http://localhost:8000/fr/")
        print()
        print("⚠️  IMPORTANT: Laissez la console du serveur ouverte !")
        print("   Pour arrêter le serveur, fermez la console ou appuyez sur Ctrl+C")
    else:
        print("⚠️  PROBLÈME DÉTECTÉ")
        print()
        print(f"📌 {msg}")
        print()
        print("💡 Solutions possibles:")
        print("   1. Vérifiez qu'aucun autre projet Django ne tourne")
        print("   2. Redémarrez votre ordinateur si nécessaire")
        print("   3. Vérifiez les processus avec: netstat -ano | findstr :8000")
    
    print("=" * 70)
    
    return 0 if is_correct else 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n❌ Interrompu par l'utilisateur")
        sys.exit(1)

