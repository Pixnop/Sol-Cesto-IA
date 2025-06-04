# Sol Cesto IA

Intelligence artificielle pour analyser et recommander les meilleurs coups dans le jeu Sol Cesto.

## Installation

1. Installer les dépendances :
```bash
pip install -r requirements.txt
```

2. Installer Tesseract OCR :
- Windows : Télécharger depuis https://github.com/UB-Mannheim/tesseract/wiki
- Linux : `sudo apt-get install tesseract-ocr`
- Mac : `brew install tesseract`

## Utilisation

### Interface graphique
```bash
python -m sol_cesto_ia.gui
```

### Ligne de commande
```bash
python main.py screenshot.png
```

Avec mode verbeux :
```bash
python main.py screenshot.png --verbose
```

## Fonctionnalités

- Détection automatique de la grille 4x4
- Identification des types de cases (monstres, coffres, pièges, etc.)
- Calcul des probabilités avec modificateurs
- Évaluation risque/récompense
- Recommandations adaptées au contexte (PV faibles, phase de jeu)
- Support des objets et bénédictions

## Architecture

- `analyzer.py` : Analyse d'image et extraction des données
- `probability_calculator.py` : Calculs probabilistes
- `recommender.py` : Système de recommandation
- `strategies.py` : Gestion des stratégies et objets
- `gui.py` : Interface graphique