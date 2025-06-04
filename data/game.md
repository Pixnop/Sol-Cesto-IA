# Sol Cesto : Recherche approfondie et prompt pour IA

## Synthèse complète du jeu Sol Cesto

Sol Cesto est un roguelite tactique sorti en Early Access sur Steam le 27 mai 2025, développé par Géraud Zucchini et Chariospirale, publié par Goblinz Publishing. Le jeu combine des mécaniques de gestion de probabilités avec un système de grille 4x4 unique.

### 1. Mécaniques exactes du jeu

**Système de grille 4x4 :**
- Chaque écran présente une grille de 16 cases (4 rangées × 4 colonnes)
- Le joueur choisit l'une des 4 rangées
- Le jeu détermine aléatoirement sur quelle case de la rangée le joueur atterrit
- **Probabilité de base :** 25% par case dans la rangée sélectionnée
- Les cases doivent être vidées pour progresser vers l'écran suivant

**Types de cases :**
- **Monstres physiques** : Comparent leur force à la résistance physique du joueur
- **Monstres magiques** : Comparent leur magie à la résistance magique du joueur
- **Coffres au trésor** : Fournissent de l'or pour les achats
- **Fraises** : Restaurent 1 point de vie manquant
- **Pièges** : Infligent des dégâts automatiques (poison, dégâts directs)
- **Secrets/Cases vides** : Contenu variable ou aucun effet

### 2. Objets et améliorations

**Dents maudites (~30 disponibles) :**
- **Dents de pierre** : Modifient les probabilités en faveur du joueur
- **Dents de métal** : Déclenchent des malédictions et combos dévastateurs
- Exemple : +21% chance monstres de force, +9% chance pièges

**Objets marchands (14 disponibles) :**
- Améliorations de combat
- Manipulation de probabilités
- Soins et récupération
- Objets utilitaires
- Génération d'or

**Objets de fontaine magique (7 disponibles) :**
- Bénédictions permanentes pour la run
- Modifications positives des probabilités
- Effets de soin ou réduction de dégâts

**Améliorations permanentes (~40 étoiles) :**
- Système de méta-progression
- Conversion de l'or en améliorations permanentes
- Persistent entre les runs

### 3. Stratégies optimales et calculs

**Calcul de combat :**
```
Si Stat_Joueur >= Stat_Monstre : Pas de dégâts, monstre vaincu
Si Stat_Joueur < Stat_Monstre : Dégâts = Stat_Monstre - Stat_Joueur
```

**Modification des probabilités :**
```
Probabilité_finale = Probabilité_base × Modificateurs_dents
Base : 25% par case
Avec dents : Peut varier significativement (ex: 21%/33%/21%/25%)
```

**Stratégies de sélection de rangée :**
1. Évaluer la composition de chaque rangée
2. Calculer les probabilités modifiées
3. Estimer le ratio risque/récompense
4. Prioriser l'or en début de partie
5. Gérer la santé en fin de biome

### 4. Système de combat

- **Deux types de stats** : Physique et Magique
- **Comparaison directe** : Stat joueur vs stat monstre
- **Dégâts** : Différence si le monstre est plus fort
- **Pas de dégâts** : Si le joueur égale ou dépasse la stat du monstre

### 5. Modes et progression

**Contenu actuel (Early Access) :**
- 3 biomes (5 prévus)
- 4 personnages (8 prévus)
- 25 étages actuellement
- 2 boss implémentés

**Personnages disponibles :**
1. **Chevalier** : Placement stratégique du pouvoir solaire
2. **Guerrier** : Plus de vie mais ennemis plus forts
3. Deux autres personnages (noms non confirmés)

### 6. Exemples de gameplay

**Décision type :**
- Rangée 1 : [Monstre Fort 5][Coffre][Piège][Fraise]
- Rangée 2 : [Coffre][Monstre Faible 2][Coffre][Vide]
- Rangée 3 : [Piège][Piège][Monstre Moyen 3][Coffre]
- Rangée 4 : [Fraise][Vide][Monstre Faible 1][Coffre]

Avec stats actuelles (Force: 3, Magie: 2), la rangée 2 offre le meilleur ratio risque/récompense.

### 7. Structure visuelle pour analyse IA

**Interface principale :**
- Grille 4x4 centrale dominant l'écran
- Indicateurs de probabilité par case
- Affichage des stats du personnage (vie, force, magie)
- Inventaire des dents et objets actifs

**Éléments visuels distinctifs :**
- Style artistique "étrange, troublant et onirique"
- Couleurs sombres et atmosphériques
- Animations distinctes par type de case
- Feedback visuel pour les modificateurs actifs