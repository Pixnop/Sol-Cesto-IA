#!/usr/bin/env python3
"""
Sol Cesto IA - Version Modulaire
Architecture propre avec séparation des responsabilités
"""

import sys
import os

# Ajoute le répertoire parent au path pour l'import
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sol_cesto.core.enums import HeroClass, ObjectType
from sol_cesto.core.models import Position
from sol_cesto.heroes import HeroSelector, HeroFactory, EnhancedGameStats
from sol_cesto.patterns.factory import GameObjectFactory
from sol_cesto.patterns.observer import EventPublisher, GameLogger, StatsTracker
from sol_cesto.patterns.command import CommandHistory, MoveCommand, InteractCommand

import json
from typing import Dict, Any


class ModularSolCestoGame:
    """Jeu Sol Cesto avec architecture modulaire"""
    
    def __init__(self):
        # Composants modulaires
        self.hero_selector = HeroSelector()
        self.event_publisher = EventPublisher()
        self.command_history = CommandHistory()
        
        # Observers
        self.game_logger = GameLogger()
        self.stats_tracker = StatsTracker()
        
        # Configuration du jeu
        self.setup_observers()
        
        # État du jeu
        self.selected_hero = None
        self.hero_stats = None
        self.game_grid = {}  # Position -> (ObjectType, ObjectBehavior)
        self.hero_position = Position(0, 0)
        self.game_active = False
    
    def setup_observers(self):
        """Configure les observers du jeu"""
        self.event_publisher.add_observer(self.game_logger)
        self.event_publisher.add_observer(self.stats_tracker)
    
    def start_game(self):
        """Démarre une nouvelle partie"""
        print("=== SOL CESTO IA - VERSION MODULAIRE ===\n")
        
        # 1. Sélection du héros
        self.select_hero_interactive()
        
        # 2. Configuration de la grille
        self.setup_game_grid()
        
        # 3. Simulation de jeu
        self.simulate_gameplay()
        
        # 4. Résultats finaux
        self.show_final_results()
    
    def select_hero_interactive(self):
        """Sélection interactive du héros"""
        print("🏰 SÉLECTION DU HÉROS\n")
        
        # Affichage des héros disponibles
        heroes_info = self.hero_selector.list_available_heroes()
        
        print("Classes de héros disponibles:")
        for i, (class_name, info) in enumerate(heroes_info.items(), 1):
            print(f"\n{i}. {info['name']} ({class_name.upper()})")
            print(f"   💪 Vie: {info['health']} | ⚡ Mana: {info['mana']} | ⚔️ ATK: {info['attack']} | 🛡️ DEF: {info['defense']}")
            print(f"   📖 {info['description']}")
            print(f"   🎯 Forces: {', '.join(info['strengths'])}")
            print(f"   ⚠️ Faiblesses: {', '.join(info['weaknesses'])}")
        
        # Recommandations par style de jeu
        print(f"\n💡 RECOMMANDATIONS PAR STYLE:")
        styles = ["aggressive", "defensive", "magical", "balanced"]
        
        for style in styles:
            recommendations = self.hero_selector.get_recommendations(style)
            top_rec = recommendations[0] if recommendations else None
            if top_rec:
                print(f"   {style.capitalize()}: {top_rec['name']} (Score: {top_rec['match_score']:.1f})")
        
        # Sélection automatique pour la démo (Paladin équilibré)
        selected_class = HeroClass.PALADIN
        custom_name = "Héros Modulaire"
        
        print(f"\n🎯 Sélection automatique: {selected_class.value} - {custom_name}")
        
        # Création du héros
        self.selected_hero = self.hero_selector.select_hero(selected_class, custom_name)
        hero_template = HeroFactory.get_hero_templates()[selected_class]
        self.hero_stats = EnhancedGameStats(self.selected_hero, hero_template)
        
        # Affichage du résumé
        summary = self.hero_selector.get_hero_summary()
        print(f"\n✅ HÉROS CRÉÉ:")
        print(f"   🆔 {summary['description']}")
        print(f"   🌟 Capacités: {', '.join(summary['special_abilities']) if summary['special_abilities'] else 'Aucune'}")
        print(f"   🛡️ Réduction dégâts: {summary['damage_reduction']}")
        print(f"   ⚔️ Bonus attaque: {summary['attack_bonus']}")
        print(f"   💚 Bonus soins: {summary['healing_bonus']}")
        
        # Amélioration optionnelle
        print(f"\n🔧 Application d'améliorations...")
        if self.hero_selector.enhance_selected_hero("super_regen"):
            enhanced_summary = self.hero_selector.get_hero_summary()
            print(f"   ✨ Amélioré: {enhanced_summary['description']}")
            print(f"   🆕 Nouvelles capacités: {', '.join(enhanced_summary['special_abilities'])}")
        
        print()
    
    def setup_game_grid(self):
        """Configure la grille de jeu avec les objets"""
        print("🗺️ CONFIGURATION DE LA GRILLE\n")
        
        # Configuration basée sur l'image de référence
        grid_objects = [
            # Rangée 0 - Risque élevé
            (Position(0, 0), ObjectType.SLIME_GREEN),
            (Position(0, 1), ObjectType.KEY_BLUE),
            (Position(0, 2), ObjectType.SLIME_GREEN),
            (Position(0, 3), ObjectType.DAGGER_RED),
            
            # Rangée 1 - Risque moyen
            (Position(1, 0), ObjectType.SLIME_GREEN),
            (Position(1, 1), ObjectType.CHAINS),
            (Position(1, 2), ObjectType.DAGGER_RED),
            (Position(1, 3), ObjectType.TREASURE_CHEST),
            
            # Rangée 2 - Recommandée par l'IA (meilleur ratio risque/récompense)
            (Position(2, 0), ObjectType.TREASURE_CHEST),
            (Position(2, 1), ObjectType.HEALTH_POTION),
            (Position(2, 2), ObjectType.DAGGER_RED),
            (Position(2, 3), ObjectType.TREASURE_CHEST),
            
            # Rangée 3 - Risque moyen
            (Position(3, 0), ObjectType.SLIME_GREEN),
            (Position(3, 1), ObjectType.CHAINS),
            (Position(3, 2), ObjectType.HEART_RED),
            (Position(3, 3), ObjectType.SLIME_GREEN),
        ]
        
        # Création des objets avec la Factory
        for position, obj_type in grid_objects:
            obj_type_created, behavior = GameObjectFactory.create_object(obj_type)
            self.game_grid[position] = (obj_type_created, behavior)
        
        print(f"✅ Grille configurée avec {len(self.game_grid)} objets")
        self.display_grid_info()
    
    def display_grid_info(self):
        """Affiche les informations de la grille"""
        print("\n📊 ANALYSE DE LA GRILLE:")
        
        # Comptage par catégorie
        categories = {"monster": 0, "treasure": 0, "trap": 0, "healing": 0, "utility": 0}
        total_threat = 0
        total_reward = 0
        
        for position, (obj_type, behavior) in self.game_grid.items():
            info = GameObjectFactory.get_object_info(obj_type)
            categories[info['category']] += 1
            total_threat += info['threat_level']
            total_reward += info['reward_value']
        
        print(f"   🏹 Monstres: {categories['monster']}")
        print(f"   💰 Trésors: {categories['treasure']}")
        print(f"   🕳️ Pièges: {categories['trap']}")
        print(f"   💚 Soins: {categories['healing']}")
        print(f"   🔧 Utilitaires: {categories['utility']}")
        print(f"   ⚡ Menace totale: {total_threat}")
        print(f"   🎁 Récompense totale: {total_reward}")
        
        # Analyse par rangée
        print(f"\n📋 ANALYSE PAR RANGÉE:")
        for row in range(4):
            row_objects = [(pos, obj) for pos, obj in self.game_grid.items() if pos.row == row]
            row_threat = sum(GameObjectFactory.get_object_info(obj[0])['threat_level'] for _, obj in row_objects)
            row_reward = sum(GameObjectFactory.get_object_info(obj[0])['reward_value'] for _, obj in row_objects)
            score = row_reward - row_threat
            
            risk_level = "FAIBLE" if row_threat < 10 else "MOYEN" if row_threat < 20 else "ÉLEVÉ"
            
            print(f"   Rangée {row}: Menace {row_threat} | Récompense {row_reward} | Score {score:+} | Risque {risk_level}")
        
        print()
    
    def simulate_gameplay(self):
        """Simule une partie de jeu"""
        print("🎮 SIMULATION DE PARTIE\n")
        
        # L'IA recommande la rangée 2 (meilleur score risque/récompense)
        recommended_row = 2
        print(f"🤖 IA recommande la rangée {recommended_row}")
        
        # Affichage du statut initial
        initial_status = self.hero_stats.get_detailed_status()
        print(f"📊 État initial: {initial_status['stats']['health']} HP, {initial_status['stats']['gold']} or")
        
        # Exploration de la rangée recommandée
        self.explore_row(recommended_row)
        
        print(f"\n🏁 Fin de l'exploration de la rangée {recommended_row}")
    
    def explore_row(self, row: int):
        """Explore une rangée complète"""
        print(f"\n🚀 EXPLORATION DE LA RANGÉE {row}:")
        
        for col in range(4):
            target_pos = Position(row, col)
            
            print(f"\n  📍 Mouvement vers {target_pos}")
            
            # Commande de déplacement
            move_cmd = MoveCommand(self.hero_position, target_pos)
            move_result = self.command_history.execute_command(move_cmd)
            
            if move_result['success']:
                # Notification du déplacement
                old_pos = Position(self.hero_position.row, self.hero_position.col)
                self.event_publisher.notify_hero_moved(old_pos, target_pos)
                
                # Interaction avec l'objet s'il y en a un
                if target_pos in self.game_grid:
                    obj_type, behavior = self.game_grid[target_pos]
                    print(f"    🎯 Objet trouvé: {obj_type.value}")
                    
                    # Commande d'interaction
                    interact_cmd = InteractCommand(self.hero_stats, obj_type, behavior, target_pos)
                    interact_result = self.command_history.execute_command(interact_cmd)
                    
                    if interact_result['success']:
                        # Traitement spécialisé selon le type d'interaction
                        result_summary = self.process_interaction_result(interact_result)
                        print(f"    📊 {result_summary}")
                        
                        # Notification d'interaction
                        self.event_publisher.notify_object_interacted(obj_type, interact_result)
                        self.event_publisher.notify_stats_changed(self.hero_stats)
                        
                        # Supprime l'objet après interaction (sauf pièges persistants)
                        if obj_type not in [ObjectType.SPIKE_TRAP, ObjectType.POISON_TRAP]:
                            del self.game_grid[target_pos]
                        
                        # Vérifie si le héros est toujours vivant
                        if not self.hero_stats.is_alive():
                            print(f"    💀 Héros vaincu!")
                            break
                    else:
                        print(f"    ❌ Interaction échouée: {interact_result.get('reason', 'Erreur inconnue')}")
                else:
                    print(f"    ⬜ Case vide")
                
                # Affichage du statut actuel
                current_status = self.hero_stats.get_detailed_status()
                print(f"    💪 Statut: {current_status['stats']['health']} HP, {current_status['stats']['gold']} or")
                
            else:
                print(f"    ❌ Déplacement échoué: {move_result.get('reason', 'Erreur inconnue')}")
                break
    
    def process_interaction_result(self, result: Dict[str, Any]) -> str:
        """Traite et formate le résultat d'une interaction"""
        action = result.get('action', 'unknown')
        
        if action == 'treasure_opened':
            gold = result.get('gold_gained', 0)
            items = result.get('items_gained', [])
            return f"Trésor ouvert! +{gold} or" + (f", objets: {items}" if items else "")
        
        elif action == 'healing_used':
            heal_amount = result.get('heal_amount', 0)
            heal_type = result.get('heal_type', 'health')
            return f"Soin utilisé! +{heal_amount} {heal_type}"
        
        elif action == 'combat':
            damage = result.get('damage_taken', 0)
            gold = result.get('gold_gained', 0)
            return f"Combat! -{damage} HP" + (f", +{gold} or" if gold > 0 else "")
        
        elif action == 'item_acquired':
            item = result.get('item', 'objet')
            bonuses = result.get('bonuses', {})
            return f"Objet acquis: {item}" + (f" (bonus: {bonuses})" if bonuses else "")
        
        elif action == 'trap_triggered':
            damage = result.get('damage_taken', 0)
            effect = result.get('effect', 'effet inconnu')
            return f"Piège! -{damage} HP ({effect})"
        
        else:
            return f"Action: {action}"
    
    def show_final_results(self):
        """Affiche les résultats finaux de la partie"""
        print(f"\n🏆 RÉSULTATS FINAUX\n")
        
        # Statut détaillé du héros
        final_status = self.hero_stats.get_detailed_status()
        
        print(f"👤 HÉROS FINAL:")
        print(f"   🆔 {final_status['hero_info']['description']}")
        print(f"   📊 Niveau {final_status['hero_info']['level']} (EXP: {final_status['hero_info']['experience']})")
        print(f"   💪 {final_status['stats']['health']} HP | ⚡ {final_status['stats']['mana']} MP")
        print(f"   💰 {final_status['stats']['gold']} or | 🎒 {final_status['inventory']['item_count']} objets")
        print(f"   🏥 État: {final_status['condition']}")
        
        if final_status['hero_info']['special_abilities']:
            print(f"   🌟 Capacités: {', '.join(final_status['hero_info']['special_abilities'])}")
        
        # Statistiques de combat
        combat_stats = final_status['combat_stats']
        print(f"\n⚔️ STATISTIQUES DE COMBAT:")
        print(f"   🏹 Dégâts infligés: {combat_stats['damage_dealt']}")
        print(f"   🛡️ Dégâts subis: {combat_stats['damage_taken']}")
        print(f"   💚 Soins reçus: {combat_stats['healing_received']}")
        print(f"   🏆 Combats gagnés: {combat_stats['battles_won']}")
        print(f"   🔮 Sorts lancés: {combat_stats['spells_cast']}")
        
        # Statistiques de jeu
        game_stats = self.stats_tracker.get_summary()
        print(f"\n📊 STATISTIQUES DE JEU:")
        print(f"   🚶 Déplacements: {game_stats['total_moves']}")
        print(f"   🎯 Interactions: {game_stats['total_interactions']}")
        print(f"   💰 Or gagné: {game_stats['gold_earned']}")
        print(f"   🎒 Objets collectés: {game_stats['items_collected']}")
        print(f"   💀 Monstres vaincus: {game_stats['monsters_defeated']}")
        print(f"   📦 Trésors ouverts: {game_stats['treasures_opened']}")
        
        # Métriques d'efficacité
        efficiency = final_status['efficiency_metrics']
        if efficiency:
            print(f"\n📈 EFFICACITÉ:")
            for metric, value in efficiency.items():
                print(f"   {metric}: {value:.2f}")
        
        # Historique des commandes
        cmd_summary = self.command_history.get_history_summary()
        print(f"\n📝 HISTORIQUE DES ACTIONS:")
        print(f"   Total: {cmd_summary['total_commands']} commandes")
        for cmd_type, count in cmd_summary['command_types'].items():
            print(f"   {cmd_type}: {count}")
        
        # Résumé des événements
        events_summary = self.game_logger.get_events_summary()
        print(f"\n📋 ÉVÉNEMENTS ENREGISTRÉS:")
        print(f"   Total: {events_summary['total_events']} événements")
        for event_type, count in events_summary['event_types'].items():
            print(f"   {event_type}: {count}")
        
        # Évaluation finale
        self.evaluate_performance()
        
        # Sauvegarde des résultats
        self.save_results(final_status, game_stats, events_summary)
    
    def evaluate_performance(self):
        """Évalue la performance du joueur"""
        final_status = self.hero_stats.get_detailed_status()
        
        # Calcul du score
        score = 0
        score += final_status['stats']['gold']  # Or gagné
        score += final_status['inventory']['item_count'] * 10  # Objets collectés
        score += self.hero_stats.current_health  # Points de vie restants
        score += (final_status['hero_info']['level'] - 1) * 50  # Niveaux gagnés
        
        # Pénalités
        combat_stats = final_status['combat_stats']
        score -= combat_stats['damage_taken']  # Dégâts subis
        
        print(f"\n🎯 ÉVALUATION DE PERFORMANCE:")
        print(f"   Score final: {score}")
        
        if self.hero_stats.is_alive():
            if score >= 200:
                print(f"   🏆 PERFORMANCE EXCELLENTE!")
                grade = "S"
            elif score >= 150:
                print(f"   🥇 TRÈS BONNE PERFORMANCE!")
                grade = "A"
            elif score >= 100:
                print(f"   🥈 BONNE PERFORMANCE!")
                grade = "B"
            elif score >= 50:
                print(f"   🥉 PERFORMANCE ACCEPTABLE!")
                grade = "C"
            else:
                print(f"   📈 PEUT MIEUX FAIRE!")
                grade = "D"
        else:
            print(f"   💀 ÉCHEC - Héros vaincu!")
            grade = "F"
        
        print(f"   Note: {grade}")
        return score, grade
    
    def save_results(self, final_status: Dict, game_stats: Dict, events_summary: Dict):
        """Sauvegarde les résultats de la partie"""
        results = {
            'hero_final_status': final_status,
            'game_statistics': game_stats,
            'events_summary': events_summary,
            'command_history': self.command_history.get_history_summary(),
            'hero_selection_history': self.hero_selector.get_selection_history(),
            'grid_objects_remaining': len(self.game_grid),
            'timestamp': self.game_logger.events[-1]['timestamp'] if self.game_logger.events else None
        }
        
        filename = 'modular_game_results.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Résultats sauvegardés: {filename}")


def main():
    """Lance le jeu modulaire"""
    try:
        game = ModularSolCestoGame()
        game.start_game()
    except KeyboardInterrupt:
        print(f"\n\n⏹️ Jeu interrompu par l'utilisateur")
    except Exception as e:
        print(f"\n\n❌ Erreur inattendue: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()