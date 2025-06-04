#!/usr/bin/env python
"""
Test de l'analyseur avec grille manuelle
"""
import json
import cv2
from sol_cesto_ia.analyzer_v2 import GameAnalyzerV2
from sol_cesto_ia.recommender import MoveRecommender

def load_manual_grid_config():
    """Charge la configuration de grille manuelle"""
    try:
        with open("grid_config.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("Fichier grid_config.json non trouvé !")
        print("Utilisez d'abord: python set_manual_grid.py")
        return None
    except Exception as e:
        print(f"Erreur lors du chargement de grid_config.json: {e}")
        return None

def analyze_with_manual_grid(image_path):
    """Analyse l'image avec la grille manuelle"""
    
    # Charger la configuration
    config = load_manual_grid_config()
    if config is None:
        return
    
    # Vérifier que c'est la même image
    if config["image_path"] != image_path:
        print(f"ATTENTION: La configuration était pour {config['image_path']}")
        print(f"Vous analysez: {image_path}")
        choice = input("Continuer quand même ? (o/n): ").strip().lower()
        if choice != 'o':
            return
    
    # Extraire les coordonnées
    grid_rect = config["grid_rect"]
    x, y, w, h = grid_rect["x"], grid_rect["y"], grid_rect["width"], grid_rect["height"]
    
    print(f"Utilisation de la grille manuelle: x={x}, y={y}, w={w}, h={h}")
    
    # Charger l'image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Erreur: Impossible de charger {image_path}")
        return
    
    # Créer l'analyseur
    analyzer = GameAnalyzerV2()
    
    # Remplacer la méthode de détection automatique
    def _detecter_zones_manuel_fixe(self, image):
        return {
            'grille': (x, y, w, h),
            'stats': (0, 0, x, y),  # Zone au-dessus de la grille
            'dents': (0, y + h, image.shape[1], image.shape[0] - y - h)  # Zone en dessous
        }
    
    # Monkey patch pour utiliser les coordonnées fixes
    analyzer._detecter_zones_auto = _detecter_zones_manuel_fixe.__get__(analyzer, GameAnalyzerV2)
    
    print("\n" + "="*60)
    print("ANALYSE AVEC GRILLE MANUELLE")
    print("="*60)
    
    try:
        # Analyser l'image
        etat_jeu = analyzer.analyser_capture(image_path)
        
        print(f"\n=== ÉTAT DU JEU DÉTECTÉ ===")
        print(f"PV: {etat_jeu['stats_joueur']['pv']}")
        print(f"Force: {etat_jeu['stats_joueur']['force']}")
        print(f"Magie: {etat_jeu['stats_joueur']['magie']}")
        
        print(f"\n=== GRILLE DÉTECTÉE ===")
        for i, rangee in enumerate(etat_jeu['grille']):
            types = [case['type'] for case in rangee]
            print(f"Rangée {i+1}: {types}")
            
            # Détails de chaque case
            for j, case in enumerate(rangee):
                if case['stats']:
                    print(f"  Case ({i+1},{j+1}): {case['type']} - Stats: {case['stats']}")
                else:
                    print(f"  Case ({i+1},{j+1}): {case['type']}")
        
        # Obtenir une recommandation
        recommender = MoveRecommender()
        resultat = recommender.recommander_coup(
            grille=etat_jeu['grille'],
            stats=etat_jeu['stats_joueur'],
            modificateurs=etat_jeu['dents_actives']
        )
        
        print(f"\n=== RECOMMANDATION ===")
        print(f"Choisir rangée {resultat['rangee_optimale']}")
        print(f"Raison: {resultat['justification']}")
        print(f"\nGains espérés: {resultat['esperance_gains']:.2f}")
        print(f"Risque de dégâts: {resultat['risque_degats']:.2f}")
        print(f"Probabilité de survie: {resultat['probabilite_survie']:.1%}")
        
        # Créer une visualisation
        viz = image.copy()
        
        # Dessiner la grille
        cv2.rectangle(viz, (x, y), (x + w, y + h), (255, 0, 0), 3)
        cv2.putText(viz, "GRILLE MANUELLE", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        
        # Dessiner les divisions des cases
        case_w = w // 4
        case_h = h // 4
        
        for i in range(1, 4):
            # Lignes verticales
            cv2.line(viz, (x + i * case_w, y), (x + i * case_w, y + h), (0, 255, 255), 1)
            # Lignes horizontales
            cv2.line(viz, (x, y + i * case_h), (x + w, y + i * case_h), (0, 255, 255), 1)
        
        # Annoter chaque case avec son type
        for i, rangee in enumerate(etat_jeu['grille']):
            for j, case in enumerate(rangee):
                cx = x + j * case_w + 5
                cy = y + i * case_h + 20
                
                # Couleur selon le type
                color = {
                    'monstre_physique': (0, 0, 255),    # Rouge
                    'monstre_magique': (255, 0, 255),   # Magenta
                    'coffre': (0, 255, 255),            # Jaune
                    'fraise': (255, 192, 203),          # Rose
                    'piege': (128, 128, 128),           # Gris
                    'vide': (255, 255, 255)             # Blanc
                }.get(case['type'], (255, 255, 255))
                
                cv2.putText(viz, case['type'][:4], (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
                
                if case['stats']:
                    cv2.putText(viz, f"{case['stats'].get('valeur', '?')}", (cx, cy + 15), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
        
        # Mettre en évidence la rangée recommandée
        rangee_rec = resultat['rangee_optimale'] - 1  # Convert to 0-based
        rec_y = y + rangee_rec * case_h
        cv2.rectangle(viz, (x - 5, rec_y - 5), (x + w + 5, rec_y + case_h + 5), (0, 255, 0), 3)
        cv2.putText(viz, f"RECOMMANDEE: Rangee {resultat['rangee_optimale']}", 
                   (x, rec_y - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        cv2.imwrite("analyse_avec_grille_manuelle.jpg", viz)
        print(f"\nVisualisation sauvegardée: analyse_avec_grille_manuelle.jpg")
        
        print(f"\n{'='*60}")
        print("SUCCÈS ! La grille manuelle fonctionne correctement.")
        print("Vous pouvez maintenant intégrer ces coordonnées dans l'analyseur principal.")
        print(f"{'='*60}")
        
    except Exception as e:
        print(f"Erreur lors de l'analyse: {e}")
        import traceback
        traceback.print_exc()

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python test_with_manual_grid.py <image_path>")
        print("\nAssurez-vous d'avoir d'abord défini la grille avec:")
        print("  python set_manual_grid.py <image_path>")
        sys.exit(1)
    
    analyze_with_manual_grid(sys.argv[1])

if __name__ == "__main__":
    main()