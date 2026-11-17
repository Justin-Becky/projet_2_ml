# Prédicteur des chances de gagner sur Clash Royal

> Projet 2 — INF1007, automne 2026
> Équipe : Justin Arseneault (2534578), Louis Emery (2534613)

## Description

Ce projet analyse multiples partie jouées et prédit l’issue d’un match de Clash Royale à partir des données de l’API officielle.

## Jeu de données

Pour analyser des nouvelles données à partir d'un fichier .parquet,
1. Créer un fichier .py dans .src nommé variables_secretes.py
2. Dans ce fichier, ajouter une variable nommée CR_API_KEY
3. Allez sur le site officiel de API Clash Royale https://developer.clashroyale.com/
4. Faites-vous un 
5. Appuiez sur My Account
6. Créez une nouvelle clé avec le nom que vous voulez
7. Mettez 45.79.218.79 comme IP authorisée, c'est l'IP du proxy utilisée pour acceder votre clé peut importe l'adresse IP
8. Copier le token et collez la dans votre variable entre des guillemets

| Élément                 | Détail                                                                           |
|-------------------------|----------------------------------------------------------------------------------|
| Nom                     | Clash-Royale-Matchups-June2026                                                   |
| Source                  | https://www.kaggle.com/datasets/jackmangione/clash-royale-matchups-june2026/data |
| Licence                 | CC BY-NC-SA 4.0                                                                  |
| Taille                  | 737 280 lignes, 36 colonnes                                                      |

### Variables catégorielles

| Colonne                                 | Description                                         |
|-----------------------------------------|-----------------------------------------------------|
| `game_mode`                             | Mode de jeu (ex. `Ladder`)                          |
| `Joueur_A_carte_1` à `Joueur_A_carte_8` | Identifiant des 8 cartes du deck du premier joueur  |
| `Joueur_B_carte_1` à `Joueur_B_carte_8` | Identifiant des 8 cartes du deck du deuxieme joueur |

### Variables numériques

| Colonne                                               | Description                                       |
|-------------------------------------------------------|---------------------------------------------------|
| `Joueur_A_niveau_carte_1` à `Joueur_A_niveau_carte_8` | Niveau de chacune des 8 cartes du premier joueur  |
| `Joueur_B_niveau_carte_1` à `Joueur_B_niveau_carte_8` | Niveau de chacune des 8 cartes du deuxieme joueur |
| `Joueur_A_winrate`, `Joueur_B_winrate`                | Taux de victoires des deux joueurs                |
| `Joueur_A_gagne`                                      | True si le joueur A gagne, False si il perd       |

### Colonnes retirées

| Colonne                 | Raison                                                |
|-------------------------|-------------------------------------------------------|
| `Joueur_A`, `Joueur_B`  | Identifiants de joueurs (données personnelles)        |
| `time`                  | Horodatage de la partie, non utile pour la prédiction |

## Installation

```bash
git clone https://github.com/utilisateur/projet_inf1007.git
cd projet_inf1007
python -m venv .venv
source .venv/bin/activate   # Windows : .venv\Scripts\activate
pip install -r requirements.txt
```

## Lancement

```bash
python src/main.py
```

Pour ré-entraîner le modèle (facultatif, le modèle est déjà sauvegardé dans `modeles/`) :
1. Selectionnez le tab Entrainement
2. Choisissez votre modèle
3. Appuez sur TRAIN

## Structure du code

```
projet_inf1007/
├── src/
│   ├── images/        # images utilisées pour le projet
│   ├── donnees.py     # lecture, nettoyage, classes Variable
│   ├── modele.py      # entraînement, évaluation, prédiction
│   ├── exceptions.py  # exceptions personnalisées
│   ├── interface.py   # interface graphique
│   ├── deck.py        # interface graphique du deck
│   ├── entraineur.py  # interface graphique du système d'entrainement
│   ├── scroll.py      # systeme de défillage pour les graphics
│   ├── config.py      # constantes utilisées pour l'interface
│   └── main.py        # point d'entrée
├── tests/             # tests pytest
├── donnees/           # jeu de données CSV et cache de joueurs JSON
└── modeles/           # modèle .joblib + métadonnées .json
```

### Classes principales

- *******

## Résultats du modèle

| Modèle              | Métrique (RMSE) | R    |
|---------------------|-----------------|------|
| Référence (moyenne) | **              | **** |

limites, % trompe, batte les références ?

## Tests et couverture

```bash
pytest
coverage run -m pytest
```

## Outil du chapitre 7

Le décorateur `@chronometrer` (dans `modele.py`) mesure et affiche la durée de 
l'entraînement sans modifier le code de la fonction entraînée.

## Documentation consultée

- pandas : [10 minutes to pandas](https://pandas.pydata.org/docs/user_guide/10min.html)
- scikit-learn : [RandomForestRegressor](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestRegressor.html)
- Tkinter : [tkinter — Python interface to Tcl/Tk](https://docs.python.org/3/library/tkinter.html)
- Matplotlib : [Embedding in Tk](https://matplotlib.org/stable/gallery/user_interfaces/embedding_in_tk_sgskip.html)
