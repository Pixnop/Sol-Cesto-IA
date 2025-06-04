#!/usr/bin/env python
"""
Script de test pour analyser la détection des cases
"""
import cv2
import numpy as np
from sol_cesto_ia.analyzer_v2 import GameAnalyzerV2

def test_image(image_path):
    print(f"Analyse de l'image: {image_path}")
    
    # Charger l'image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Erreur: Impossible de charger l'image {image_path}")
        return
    
    print(f"Dimensions de l'image: {image.shape}")
    
    # Créer l'analyseur
    analyzer = GameAnalyzerV2()
    
    # Essayer de détecter les zones
    print("\n=== TENTATIVE DE DÉTECTION AUTOMATIQUE ===")
    zones = analyzer._detecter_zones_auto(image)
    
    # Déboguer la détection de grille avec filtrage
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cv2.imwrite("debug_gray.jpg", gray)
    print("Image en niveaux de gris sauvegardée: debug_gray.jpg")
    
    # Appliquer un filtre gaussien pour réduire le bruit
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    cv2.imwrite("debug_blurred.jpg", blurred)
    print("Image floutée sauvegardée: debug_blurred.jpg")
    
    # Détection des contours avec seuils ajustés
    edges = cv2.Canny(blurred, 30, 100)
    cv2.imwrite("debug_edges.jpg", edges)
    print("Image des contours sauvegardée: debug_edges.jpg")
    
    # Fermeture morphologique pour connecter les lignes interrompues
    kernel = np.ones((3,3), np.uint8)
    edges_closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
    cv2.imwrite("debug_edges_closed.jpg", edges_closed)
    print("Image des contours fermés sauvegardée: debug_edges_closed.jpg")
    
    contours, _ = cv2.findContours(edges_closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    print(f"Nombre de contours trouvés: {len(contours)}")
    
    # Analyser et visualiser les contours carrés potentiels
    cases_potentielles = []
    contour_viz = image.copy()
    
    for i, contour in enumerate(contours):
        area = cv2.contourArea(contour)
        if area > 1000 and area < 50000:
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / h
            if 0.7 < aspect_ratio < 1.3:
                cases_potentielles.append((x, y, w, h, area))
                # Dessiner le contour en vert
                cv2.rectangle(contour_viz, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(contour_viz, f"{len(cases_potentielles)}", (x+5, y+20), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    
    cv2.imwrite("debug_contours_detectes.jpg", contour_viz)
    print(f"Nombre de cases potentielles: {len(cases_potentielles)}")
    print("Visualisation des contours détectés sauvegardée: debug_contours_detectes.jpg")
    
    # Afficher les détails des cases potentielles
    for i, (x, y, w, h, area) in enumerate(cases_potentielles[:10]):  # Limite à 10 pour éviter le spam
        print(f"  Case {i+1}: x={x}, y={y}, w={w}, h={h}, area={area}")
    
    print("\n=== ZONES DÉTECTÉES ===")
    for nom, coords in zones.items():
        if coords:
            print(f"{nom}: x={coords[0]}, y={coords[1]}, w={coords[2]}, h={coords[3]}")
        else:
            print(f"{nom}: Non trouvé")
    
    # Si on a trouvé une grille, l'analyser
    if zones['grille']:
        x, y, w, h = zones['grille']
        grille_img = image[y:y+h, x:x+w]
        
        print(f"\n=== ANALYSE DE LA GRILLE ===")
        print(f"Taille de la grille extraite: {grille_img.shape}")
        
        # Analyser chaque case
        case_w = w // 4
        case_h = h // 4
        
        for row in range(4):
            for col in range(4):
                cx = col * case_w
                cy = row * case_h
                
                case_img = grille_img[cy:cy+case_h, cx:cx+case_w]
                
                # Calculer la couleur moyenne
                avg_color = np.mean(case_img, axis=(0, 1))
                b, g, r = avg_color
                
                print(f"\nCase ({row}, {col}):")
                print(f"  Couleur moyenne BGR: ({b:.0f}, {g:.0f}, {r:.0f})")
                print(f"  Max: {np.max(avg_color):.0f}, Std: {np.std(avg_color):.0f}")
                
                # Sauvegarder la case pour inspection
                case_filename = f"debug_case_{row}_{col}.jpg"
                cv2.imwrite(case_filename, case_img)
                print(f"  Sauvegardé dans: {case_filename}")
    else:
        print("\nAucune grille détectée automatiquement!")
        
        # Essayer la détection manuelle
        print("\n=== TENTATIVE DE DÉTECTION MANUELLE ===")
        zones_manuel = analyzer._detecter_zones_manuel(image)
        
        for nom, coords in zones_manuel.items():
            if coords:
                print(f"{nom}: x={coords[0]}, y={coords[1]}, w={coords[2]}, h={coords[3]}")
            else:
                print(f"{nom}: Non trouvé")
        
        # Si on a une grille manuelle, l'analyser
        if zones_manuel['grille']:
            print("\n=== ANALYSE DE LA GRILLE (MANUELLE) ===")
            x, y, w, h = zones_manuel['grille']
            grille_img = image[y:y+h, x:x+w]
            
            # Sauvegarder la zone de grille extraite
            cv2.imwrite("debug_grille_extraite.jpg", grille_img)
            print(f"Grille extraite sauvegardée: debug_grille_extraite.jpg")
            
            # Analyser chaque case
            case_w = w // 4
            case_h = h // 4
            
            print(f"Taille des cases: {case_w}x{case_h}")
            
            # Créer une grille pour visualiser les divisions
            grille_viz = grille_img.copy()
            for i in range(1, 4):
                # Lignes verticales
                cv2.line(grille_viz, (i * case_w, 0), (i * case_w, h), (255, 0, 0), 2)
                # Lignes horizontales  
                cv2.line(grille_viz, (0, i * case_h), (w, i * case_h), (255, 0, 0), 2)
            
            cv2.imwrite("debug_grille_avec_divisions.jpg", grille_viz)
            print("Grille avec divisions sauvegardée: debug_grille_avec_divisions.jpg")
            
            for row in range(4):
                for col in range(4):
                    cx = col * case_w
                    cy = row * case_h
                    
                    case_img = grille_img[cy:cy+case_h, cx:cx+case_w]
                    
                    if case_img.size == 0:
                        print(f"\nCase ({row}, {col}): VIDE (taille 0)")
                        continue
                    
                    # Calculer la couleur moyenne
                    avg_color = np.mean(case_img, axis=(0, 1))
                    b, g, r = avg_color
                    
                    # Déterminer le type selon les règles actuelles
                    type_case = analyzer._identifier_type_case_v2(case_img)
                    
                    print(f"\nCase ({row}, {col}): {type_case}")
                    print(f"  Couleur moyenne BGR: ({b:.0f}, {g:.0f}, {r:.0f})")
                    print(f"  Max: {np.max(avg_color):.0f}, Std: {np.std(avg_color):.0f}")
                    print(f"  Taille case: {case_img.shape}")
                    
                    # Sauvegarder la case pour inspection
                    case_filename = f"debug_case_{row}_{col}.jpg"
                    cv2.imwrite(case_filename, case_img)
        
    # Essayer avec toute l'image
    print("\n=== ANALYSE COMPLETE DE L'IMAGE ===")
    try:
        etat_jeu = analyzer.analyser_capture(image_path)
        print(f"Grille détectée: {len(etat_jeu['grille'])} rangées")
        print(f"Stats joueur: {etat_jeu['stats_joueur']}")
        
        # Afficher un résumé de la grille
        print("\nRésumé de la grille:")
        for i, rangee in enumerate(etat_jeu['grille']):
            types = [case['type'] for case in rangee]
            print(f"  Rangée {i+1}: {types}")
            
    except Exception as e:
        print(f"Erreur lors de l'analyse complète: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python test_analyzer.py <image_path>")
        sys.exit(1)
    
    test_image(sys.argv[1])