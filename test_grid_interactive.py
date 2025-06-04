#!/usr/bin/env python
"""
Script interactif pour optimiser les paramètres de détection de grille
"""
import cv2
import numpy as np
import os
import time

class GridDetectionOptimizer:
    def __init__(self, image_path):
        self.image_path = image_path
        self.image = cv2.imread(image_path)
        if self.image is None:
            raise ValueError(f"Impossible de charger {image_path}")
        
        # Paramètres de base
        self.base_params = {
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
        
        # Meilleurs paramètres trouvés
        self.best_params = self.base_params.copy()
        self.best_score = 0
        
        # Variations à tester
        self.param_variations = {
            'blur_kernel': [3, 5, 7, 9],
            'canny_low': [20, 30, 40, 50],
            'canny_high': [80, 100, 120, 150],
            'min_area': [500, 1000, 2000, 3000],
            'max_area': [20000, 35000, 50000, 75000],
            'aspect_ratio_min': [0.5, 0.6, 0.7, 0.8],
            'aspect_ratio_max': [1.2, 1.3, 1.4, 1.5],
            'y_tolerance': [10, 20, 30, 50],
            'morph_kernel': [3, 5, 7]
        }
    
    def test_params(self, params):
        """Teste une combinaison de paramètres"""
        try:
            # Prétraitement
            gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (params['blur_kernel'], params['blur_kernel']), 0)
            edges = cv2.Canny(blurred, params['canny_low'], params['canny_high'])
            
            # Fermeture morphologique
            kernel = np.ones((params['morph_kernel'], params['morph_kernel']), np.uint8)
            edges_closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
            
            # Contours
            contours, _ = cv2.findContours(edges_closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Filtrer les contours
            cases_potentielles = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if params['min_area'] <= area <= params['max_area']:
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = w / h
                    if params['aspect_ratio_min'] <= aspect_ratio <= params['aspect_ratio_max']:
                        cases_potentielles.append((x, y, w, h, area))
            
            # Créer la visualisation
            viz = self.image.copy()
            for i, (x, y, w, h, area) in enumerate(cases_potentielles):
                cv2.rectangle(viz, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(viz, f"{i+1}", (x+5, y+20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # Essayer de trouver une grille 4x4
            grille_trouvee = False
            grille_rect = None
            
            if len(cases_potentielles) >= 16:
                # Grouper par rangées
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
                
                # Chercher une grille 4x4
                for i in range(len(rangees) - 3):
                    if all(len(rangees[i+j]) >= 4 for j in range(4)):
                        min_x = min(case[0] for row in rangees[i:i+4] for case in row[:4])
                        min_y = rangees[i][0][1]
                        max_x = max(case[0] + case[2] for row in rangees[i:i+4] for case in row[:4])
                        max_y = rangees[i+3][0][1] + rangees[i+3][0][3]
                        
                        grille_rect = (min_x - 10, min_y - 10, max_x - min_x + 20, max_y - min_y + 20)
                        grille_trouvee = True
                        
                        # Dessiner la grille
                        cv2.rectangle(viz, (grille_rect[0], grille_rect[1]), 
                                    (grille_rect[0] + grille_rect[2], grille_rect[1] + grille_rect[3]), 
                                    (255, 0, 0), 3)
                        break
            
            return {
                'success': True,
                'cases_count': len(cases_potentielles),
                'grille_trouvee': grille_trouvee,
                'grille_rect': grille_rect,
                'visualization': viz,
                'info': f"Cases: {len(cases_potentielles)}, Grille: {'Oui' if grille_trouvee else 'Non'}"
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'info': f"Erreur: {e}"
            }
    
    def show_result(self, params, result, test_num):
        """Affiche le résultat d'un test"""
        print(f"\n{'='*50}")
        print(f"TEST {test_num}")
        print(f"{'='*50}")
        
        print("Paramètres:")
        for key, value in params.items():
            if value != self.base_params[key]:
                print(f"  {key}: {value} (modifié depuis {self.base_params[key]})")
            else:
                print(f"  {key}: {value}")
        
        print(f"\nRésultat: {result['info']}")
        
        if result['success']:
            # Sauvegarder l'image de test
            test_filename = f"test_{test_num}_result.jpg"
            cv2.imwrite(test_filename, result['visualization'])
            print(f"\n*** IMAGE SAUVEGARDÉE: {test_filename} ***")
            print(">>> OUVREZ CETTE IMAGE POUR VOIR LE RÉSULTAT <<<")
            print("Les rectangles VERTS montrent les cases détectées")
            if result['grille_trouvee']:
                print("Le rectangle BLEU montre la grille 4x4 détectée")
            else:
                print("AUCUNE grille 4x4 détectée (pas de rectangle bleu)")
            
            # Calculer un score automatique (optionnel)
            auto_score = 0
            if result['grille_trouvee']:
                auto_score += 50
            if 12 <= result['cases_count'] <= 20:  # Nombre idéal de cases
                auto_score += 30
            elif result['cases_count'] >= 8:
                auto_score += 20
            
            print(f"\nScore automatique: {auto_score}/80")
            print(f"Nombre de cases détectées: {result['cases_count']}")
            print(f"Grille 4x4 trouvée: {'OUI' if result['grille_trouvee'] else 'NON'}")
        
    def ask_user_feedback(self):
        """Demande l'avis de l'utilisateur"""
        while True:
            try:
                print("\n" + "="*60)
                print("REGARDEZ L'IMAGE GÉNÉRÉE ET ÉVALUEZ LE RÉSULTAT:")
                print("- Rectangles VERTS = cases détectées")
                print("- Rectangle BLEU = grille 4x4 (si trouvée)")
                print("="*60)
                print("Que pensez-vous de ce résultat ?")
                print("1 - Excellent: Grille parfaitement détectée, 16 cases bien placées")
                print("2 - Bon: Grille détectée avec quelques cases en plus/moins")
                print("3 - Moyen: Beaucoup de cases mais pas de grille claire")
                print("4 - Mauvais: Peu de cases détectées")
                print("5 - Très mauvais: Aucune case ou que du bruit")
                print("q - Quitter")
                
                choice = input("Votre choix (1-5 ou q): ").strip().lower()
                
                if choice == 'q':
                    return None
                elif choice == '1':
                    return 95
                elif choice == '2':
                    return 80
                elif choice == '3':
                    return 60
                elif choice == '4':
                    return 35
                elif choice == '5':
                    return 10
                else:
                    print("Choix invalide, essayez encore.")
                    
            except KeyboardInterrupt:
                return None
    
    def run_optimization(self):
        """Lance l'optimisation interactive"""
        print(f"Optimisation de la détection de grille pour: {self.image_path}")
        print(f"Dimensions de l'image: {self.image.shape}")
        
        test_num = 1
        
        # Test initial avec les paramètres de base
        print(f"\n{'-'*40}")
        print("TEST INITIAL avec les paramètres de base")
        print(f"{'-'*40}")
        result = self.test_params(self.base_params)
        self.show_result(self.base_params, result, test_num)
        
        input("\n>>> Appuyez sur Entrée quand vous avez regardé l'image... <<<")
        
        if result['success']:
            score = self.ask_user_feedback()
            if score is None:
                return
            self.best_score = score
            print(f"Score enregistré: {score}")
        
        test_num += 1
        
        # Tester des variations d'un paramètre à la fois
        for param_name, values in self.param_variations.items():
            print(f"\n{'='*60}")
            print(f"OPTIMISATION DU PARAMÈTRE: {param_name}")
            print(f"{'='*60}")
            
            for value in values:
                if value == self.base_params[param_name]:
                    continue  # Skip la valeur par défaut déjà testée
                
                # Créer les nouveaux paramètres
                test_params = self.best_params.copy()
                test_params[param_name] = value
                
                print(f"\n{'-'*40}")
                print(f"TEST {test_num}: {param_name} = {value}")
                print(f"{'-'*40}")
                result = self.test_params(test_params)
                self.show_result(test_params, result, test_num)
                
                # Pause pour laisser le temps de regarder
                input("\n>>> Appuyez sur Entrée quand vous avez regardé l'image... <<<")
                
                if result['success']:
                    score = self.ask_user_feedback()
                    if score is None:
                        print("\\nOptimisation interrompue.")
                        break
                    
                    print(f"Score: {score} (meilleur actuel: {self.best_score})")
                    
                    if score > self.best_score:
                        self.best_score = score
                        self.best_params = test_params.copy()
                        print(f"✓ NOUVEAU MEILLEUR SCORE ! Paramètres sauvegardés.")
                    
                test_num += 1
            
            if 'score' in locals() and score is None:
                break
        
        # Afficher les meilleurs paramètres
        print(f"\n{'='*60}")
        print("RÉSULTATS FINAUX")
        print(f"{'='*60}")
        print(f"Meilleur score: {self.best_score}")
        print("Meilleurs paramètres:")
        for key, value in self.best_params.items():
            if value != self.base_params[key]:
                print(f"  {key}: {value} (modifié depuis {self.base_params[key]})")
            else:
                print(f"  {key}: {value}")
        
        # Sauvegarder les paramètres optimisés
        with open("parametres_optimises.txt", "w") as f:
            f.write("# Paramètres optimisés pour la détection de grille\\n")
            f.write(f"# Score obtenu: {self.best_score}\\n")
            f.write(f"# Image testée: {self.image_path}\\n\\n")
            for key, value in self.best_params.items():
                f.write(f"{key} = {value}\\n")
        
        print("\\nParamètres sauvegardés dans: parametres_optimises.txt")

def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: python test_grid_interactive.py <image_path>")
        sys.exit(1)
    
    try:
        optimizer = GridDetectionOptimizer(sys.argv[1])
        optimizer.run_optimization()
    except Exception as e:
        print(f"Erreur: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()