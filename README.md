# Prédicteur des chances de gagner sur Clash Royal

> Projet 2 — INF1007, automne 2026
> Équipe : Justin Arseneault (2534578), Louis Emery (2534613)

## Description

*************

## Jeu de données

| Élément                 | Détail                                                                           |
|-------------------------|----------------------------------------------------------------------------------|
| Nom                     | Clash-Royale-Matchups-June2026                                                   |
| Source                  | https://www.kaggle.com/datasets/jackmangione/clash-royale-matchups-june2026/data |
| Licence                 | CC BY-NC-SA 4.0                                                                  |
| Taille                  | 737 280 lignes, 36 colonnes                                                      |
| Variable cible          | gagne (oui ou non)                                                               |
| Variables numériques    | `superficie`, `annee_construction`, `nb_chambres`, ...                           |
| Variables catégorielles | `quartier`, `type_logement`, ...                                                 |

Les fichiers sont trop lourd, c'est pourquoi ils ne sont pas dans github. Pour les télécharger, il suffit d'aller 
sur https://www.kaggle.com/datasets/jackmangione/clash-royale-matchups-june2026/data et de télécharger les six premiers
fichiers soit (0, 1, 2, 3, 4, 5) et de les mettre dans le dossier donnees.

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

```bash
python src/modele.py
```

## Structure du code

```
projet_inf1007/
├── src/
│   ├── donnees.py     # lecture, nettoyage, classes Variable
│   ├── modele.py      # entraînement, évaluation, prédiction
│   ├── exceptions.py  # exceptions personnalisées
│   ├── interface.py   # interface graphique
│   └── main.py        # point d'entrée
├── tests/             # tests pytest
├── donnees/           # jeu de données CSV
└── modeles/           # modèle .joblib + métadonnées .json
```

### Classes principales

- *******

## Résultats du modèle

| Modèle              | Métrique (RMSE) | R    |
|---------------------|-----------------|------|
| Référence (moyenne) | **              | **** |
| Forêt aléatoire     | **              | **** |

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
