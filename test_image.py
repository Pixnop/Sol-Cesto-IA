"""
Script de test pour analyser une image spécifique et visualiser les zones détectées.
"""
import cv2
import matplotlib.pyplot as plt
from sol_cesto_ia.analyzer_v2 import GameAnalyzerV2 as GameAnalyzer
import numpy as np


def visualiser_detection(image_path):
    """Visualise les zones détectées sur l'image."""
    analyzer = GameAnalyzer()
    image = cv2.imread(image_path)
    
    if image is None:
        print(f"Erreur: Impossible de charger {image_path}")
        return
        
    # Convertir BGR vers RGB pour matplotlib
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Créer une copie pour dessiner
    image_annotee = image_rgb.copy()
    
    hauteur, largeur = image.shape[:2]
    
    # Zones actuelles utilisées par l'analyseur
    grille_x = largeur // 3
    grille_y = hauteur // 3
    grille_largeur = largeur // 3
    grille_hauteur = hauteur // 2
    
    # Dessiner le rectangle de la grille
    cv2.rectangle(image_annotee, 
                  (grille_x, grille_y), 
                  (grille_x + grille_largeur, grille_y + grille_hauteur),
                  (255, 0, 0), 3)
    
    # Dessiner les cases individuelles
    taille_case_x = grille_largeur // 4
    taille_case_y = grille_hauteur // 4
    
    for row in range(4):
        for col in range(4):
            x = grille_x + col * taille_case_x
            y = grille_y + row * taille_case_y
            
            cv2.rectangle(image_annotee,
                          (x, y),
                          (x + taille_case_x, y + taille_case_y),
                          (0, 255, 0), 1)
            
    # Zone des stats joueur
    stats_x, stats_y = 0, 0
    stats_w, stats_h = largeur // 3, hauteur // 4
    cv2.rectangle(image_annotee,
                  (stats_x, stats_y),
                  (stats_x + stats_w, stats_y + stats_h),
                  (255, 255, 0), 3)
    cv2.putText(image_annotee, "Stats", (stats_x + 10, stats_y + 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
    
    # Afficher
    plt.figure(figsize=(12, 8))
    plt.imshow(image_annotee)
    plt.title("Zones détectées par l'analyseur actuel")
    plt.axis('off')
    plt.show()
    
    # Tester l'analyse
    try:
        resultat = analyzer.analyser_capture(image_path)
        print("\nRésultat de l'analyse:")
        print(f"Stats joueur: {resultat['stats_joueur']}")
        print(f"Nombre de dents actives: {len(resultat['dents_actives'])}")
        print("\nGrille détectée:")
        for i, rangee in enumerate(resultat['grille']):
            types = [case['type'] for case in rangee]
            print(f"Rangée {i+1}: {types}")
    except Exception as e:
        print(f"Erreur lors de l'analyse: {e}")


if __name__ == "__main__":
    # Tester avec l'image fournie
    visualiser_detection("20250604220023_1.jpg")