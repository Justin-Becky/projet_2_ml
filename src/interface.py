from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMainWindow, QApplication, QHBoxLayout, QWidget, QLabel, QTabWidget, QVBoxLayout

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

        # <editor-fold desc="Variables">
        self.data = None  # Les données
        # </editor-fold>

        # <editor-fold desc="Layout">
        self.widget_principal = QWidget()
        self.setCentralWidget(self.widget_principal)
        self.tabs, self.layout_principal = MainWindow.setup_layout(self.widget_principal)
        self.setup_tabs(self.tabs, TABS_NAME)
        # </editor-fold>

    @staticmethod
    def setup_layout(widget_principal: QWidget = None, *args) -> (QTabWidget, QVBoxLayout):
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


if __name__ == "__main__":
    app = QApplication()
    main_window = MainWindow()
    main_window.show()
    app.exec()
