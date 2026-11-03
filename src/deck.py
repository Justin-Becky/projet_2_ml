from PySide6.QtWidgets import QVBoxLayout, QGridLayout, QLabel, QGraphicsOpacityEffect, QFrame
from PySide6.QtCore import Signal
from PySide6.QtGui import QPixmap, Qt

from config import CARTES
from scroll import scroll_area


class CreationDeck(QVBoxLayout):
    """
    Cette classe crée un layout qui contient les deux emplacements pour créer le deck du joueur A et celui du Joueur B
    avec en bas, toutes les cartes de clash royal pour qu'ils puissent faire leur deck (joueur A) et celui de leur
    adversaire (joueur B).

    Retourne QVBoxLayout
    """
    def __init__(self):
        super().__init__()
        # Le deck du joueur la position: le numéro de la carte
        scroll, self.contenu_layout = scroll_area(layout=QGridLayout())
        self.layout_deck = QVBoxLayout()
        self.addLayout(self.layout_deck)
        self.addWidget(scroll)

        self.deck_panel = self.creer_deck_panel()
        self.creer_cartes()

    def creer_cartes(self):
        """
        Prend chaque carte de clash royal (dans CARTES) avec leur index et mets leur image dans un QGridLayout quatre
        par ligne.

        Retourne None
        """
        i = 0
        for nom, index in CARTES.items():
            j = index % 4
            carte = Carte(nom, index)
            carte.entree.connect(self.survol)
            carte.sortie.connect(self.sortie)
            carte.click.connect(self.mettre_carte)
            carte_phantom = Carte(nom, index, phantom=True)
            self.contenu_layout.addWidget(carte_phantom, i, j)
            self.contenu_layout.addWidget(carte, i, j)

            if j == 3:
                i += 1

    def creer_deck_panel(self):
        deck_panel = DeckPanel()
        self.layout_deck.addWidget(deck_panel)
        return deck_panel

    @staticmethod
    def survol(carte):
        carte.scale_pix(120)

    @staticmethod
    def sortie(carte):
        carte.scale_pix()

    def mettre_carte(self, nom: str):
        self.deck_panel.rajouter(nom)
        # Todo : faire que la carte devienne grise et qu'en re-clickant dessus on puisse l'enlever du deck

    def enlever_carte(self, index: int):
        pass


class Carte(QLabel):
    # Les signaux pour prévenir le deck, il retourne l'index de la carte
    entree = Signal(QLabel)
    sortie = Signal(QLabel)
    click = Signal(str)

    def __init__(self, nom, index, phantom: bool = False):
        super().__init__()
        self.phantom = phantom
        self.nom = nom
        self.index = index
        self.scale_pix()
        self.setCursor(Qt.CursorShape.PointingHandCursor)  # petite main au survol
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Centre la carte et son phantom

        if self.phantom:
            self.effet = QGraphicsOpacityEffect()
            self.effet.setOpacity(0.0)
            self.setGraphicsEffect(self.effet)

    def scale_pix(self, n: int = 100):
        if self.phantom:
            n = 120
        self.setPixmap(QPixmap(f"Images/cartes_clash_royale/{self.nom}_{self.index}.png").scaled(
            n, n, Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation))

    def enterEvent(self, event):
        if self.phantom:
            return
        self.entree.emit(self)
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self.phantom:
            return
        self.sortie.emit(self)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if self.phantom:
            return
        self.click.emit(self.nom)
        super().mousePressEvent(event)


class CaseDeck(Carte):

    retirer = Signal(int)

    def __init__(self, nom, index, setup: bool = False):
        super().__init__(None, None)
        self.nom = nom
        self.index = index
        if setup:
            self.set_up_case_vide()
        else:
            self.scale_pix()

    def scale_pix(self, n: int = 120):
        if self.nom is None:
            self.setPixmap(QPixmap("Images/case_vide.png").scaled(
                n, n, Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation))
        else:
            self.setPixmap(QPixmap(f"Images/cartes_clash_royale/{self.nom}_{self.index}.png").scaled(
                n, n, Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation))

    def set_up_case_vide(self, n: int = 120):
        self.setPixmap(QPixmap("Images/case_vide.png").scaled(
            n, n, Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation))


class DeckPanel(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameStyle(QFrame.Shape.Panel | QFrame.Shadow.Raised)
        self.setLineWidth(3)
        self.grille = QGridLayout()
        self.setLayout(self.grille)
        self.deck = {"0": None, "1": None, "2": None, "3": None, "4": None, "5": None, "6": None, "7": None}
        self.setup_panel()

    def setup_panel(self):
        i = 0
        for j, carte in self.deck.items():
            j = int(j) % 4
            carte = CaseDeck("case_vide", -1, setup=True)
            self.grille.addWidget(carte, i, j)

            if j == 3:
                i += 1

    def rajouter(self, nom):
        for i, carte in self.deck.items():
            i = int(i)
            if carte is None:
                carte = CaseDeck(nom, CARTES[nom])
                self.grille.addWidget(carte, i // 4, i % 4)
                self.deck[str(i)] = carte
                break

    def enlever(self):
        pass
