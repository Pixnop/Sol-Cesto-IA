import numpy as np
from typing import List, Dict, Tuple, Any


class ProbabilityCalculator:
    """Calcule les probabilités réelles en appliquant les modificateurs."""
    
    def __init__(self):
        self.modificateurs_dents = {
            'dent_pierre': {
                'monstre_physique': 0.21,
                'piege': 0.09,
                'autres': -0.30
            },
            'dent_metal': {
                'combo_multiplicateur': 1.5
            }
        }
    
    def calculer_probabilites(self, rangee: int, grille: List[List[Dict]], 
                            modificateurs: List[Dict[str, Any]], 
                            probabilites_base: Dict[Tuple[int, int], float]) -> Dict[int, float]:
        """
        Calcule les probabilités pour chaque case d'une rangée.
        
        Args:
            rangee: Index de la rangée (0-3)
            grille: État de la grille
            modificateurs: Liste des dents/modificateurs actifs
            probabilites_base: Probabilités de base affichées
            
        Returns:
            Dict avec probabilité pour chaque colonne
        """
        probas = {}
        
        for col in range(4):
            proba_base = probabilites_base.get((rangee, col), 0.25)
            proba_modifiee = proba_base
            
            case = grille[rangee][col]
            type_case = case['type']
            
            for mod in modificateurs:
                if mod['type'] == 'dent_pierre':
                    if type_case == 'monstre_physique':
                        proba_modifiee *= 1.21
                    elif type_case == 'piege':
                        proba_modifiee *= 1.09
                    else:
                        proba_modifiee *= 0.70
                        
                elif mod['type'] == 'dent_metal':
                    if 'combo' in mod:
                        proba_modifiee *= 1.5
                        
            probas[col] = proba_modifiee
            
        total = sum(probas.values())
        if total > 0:
            for col in probas:
                probas[col] /= total
                
        return probas
    
    def calculer_esperance_degats(self, rangee: int, grille: List[List[Dict]], 
                                stats_joueur: Dict[str, int], 
                                probabilites: Dict[int, float]) -> float:
        """
        Calcule l'espérance de dégâts pour une rangée.
        """
        esperance = 0.0
        
        for col, proba in probabilites.items():
            case = grille[rangee][col]
            degats = self._calculer_degats_case(case, stats_joueur)
            esperance += degats * proba
            
        return esperance
    
    def calculer_esperance_gains(self, rangee: int, grille: List[List[Dict]], 
                               probabilites: Dict[int, float]) -> float:
        """
        Calcule l'espérance de gains (or, soins) pour une rangée.
        """
        esperance = 0.0
        
        for col, proba in probabilites.items():
            case = grille[rangee][col]
            gains = self._calculer_gains_case(case)
            esperance += gains * proba
            
        return esperance
    
    def _calculer_degats_case(self, case: Dict, stats_joueur: Dict[str, int]) -> float:
        """
        Calcule les dégâts potentiels d'une case.
        """
        type_case = case['type']
        
        if type_case == 'monstre_physique' and case['stats']:
            force_monstre = case['stats']['valeur']
            if stats_joueur['force'] < force_monstre:
                return force_monstre - stats_joueur['force']
                
        elif type_case == 'monstre_magique' and case['stats']:
            magie_monstre = case['stats']['valeur']
            if stats_joueur['magie'] < magie_monstre:
                return magie_monstre - stats_joueur['magie']
                
        elif type_case == 'piege':
            return 3.0
            
        return 0.0
    
    def _calculer_gains_case(self, case: Dict) -> float:
        """
        Calcule les gains potentiels d'une case.
        """
        type_case = case['type']
        
        if type_case == 'coffre':
            return 10.0
        elif type_case == 'fraise':
            return 1.0
        elif type_case in ['monstre_physique', 'monstre_magique']:
            return 5.0
            
        return 0.0