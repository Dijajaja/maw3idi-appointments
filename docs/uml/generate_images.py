#!/usr/bin/env python3
"""
Script pour générer les images PNG à partir des fichiers PlantUML
Utilise l'API en ligne de PlantUML pour générer les diagrammes
"""

import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path
import base64
import zlib

def encode_plantuml(content):
    """
    Encode le contenu PlantUML en format URL-safe
    Utilise la compression zlib puis base64 comme spécifié par PlantUML
    """
    # Compresser avec zlib
    compressed = zlib.compress(content.encode('utf-8'), level=9)
    # Encoder en base64
    encoded = base64.b64encode(compressed).decode('ascii')
    # Remplacer les caractères non-URL-safe
    # PlantUML utilise un encodage spécifique
    def translate(ch):
        if ch.isalnum() or ch in ['-', '_', '.', '~']:
            return ch
        elif ch == '+':
            return '-'
        elif ch == '/':
            return '_'
        else:
            return ''
    
    return ''.join(translate(c) for c in encoded)

def generate_image_from_plantuml(puml_file, output_dir=None):
    """
    Génère une image PNG à partir d'un fichier PlantUML
    """
    if output_dir is None:
        output_dir = os.path.dirname(puml_file)
    
    # Lire le fichier PlantUML
    with open(puml_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Encoder le contenu
    encoded = encode_plantuml(content)
    
    # URL de l'API PlantUML
    url = f"http://www.plantuml.com/plantuml/png/{encoded}"
    
    # Nom du fichier de sortie
    puml_name = Path(puml_file).stem
    output_file = os.path.join(output_dir, f"{puml_name}.png")
    
    try:
        print(f"Génération de {puml_name}.png...", end=" ")
        
        # Télécharger l'image
        with urllib.request.urlopen(url, timeout=30) as response:
            image_data = response.read()
        
        # Sauvegarder l'image
        with open(output_file, 'wb') as f:
            f.write(image_data)
        
        print(f"✓ ({len(image_data)} bytes)")
        return True
        
    except Exception as e:
        print(f"✗ Erreur: {e}")
        return False

def main():
    """
    Fonction principale - génère toutes les images
    """
    # Répertoire des fichiers PlantUML
    script_dir = Path(__file__).parent
    uml_dir = script_dir
    
    print("=" * 60)
    print("Génération des diagrammes UML en images PNG")
    print("=" * 60)
    print()
    
    # Trouver tous les fichiers .puml
    puml_files = list(uml_dir.glob("*.puml"))
    
    if not puml_files:
        print("Aucun fichier .puml trouvé dans le répertoire.")
        return 1
    
    print(f"{len(puml_files)} fichier(s) trouvé(s):\n")
    
    success_count = 0
    failed_files = []
    
    for puml_file in sorted(puml_files):
        if generate_image_from_plantuml(puml_file, uml_dir):
            success_count += 1
        else:
            failed_files.append(puml_file.name)
        print()
    
    # Résumé
    print("=" * 60)
    print(f"Résumé: {success_count}/{len(puml_files)} image(s) générée(s)")
    if failed_files:
        print(f"Fichiers en échec: {', '.join(failed_files)}")
        return 1
    
    print("=" * 60)
    print("Toutes les images ont été générées avec succès!")
    print(f"Emplacement: {uml_dir}")
    return 0

if __name__ == "__main__":
    sys.exit(main())

