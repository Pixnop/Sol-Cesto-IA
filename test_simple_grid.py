#!/usr/bin/env python
"""
Test simple pour voir ce que détecte actuellement l'analyseur
"""
import cv2
import numpy as np

def test_simple(image_path):
    print(f"Test simple sur: {image_path}")
    
    # Charger l'image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Erreur: Impossible de charger {image_path}")
        return
    
    print(f"Dimensions: {image.shape}")
    
    # Paramètres actuels de l'analyseur
    params = {
        'blur_kernel': 5,
        'canny_low': 30,
        'canny_high': 100,
        'min_area': 1000,
        'max_area': 50000,
        'aspect_ratio_min': 0.7,
        'aspect_ratio_max': 1.3,
        'y_tolerance': 20,
        'morph_kernel': 3
    }
    
    # Prétraitement
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (params['blur_kernel'], params['blur_kernel']), 0)
    edges = cv2.Canny(blurred, params['canny_low'], params['canny_high'])
    
    # Fermeture morphologique
    kernel = np.ones((params['morph_kernel'], params['morph_kernel']), np.uint8)
    edges_closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
    
    # Sauvegarder les étapes
    cv2.imwrite("etape1_original.jpg", image)
    cv2.imwrite("etape2_gray.jpg", gray)
    cv2.imwrite("etape3_blurred.jpg", blurred)
    cv2.imwrite("etape4_edges.jpg", edges)
    cv2.imwrite("etape5_edges_closed.jpg", edges_closed)
    
    print("Étapes sauvegardées:")
    print("  etape1_original.jpg - Image originale")
    print("  etape2_gray.jpg - En niveaux de gris")
    print("  etape3_blurred.jpg - Après flou gaussien")
    print("  etape4_edges.jpg - Contours Canny")
    print("  etape5_edges_closed.jpg - Après fermeture morphologique")
    
    # Trouver les contours
    contours, _ = cv2.findContours(edges_closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    print(f"\nNombre total de contours: {len(contours)}")
    
    # Filtrer les contours
    cases_potentielles = []
    result_image = image.copy()
    
    for i, contour in enumerate(contours):
        area = cv2.contourArea(contour)
        if params['min_area'] <= area <= params['max_area']:
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / h
            if params['aspect_ratio_min'] <= aspect_ratio <= params['aspect_ratio_max']:
                cases_potentielles.append((x, y, w, h, area))
                # Dessiner en vert
                cv2.rectangle(result_image, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(result_image, f"{len(cases_potentielles)}", (x+5, y+20), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    
    print(f"Cases potentielles trouvées: {len(cases_potentielles)}")
    
    # Essayer de grouper en grille
    if len(cases_potentielles) >= 16:
        print("Tentative de groupement en grille 4x4...")
        
        # Trier par Y
        cases_potentielles.sort(key=lambda c: c[1])
        
        rangees = []
        current_row = []
        last_y = -100
        
        for case in cases_potentielles:
            if abs(case[1] - last_y) > params['y_tolerance']:
                if current_row:
                    rangees.append(current_row)
                current_row = [case]
                last_y = case[1]
            else:
                current_row.append(case)
        
        if current_row:
            rangees.append(current_row)
        
        print(f"Rangées détectées: {len(rangees)}")
        for i, rangee in enumerate(rangees):
            print(f"  Rangée {i+1}: {len(rangee)} cases")
        
        # Chercher grille 4x4
        grille_trouvee = False
        for i in range(len(rangees) - 3):
            if all(len(rangees[i+j]) >= 4 for j in range(4)):
                min_x = min(case[0] for row in rangees[i:i+4] for case in row[:4])
                min_y = rangees[i][0][1]
                max_x = max(case[0] + case[2] for row in rangees[i:i+4] for case in row[:4])
                max_y = rangees[i+3][0][1] + rangees[i+3][0][3]
                
                grille_rect = (min_x - 10, min_y - 10, max_x - min_x + 20, max_y - min_y + 20)
                
                # Dessiner la grille en bleu
                cv2.rectangle(result_image, (grille_rect[0], grille_rect[1]), 
                            (grille_rect[0] + grille_rect[2], grille_rect[1] + grille_rect[3]), 
                            (255, 0, 0), 3)
                
                print(f"GRILLE 4x4 TROUVÉE ! Rectangle: {grille_rect}")
                grille_trouvee = True
                break
        
        if not grille_trouvee:
            print("Aucune grille 4x4 trouvée")
    else:
        print(f"Pas assez de cases pour une grille (besoin: 16, trouvé: {len(cases_potentielles)})")
    
    # Sauvegarder le résultat final
    cv2.imwrite("resultat_final.jpg", result_image)
    
    print(f"\n{'='*60}")
    print("RÉSULTAT FINAL sauvegardé dans: resultat_final.jpg")
    print("- Rectangles VERTS = cases détectées")
    if 'grille_trouvee' in locals() and grille_trouvee:
        print("- Rectangle BLEU = grille 4x4 détectée")
    else:
        print("- Aucun rectangle bleu = aucune grille détectée")
    print(f"{'='*60}")
    
    return len(cases_potentielles), 'grille_trouvee' in locals() and grille_trouvee

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python test_simple_grid.py <image_path>")
        sys.exit(1)
    
    test_simple(sys.argv[1])