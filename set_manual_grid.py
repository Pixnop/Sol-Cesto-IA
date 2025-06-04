#!/usr/bin/env python
"""
Script pour définir manuellement les coordonnées de la grille
"""
import cv2
import numpy as np
import json

class ManualGridSelector:
    def __init__(self, image_path):
        self.image_path = image_path
        self.image = cv2.imread(image_path)
        if self.image is None:
            raise ValueError(f"Impossible de charger {image_path}")
        
        self.display_image = self.image.copy()
        self.points = []
        self.grid_rect = None
        
        print(f"Image chargée: {image_path}")
        print(f"Dimensions: {self.image.shape}")
        
    def mouse_callback(self, event, x, y, flags, param):
        """Callback pour la souris"""
        if event == cv2.EVENT_LBUTTONDOWN:
            self.points.append((x, y))
            print(f"Point {len(self.points)}: ({x}, {y})")
            
            # Dessiner le point
            cv2.circle(self.display_image, (x, y), 5, (0, 255, 0), -1)
            cv2.putText(self.display_image, f"{len(self.points)}", (x+10, y-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            if len(self.points) == 2:
                # Dessiner le rectangle
                x1, y1 = self.points[0]
                x2, y2 = self.points[1]
                
                # S'assurer que x1,y1 est le coin supérieur gauche
                x1, x2 = min(x1, x2), max(x1, x2)
                y1, y2 = min(y1, y2), max(y1, y2)
                
                self.grid_rect = (x1, y1, x2-x1, y2-y1)
                
                cv2.rectangle(self.display_image, (x1, y1), (x2, y2), (255, 0, 0), 2)
                cv2.putText(self.display_image, "GRILLE", (x1, y1-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                
                print(f"Rectangle de grille: x={x1}, y={y1}, w={x2-x1}, h={y2-y1}")
                print("Appuyez sur 's' pour sauvegarder, 'r' pour recommencer, 'q' pour quitter")
    
    def select_grid_interactive(self):
        """Sélection interactive de la grille"""
        print("\n" + "="*60)
        print("SÉLECTION MANUELLE DE LA GRILLE")
        print("="*60)
        print("Instructions:")
        print("1. Cliquez sur le coin SUPÉRIEUR GAUCHE de la grille")
        print("2. Cliquez sur le coin INFÉRIEUR DROIT de la grille")
        print("3. Appuyez sur 's' pour sauvegarder")
        print("4. Appuyez sur 'r' pour recommencer")
        print("5. Appuyez sur 'q' pour quitter")
        print("="*60)
        
        cv2.namedWindow('Selection de grille', cv2.WINDOW_NORMAL)
        cv2.setMouseCallback('Selection de grille', self.mouse_callback)
        
        while True:
            cv2.imshow('Selection de grille', self.display_image)
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                break
            elif key == ord('r'):
                # Recommencer
                self.points = []
                self.grid_rect = None
                self.display_image = self.image.copy()
                print("Recommencer - cliquez sur les deux coins de la grille")
            elif key == ord('s'):
                if self.grid_rect is not None:
                    self.save_grid_config()
                    break
                else:
                    print("Aucune grille sélectionnée !")
        
        cv2.destroyAllWindows()
    
    def save_grid_config(self):
        """Sauvegarde la configuration de grille"""
        if self.grid_rect is None:
            print("Aucune grille à sauvegarder")
            return
        
        x, y, w, h = self.grid_rect
        
        config = {
            "image_path": self.image_path,
            "image_dimensions": list(self.image.shape),
            "grid_rect": {
                "x": x,
                "y": y,
                "width": w,
                "height": h
            },
            "grid_coordinates": {
                "top_left": [x, y],
                "top_right": [x + w, y],
                "bottom_left": [x, y + h],
                "bottom_right": [x + w, y + h]
            }
        }
        
        # Sauvegarder en JSON
        with open("grid_config.json", "w") as f:
            json.dump(config, f, indent=2)
        
        print(f"\nConfiguration sauvegardée dans: grid_config.json")
        print(f"Rectangle de grille: x={x}, y={y}, w={w}, h={h}")
        
        # Tester l'extraction de la grille
        self.test_grid_extraction()
    
    def test_grid_extraction(self):
        """Teste l'extraction de la grille avec les coordonnées définies"""
        if self.grid_rect is None:
            return
        
        x, y, w, h = self.grid_rect
        
        # Extraire la grille
        grid_img = self.image[y:y+h, x:x+w]
        cv2.imwrite("grille_extraite.jpg", grid_img)
        
        # Diviser en cases 4x4
        case_w = w // 4
        case_h = h // 4
        
        print(f"\nTaille des cases: {case_w}x{case_h}")
        
        # Créer une visualisation avec les divisions
        grid_viz = grid_img.copy()
        
        # Dessiner les lignes de division
        for i in range(1, 4):
            # Lignes verticales
            cv2.line(grid_viz, (i * case_w, 0), (i * case_w, h), (0, 255, 255), 2)
            # Lignes horizontales
            cv2.line(grid_viz, (0, i * case_h), (w, i * case_h), (0, 255, 255), 2)
        
        # Numéroter les cases
        for row in range(4):
            for col in range(4):
                cx = col * case_w + case_w // 2
                cy = row * case_h + case_h // 2
                case_num = row * 4 + col + 1
                cv2.putText(grid_viz, f"{case_num}", (cx-10, cy+5), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
        
        cv2.imwrite("grille_avec_divisions.jpg", grid_viz)
        
        print("Images créées:")
        print("  grille_extraite.jpg - Grille extraite")
        print("  grille_avec_divisions.jpg - Grille avec divisions et numéros")
        
        # Extraire et analyser chaque case
        from sol_cesto_ia.analyzer_v2 import GameAnalyzerV2
        analyzer = GameAnalyzerV2()
        
        print(f"\n{'='*50}")
        print("ANALYSE DES CASES")
        print(f"{'='*50}")
        
        for row in range(4):
            for col in range(4):
                cx = col * case_w
                cy = row * case_h
                
                case_img = grid_img[cy:cy+case_h, cx:cx+case_w]
                
                if case_img.size > 0:
                    # Sauvegarder la case
                    case_filename = f"case_{row+1}_{col+1}.jpg"
                    cv2.imwrite(case_filename, case_img)
                    
                    # Analyser la case
                    type_case = analyzer._identifier_type_case_v2(case_img, debug=True)
                    
                    # Couleur moyenne
                    avg_color = np.mean(case_img, axis=(0, 1))
                    b, g, r = avg_color
                    
                    print(f"\nCase ({row+1}, {col+1}): {type_case}")
                    print(f"  Couleur BGR: ({b:.0f}, {g:.0f}, {r:.0f})")
                    print(f"  Fichier: {case_filename}")
        
        print(f"\n{'='*50}")
        print("FICHIERS GÉNÉRÉS:")
        print("- grid_config.json : Configuration des coordonnées")
        print("- grille_extraite.jpg : Grille extraite")
        print("- grille_avec_divisions.jpg : Grille avec divisions")
        print("- case_X_Y.jpg : Chaque case individuellement")
        print(f"{'='*50}")

def select_with_coordinates():
    """Permet de saisir les coordonnées directement"""
    print("\n" + "="*60)
    print("SAISIE MANUELLE DES COORDONNÉES")
    print("="*60)
    
    try:
        image_path = input("Chemin vers l'image: ").strip()
        if not image_path:
            print("Aucun chemin fourni")
            return
        
        image = cv2.imread(image_path)
        if image is None:
            print(f"Impossible de charger {image_path}")
            return
        
        print(f"Dimensions de l'image: {image.shape}")
        
        print("\nEntrez les coordonnées de la grille:")
        x = int(input("X (coin supérieur gauche): "))
        y = int(input("Y (coin supérieur gauche): "))
        w = int(input("Largeur: "))
        h = int(input("Hauteur: "))
        
        # Valider les coordonnées
        if x < 0 or y < 0 or x + w > image.shape[1] or y + h > image.shape[0]:
            print("Coordonnées invalides !")
            return
        
        # Créer la configuration
        config = {
            "image_path": image_path,
            "image_dimensions": list(image.shape),
            "grid_rect": {
                "x": x,
                "y": y,
                "width": w,
                "height": h
            }
        }
        
        # Sauvegarder
        with open("grid_config.json", "w") as f:
            json.dump(config, f, indent=2)
        
        print(f"\nConfiguration sauvegardée dans: grid_config.json")
        
        # Visualiser
        viz = image.copy()
        cv2.rectangle(viz, (x, y), (x + w, y + h), (255, 0, 0), 3)
        cv2.imwrite("grille_manuelle.jpg", viz)
        print("Visualisation sauvegardée: grille_manuelle.jpg")
        
        # Tester l'extraction
        selector = ManualGridSelector(image_path)
        selector.grid_rect = (x, y, w, h)
        selector.test_grid_extraction()
        
    except ValueError:
        print("Erreur: Entrez des nombres valides")
    except Exception as e:
        print(f"Erreur: {e}")

def main():
    import sys
    
    print("Sélection manuelle de grille")
    print("1. Mode interactif (clic souris)")
    print("2. Mode coordonnées (saisie manuelle)")
    
    if len(sys.argv) >= 2:
        # Mode interactif avec image fournie
        try:
            selector = ManualGridSelector(sys.argv[1])
            selector.select_grid_interactive()
        except Exception as e:
            print(f"Erreur: {e}")
    else:
        # Choisir le mode
        choice = input("Votre choix (1 ou 2): ").strip()
        
        if choice == "1":
            image_path = input("Chemin vers l'image: ").strip()
            if image_path:
                try:
                    selector = ManualGridSelector(image_path)
                    selector.select_grid_interactive()
                except Exception as e:
                    print(f"Erreur: {e}")
        elif choice == "2":
            select_with_coordinates()
        else:
            print("Choix invalide")

if __name__ == "__main__":
    main()