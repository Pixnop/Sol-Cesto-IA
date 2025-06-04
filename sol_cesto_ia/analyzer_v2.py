import cv2
import numpy as np
from PIL import Image
import pytesseract
from typing import Dict, List, Tuple, Any, Optional
import re
import os
import platform

# Configuration Tesseract pour Windows
if platform.system() == 'Windows':
    # Essayer de charger la configuration locale
    try:
        from tesseract_config import TESSERACT_PATH
        pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
    except ImportError:
        # Chemins par défaut Windows
        possible_paths = [
            r'C:\Program Files\Tesseract-OCR\tesseract.exe',
            r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'
        ]
        for path in possible_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                break


class GameAnalyzerV2:
    """Version améliorée de l'analyseur avec détection adaptative de la grille."""
    
    def __init__(self):
        self.types_cases = {
            'monstre_physique': {'couleurs': [(200, 50, 50), (255, 100, 100)], 'symbole': 'sword'},
            'monstre_magique': {'couleurs': [(100, 50, 200), (150, 100, 255)], 'symbole': 'magic'},
            'coffre': {'couleurs': [(200, 150, 50), (255, 215, 100)], 'symbole': 'chest'},
            'fraise': {'couleurs': [(200, 100, 150), (255, 182, 220)], 'symbole': 'berry'},
            'piege': {'couleurs': [(100, 50, 30), (180, 100, 70)], 'symbole': 'trap'},
            'vide': {'couleurs': [(50, 50, 50), (150, 150, 150)], 'symbole': 'empty'}
        }
        
    def analyser_capture(self, image_path: str) -> Dict[str, Any]:
        """
        Analyse une capture d'écran avec détection adaptative.
        """
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Impossible de charger l'image: {image_path}")
            
        # Détecter automatiquement les zones
        zones = self._detecter_zones_auto(image)
        
        if not zones['grille']:
            # Fallback sur l'ancienne méthode si échec
            zones = self._detecter_zones_manuel(image)
            
        grille = self._extraire_grille(image, zones['grille'])
        stats_joueur = self._extraire_stats_joueur(image, zones['stats'])
        dents_actives = self._detecter_dents_actives(image, zones.get('dents'))
        probabilites = self._extraire_probabilites_grille(image, zones['grille'])
        
        return {
            'grille': grille,
            'stats_joueur': stats_joueur,
            'dents_actives': dents_actives,
            'probabilites': probabilites,
            'zones_detectees': zones
        }
    
    def _detecter_zones_auto(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Détecte automatiquement les zones importantes du jeu.
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Rechercher la grille 4x4 par détection de contours
        grille_rect = self._trouver_grille(gray)
        
        # Rechercher la zone de stats (généralement en haut à gauche)
        stats_rect = self._trouver_zone_stats(gray)
        
        # Rechercher la zone des dents (généralement en bas)
        dents_rect = self._trouver_zone_dents(gray, image.shape[0])
        
        return {
            'grille': grille_rect,
            'stats': stats_rect,
            'dents': dents_rect
        }
    
    def _trouver_grille(self, gray: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """
        Trouve la grille 4x4 en cherchant un pattern régulier de cases.
        """
        # Détection des bords
        edges = cv2.Canny(gray, 50, 150)
        
        # Trouver les contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filtrer les contours carrés/rectangulaires de taille similaire
        cases_potentielles = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 1000 and area < 50000:  # Ajuster selon la résolution
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h
                if 0.7 < aspect_ratio < 1.3:  # Forme relativement carrée
                    cases_potentielles.append((x, y, w, h))
        
        if len(cases_potentielles) < 16:
            return None
            
        # Analyser les positions pour trouver une grille 4x4
        # Grouper par position Y (rangées)
        cases_potentielles.sort(key=lambda c: c[1])  # Trier par Y
        
        rangees = []
        current_row = []
        last_y = -100
        
        for case in cases_potentielles:
            if abs(case[1] - last_y) > 20:  # Nouvelle rangée
                if current_row:
                    rangees.append(current_row)
                current_row = [case]
                last_y = case[1]
            else:
                current_row.append(case)
                
        if current_row:
            rangees.append(current_row)
            
        # Chercher 4 rangées consécutives avec 4 cases chacune
        for i in range(len(rangees) - 3):
            if all(len(rangees[i+j]) >= 4 for j in range(4)):
                # Calculer les limites de la grille
                min_x = min(case[0] for row in rangees[i:i+4] for case in row[:4])
                min_y = rangees[i][0][1]
                max_x = max(case[0] + case[2] for row in rangees[i:i+4] for case in row[:4])
                max_y = rangees[i+3][0][1] + rangees[i+3][0][3]
                
                return (min_x - 10, min_y - 10, max_x - min_x + 20, max_y - min_y + 20)
                
        return None
    
    def _trouver_zone_stats(self, gray: np.ndarray) -> Tuple[int, int, int, int]:
        """
        Trouve la zone des statistiques du joueur.
        """
        h, w = gray.shape
        
        # Rechercher du texte dans le quart supérieur gauche
        roi = gray[0:h//3, 0:w//2]
        
        # Appliquer un seuillage pour améliorer la détection de texte
        _, thresh = cv2.threshold(roi, 150, 255, cv2.THRESH_BINARY)
        
        # Rechercher des zones de texte
        text = pytesseract.image_to_string(thresh, config='--psm 11')
        
        # Chercher des mots-clés
        if any(keyword in text.upper() for keyword in ['PV', 'HP', 'FORCE', 'MAGIE', 'MAGIC']):
            # Zone probable des stats trouvée
            return (0, 0, w//2, h//3)
        
        # Fallback: coin supérieur gauche
        return (0, 0, w//3, h//4)
    
    def _trouver_zone_dents(self, gray: np.ndarray, height: int) -> Tuple[int, int, int, int]:
        """
        Trouve la zone des dents/modificateurs (généralement en bas).
        """
        w = gray.shape[1]
        
        # Rechercher dans le tiers inférieur
        return (0, height * 2 // 3, w, height // 3)
    
    def _detecter_zones_manuel(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Méthode de fallback avec positions fixes.
        """
        h, w = image.shape[:2]
        
        return {
            'grille': (w//3, h//3, w//3, h//2),
            'stats': (0, 0, w//3, h//4),
            'dents': (0, h*3//4, w, h//4)
        }
    
    def _extraire_grille(self, image: np.ndarray, 
                        grille_rect: Tuple[int, int, int, int]) -> List[List[Dict]]:
        """
        Extrait la grille depuis la zone détectée.
        """
        x, y, w, h = grille_rect
        grille_img = image[y:y+h, x:x+w]
        
        case_w = w // 4
        case_h = h // 4
        
        grille = []
        
        for row in range(4):
            rangee = []
            for col in range(4):
                cx = col * case_w
                cy = row * case_h
                
                case_img = grille_img[cy:cy+case_h, cx:cx+case_w]
                
                # Debug: sauvegarder les cases individuelles si mode debug
                debug_mode = hasattr(self, 'debug_mode') and self.debug_mode
                if debug_mode:
                    case_path = f"case_{row}_{col}.jpg"
                    cv2.imwrite(case_path, case_img)
                    print(f"\nCase ({row}, {col}):")
                
                type_case = self._identifier_type_case_v2(case_img, debug=debug_mode)
                stats_monstre = None
                
                if type_case in ['monstre_physique', 'monstre_magique']:
                    stats_monstre = self._extraire_stats_monstre_v2(case_img)
                
                rangee.append({
                    'type': type_case,
                    'stats': stats_monstre,
                    'position': (row, col)
                })
                
            grille.append(rangee)
            
        return grille
    
    def _identifier_type_case_v2(self, case_image: np.ndarray, debug=False) -> str:
        """
        Identification améliorée du type de case.
        """
        if case_image.size == 0:
            return 'vide'
            
        # Calculer l'histogramme de couleurs
        hist_b = cv2.calcHist([case_image], [0], None, [256], [0, 256])
        hist_g = cv2.calcHist([case_image], [1], None, [256], [0, 256])
        hist_r = cv2.calcHist([case_image], [2], None, [256], [0, 256])
        
        # Couleur dominante
        avg_color = np.mean(case_image, axis=(0, 1))
        
        # Analyse des couleurs dominantes
        b, g, r = avg_color
        
        if debug:
            print(f"\nCouleur moyenne BGR: ({b:.0f}, {g:.0f}, {r:.0f})")
        
        # Rouge dominant -> Monstre physique
        if r > 150 and r > g * 1.5 and r > b * 1.5:
            return 'monstre_physique'
            
        # Violet/Magenta -> Monstre magique  
        if b > 100 and r > 100 and g < 100:
            return 'monstre_magique'
            
        # Jaune/Or -> Coffre
        if r > 150 and g > 150 and b < 100:
            return 'coffre'
            
        # Rose -> Fraise
        if r > 150 and g > 100 and b > 100 and r > g:
            return 'fraise'
            
        # Gris/Blanc -> Vide
        if min(b, g, r) > 180:  # Couleurs claires
            return 'vide'
            
        # Marron/Sombre -> Piège (seulement si vraiment sombre)
        if np.max(avg_color) < 80 and np.std(avg_color) < 20:
            return 'piege'
            
        # Par défaut, si on ne reconnait pas -> vide
        return 'vide'
    
    def _extraire_stats_monstre_v2(self, case_image: np.ndarray) -> Dict[str, int]:
        """
        Extraction améliorée des stats de monstre.
        """
        # Prétraitement pour améliorer l'OCR
        gray = cv2.cvtColor(case_image, cv2.COLOR_BGR2GRAY)
        
        # Augmenter le contraste
        alpha = 2.0
        beta = 0
        enhanced = cv2.convertScaleAbs(gray, alpha=alpha, beta=beta)
        
        # Seuillage adaptatif
        thresh = cv2.adaptiveThreshold(enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                      cv2.THRESH_BINARY, 11, 2)
        
        # OCR sur différentes configurations
        configs = ['--psm 8', '--psm 7', '--psm 13']
        
        for config in configs:
            text = pytesseract.image_to_string(thresh, config=config)
            numbers = re.findall(r'\\d+', text)
            if numbers:
                try:
                    return {'valeur': int(numbers[0])}
                except ValueError:
                    continue
                    
        return {'valeur': 5}  # Valeur par défaut
    
    def _extraire_stats_joueur(self, image: np.ndarray, 
                               stats_rect: Tuple[int, int, int, int]) -> Dict[str, int]:
        """
        Extraction améliorée des stats joueur.
        """
        x, y, w, h = stats_rect
        stats_img = image[y:y+h, x:x+w]
        
        gray = cv2.cvtColor(stats_img, cv2.COLOR_BGR2GRAY)
        
        # Améliorer pour l'OCR
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
        
        text = pytesseract.image_to_string(thresh, config='--psm 6')
        
        stats = {
            'pv': self._extraire_stat(text, ['PV', 'HP', 'VIE']),
            'force': self._extraire_stat(text, ['FORCE', 'FOR', 'STR', 'STRENGTH']),
            'magie': self._extraire_stat(text, ['MAGIE', 'MAG', 'MAGIC'])
        }
        
        # Valeurs par défaut si non trouvées
        if stats['pv'] == 0:
            stats['pv'] = 10
        if stats['force'] == 0:
            stats['force'] = 5
        if stats['magie'] == 0:
            stats['magie'] = 3
            
        return stats
    
    def _extraire_stat(self, text: str, keywords: List[str]) -> int:
        """
        Extrait une statistique depuis le texte.
        """
        text_upper = text.upper()
        
        for keyword in keywords:
            patterns = [
                f'{keyword}\\s*[:=]\\s*(\\d+)',
                f'{keyword}\\s*(\\d+)',
                f'(\\d+)\\s*{keyword}'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text_upper)
                if match:
                    try:
                        return int(match.group(1))
                    except (ValueError, IndexError):
                        continue
                        
        return 0
    
    def _detecter_dents_actives(self, image: np.ndarray, 
                               dents_rect: Optional[Tuple[int, int, int, int]]) -> List[Dict[str, Any]]:
        """
        Détection améliorée des dents actives.
        """
        if not dents_rect:
            return []
            
        x, y, w, h = dents_rect
        dents_img = image[y:y+h, x:x+w]
        
        # Convertir en niveaux de gris
        gray = cv2.cvtColor(dents_img, cv2.COLOR_BGR2GRAY)
        
        # Détection de contours pour trouver les icônes
        _, thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        dents = []
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if 500 < area < 5000:  # Taille typique d'une icône
                cx, cy, cw, ch = cv2.boundingRect(contour)
                
                # Analyser la couleur pour identifier le type
                dent_img = dents_img[cy:cy+ch, cx:cx+cw]
                avg_color = np.mean(dent_img, axis=(0, 1))
                
                # Classifier selon la couleur
                if avg_color[2] > 150:  # Rouge dominant
                    dent_type = 'dent_pierre'
                elif avg_color[0] > 150:  # Bleu dominant
                    dent_type = 'dent_metal'
                else:
                    dent_type = 'dent_inconnue'
                    
                dents.append({
                    'type': dent_type,
                    'effet': self._get_effet_dent(dent_type)
                })
                
        return dents
    
    def _get_effet_dent(self, dent_type: str) -> Dict[str, Any]:
        """
        Retourne l'effet d'une dent selon son type.
        """
        effets = {
            'dent_pierre': {'modificateur_probabilite': 0.21, 'cible': 'monstre_physique'},
            'dent_metal': {'combo_multiplicateur': 1.5},
            'dent_inconnue': {'modificateur_probabilite': 0.1}
        }
        
        return effets.get(dent_type, {'modificateur_probabilite': 0.0})
    
    def _extraire_probabilites_grille(self, image: np.ndarray, 
                                     grille_rect: Tuple[int, int, int, int]) -> Dict[Tuple[int, int], float]:
        """
        Extrait les probabilités affichées sur chaque case.
        """
        x, y, w, h = grille_rect
        grille_img = image[y:y+h, x:x+w]
        
        probabilites = {}
        case_w = w // 4
        case_h = h // 4
        
        for row in range(4):
            for col in range(4):
                cx = col * case_w
                cy = row * case_h
                
                case_img = grille_img[cy:cy+case_h, cx:cx+case_w]
                
                # Chercher un pourcentage dans la case
                gray = cv2.cvtColor(case_img, cv2.COLOR_BGR2GRAY)
                text = pytesseract.image_to_string(gray, config='--psm 8')
                
                match = re.search(r'(\\d+)\\s*%', text)
                if match:
                    try:
                        prob = float(match.group(1)) / 100.0
                        probabilites[(row, col)] = prob
                    except ValueError:
                        probabilites[(row, col)] = 0.25
                else:
                    probabilites[(row, col)] = 0.25
                    
        return probabilites