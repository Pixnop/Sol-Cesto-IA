from sol_cesto_ia.analyzer_v2 import GameAnalyzerV2 as GameAnalyzer
from sol_cesto_ia.recommender import MoveRecommender
import argparse
import sys


def main():
    parser = argparse.ArgumentParser(description="IA pour Sol Cesto - Analyse et recommandation de coups")
    parser.add_argument('image_path', help="Chemin vers la capture d'écran du jeu")
    parser.add_argument('--verbose', '-v', action='store_true', help="Mode verbeux")
    parser.add_argument('--debug', '-d', action='store_true', help="Mode debug avec visualisation")
    
    args = parser.parse_args()
    
    analyzer = GameAnalyzer()
    if args.debug:
        analyzer.debug_mode = True
    recommender = MoveRecommender()
    
    try:
        if args.debug:
            # Mode debug pour voir les zones détectées
            import cv2
            image = cv2.imread(args.image_path)
            zones = analyzer._detecter_zones_auto(image)
            print("\n=== ZONES DÉTECTÉES ===")
            for nom, coords in zones.items():
                print(f"{nom}: {coords}")
            
            if zones['grille']:
                # Créer une visualisation
                viz = image.copy()
                colors = {
                    'grille': (0, 255, 0),
                    'stats': (255, 0, 0),
                    'dents': (0, 0, 255),
                    'compteur': (255, 255, 0)
                }
                
                for nom, coords in zones.items():
                    if coords:
                        x, y, w, h = coords
                        color = colors.get(nom, (255, 255, 255))
                        cv2.rectangle(viz, (x, y), (x+w, y+h), color, 2)
                        cv2.putText(viz, nom, (x+5, y+20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                
                # Sauvegarder l'image annotée
                debug_path = args.image_path.replace('.jpg', '_debug.jpg')
                cv2.imwrite(debug_path, viz)
                print(f"\nImage annotée sauvegardée: {debug_path}")
            else:
                print("\nAucune grille détectée automatiquement!")
        
        etat_jeu = analyzer.analyser_capture(args.image_path)
        
        if args.verbose:
            print("\n=== ÉTAT DU JEU DÉTECTÉ ===")
            print(f"PV: {etat_jeu['stats_joueur']['pv']}")
            print(f"Force: {etat_jeu['stats_joueur']['force']}")
            print(f"Magie: {etat_jeu['stats_joueur']['magie']}")
            print(f"\nGrille détectée:")
            for i, rangee in enumerate(etat_jeu['grille']):
                print(f"Rangée {i+1}: {rangee}")
        
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
        
    except Exception as e:
        print(f"Erreur: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
