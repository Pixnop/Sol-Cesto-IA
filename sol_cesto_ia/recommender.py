from typing import Dict, List, Any, Tuple
import numpy as np
from .probability_calculator import ProbabilityCalculator


class MoveRecommender:
    """Recommande le meilleur coup basé sur l'analyse risque/récompense."""
    
    def __init__(self):
        self.calculator = ProbabilityCalculator()
        
    def recommander_coup(self, grille: List[List[Dict]], 
                        stats: Dict[str, int], 
                        modificateurs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyse toutes les rangées et recommande la meilleure.
        
        Args:
            grille: État actuel de la grille 4x4
            stats: Stats du joueur (PV, Force, Magie)
            modificateurs: Dents/modificateurs actifs
            
        Returns:
            Dict avec recommandation détaillée
        """
        meilleur_score = float('-inf')
        meilleure_rangee = 0
        details_rangees = []
        
        probabilites_base = self._generer_probabilites_base()
        
        for rangee in range(4):
            probabilites = self.calculator.calculer_probabilites(
                rangee, grille, modificateurs, probabilites_base
            )
            
            esperance_degats = self.calculator.calculer_esperance_degats(
                rangee, grille, stats, probabilites
            )
            
            esperance_gains = self.calculator.calculer_esperance_gains(
                rangee, grille, probabilites
            )
            
            score = self._calculer_score_rangee(
                esperance_gains, esperance_degats, stats['pv']
            )
            
            details = {
                'rangee': rangee + 1,
                'score': score,
                'esperance_degats': esperance_degats,
                'esperance_gains': esperance_gains,
                'probabilite_survie': self._calculer_probabilite_survie(
                    esperance_degats, stats['pv']
                )
            }
            details_rangees.append(details)
            
            if score > meilleur_score:
                meilleur_score = score
                meilleure_rangee = rangee
        
        meilleur = details_rangees[meilleure_rangee]
        
        return {
            'rangee_optimale': meilleure_rangee + 1,
            'justification': self._generer_justification(
                meilleur, stats, grille[meilleure_rangee]
            ),
            'esperance_gains': meilleur['esperance_gains'],
            'risque_degats': meilleur['esperance_degats'],
            'probabilite_survie': meilleur['probabilite_survie'],
            'details_toutes_rangees': details_rangees
        }
    
    def _calculer_score_rangee(self, gains: float, degats: float, pv_actuel: int) -> float:
        """
        Calcule un score composite pour une rangée.
        """
        if pv_actuel <= 3:
            poids_survie = 10.0
        elif pv_actuel <= 5:
            poids_survie = 5.0
        else:
            poids_survie = 2.0
            
        penalite_degats = degats * poids_survie
        
        if degats >= pv_actuel:
            penalite_degats *= 100
            
        score = gains - penalite_degats
        
        if degats == 0 and gains > 0:
            score *= 1.5
            
        return score
    
    def _calculer_probabilite_survie(self, esperance_degats: float, pv_actuel: int) -> float:
        """
        Estime la probabilité de survie après avoir choisi cette rangée.
        """
        if esperance_degats >= pv_actuel:
            return 0.0
        elif esperance_degats == 0:
            return 1.0
        else:
            return max(0, 1 - (esperance_degats / pv_actuel))
    
    def _generer_justification(self, details: Dict, stats: Dict[str, int], 
                              rangee_cases: List[Dict]) -> str:
        """
        Génère une justification textuelle pour la recommandation.
        """
        if stats['pv'] <= 3:
            if details['esperance_degats'] == 0:
                return "Rangée sans risque - Survie garantie avec PV critiques"
            else:
                return f"Risque minimal ({details['esperance_degats']:.1f} dégâts moyens) pour PV faibles"
                
        types_cases = [case['type'] for case in rangee_cases]
        
        if 'coffre' in types_cases and details['esperance_degats'] < stats['pv'] * 0.3:
            return "Bon équilibre risque/récompense avec coffre(s)"
            
        if all(t == 'fraise' for t in types_cases):
            return "Rangée de soins purs"
            
        if details['esperance_gains'] > 15:
            return f"Gains élevés ({details['esperance_gains']:.0f}) avec risque acceptable"
            
        if details['esperance_degats'] == 0:
            return "Aucun risque de dégâts"
            
        ratio = details['esperance_gains'] / (details['esperance_degats'] + 1)
        if ratio > 3:
            return f"Excellent ratio gain/risque ({ratio:.1f}:1)"
        else:
            return f"Meilleur compromis disponible (ratio {ratio:.1f}:1)"
    
    def _generer_probabilites_base(self) -> Dict[Tuple[int, int], float]:
        """
        Génère des probabilités de base si non détectées.
        """
        probas = {}
        for row in range(4):
            for col in range(4):
                probas[(row, col)] = 0.25
        return probas