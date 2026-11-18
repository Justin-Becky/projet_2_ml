import time
import pandas as pd
from sklearn.linear_model import LogisticRegression
import joblib
import os
import json
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from config import FICHIER_FINALE, dossier_modeles

CARTES_A = [f'Joueur_A_carte_{i}' for i in range(1,  9)]
CARTES_B = [f'Joueur_B_carte_{i}' for i in range(1, 9)]
NIVEAUX_A = [f'Joueur_A_niveau_carte_{i}' for i in range(1, 9)]
NIVEAUX_B = [f'Joueur_B_niveau_carte_{i}' for i in range(1, 9)]


class RegressionLineaire:
    def __init__(self, nom, nb_igne):
        self.nom = nom
        self.nb_ligne = nb_igne
        self.score = 0
        self.running_time = 0
        self.modele = make_pipeline(
            StandardScaler(),
            LogisticRegression(C=0.01, max_iter=2000),
        )
        self.colonnes = []
        self.cartes_connues = []

    def train(self):
        df = pd.read_parquet(FICHIER_FINALE)
        df = df.dropna()
        df = df.head(self.nb_ligne)
        y = df["Joueur_A_gagne"]
        x = df.drop(columns=["Joueur_A_gagne"])

        colonnes_texte = x.select_dtypes(exclude="number").columns
        x = x.drop(columns=colonnes_texte)
        self.colonnes = list(x.columns)

        self.cartes_connues = np.unique(x[CARTES_A + CARTES_B].to_numpy()).astype(int).tolist()

        x_train, x_test, y_train, y_test = train_test_split(
            x, y, test_size=0.2, random_state=42
        )
        debut = time.perf_counter()
        self.modele.fit(x_train, y_train)
        self.running_time = time.perf_counter() - debut
        self.calculer_score(x_test, y_test)

    def predict(self, winrate_a, cartes_a, niveaux_a, winrate_b, cartes_b, niveaux_b) -> float:
        partie = {'Joueur_A_winrate': winrate_a, 'Joueur_B_winrate': winrate_b}
        for i in range(8):
            partie[CARTES_A[i]] = cartes_a[i]
            partie[CARTES_B[i]] = cartes_b[i]
            partie[NIVEAUX_A[i]] = niveaux_a[i]
            partie[NIVEAUX_B[i]] = niveaux_b[i]

        x = pd.DataFrame([partie])[self.colonnes]
        return float(self.modele.predict_proba(x)[0, 1])

    def calculer_score(self, x_test, y_test):
        score = self.modele.score(x_test, y_test)
        self.score = score

    def metadonnees(self) -> dict:
        """
        Renvoie les métadonnées du modèle dans un dict prêt à être écrit en JSON :
        colonnes, valeurs possibles des cartes et intervalles des variables.
        """
        return {
            "nom": self.nom,
            "nb_lignes": self.nb_ligne,
            "colonnes": self.colonnes,
            "categorielles": {"cartes": self.cartes_connues},
            "numeriques": {"niveau": [1, 16], "winrate": [0.0, 1.0]},
            "score": float(self.score),
            "temps_entrainement": self.running_time,
        }

    def save_model(self):
        os.makedirs(dossier_modeles, exist_ok=True)
        fichier = os.path.join(dossier_modeles, self.nom + ".joblib")
        joblib.dump(self, fichier)

        fichier_json = os.path.join(dossier_modeles, self.nom + ".json")
        with open(fichier_json, "w", encoding="utf-8") as f:
            json.dump(self.metadonnees(), f, ensure_ascii=False, indent=2)

        return fichier

    @staticmethod
    def load(fichier):
        return joblib.load(fichier)

    # pour toi Louis cadeau pour utiliser la classe
    @staticmethod
    def charger_ou_entrainer(nom, nb_ligne, forcer=False):
        fichier = os.path.join(dossier_modeles, nom + ".joblib")
        if os.path.exists(fichier) and not forcer:
            return RegressionLineaire.load(fichier)

        modele = RegressionLineaire(nom, nb_ligne)
        modele.train()
        modele.save_model()
        return modele


def lire_metadonnees(nom: str) -> dict:
    """
    Lit le fichier JSON de métadonnées d'un modèle sauvegardé.

    Reçoit le nom du modèle (ex. : "regression_5000"), renvoie le dict des métadonnées.
    Lève FileNotFoundError si le fichier JSON n'existe pas.
    """
    fichier = os.path.join(dossier_modeles, nom + ".json")
    if not os.path.exists(fichier):
        raise FileNotFoundError(f"Métadonnées introuvables : {fichier}")
    with open(fichier, encoding="utf-8") as f:
        return json.load(f)


def lister_modeles() -> list[str]:
    """
    Renvoie le nom de tous les modèles qui ont un fichier JSON dans le dossier des modèles,
    triés du plus petit au plus grand nombre de lignes. Renvoie une liste vide si le dossier n'existe pas.
    """
    if not os.path.exists(dossier_modeles):
        return []
    noms = [os.path.splitext(f)[0] for f in os.listdir(dossier_modeles) if f.endswith(".json")]
    return sorted(noms, key=lambda nom: (len(nom), nom))
