#!/usr/bin/env python3

import cv2
import numpy as np
import json
from typing import Tuple
import os

class CalibrationApplier:
    """Applique une configuration de calibrage sauvegardée"""
    
    def __init__(self):
        self.config = None
        self.load_calibration()
    
    def load_calibration(self):
        """Charge la configuration de calibrage"""
        config_file = '/home/fievetl/PycharmProjects/Sol-Cesto-IA/grid_calibration_config.json'
        
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                self.config = json.load(f)
            print("✓ Configuration de calibrage chargée")
        else:
            print("❌ Aucune configuration trouvée. Lancez d'abord interactive_calibrator.py")
    
    def get_cell_coordinates(self, row: int, col: int, width: int, height: int) -> Tuple[int, int, int, int]:
        """Retourne les coordonnées calibrées d'une cellule"""
        
        if not self.config:
            raise ValueError("Aucune configuration de calibrage disponible")
        
        # Utilise la configuration calibrée
        grid_config = self.config['grid_config']
        
        # Calcul des ratios par rapport à la taille originale
        orig_width, orig_height = self.config['image_dimensions']
        
        # Mise à l'échelle pour la nouvelle taille d'image
        scale_x = width / orig_width
        scale_y = height / orig_height
        
        # Application des ratios
        grid_x1 = int(grid_config['grid_x1'] * scale_x)
        grid_y1 = int(grid_config['grid_y1'] * scale_y)
        
        h_spacing = int(grid_config['h_spacing'] * scale_x)
        v_spacing = int(grid_config['v_spacing'] * scale_y)
        
        cell_width = int(grid_config['cell_width'] * scale_x)
        cell_height = int(grid_config['cell_height'] * scale_y)
        
        # Position de la cellule
        cell_x1 = grid_x1 + col * (cell_width + h_spacing)
        cell_y1 = grid_y1 + row * (cell_height + v_spacing)
        cell_x2 = cell_x1 + cell_width
        cell_y2 = cell_y1 + cell_height
        
        return cell_x1, cell_y1, cell_x2, cell_y2
    
    def visualize_calibrated_grid(self, image_path: str, output_path: str):
        """Visualise la grille avec la configuration calibrée"""
        
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Impossible de charger l'image: {image_path}")
        
        height, width = image.shape[:2]
        
        # Dessiner la grille calibrée
        for row in range(4):
            for col in range(4):
                x1, y1, x2, y2 = self.get_cell_coordinates(row, col, width, height)
                
                # Couleur alternée pour mieux voir
                color = (0, 255, 0) if (row + col) % 2 == 0 else (0, 255, 255)
                
                # Rectangle de la cellule
                cv2.rectangle(image, (x1, y1), (x2, y2), color, 3)
                
                # Informations de la cellule
                cv2.putText(image, f"({row},{col})", (x1+5, y1+20), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                
                # Taille de la cellule
                size_text = f"{x2-x1}x{y2-y1}"
                cv2.putText(image, size_text, (x1+5, y2-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
        
        # Titre
        cv2.putText(image, "GRILLE CALIBRÉE INTERACTIVEMENT", 
                   (width//2 - 200, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
        
        # Informations de calibrage
        if self.config:
            info_y = height - 60
            grid_config = self.config['grid_config']
            info_text = f"Espacement: H={grid_config['h_spacing']}, V={grid_config['v_spacing']} | Cellules: {grid_config['cell_width']}x{grid_config['cell_height']}"
            cv2.putText(image, info_text, (10, info_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        cv2.imwrite(output_path, image)
        print(f"✓ Grille calibrée visualisée: {output_path}")
    
    def update_detector_file(self, detector_file_path: str):
        """Met à jour un fichier de détecteur avec la configuration calibrée"""
        
        if not self.config:
            print("❌ Aucune configuration disponible")
            return
        
        # Génère le code de remplacement
        grid_config = self.config['grid_config']
        orig_width, orig_height = self.config['image_dimensions']
        
        # Calcul des ratios
        grid_x1_ratio = grid_config['grid_x1'] / orig_width
        grid_x2_ratio = grid_config['grid_x2'] / orig_width
        grid_y1_ratio = grid_config['grid_y1'] / orig_height
        grid_y2_ratio = grid_config['grid_y2'] / orig_height
        
        total_width = grid_config['grid_x2'] - grid_config['grid_x1']
        total_height = grid_config['grid_y2'] - grid_config['grid_y1']
        
        h_spacing_ratio = grid_config['h_spacing'] / total_width if total_width > 0 else 0
        v_spacing_ratio = grid_config['v_spacing'] / total_height if total_height > 0 else 0
        
        replacement_code = f'''        # Zone de la grille - CALIBRÉE INTERACTIVEMENT
        grid_x1 = int(width * {grid_x1_ratio:.6f})
        grid_x2 = int(width * {grid_x2_ratio:.6f})
        grid_y1 = int(height * {grid_y1_ratio:.6f})
        grid_y2 = int(height * {grid_y2_ratio:.6f})
        
        # Espacement calibré interactivement
        total_width = grid_x2 - grid_x1
        total_height = grid_y2 - grid_y1
        
        h_spacing = int(total_width * {h_spacing_ratio:.6f})
        v_spacing = int(total_height * {v_spacing_ratio:.6f})'''
        
        print(f"\n📋 CODE À REMPLACER dans {detector_file_path}:")
        print("=" * 60)
        print(replacement_code)
        print("=" * 60)
        print("\n📝 Copiez ce code pour remplacer la section de calibrage dans votre détecteur")

def main():
    """Test de l'application de calibrage"""
    
    applier = CalibrationApplier()
    
    if not applier.config:
        print("\n❌ Aucune configuration trouvée !")
        print("Lancez d'abord: python interactive_calibrator.py")
        return
    
    image_path = '/home/fievetl/PycharmProjects/Sol-Cesto-IA/data/20250604220023_1.jpg'
    
    try:
        # Visualisation de la grille calibrée
        applier.visualize_calibrated_grid(
            image_path,
            '/home/fievetl/PycharmProjects/Sol-Cesto-IA/calibrated_grid_result.jpg'
        )
        
        # Affichage du code à utiliser
        print("\n🎯 CONFIGURATION CALIBRÉE PRÊTE !")
        print("Utilisez la fonction get_cell_coordinates() pour obtenir les coordonnées exactes")
        
        # Test des coordonnées
        image = cv2.imread(image_path)
        height, width = image.shape[:2]
        
        print(f"\n📊 TEST DES COORDONNÉES (image {width}x{height}):")
        for row in range(4):
            for col in range(4):
                x1, y1, x2, y2 = applier.get_cell_coordinates(row, col, width, height)
                print(f"Cellule ({row},{col}): ({x1},{y1}) -> ({x2},{y2}) [{x2-x1}x{y2-y1}]")
        
        # Proposition de mise à jour du détecteur
        applier.update_detector_file('final_aligned_detector.py')
        
    except Exception as e:
        print(f"Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()