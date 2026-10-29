from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMainWindow, QApplication, QHBoxLayout, QWidget, QTabWidget, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pandas as pd

# winner_card_0_level ... winner_card_7_level et la même chose pour loser
COLONNES_NIVEAUX = [
    f"{joueur}_card_{i}_level"
    for joueur in ("winner", "loser")
    for i in range(8)
]

TABS_NAME = ["Entrainement", "Prédiction"]

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
        self.tabs, self.layout_principal = self.setup_layout(self.widget_principal)
        self.setup_tabs(self.tabs, TABS_NAME)
        # </editor-fold>

    @staticmethod
    def setup_layout(widget_principal: QWidget = None) -> (QTabWidget, QVBoxLayout):
        """
        prend un widget_principal

        Construit un layout horizontal contenant QTabWidget() (un widget qui permet d'avoir plusieurs tabs et de se
        déplacer de l'un à l'autre) à gauche et un QVBoxLayout() à droite.

        Met le layout horizontal dans le widget_principal

        Il retourne le QTabWidget et le QVBoxLayout
        """
        if widget_principal is None:
            return None, None

        layout = QHBoxLayout()

        tabs = QTabWidget()
        layout.addWidget(tabs)

        layout_graphique = QVBoxLayout()
        canevas = Canevas()
        layout_graphique.addWidget(canevas)
        layout.addLayout(layout_graphique)

        widget_principal.setLayout(layout)
        return tabs, layout_graphique

    @staticmethod
    def setup_tabs(tab_widget: QTabWidget, tabs_rajouter: list) -> None:
        """
        Prend en paramètre tab_widget un QTabWidget et lui rajoute les tabs de la liste tabs_rajouter avec chacun le nom
        comme titre et un QVBoxLayout

        Retourne None
        """
        for tab in tabs_rajouter:
            widget = QWidget()
            layout = QVBoxLayout()
            widget.setLayout(layout)
            tab_widget.addTab(widget, tab)


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
        colonnes = ["winner_id", "loser_id"] + COLONNES_NIVEAUX

        # Les dix premières lignes des colonnes voulues
        df = pd.read_parquet(
            "../donnees/2026-06-21_0.parquet", columns=colonnes).head(10)

        colonnes_loser = [f"loser_card_{i}_level" for i in range(8)]
        colonnes_winner = [f"winner_card_{i}_level" for i in range(8)]

        df_graphique = pd.DataFrame({
            "match": df["winner_id"].astype(str) + "/" + df["loser_id"].astype(str),
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


if __name__ == "__main__":
    app = QApplication()
    main_window = MainWindow()
    main_window.setFixedSize(800, 600)
    main_window.show()
    app.exec()
