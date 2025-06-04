from typing import Dict, List, Any
from enum import Enum


class GamePhase(Enum):
    """Phases du jeu pour adapter la stratégie."""
    DEBUT = "debut"
    MILIEU = "milieu"
    BOSS = "boss"
    CRITIQUE = "critique"


class StrategyManager:
    """Gère les stratégies contextuelles et les objets."""
    
    def __init__(self):
        self.objets_marchands = {
            'epee_rouille': {'effet': 'force', 'valeur': 2},
            'baton_magique': {'effet': 'magie', 'valeur': 2},
            'armure_legere': {'effet': 'reduction_degats', 'valeur': 1},
            'potion_soin': {'effet': 'soin', 'valeur': 5},
            'bague_chance': {'effet': 'modifier_proba', 'valeur': 0.1},
            'bottes_vitesse': {'effet': 'esquive', 'valeur': 0.2},
            'amulette_vie': {'effet': 'pv_max', 'valeur': 3},
            'cape_ombre': {'effet': 'invisibilite', 'valeur': 0.3},
            'grimoire': {'effet': 'magie', 'valeur': 3},
            'bouclier': {'effet': 'reduction_degats', 'valeur': 2},
            'elixir': {'effet': 'stats_tous', 'valeur': 1},
            'pierre_ame': {'effet': 'resurrection', 'valeur': 1},
            'couronne': {'effet': 'or_bonus', 'valeur': 0.5},
            'gants_force': {'effet': 'force', 'valeur': 3}
        }
        
        self.benedictions = {
            'benediction_force': {'effet': 'force', 'valeur': 5},
            'benediction_magie': {'effet': 'magie', 'valeur': 5},
            'benediction_vie': {'effet': 'pv_max', 'valeur': 10},
            'benediction_chance': {'effet': 'modifier_proba', 'valeur': 0.25},
            'benediction_protection': {'effet': 'reduction_degats', 'valeur': 3},
            'benediction_richesse': {'effet': 'or_bonus', 'valeur': 1.0},
            'benediction_guerison': {'effet': 'regen', 'valeur': 2}
        }
    
    def determiner_phase(self, stats: Dict[str, int], niveau: int = 1) -> GamePhase:
        """
        Détermine la phase actuelle du jeu.
        """
        if stats['pv'] <= 3:
            return GamePhase.CRITIQUE
        elif niveau >= 10:
            return GamePhase.BOSS
        elif niveau <= 3:
            return GamePhase.DEBUT
        else:
            return GamePhase.MILIEU
    
    def ajuster_poids_strategiques(self, phase: GamePhase, 
                                  stats: Dict[str, int]) -> Dict[str, float]:
        """
        Ajuste les poids pour l'évaluation selon la phase.
        
        Returns:
            Dict avec poids pour gains, survie, exploration
        """
        if phase == GamePhase.CRITIQUE:
            return {
                'gains': 0.1,
                'survie': 10.0,
                'exploration': 0.0
            }
        elif phase == GamePhase.DEBUT:
            return {
                'gains': 3.0,
                'survie': 1.0,
                'exploration': 2.0
            }
        elif phase == GamePhase.BOSS:
            return {
                'gains': 0.5,
                'survie': 5.0,
                'exploration': 0.2
            }
        else:
            return {
                'gains': 2.0,
                'survie': 2.0,
                'exploration': 1.0
            }
    
    def appliquer_effets_objets(self, stats_base: Dict[str, int], 
                               objets_actifs: List[str]) -> Dict[str, int]:
        """
        Applique les effets des objets aux stats du joueur.
        """
        stats = stats_base.copy()
        reduction_degats = 0
        
        for objet in objets_actifs:
            if objet in self.objets_marchands:
                effet = self.objets_marchands[objet]['effet']
                valeur = self.objets_marchands[objet]['valeur']
                
                if effet == 'force':
                    stats['force'] += int(valeur)
                elif effet == 'magie':
                    stats['magie'] += int(valeur)
                elif effet == 'pv_max':
                    stats['pv_max'] = stats.get('pv_max', stats['pv']) + int(valeur)
                elif effet == 'reduction_degats':
                    reduction_degats += valeur
                elif effet == 'stats_tous':
                    stats['force'] += int(valeur)
                    stats['magie'] += int(valeur)
        
        stats['reduction_degats'] = reduction_degats
        return stats
    
    def evaluer_synergie_objets(self, objets_actifs: List[str]) -> float:
        """
        Évalue la synergie entre objets actifs.
        """
        score_synergie = 1.0
        
        types_effets = set()
        for objet in objets_actifs:
            if objet in self.objets_marchands:
                types_effets.add(self.objets_marchands[objet]['effet'])
        
        if 'force' in types_effets and 'reduction_degats' in types_effets:
            score_synergie *= 1.3
            
        if 'magie' in types_effets and 'modifier_proba' in types_effets:
            score_synergie *= 1.25
            
        if len(types_effets) >= 4:
            score_synergie *= 1.15
            
        return score_synergie
    
    def recommander_priorite_coffre(self, stats: Dict[str, int], 
                                   or_actuel: int, phase: GamePhase) -> bool:
        """
        Détermine si les coffres doivent être prioritaires.
        """
        if phase == GamePhase.DEBUT:
            return True
            
        if or_actuel < 50 and phase != GamePhase.CRITIQUE:
            return True
            
        if stats['force'] < 10 or stats['magie'] < 10:
            return True
            
        return False