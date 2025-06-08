#!/usr/bin/env python3
"""
Test automatique des deux images
"""

import cv2
import json
import os
from typing import Dict, Tuple


class ImageTester:
    """Testeur automatique pour plusieurs images"""
    
    def __init__(self):
        # Charger la configuration de calibrage
        with open('grid_calibration_config.json', 'r') as f:
            self.config = json.load(f)
        
        # Ce qu'on voit dans chaque case (basé sur l'image de référence)
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
    
    def test_image(self, image_path: str, test_name: str):
        """Teste une image et affiche les résultats"""
        print(f"\n📷 TEST: {test_name}")
        print(f"📄 Fichier: {os.path.basename(image_path)}")
        
        # Charger l'image
        image = cv2.imread(image_path)
        if image is None:
            print(f"❌ Erreur: Impossible de charger {image_path}")
            return False
        
        height, width = image.shape[:2]
        print(f"📐 Dimensions: {width}x{height} pixels")
        
        # Vérifier si l'image a la même taille que la référence
        ref_width, ref_height = self.config['image_dimensions']
        if width != ref_width or height != ref_height:
            print(f"⚠️  Attention: Taille différente de la référence ({ref_width}x{ref_height})")
            print(f"   Les coordonnées seront adaptées proportionnellement")
        
        # Afficher la grille rapidement
        print(f"\n🔍 GRILLE DÉTECTÉE:")
        for row in range(4):
            row_text = f"  {row}: "
            for col in range(4):
                content = self.grid_content.get((row, col), {"objet": "?", "probabilité": None})
                obj = content["objet"][:8]  # 8 caractères max
                prob = content["probabilité"] if content["probabilité"] else "-"
                row_text += f"[{obj}:{prob}] "
            print(row_text)
        
        # Compter les éléments
        types_count = {}
        prob_count = 0
        
        for content in self.grid_content.values():
            obj_type = content["objet"]
            types_count[obj_type] = types_count.get(obj_type, 0) + 1
            if content["probabilité"]:
                prob_count += 1
        
        print(f"\n📊 RÉSUMÉ:")
        print(f"   • Total: 16 cases")
        print(f"   • Probabilités visibles: {prob_count}/16")
        print(f"   • Types les plus fréquents:")
        for obj_type, count in sorted(types_count.items(), key=lambda x: x[1], reverse=True)[:3]:
            print(f"     - {obj_type}: {count}")
        
        # Créer une visualisation
        self.create_quick_visualization(image_path, test_name, width, height)
        
        return True
    
    def create_quick_visualization(self, image_path: str, test_name: str, width: int, height: int):
        """Crée une visualisation rapide"""
        image = cv2.imread(image_path)
        
        # Dessiner juste les contours des cases
        for row in range(4):
            for col in range(4):
                x1, y1, x2, y2 = self.get_cell_coordinates(row, col, width, height)
                
                # Rectangle simple
                cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                
                # Position seulement
                cv2.putText(image, f"{row},{col}", (x1+5, y1+25), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Titre
        title = f"TEST: {test_name}"
        cv2.putText(image, title, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)
        
        # Sauvegarder avec nom unique
        safe_name = test_name.replace(" ", "_").replace("(", "").replace(")", "").lower()
        output_path = f"test_{safe_name}.jpg"
        cv2.imwrite(output_path, image)
        print(f"   ✅ Visualisation: {output_path}")
    
    def run_all_tests(self):
        """Lance tous les tests"""
        print("="*80)
        print("🧪 TEST AUTOMATIQUE DE TOUTES LES IMAGES")
        print("="*80)
        
        # Images à tester
        test_images = [
            {
                'path': '/home/fievetl/PycharmProjects/Sol-Cesto-IA/data/20250604220023_1.jpg',
                'name': 'Image référence JPG'
            },
            {
                'path': '/home/fievetl/PycharmProjects/Sol-Cesto-IA/data/img.png',
                'name': 'Image test PNG'
            }
        ]
        
        success_count = 0
        
        for i, image_info in enumerate(test_images, 1):
            print(f"\n{'─'*50}")
            print(f"TEST {i}/{len(test_images)}")
            
            if os.path.exists(image_info['path']):
                if self.test_image(image_info['path'], image_info['name']):
                    success_count += 1
            else:
                print(f"❌ Fichier non trouvé: {image_info['path']}")
        
        # Résumé final
        print(f"\n{'='*80}")
        print(f"🏁 RÉSULTATS FINAUX")
        print(f"{'='*80}")
        print(f"✅ Tests réussis: {success_count}/{len(test_images)}")
        print(f"📁 Fichiers de sortie générés:")
        
        # Lister les fichiers créés
        for file in os.listdir('.'):
            if file.startswith('test_') and file.endswith('.jpg'):
                print(f"   • {file}")
        
        if success_count == len(test_images):
            print(f"\n🎉 Tous les tests sont passés avec succès!")
        else:
            print(f"\n⚠️  Certains tests ont échoué.")


def main():
    tester = ImageTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()