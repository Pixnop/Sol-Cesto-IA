#!/usr/bin/env python3

import cv2
import numpy as np
import json
from typing import List, Tuple, Dict

class InteractiveGridCalibrator:
    """Calibrateur interactif pour ajuster la grille en cliquant sur l'image"""
    
    def __init__(self, image_path: str):
        self.image_path = image_path
        self.image = cv2.imread(image_path)
        if self.image is None:
            raise ValueError(f"Impossible de charger l'image: {image_path}")
        
        self.original_image = self.image.copy()
        self.height, self.width = self.image.shape[:2]
        
        # Points cliqués pour définir la grille
        self.corner_points = []  # [top_left, top_right, bottom_left, bottom_right]
        self.cell_corners = []   # Points pour définir des cellules spécifiques
        
        # Mode de calibrage
        self.calibration_mode = "corners"  # "corners" ou "cells"
        
        # Configuration actuelle
        self.grid_config = {
            'grid_x1': 0, 'grid_y1': 0, 'grid_x2': 0, 'grid_y2': 0,
            'h_spacing': 0, 'v_spacing': 0,
            'cell_width': 0, 'cell_height': 0
        }
        
        print("=== CALIBRATEUR INTERACTIF SOL CESTO ===")
        print("Instructions:")
        print("1. Cliquez sur les 4 coins de la grille dans l'ordre:")
        print("   - Coin supérieur gauche")
        print("   - Coin supérieur droit") 
        print("   - Coin inférieur gauche")
        print("   - Coin inférieur droit")
        print("2. Appuyez sur 'r' pour recommencer")
        print("3. Appuyez sur 's' pour sauvegarder")
        print("4. Appuyez sur 'q' pour quitter")
        print("5. Appuyez sur 'c' pour mode cellule individuelle")
    
    def mouse_callback(self, event, x, y, flags, param):
        """Callback pour les clics de souris"""
        if event == cv2.EVENT_LBUTTONDOWN:
            if self.calibration_mode == "corners":
                self._handle_corner_click(x, y)
            elif self.calibration_mode == "cells":
                self._handle_cell_click(x, y)
    
    def _handle_corner_click(self, x: int, y: int):
        """Gère les clics pour définir les coins de la grille"""
        if len(self.corner_points) < 4:
            self.corner_points.append((x, y))
            print(f"Point {len(self.corner_points)}: ({x}, {y})")
            
            # Redessiner l'image avec les points
            self._draw_current_state()
            
            if len(self.corner_points) == 4:
                print("\n✓ 4 coins définis ! Calcul de la grille...")
                self._calculate_grid_from_corners()
    
    def _handle_cell_click(self, x: int, y: int):
        """Gère les clics pour définir des cellules individuelles"""
        self.cell_corners.append((x, y))
        print(f"Point cellule {len(self.cell_corners)}: ({x}, {y})")
        self._draw_current_state()
    
    def _calculate_grid_from_corners(self):
        """Calcule les paramètres de grille à partir des 4 coins"""
        if len(self.corner_points) != 4:
            return
        
        top_left, top_right, bottom_left, bottom_right = self.corner_points
        
        # Zone de la grille
        self.grid_config['grid_x1'] = top_left[0]
        self.grid_config['grid_y1'] = top_left[1]
        self.grid_config['grid_x2'] = top_right[0]
        self.grid_config['grid_y2'] = bottom_left[1]
        
        # Dimensions totales
        total_width = self.grid_config['grid_x2'] - self.grid_config['grid_x1']
        total_height = self.grid_config['grid_y2'] - self.grid_config['grid_y1']
        
        # Calcul de l'espacement en analysant les distances
        # Espacement horizontal : différence entre cellules
        expected_cell_width = total_width // 4
        actual_spacing_h = (total_width - 4 * expected_cell_width) // 3
        
        expected_cell_height = total_height // 4
        actual_spacing_v = (total_height - 4 * expected_cell_height) // 3
        
        # Ajustement pour un espacement régulier
        self.grid_config['h_spacing'] = max(0, actual_spacing_h)
        self.grid_config['v_spacing'] = max(0, actual_spacing_v)
        
        # Recalcul des dimensions des cellules
        self.grid_config['cell_width'] = (total_width - 3 * self.grid_config['h_spacing']) // 4
        self.grid_config['cell_height'] = (total_height - 3 * self.grid_config['v_spacing']) // 4
        
        print(f"\nConfiguration calculée:")
        print(f"Zone grille: ({self.grid_config['grid_x1']}, {self.grid_config['grid_y1']}) -> ({self.grid_config['grid_x2']}, {self.grid_config['grid_y2']})")
        print(f"Espacement: H={self.grid_config['h_spacing']}, V={self.grid_config['v_spacing']}")
        print(f"Cellules: {self.grid_config['cell_width']}x{self.grid_config['cell_height']}")
        
        self._draw_calculated_grid()
    
    def _draw_current_state(self):
        """Dessine l'état actuel avec les points cliqués"""
        self.image = self.original_image.copy()
        
        # Dessiner les points des coins
        for i, point in enumerate(self.corner_points):
            color = [(0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 255, 0)][i]
            cv2.circle(self.image, point, 8, color, -1)
            cv2.putText(self.image, f"{i+1}", (point[0]+10, point[1]), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        # Dessiner les points des cellules
        for i, point in enumerate(self.cell_corners):
            cv2.circle(self.image, point, 5, (255, 255, 255), -1)
            cv2.putText(self.image, f"C{i+1}", (point[0]+5, point[1]), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        
        # Informations en haut
        info_text = f"Mode: {self.calibration_mode} | Points coins: {len(self.corner_points)}/4"
        cv2.putText(self.image, info_text, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        cv2.imshow('Calibrateur Interactif', self.image)
    
    def _draw_calculated_grid(self):
        """Dessine la grille calculée"""
        self.image = self.original_image.copy()
        
        # Dessiner la grille
        for row in range(4):
            for col in range(4):
                x1, y1, x2, y2 = self._get_cell_coords(row, col)
                
                # Rectangle de la cellule
                color = (0, 255, 0) if (row + col) % 2 == 0 else (0, 255, 255)
                cv2.rectangle(self.image, (x1, y1), (x2, y2), color, 2)
                
                # Numéro de cellule
                cv2.putText(self.image, f"({row},{col})", (x1+5, y1+20), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
        
        # Points de référence
        for i, point in enumerate(self.corner_points):
            color = [(0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 255, 0)][i]
            cv2.circle(self.image, point, 5, color, -1)
        
        cv2.imshow('Calibrateur Interactif', self.image)
    
    def _get_cell_coords(self, row: int, col: int) -> Tuple[int, int, int, int]:
        """Calcule les coordonnées d'une cellule"""
        x1 = self.grid_config['grid_x1'] + col * (self.grid_config['cell_width'] + self.grid_config['h_spacing'])
        y1 = self.grid_config['grid_y1'] + row * (self.grid_config['cell_height'] + self.grid_config['v_spacing'])
        x2 = x1 + self.grid_config['cell_width']
        y2 = y1 + self.grid_config['cell_height']
        return x1, y1, x2, y2
    
    def save_configuration(self):
        """Sauvegarde la configuration"""
        config_data = {
            'image_dimensions': (self.width, self.height),
            'corner_points': self.corner_points,
            'grid_config': self.grid_config,
            'calibration_code': self._generate_code()
        }
        
        with open('/home/fievetl/PycharmProjects/Sol-Cesto-IA/grid_calibration_config.json', 'w') as f:
            json.dump(config_data, f, indent=2)
        
        print(f"\n✓ Configuration sauvegardée dans grid_calibration_config.json")
        print(f"✓ Code généré et sauvegardé")
    
    def _generate_code(self) -> str:
        """Génère le code Python pour utiliser cette configuration"""
        
        # Calcul des ratios par rapport à la taille de l'image
        grid_x1_ratio = self.grid_config['grid_x1'] / self.width
        grid_x2_ratio = self.grid_config['grid_x2'] / self.width
        grid_y1_ratio = self.grid_config['grid_y1'] / self.height
        grid_y2_ratio = self.grid_config['grid_y2'] / self.height
        
        total_width = self.grid_config['grid_x2'] - self.grid_config['grid_x1']
        total_height = self.grid_config['grid_y2'] - self.grid_config['grid_y1']
        
        h_spacing_ratio = self.grid_config['h_spacing'] / total_width if total_width > 0 else 0
        v_spacing_ratio = self.grid_config['v_spacing'] / total_height if total_height > 0 else 0
        
        code = f'''# Configuration générée par le calibrateur interactif
def get_calibrated_cell_coordinates(row: int, col: int, width: int, height: int):
    """Coordonnées calibrées interactivement"""
    
    # Zone de la grille (ratios calibrés)
    grid_x1 = int(width * {grid_x1_ratio:.6f})
    grid_x2 = int(width * {grid_x2_ratio:.6f})
    grid_y1 = int(height * {grid_y1_ratio:.6f})
    grid_y2 = int(height * {grid_y2_ratio:.6f})
    
    # Espacement calibré
    total_width = grid_x2 - grid_x1
    total_height = grid_y2 - grid_y1
    
    h_spacing = int(total_width * {h_spacing_ratio:.6f})
    v_spacing = int(total_height * {v_spacing_ratio:.6f})
    
    # Dimensions des cellules
    cell_width = (total_width - 3 * h_spacing) // 4
    cell_height = (total_height - 3 * v_spacing) // 4
    
    # Position de la cellule
    cell_x1 = grid_x1 + col * (cell_width + h_spacing)
    cell_y1 = grid_y1 + row * (cell_height + v_spacing)
    cell_x2 = cell_x1 + cell_width
    cell_y2 = cell_y1 + cell_height
    
    return cell_x1, cell_y1, cell_x2, cell_y2

# Valeurs absolues pour image {self.width}x{self.height}:
# Zone grille: ({self.grid_config['grid_x1']}, {self.grid_config['grid_y1']}) -> ({self.grid_config['grid_x2']}, {self.grid_config['grid_y2']})
# Espacement: H={self.grid_config['h_spacing']}, V={self.grid_config['v_spacing']}
# Cellules: {self.grid_config['cell_width']}x{self.grid_config['cell_height']}'''
        
        # Sauvegarder le code
        with open('/home/fievetl/PycharmProjects/Sol-Cesto-IA/calibrated_coordinates.py', 'w') as f:
            f.write(code)
        
        return code
    
    def run(self):
        """Lance le calibrateur interactif"""
        cv2.namedWindow('Calibrateur Interactif', cv2.WINDOW_NORMAL)
        cv2.setMouseCallback('Calibrateur Interactif', self.mouse_callback)
        
        # Affichage initial
        self._draw_current_state()
        
        while True:
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):  # Quitter
                break
            elif key == ord('r'):  # Reset
                self.corner_points = []
                self.cell_corners = []
                self.calibration_mode = "corners"
                print("\n🔄 Reset - Recliquez sur les 4 coins")
                self._draw_current_state()
            elif key == ord('s'):  # Sauvegarder
                if len(self.corner_points) == 4:
                    self.save_configuration()
                else:
                    print("❌ Définissez d'abord les 4 coins !")
            elif key == ord('c'):  # Mode cellule
                if len(self.corner_points) == 4:
                    self.calibration_mode = "cells"
                    print("\n📍 Mode cellule - Cliquez sur des coins de cellules pour affiner")
                else:
                    print("❌ Définissez d'abord les 4 coins de la grille !")
            elif key == ord('g'):  # Afficher grille
                if len(self.corner_points) == 4:
                    self._draw_calculated_grid()
        
        cv2.destroyAllWindows()

def main():
    """Lance le calibrateur interactif"""
    image_path = '/home/fievetl/PycharmProjects/Sol-Cesto-IA/data/20250604220023_1.jpg'
    
    try:
        calibrator = InteractiveGridCalibrator(image_path)
        calibrator.run()
        
    except Exception as e:
        print(f"Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()