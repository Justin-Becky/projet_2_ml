import time
import pandas as pd
from sklearn.linear_model import LogisticRegression
import joblib
import os

from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

dossier_modeles = "../modeles"

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

    def train(self):
        fichiers = "../donnees/data_set_final.parquet"
        df = pd.read_parquet(fichiers)
        df = df.dropna()
        df = df.head(self.nb_ligne)
        y = df["Joueur_A_gagne"]
        x = df.drop(columns=["Joueur_A_gagne"])

        colonnes_texte = x.select_dtypes(exclude="number").columns
        x = x.drop(columns=colonnes_texte)
        self.colonnes = list(x.columns)
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

    def save_model(self) -> str:
        os.makedirs(dossier_modeles, exist_ok=True)
        fichier = os.path.join(dossier_modeles, self.nom + ".joblib")
        joblib.dump(self, fichier)
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
