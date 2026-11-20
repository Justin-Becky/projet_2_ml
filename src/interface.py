
from PySide6.QtGui import QIcon, Qt
from PySide6.QtWidgets import QMainWindow, QApplication, QHBoxLayout, QWidget, QTabWidget
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pandas as pd
from config import TABS_NAME, COLONNES_NIVEAUX, FICHIER_FINALE
from scroll import scroll_area
from deck import CreationDeck
from entraineur import Entraineur


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # <editor-fold desc="Titre et Icon">
        self.window_icon = QIcon("Images/window_icon")
        self.setWindowIcon(self.window_icon)
        self.window_name = "Projet 2 Machine Learning"
        self.setWindowTitle(self.window_name)
        # </editor-fold>

        # <editor-fold desc="Layout">
        self.widget_principal = QWidget()
        self.setCentralWidget(self.widget_principal)
        self.tabs = QTabWidget()
        self.tabs_widget = self.setup_tabs(self.tabs, TABS_NAME)
        self.layout_principal = self.setup_layout(self.widget_principal)
        # </editor-fold>

    def setup_layout(self, widget_principal: QWidget = None) -> QHBoxLayout | None:
        """
        prend un widget_principal

        Construit un layout horizontal contenant QTabWidget() (un widget qui permet d'avoir plusieurs tabs et de se
        déplacer de l'un à l'autre) à gauche et un QVBoxLayout() à droite.

        Met le layout horizontal dans le widget_principal

        Il retourne le QTabWidget et le QVBoxLayout
        """
        if widget_principal is None:
            return None

        layout = QHBoxLayout()

        scroll, contenu_layout = scroll_area()
        self.tabs.addTab(scroll, "Comparaison joueur")

        for _ in range(2):
            canevas = Canevas()
            canevas.setMinimumHeight(500)
            contenu_layout.addWidget(canevas)

        layout.addWidget(self.tabs)
        widget_principal.setLayout(layout)
        return layout

    @staticmethod
    def setup_tabs(tab_widget: QTabWidget, tabs_rajouter: list):
        """
        Prend en paramètre tab_widget un QTabWidget et lui rajoute les tabs de la liste tabs_rajouter avec chacun le nom
        comme titre et un QVBoxLayout

        Retourne None
        """
        for tab in tabs_rajouter:
            widget = QWidget()
            layout = CreationDeck() if tab == "Prédiction" else Entraineur()
            widget.setLayout(layout)

            if tab == "Prédiction":
                widget.setMaximumSize(600, 1000)
                # La page de l'onglet est un conteneur qui centre le widget horizontalement
                page = QWidget()
                layout_page = QHBoxLayout(page)
                layout_page.addWidget(widget, alignment=Qt.AlignmentFlag.AlignHCenter)
                tab_widget.addTab(page, tab)
            else:
                tab_widget.addTab(widget, tab)

        return tab_widget


class Canevas(FigureCanvas):
    def __init__(self, graphique=None):
        super().__init__()
        if graphique is None:
            self.creer_graphique_exemple()

    def creer_graphique_exemple(self):
        """
        Cette fonction va prendre l'id du gagnant et du perdant des dix premières parties et compare
        le niveau moyen de ces cartes avec un diagramme à bande. Avant de rajouter ce graphique au canevas.

        Retourne None
        """
        # les titres des colonnes qu'on a besoin, soit l'id des gagnants, des perdants et le niveau de chaque carte
        # du gagnant et du perdant.
        colonnes = ["Joueur_A", "Joueur_B"] + COLONNES_NIVEAUX

        # Les dix premières lignes des colonnes voulues
        df = pd.read_parquet(FICHIER_FINALE, columns=colonnes).head(10)

        colonnes_loser = [f"Joueur_A_niveau_carte_{i}" for i in range(1, 9)]
        colonnes_winner = [f"Joueur_B_niveau_carte_{i}" for i in range(1, 9)]

        df_graphique = pd.DataFrame({
            "match": df["Joueur_A"].astype(str) + "/" + df["Joueur_B"].astype(str),
            "Gagnant": df[colonnes_winner].mean(axis=1),  # calcul la moyenne des cartes du gagnant
            "Perdant": df[colonnes_loser].mean(axis=1),  # calcul la moyenne des cartes du perdant
        })

        figure = Figure(figsize=(5, 5))
        self.figure = figure
        ax = figure.add_subplot()

        df_graphique.plot(x="match", kind="bar", ax=ax, rot=45)
        ax.set_ylabel("Niveau moyen des cartes")
        ax.set_title("Niveau moyen : gagnant vs perdant")
        figure.tight_layout()

    def wheelEvent(self, event):
        # Ignore le wheelEvent pour le laisser au QScrollArea
        event.ignore()


if __name__ == "__main__":
    app = QApplication()
    main_window = MainWindow()
    main_window.show()
    app.exec()
