import glob
import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QGridLayout, QLabel, QPushButton, QSpinBox, QWidget

from modele import RegressionLineaire, dossier_modeles


class PanneauPrediction(QWidget):
    """
    Panneau sous les decks : choix du modèle, winrate des deux joueurs, bouton Prédire et résultat.
    Il lit les cartes et les niveaux directement dans les deux DeckPanel.
    """
    def __init__(self, deck_panel_a, deck_panel_b):
        super().__init__()
        self.deck_panel_a = deck_panel_a
        self.deck_panel_b = deck_panel_b
        # Les modèles déjà chargés, pour ne pas relire le fichier à chaque prédiction
        self.modeles = {}

        layout = QGridLayout(self)

        # Première ligne, le choix du modèle
        layout.addWidget(QLabel("Modèle :"), 0, 0)
        self.choix_modele = QComboBox()
        layout.addWidget(self.choix_modele, 0, 1, 1, 3)

        # Deuxième ligne, le winrate des deux joueurs
        layout.addWidget(QLabel("Winrate joueur A :"), 1, 0)
        self.winrate_a = self.creer_winrate()
        layout.addWidget(self.winrate_a, 1, 1)
        layout.addWidget(QLabel("Winrate joueur B :"), 1, 2)
        self.winrate_b = self.creer_winrate()
        layout.addWidget(self.winrate_b, 1, 3)

        # Troisième lige, le bouton pour prédire
        self.bouton_predire = QPushButton("Prédire")
        self.bouton_predire.clicked.connect(self.predire)
        layout.addWidget(self.bouton_predire, 2, 0, 1, 4)

        # La quartrième ligne pour les messages d'erreurs et les résultats
        self.resultat = QLabel("Mets 8 cartes dans chaque deck, puis clique sur Prédire.")
        self.resultat.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.resultat.setWordWrap(True)
        layout.addWidget(self.resultat, 4, 0, 1, 4)

        self.remplir_modeles()

    @staticmethod
    def creer_winrate():
        """
        Une case pour entrer un winrate en pourcentage (50 % par défaut).
        Retourne le winrate
        """
        winrate = QSpinBox()
        winrate.setRange(0, 100)
        winrate.setValue(50)
        winrate.setSuffix(" %")
        return winrate

    def remplir_modeles(self):
        """Met dans la liste tous les fichiers .joblib du dossier des modèles"""
        fichiers = glob.glob(os.path.join(dossier_modeles, "*.joblib"))
        # Trier par longueur puis par nom met regression_5000 avant regression_20000
        for fichier in sorted(fichiers, key=lambda f: (len(f), f)):
            nom = os.path.splitext(os.path.basename(fichier))[0]
            self.choix_modele.addItem(nom, fichier)

        if self.choix_modele.count() == 0:
            self.choix_modele.addItem("Aucun modèle : entraîne-en un d'abord")
            self.bouton_predire.setEnabled(False)

    def modele_choisi(self) -> RegressionLineaire:
        """Charge le modèle choisi la première fois, puis le garde en mémoire."""
        fichier = self.choix_modele.currentData()
        if fichier not in self.modeles:
            self.modeles[fichier] = RegressionLineaire.load(fichier)
        return self.modeles[fichier]

    def predire(self):
        incomplets = [panel.titre for panel in (self.deck_panel_a, self.deck_panel_b) if not panel.est_complet()]
        if incomplets:
            self.resultat.setText(f"Deck incomplet : {incomplets}. Il faut 8 cartes dans chaque deck.")
            return

        cartes_a, niveaux_a = self.deck_panel_a.cartes_et_niveaux()
        cartes_b, niveaux_b = self.deck_panel_b.cartes_et_niveaux()
        modele = self.modele_choisi()

        # Les spinbox sont en %, le modèle a été entraîné avec des winrates entre 0 et 1, donc on les convertit.
        proba_a = modele.predict(self.winrate_a.value() / 100, cartes_a, niveaux_a,
                                 self.winrate_b.value() / 100, cartes_b, niveaux_b)

        favori = "Joueur A" if proba_a >= 0.5 else "Joueur B"
        self.resultat.setText(
            f"{favori} favori. A : {proba_a:.0%}, B : {1 - proba_a:.0%} "
            f"(modèle {modele.nom}, précision {modele.score:.1%})"
        )
