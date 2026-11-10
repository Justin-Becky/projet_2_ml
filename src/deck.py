from PySide6.QtWidgets import QVBoxLayout, QGridLayout, QLabel, QGraphicsOpacityEffect, QFrame
from PySide6.QtCore import Signal
from PySide6.QtGui import QPixmap, Qt, QIcon

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

        # Pour pouvoir griser les cartes qui sont dans le deck
        self.cartes = {}

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
            self.cartes[nom] = carte
            carte.entree.connect(self.survol)
            carte.sortie.connect(self.sortie)
            carte.click.connect(self.deck_panel.rajouter)
            carte_phantom = Carte(nom, index, phantom=True)
            self.contenu_layout.addWidget(carte_phantom, i, j)
            self.contenu_layout.addWidget(carte, i, j)

            if j == 3:
                i += 1

    def creer_deck_panel(self):
        """
        Créer le deck panel et le rajout au layout

        Retourne le DeckPanel
        """
        deck_panel = DeckPanel(self)
        self.layout_deck.addWidget(deck_panel)
        return deck_panel

    @staticmethod
    def survol(carte):
        """
        prend en paramètre la Carte qui a été survolé par la souris et la fait grossir.
        """
        carte.scale_pix(120)

    @staticmethod
    def sortie(carte):
        """
        prend en paramètre la Carte qui n'est plus survolée par la souris et la fait revenir à sa grosseur de base.
        """
        carte.scale_pix()


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
        self.gris = False

        self.scale_pix()
        self.setCursor(Qt.CursorShape.PointingHandCursor)  # petite main au survol
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Centre la carte et son phantom

        if self.phantom:
            self.effet = QGraphicsOpacityEffect()
            self.effet.setOpacity(0.0)
            self.setGraphicsEffect(self.effet)

    def switch_gris(self):
        if self.gris:
            pixmap_grise = QIcon(self.pixmap()).pixmap(self.pixmap().size(), QIcon.Mode.Disabled)
            self.setPixmap(pixmap_grise)
        else:
            pixmap_grise = QIcon(self.pixmap()).pixmap(self.pixmap().size(), QIcon.Mode.Active)
            self.setPixmap(pixmap_grise)

    def scale_pix(self, n: int = 100):
        if self.phantom:
            n = 120
        self.setPixmap(QPixmap(f"Images/cartes_clash_royale/{self.nom}_{self.index}.png").scaled(
            n, n, Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation))
        self.switch_gris()

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
    def __init__(self, nom, index, setup: bool = False):
        super().__init__(None, None)
        self.nom = nom
        self.index = index
        if setup:
            self.set_up_case_vide()
        else:
            self.scale_pix()

    def scale_pix(self, n: int = 115):
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
    def __init__(self, parent: CreationDeck):
        super().__init__()
        self.parent = parent
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

    @staticmethod
    def is_evo_hero(carte):
        is_evo = False
        is_hero = False
        if carte.nom.split(" ")[0] == "evo":
            is_evo = True
        elif carte.nom.split(" ")[0] == "hero":
            is_hero = True

        return is_evo, is_hero

    def rajouter(self, nom):
        carte = CaseDeck(nom, CARTES[nom])
        carte.click.connect(self.rajouter)
        for index, case in self.deck.items():
            if case is not None and case.nom == nom:
                self.enlever(index, case)
                return

        is_evo, is_hero = self.is_evo_hero(carte)

        for i, carte_in in self.deck.items():
            i = int(i)
            if is_evo and i > 1:
                break
            elif is_hero and (i == 0 or i > 2):
                continue

            if carte_in is None:
                self.parent.cartes[nom].gris = True
                self.parent.cartes[nom].switch_gris()
                self.grille.addWidget(carte, i // 4, i % 4)
                self.deck[str(i)] = carte
                break

    def enlever(self, index, carte):
        if carte in self.deck.values():
            self.parent.cartes[carte.nom].gris = False
            self.parent.cartes[carte.nom].switch_gris()
            self.parent.cartes[carte.nom].scale_pix()

            carte.deleteLater()
            self.grille.removeWidget(carte)
            self.deck[index] = None
