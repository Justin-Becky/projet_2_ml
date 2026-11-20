from PySide6.QtWidgets import (QVBoxLayout, QGridLayout, QLabel, QGraphicsOpacityEffect, QFrame, QTabWidget,
                               QPushButton, QHBoxLayout, QWidget)
from PySide6.QtCore import Signal
from PySide6.QtGui import QPixmap, Qt, QIcon
from prediction import PanneauPrediction
from config import CARTES
from scroll import scroll_area
from exceptions import DonneeInvalideError
from abc import ABCMeta, abstractmethod


class MetaCarteAbstraite(ABCMeta, type(QLabel)):
    """
    Métaclasse qui combine celle d'ABC et celle de Qt.
    QLabel a déjà sa propre métaclasse et Python n'en accepte qu'une par classe :
    sans cette combinaison, une classe ne peut pas hériter à la fois de QLabel et d'ABC.
    """


class CarteBase(QLabel, metaclass=MetaCarteAbstraite):
    """
    Classe parente abstraite de toutes les images de cartes : les cartes de la liste (Carte)
    et les cases du deck (CaseDeck).

    Elle garde le nom et l'index de la carte, sait trouver son image, gère le clic
    et fournit __str__ et __repr__. Chaque classe enfant doit redéfinir scale_pix,
    car chacune s'affiche à sa façon (polymorphisme).
    """
    # Signal envoyé au clic, avec le nom de la carte
    click = Signal(str)

    def __init__(self, nom: str | None, index: int | None):
        # Qt crée l'objet sans passer par la vérification d'ABC : on la refait nous-mêmes
        if type(self).__abstractmethods__:
            raise TypeError(f"{type(self).__name__} est abstraite : il faut redéfinir "
                            f"{', '.join(sorted(type(self).__abstractmethods__))}")
        super().__init__()
        self.nom = nom
        self.index = index
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def chemin_image(self) -> str:
        """Renvoie le chemin de l'image de la carte, ou de la case vide si la case n'a pas de carte."""
        if self.nom is None or self.nom == "case_vide":
            return "Images/case_vide.png"
        return f"Images/cartes_clash_royale/{self.nom}_{self.index}.png"

    def afficher_image(self, chemin: str, n: int) -> None:
        """Affiche l'image du chemin donné, redimensionnée à n pixels au maximum (proportions gardées)."""
        self.setPixmap(QPixmap(chemin).scaled(
            n, n, Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation))

    @abstractmethod
    def scale_pix(self, n: int = 100) -> None:
        """Affiche la carte à la taille n. Chaque classe enfant décide comment."""

    def mousePressEvent(self, event):
        """Au clic, envoie le signal click avec le nom de la carte."""
        self.click.emit(self.nom)
        super().mousePressEvent(event)

    def __str__(self) -> str:
        return f"{self.nom} (n° {self.index})"

    def __repr__(self) -> str:
        return f"{type(self).__name__}(nom={self.nom!r}, index={self.index!r})"


class Carte(CarteBase):
    """
    Carte de la liste en bas de l'onglet Prédiction : grossit au survol, devient grise quand
    elle est dans le deck actif. Une carte « phantom » est invisible et sert seulement à réserver la place.
    """
    # Les signaux pour prévenir le deck du survol, ils envoient la carte elle-même
    entree = Signal(QLabel)
    sortie = Signal(QLabel)

    def __init__(self, nom: str, index: int, phantom: bool = False):
        super().__init__(nom, index)
        self.phantom = phantom
        self.gris = False
        self.scale_pix()

        if self.phantom:
            self.effet = QGraphicsOpacityEffect()
            self.effet.setOpacity(0.0)
            self.setGraphicsEffect(self.effet)

    def switch_gris(self):
        """Affiche la carte en gris si self.gris est vrai, en couleur sinon."""
        if self.gris:
            pixmap_grise = QIcon(self.pixmap()).pixmap(self.pixmap().size(), QIcon.Mode.Disabled)
            self.setPixmap(pixmap_grise)
        else:
            pixmap = QIcon(self.pixmap()).pixmap(self.pixmap().size(), QIcon.Mode.Active)
            self.setPixmap(pixmap)

    def scale_pix(self, n: int = 100):
        """Redéfinie : taille fixe de 120 pour un phantom, puis applique le gris si besoin."""
        if self.phantom:
            n = 120
        self.afficher_image(self.chemin_image(), n)
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
        """Un phantom ne réagit pas au clic ; sinon, même comportement que CarteBase."""
        if self.phantom:
            return
        super().mousePressEvent(event)

    def __str__(self) -> str:
        return super().__str__() + (" (grisée)" if self.gris else "")


class CaseDeck(CarteBase):
    """Une des 8 cases du deck : affiche une carte (ou la case vide) et garde son niveau."""

    def __init__(self, nom: str, index: int, setup: bool = False):
        super().__init__(nom, index)
        self.niveau = 11
        self.controle = None
        if setup:
            self.set_up_case_vide()
        else:
            self.scale_pix()

    def scale_pix(self, n: int = 115):
        """Redéfinie : simple affichage, sans gris ni phantom."""
        self.afficher_image(self.chemin_image(), n)

    def set_up_case_vide(self, n: int = 120):
        """Affiche l'image de la case vide, un peu plus grande."""
        self.afficher_image("Images/case_vide.png", n)

    def __str__(self) -> str:
        return f"{super().__str__()}, niveau {self.niveau}"


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
        self.deck_panel_a, self.deck_panel_b, self.tab_widget = self.creer_deck_panel()
        self.deck_panel = self.deck_panel_a
        self.panneau_prediction = PanneauPrediction(self.deck_panel_a, self.deck_panel_b)
        self.layout().addWidget(self.panneau_prediction)
        self.addWidget(scroll)

        # Pour pouvoir griser les cartes qui sont dans le deck
        self.cartes = {}

        self.creer_cartes()
        self.tab_widget.currentChanged.connect(self.deck_panel_switch)

    def deck_panel_switch(self, index):
        """
        Appelée quand on change d'onglet, index est l'onglet sélectionné.
        change le deck du deck_panel pour celui de l'onglet et gère le grise des cartes qui sont dans le deck actif.
        """
        self.deck_panel = self.deck_panel_a if index == 0 else self.deck_panel_b
        not_deck_panel = self.deck_panel_b if index == 0 else self.deck_panel_a

        for carte in not_deck_panel.deck.values():
            if carte is not None:
                carte = self.cartes[carte.nom]
                carte.gris = False
                carte.switch_gris()
                carte.scale_pix()

        for carte in self.deck_panel.deck.values():
            if carte is not None:
                carte = self.cartes[carte.nom]
                carte.gris = True
                carte.switch_gris()
                carte.scale_pix()

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
            carte.click.connect(self.ajouter_carte)
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
        tab_widget = QTabWidget()
        deck_panel_a = DeckPanel(self, titre="Joueur A")
        deck_panel_b = DeckPanel(self, titre="Joueur B")
        tab_widget.addTab(deck_panel_a, deck_panel_a.titre)
        tab_widget.addTab(deck_panel_b, deck_panel_b.titre)
        self.layout_deck.addWidget(tab_widget)
        return deck_panel_a, deck_panel_b, tab_widget

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

    def ajouter_carte(self, nom):
        """
        Envoie la carte au deck actif au moment du clic.
        """
        self.deck_panel.rajouter(nom)


class DeckPanel(QFrame):
    def __init__(self, parent: CreationDeck, titre: str):
        super().__init__()
        self.parent = parent
        self.titre = titre
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

    def est_complet(self) -> bool:
        """Vrai si les 8 cases du deck ont une carte."""
        return all(carte is not None for carte in self.deck.values())

    def cartes_et_niveaux(self) -> tuple:
        """
        retourne Les index des cartes et leurs niveaux en tuple.
        """
        if not self.est_complet():
            raise DonneeInvalideError(f"{self.titre} : il faut 8 cartes dans le deck.")
        cartes = [carte.index for carte in self.deck.values()]
        niveaux = [carte.niveau for carte in self.deck.values()]
        return cartes, niveaux

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

                carte.controle = ControleNiveau(carte)
                self.grille.addWidget(carte.controle, i // 4, i % 4,
                                      Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter)
                break

    def enlever(self, index, carte):
        if carte in self.deck.values():
            self.parent.cartes[carte.nom].gris = False
            self.parent.cartes[carte.nom].switch_gris()
            self.parent.cartes[carte.nom].scale_pix()
            self.grille.removeWidget(carte.controle)
            carte.controle.deleteLater()
            carte.deleteLater()
            self.grille.removeWidget(carte)
            self.deck[index] = None


class ControleNiveau(QWidget):
    """
    Les petits boutons ◀ niveau ▶ affichés sous une carte du deck.
    Ils changent directement carte.niveau, entre NIVEAU_MIN et NIVEAU_MAX.
    """
    def __init__(self, carte: CaseDeck):
        super().__init__()
        self.carte = carte

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        btn_g = QPushButton("◀")
        btn_d = QPushButton("▶")
        for btn in (btn_g, btn_d):
            btn.setFixedWidth(18)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("background-color: transparent;")
        btn_g.clicked.connect(self.baisser)
        btn_d.clicked.connect(self.monter)

        self.label = QLabel(str(carte.niveau))
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("background-color: rgba(0, 0, 0, 150); color: white; "
                                 "font-weight: bold; padding: 0px 4px;")

        layout.addWidget(btn_g)
        layout.addWidget(self.label)
        layout.addWidget(btn_d)

    def changer_niveau(self, changement: int):
        nouveau = self.carte.niveau + changement
        self.carte.niveau = max(1, min(16, nouveau))
        self.label.setText(str(self.carte.niveau))

    def baisser(self):
        self.changer_niveau(-1)

    def monter(self):
        self.changer_niveau(1)
