import cv2
import numpy as np
from PIL import Image
import pytesseract
from typing import Dict, List, Tuple, Any
import re


class GameAnalyzer:
    """Analyse les captures d'écran de Sol Cesto pour extraire l'état du jeu."""
    
    def __init__(self):
        self.types_cases = {
            'monstre_physique': {'couleur': (255, 0, 0), 'symbole': 'sword'},
            'monstre_magique': {'couleur': (128, 0, 255), 'symbole': 'magic'},
            'coffre': {'couleur': (255, 215, 0), 'symbole': 'chest'},
            'fraise': {'couleur': (255, 182, 193), 'symbole': 'berry'},
            'piege': {'couleur': (139, 69, 19), 'symbole': 'trap'},
            'vide': {'couleur': (128, 128, 128), 'symbole': 'empty'}
        }
        
    def analyser_capture(self, image_path: str) -> Dict[str, Any]:
        """
        Analyse une capture d'écran et extrait toutes les informations du jeu.
        
        Args:
            image_path: Chemin vers l'image à analyser
            
        Returns:
            Dict contenant l'état du jeu avec grille, stats, etc.
        """
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Impossible de charger l'image: {image_path}")
            
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        grille = self._detecter_grille(image)
        stats_joueur = self._extraire_stats_joueur(image, gray)
        dents_actives = self._detecter_dents_actives(image)
        probabilites = self._extraire_probabilites(image, gray)
        
        return {
            'grille': grille,
            'stats_joueur': stats_joueur,
            'dents_actives': dents_actives,
            'probabilites': probabilites
        }
    
    def _detecter_grille(self, image: np.ndarray) -> List[List[Dict]]:
        """
        Détecte la grille 4x4 et identifie le type de chaque case.
        
        Returns:
            Liste 4x4 avec info sur chaque case
        """
        hauteur, largeur = image.shape[:2]
        
        grille_x = largeur // 3
        grille_y = hauteur // 3
        grille_largeur = largeur // 3
        grille_hauteur = hauteur // 2
        
        taille_case_x = grille_largeur // 4
        taille_case_y = grille_hauteur // 4
        
        grille = []
        
        for row in range(4):
            rangee = []
            for col in range(4):
                x = grille_x + col * taille_case_x
                y = grille_y + row * taille_case_y
                
                case = image[y:y+taille_case_y, x:x+taille_case_x]
                
                type_case = self._identifier_type_case(case)
                stats_monstre = None
                
                if type_case in ['monstre_physique', 'monstre_magique']:
                    stats_monstre = self._extraire_stats_monstre(case)
                
                rangee.append({
                    'type': type_case,
                    'stats': stats_monstre,
                    'position': (row, col)
                })
                
            grille.append(rangee)
            
        return grille
    
    def _identifier_type_case(self, case_image: np.ndarray) -> str:
        """
        Identifie le type d'une case par analyse de couleur et pattern.
        """
        avg_color = np.mean(case_image, axis=(0, 1))
        
        case_gray = cv2.cvtColor(case_image, cv2.COLOR_BGR2GRAY)
        
        edges = cv2.Canny(case_gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if avg_color[2] > 200 and avg_color[0] < 100:
            return 'monstre_physique'
        elif avg_color[0] > 100 and avg_color[2] > 100:
            return 'monstre_magique'
        elif avg_color[1] > 150 and avg_color[2] > 150:
            return 'coffre'
        elif avg_color[2] > 150 and avg_color[1] > 100:
            return 'fraise'
        elif np.max(avg_color) < 100:
            return 'piege'
        else:
            return 'vide'
    
    def _extraire_stats_joueur(self, image: np.ndarray, gray: np.ndarray) -> Dict[str, int]:
        """
        Extrait les stats du joueur (PV, Force, Magie) via OCR.
        """
        hauteur, largeur = image.shape[:2]
        
        stats_region = gray[0:hauteur//4, 0:largeur//3]
        
        text = pytesseract.image_to_string(stats_region, config='--psm 6')
        
        stats = {
            'pv': self._extraire_nombre(text, r'PV\s*[:=]\s*(\d+)'),
            'force': self._extraire_nombre(text, r'Force\s*[:=]\s*(\d+)'),
            'magie': self._extraire_nombre(text, r'Magie\s*[:=]\s*(\d+)')
        }
        
        if all(v == 0 for v in stats.values()):
            stats = {'pv': 10, 'force': 5, 'magie': 3}
            
        return stats
    
    def _extraire_stats_monstre(self, case_image: np.ndarray) -> Dict[str, int]:
        """
        Extrait les stats d'un monstre depuis une case.
        """
        gray = cv2.cvtColor(case_image, cv2.COLOR_BGR2GRAY)
        text = pytesseract.image_to_string(gray, config='--psm 8')
        
        match = re.search(r'(\d+)', text)
        if match:
            return {'valeur': int(match.group(1))}
        
        return {'valeur': 5}
    
    def _detecter_dents_actives(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Détecte les dents/modificateurs actifs.
        """
        dents = []
        
        hauteur, largeur = image.shape[:2]
        region_dents = image[hauteur*3//4:hauteur, 0:largeur]
        
        gray = cv2.cvtColor(region_dents, cv2.COLOR_BGR2GRAY)
        contours, _ = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 500:
                x, y, w, h = cv2.boundingRect(contour)
                dents.append({
                    'type': 'dent_inconnue',
                    'effet': {'modificateur_probabilite': 0.1}
                })
        
        return dents
    
    def _extraire_probabilites(self, image: np.ndarray, gray: np.ndarray) -> Dict[Tuple[int, int], float]:
        """
        Extrait les probabilités affichées pour chaque case.
        """
        probabilites = {}
        
        hauteur, largeur = image.shape[:2]
        grille_region = gray[hauteur//3:hauteur*2//3, largeur//3:largeur*2//3]
        
        text = pytesseract.image_to_string(grille_region, config='--psm 11')
        
        matches = re.findall(r'(\d+)\s*%', text)
        
        if len(matches) >= 16:
            idx = 0
            for row in range(4):
                for col in range(4):
                    try:
                        prob = float(matches[idx]) / 100.0
                        probabilites[(row, col)] = prob
                        idx += 1
                    except (IndexError, ValueError):
                        probabilites[(row, col)] = 0.25
        else:
            for row in range(4):
                for col in range(4):
                    probabilites[(row, col)] = 0.25
                    
        return probabilites
    
    def _extraire_nombre(self, text: str, pattern: str) -> int:
        """
        Extrait un nombre depuis du texte avec un pattern regex.
        """
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                pass
        return 0