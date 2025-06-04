#!/usr/bin/env python
"""
Script pour tester et ajuster les paramètres de détection de grille
"""
import cv2
import numpy as np

def test_grid_detection(image_path, params=None):
    """
    Teste différents paramètres pour la détection de grille
    """
    # Paramètres par défaut
    default_params = {
        'blur_kernel': 5,           # Taille du noyau de flou gaussien (5, 7, 9, etc.)
        'canny_low': 30,           # Seuil bas pour Canny (20-50)
        'canny_high': 100,         # Seuil haut pour Canny (80-150)
        'min_area': 1000,          # Surface minimale des contours (500-5000)
        'max_area': 50000,         # Surface maximale des contours (20000-100000)
        'aspect_ratio_min': 0.7,   # Ratio largeur/hauteur min (0.5-0.8)
        'aspect_ratio_max': 1.3,   # Ratio largeur/hauteur max (1.2-1.5)
        'y_tolerance': 20,         # Tolérance pour grouper en rangées (10-50)
        'morph_kernel': 3          # Taille du noyau morphologique (3, 5, 7)
    }
    
    if params:
        default_params.update(params)
    
    print("=== PARAMÈTRES UTILISÉS ===")
    for key, value in default_params.items():
        print(f"{key}: {value}")
    
    # Charger l'image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Erreur: Impossible de charger {image_path}")
        return
    
    print(f"\nDimensions image: {image.shape}")
    
    # Prétraitement
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Flou gaussien
    blurred = cv2.GaussianBlur(gray, (default_params['blur_kernel'], default_params['blur_kernel']), 0)
    
    # Détection des contours
    edges = cv2.Canny(blurred, default_params['canny_low'], default_params['canny_high'])
    
    # Fermeture morphologique
    kernel = np.ones((default_params['morph_kernel'], default_params['morph_kernel']), np.uint8)
    edges_closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
    
    # Sauvegarder les étapes
    cv2.imwrite("step1_gray.jpg", gray)
    cv2.imwrite("step2_blurred.jpg", blurred)
    cv2.imwrite("step3_edges.jpg", edges)
    cv2.imwrite("step4_edges_closed.jpg", edges_closed)
    
    # Trouver les contours
    contours, _ = cv2.findContours(edges_closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    print(f"\nNombre total de contours: {len(contours)}")
    
    # Filtrer les contours
    cases_potentielles = []
    contour_viz = image.copy()
    
    for contour in contours:
        area = cv2.contourArea(contour)
        if default_params['min_area'] <= area <= default_params['max_area']:
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / h
            if default_params['aspect_ratio_min'] <= aspect_ratio <= default_params['aspect_ratio_max']:
                cases_potentielles.append((x, y, w, h, area))
    
    print(f"Cases potentielles après filtrage: {len(cases_potentielles)}")
    
    # Visualiser les cases potentielles
    for i, (x, y, w, h, area) in enumerate(cases_potentielles):
        cv2.rectangle(contour_viz, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.putText(contour_viz, f"{i+1}", (x+5, y+20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    
    cv2.imwrite("result_cases_detectees.jpg", contour_viz)
    
    # Essayer de grouper en grille 4x4
    if len(cases_potentielles) >= 16:
        print("\n=== TENTATIVE DE GROUPEMENT EN GRILLE ===")
        
        # Trier par position Y (rangées)
        cases_potentielles.sort(key=lambda c: c[1])
        
        rangees = []
        current_row = []
        last_y = -100
        
        for case in cases_potentielles:
            if abs(case[1] - last_y) > default_params['y_tolerance']:
                if current_row:
                    rangees.append(current_row)
                current_row = [case]
                last_y = case[1]
            else:
                current_row.append(case)
        
        if current_row:
            rangees.append(current_row)
        
        print(f"Nombre de rangées détectées: {len(rangees)}")
        for i, rangee in enumerate(rangees):
            print(f"  Rangée {i+1}: {len(rangee)} cases")
        
        # Chercher une grille 4x4
        grille_trouvee = False
        for i in range(len(rangees) - 3):
            if all(len(rangees[i+j]) >= 4 for j in range(4)):
                print(f"\nGrille 4x4 potentielle trouvée aux rangées {i+1}-{i+4}")
                
                # Calculer les limites
                min_x = min(case[0] for row in rangees[i:i+4] for case in row[:4])
                min_y = rangees[i][0][1]
                max_x = max(case[0] + case[2] for row in rangees[i:i+4] for case in row[:4])
                max_y = rangees[i+3][0][1] + rangees[i+3][0][3]
                
                grille_rect = (min_x - 10, min_y - 10, max_x - min_x + 20, max_y - min_y + 20)
                print(f"Rectangle de grille: {grille_rect}")
                
                # Dessiner la grille détectée
                grid_viz = image.copy()
                cv2.rectangle(grid_viz, (grille_rect[0], grille_rect[1]), 
                            (grille_rect[0] + grille_rect[2], grille_rect[1] + grille_rect[3]), 
                            (255, 0, 0), 3)
                cv2.imwrite("result_grille_detectee.jpg", grid_viz)
                
                grille_trouvee = True
                break
        
        if not grille_trouvee:
            print("\nAucune grille 4x4 valide trouvée")
    else:
        print(f"\nPas assez de cases (besoin: 16, trouvé: {len(cases_potentielles)})")
    
    print(f"\nImages sauvegardées:")
    print("- step1_gray.jpg: Image en niveaux de gris")
    print("- step2_blurred.jpg: Image floutée")
    print("- step3_edges.jpg: Contours Canny")
    print("- step4_edges_closed.jpg: Contours après fermeture")
    print("- result_cases_detectees.jpg: Cases potentielles détectées")
    if 'grille_trouvee' in locals() and grille_trouvee:
        print("- result_grille_detectee.jpg: Grille finale détectée")

def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: python test_grid_params.py <image_path> [param1=value1] [param2=value2] ...")
        print("\nParamètres disponibles:")
        print("  blur_kernel=5        # Taille du flou (5, 7, 9)")
        print("  canny_low=30         # Seuil Canny bas (20-50)")
        print("  canny_high=100       # Seuil Canny haut (80-150)")
        print("  min_area=1000        # Surface min des contours")
        print("  max_area=50000       # Surface max des contours")
        print("  aspect_ratio_min=0.7 # Ratio min largeur/hauteur")
        print("  aspect_ratio_max=1.3 # Ratio max largeur/hauteur")
        print("  y_tolerance=20       # Tolérance groupement rangées")
        print("  morph_kernel=3       # Taille noyau morphologique")
        print("\nExemple:")
        print("  python test_grid_params.py image.jpg canny_low=20 min_area=2000")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    # Parser les paramètres
    params = {}
    for arg in sys.argv[2:]:
        if '=' in arg:
            key, value = arg.split('=', 1)
            try:
                # Essayer de convertir en nombre
                if '.' in value:
                    params[key] = float(value)
                else:
                    params[key] = int(value)
            except ValueError:
                params[key] = value
    
    test_grid_detection(image_path, params)

if __name__ == "__main__":
    main()