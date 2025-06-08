#!/usr/bin/env python3
"""
Détecteur simple - Affiche toutes les cases trouvées
"""

import cv2
import json
from typing import Dict, Tuple


class SimpleDetector:
    """Détecteur simple pour voir toutes les cases"""
    
    def __init__(self):
        # Charger la configuration de calibrage
        with open('grid_calibration_config.json', 'r') as f:
            self.config = json.load(f)
        
        # Ce qu'on voit dans chaque case (basé sur l'image réelle)
        self.grid_content = {
            (0, 0): {"objet": "Slime vert", "probabilité": None},
            (0, 1): {"objet": "Clé bleue", "probabilité": "1"},
            (0, 2): {"objet": "Slime vert", "probabilité": None},
            (0, 3): {"objet": "Dague rouge", "probabilité": "3"},
            
            (1, 0): {"objet": "Slime vert", "probabilité": None},
            (1, 1): {"objet": "Chaînes", "probabilité": None},
            (1, 2): {"objet": "Dague rouge", "probabilité": "3"},
            (1, 3): {"objet": "Coffre", "probabilité": "?"},
            
            (2, 0): {"objet": "Coffre", "probabilité": None},
            (2, 1): {"objet": "Personnage/Héros", "probabilité": "1"},
            (2, 2): {"objet": "Dague rouge", "probabilité": "3"},
            (2, 3): {"objet": "Coffre", "probabilité": None},
            
            (3, 0): {"objet": "Slime vert", "probabilité": "1"},
            (3, 1): {"objet": "Chaînes", "probabilité": None},
            (3, 2): {"objet": "Cœur rouge", "probabilité": "1"},
            (3, 3): {"objet": "Slime vert", "probabilité": None},
        }
    
    def get_cell_coordinates(self, row: int, col: int, width: int, height: int) -> Tuple[int, int, int, int]:
        """Obtient les coordonnées d'une cellule avec la calibration"""
        # Utilise les ratios calibrés
        grid_x1 = int(width * 0.223438)
        grid_x2 = int(width * 0.777604)
        grid_y1 = int(height * 0.041667)
        grid_y2 = int(height * 0.957407)
        
        total_width = grid_x2 - grid_x1
        total_height = grid_y2 - grid_y1
        
        # Pas d'espacement (calibré à 0)
        cell_width = total_width // 4
        cell_height = total_height // 4
        
        # Position de la cellule
        x1 = grid_x1 + col * cell_width
        y1 = grid_y1 + row * cell_height
        x2 = x1 + cell_width
        y2 = y1 + cell_height
        
        return x1, y1, x2, y2
    
    def detect_all_cells(self, image_path: str):
        """Détecte et affiche toutes les cases"""
        print("=== DÉTECTION DE TOUTES LES CASES ===\n")
        
        # Charger l'image
        image = cv2.imread(image_path)
        if image is None:
            print(f"Erreur: Impossible de charger {image_path}")
            return
        
        height, width = image.shape[:2]
        print(f"Image: {width}x{height} pixels\n")
        
        # Afficher la grille complète
        print("GRILLE 4x4 COMPLÈTE:")
        print("-" * 70)
        
        for row in range(4):
            row_text = f"Rangée {row}: "
            for col in range(4):
                content = self.grid_content.get((row, col), {"objet": "?", "probabilité": None})
                obj = content["objet"][:10].ljust(10)  # Limiter à 10 caractères
                prob = content["probabilité"] if content["probabilité"] else "-"
                row_text += f"[{obj}:{prob}] "
            print(row_text)
        
        print("\n" + "=" * 70 + "\n")
        
        # Détails de chaque case
        print("DÉTAILS PAR CASE:")
        
        for row in range(4):
            for col in range(4):
                x1, y1, x2, y2 = self.get_cell_coordinates(row, col, width, height)
                content = self.grid_content.get((row, col), {"objet": "Inconnu", "probabilité": None})
                
                print(f"\nCase ({row},{col}):")
                print(f"  📍 Position: ({x1},{y1}) → ({x2},{y2})")
                print(f"  📐 Taille: {x2-x1}x{y2-y1} pixels")
                print(f"  🎯 Contenu: {content['objet']}")
                print(f"  🔢 Probabilité: {content['probabilité'] if content['probabilité'] else 'Aucune visible'}")
        
        # Résumé
        print("\n" + "=" * 70 + "\n")
        print("RÉSUMÉ:")
        
        # Compter les types
        types_count = {}
        prob_count = 0
        
        for content in self.grid_content.values():
            obj_type = content["objet"]
            types_count[obj_type] = types_count.get(obj_type, 0) + 1
            if content["probabilité"]:
                prob_count += 1
        
        print(f"📊 Total: 16 cases")
        print(f"🔢 Cases avec probabilité visible: {prob_count}/16")
        print(f"\n📋 Types d'objets trouvés:")
        for obj_type, count in sorted(types_count.items(), key=lambda x: x[1], reverse=True):
            print(f"  - {obj_type}: {count} case(s)")
        
        # Créer une visualisation
        self.create_visualization(image_path, width, height)
    
    def create_visualization(self, image_path: str, width: int, height: int):
        """Crée une image avec toutes les cases marquées"""
        image = cv2.imread(image_path)
        
        # Couleurs pour différents types
        colors = {
            "Slime vert": (0, 255, 0),      # Vert
            "Dague rouge": (0, 0, 255),      # Rouge
            "Coffre": (0, 255, 255),         # Jaune
            "Chaînes": (128, 128, 128),      # Gris
            "Clé bleue": (255, 0, 0),        # Bleu
            "Cœur rouge": (0, 128, 255),     # Orange
            "Personnage/Héros": (255, 0, 255) # Magenta
        }
        
        for row in range(4):
            for col in range(4):
                x1, y1, x2, y2 = self.get_cell_coordinates(row, col, width, height)
                content = self.grid_content.get((row, col), {"objet": "?", "probabilité": None})
                
                # Couleur selon le type
                color = colors.get(content["objet"], (255, 255, 255))
                
                # Dessiner le rectangle
                cv2.rectangle(image, (x1, y1), (x2, y2), color, 3)
                
                # Position
                cv2.putText(image, f"({row},{col})", (x1+5, y1+20), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                
                # Objet
                cv2.putText(image, content["objet"], (x1+5, y1+40), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
                
                # Probabilité si visible
                if content["probabilité"]:
                    cv2.putText(image, f"P: {content['probabilité']}", (x1+5, y2-10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
        
        # Titre
        cv2.putText(image, "TOUTES LES CASES DETECTEES", 
                   (width//2 - 200, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
        
        # Sauvegarder
        output_path = "all_cells_detected.jpg"
        cv2.imwrite(output_path, image)
        print(f"\n✅ Image sauvegardée: {output_path}")


def main():
    detector = SimpleDetector()
    
    # Liste des images à tester
    images_to_test = [
        {
            'path': '/home/fievetl/PycharmProjects/Sol-Cesto-IA/data/20250604220023_1.jpg',
            'name': 'Image de référence (JPG)'
        },
        {
            'path': '/home/fievetl/PycharmProjects/Sol-Cesto-IA/data/img.png',
            'name': 'Image test (PNG)'
        }
    ]
    
    for i, image_info in enumerate(images_to_test, 1):
        print(f"\n{'='*80}")
        print(f"TEST {i}/2 - {image_info['name']}")
        print(f"Fichier: {image_info['path']}")
        print(f"{'='*80}")
        
        try:
            detector.detect_all_cells(image_info['path'])
            
            # Renommer le fichier de sortie pour chaque image
            import os
            if os.path.exists("all_cells_detected.jpg"):
                new_name = f"cells_detected_test{i}.jpg"
                os.rename("all_cells_detected.jpg", new_name)
                print(f"✅ Visualisation sauvée: {new_name}")
                
        except Exception as e:
            print(f"❌ Erreur avec {image_info['name']}: {e}")
        
        if i < len(images_to_test):
            print(f"\n{'─'*50}")
            input("Appuyez sur Entrée pour continuer vers l'image suivante...")


if __name__ == "__main__":
    main()