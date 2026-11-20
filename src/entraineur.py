import random
import numpy as np
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QFrame
from PySide6.QtCore import Qt, QPropertyAnimation, QPoint, QThread, Signal
from PySide6.QtWidgets import QMessageBox
from PySide6.QtGui import QPixmap, QFont, QPainter
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg

import modele
from config import TRAIN_IMAGES
from modele import RegressionLineaire, lire_metadonnees
import qt_themes

MODELS = []
mod_temp = modele.lister_modeles()
for mod in mod_temp:
    MODELS.append(lire_metadonnees(mod))

class TrainWorker(QThread):
    termine = Signal(str)
    echec = Signal(str)

    def __init__(self, nom, nb_lignes):
        super().__init__()
        self.nom = nom
        self.nb_lignes = nb_lignes

    def run(self):
        try:
            RegressionLineaire.charger_ou_entrainer(self.nom, self.nb_lignes, forcer=True)
            self.termine.emit(self.nom)
        except Exception as e:
            self.echec.emit(str(e))

class Entraineur(QVBoxLayout):
    def __init__(self):
        super().__init__()
        self.cm_canvas = None
        self.cm_ax = None
        self.cm_fig = None
        qt_themes.set_theme('one_dark_two')
        self.current_model = MODELS[0]
        self.worker = None
        self.animation = None
        self.train_button = None

        self.time_label = QLabel()
        self.line_num_label = QLabel()
        self.score_label = QLabel()
        self.name_label = QLabel()
        self.model_select = QComboBox()

        self.train_font = QFont()
        self.train_font.setPointSize(50)

        self.data_font = QFont()
        self.data_font.setPointSize(15)

        self.title_font = QFont()
        self.title_font.setBold(True)
        self.title_font.setPointSize(20)

        self.time_label.setFont(self.data_font)
        self.line_num_label.setFont(self.data_font)
        self.score_label.setFont(self.data_font)
        self.name_label.setFont(self.data_font)

        self.setSpacing(10)

        self.top_layout = QHBoxLayout()
        self.top_layout.setSpacing(15)
        self.top_layout.addLayout(self.create_model_layout())
        self.top_layout.addWidget(self.create_divider())
        self.top_layout.addLayout(self.create_comparison(), 1)
        self.addLayout(self.top_layout, 1)
        self.addWidget(self.create_train_button())
        self.model_select.currentIndexChanged.connect(self.update_stats)

        self.update_stats()

    @staticmethod
    def create_divider():
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.VLine)
        return divider

    def create_model_layout(self):
        model_layout = QVBoxLayout()
        model_layout.setSpacing(8)
        for model in MODELS:
            self.model_select.addItem(model['nom'], model)

        self.model_select.setFixedSize(200, 60)
        self.model_select.setFont(self.title_font)

        choose_model_title = QLabel('CHOSE MODEL')
        stats_label = QLabel('STATS')

        choose_model_title.setFont(self.title_font)
        stats_label.setFont(self.title_font)

        model_layout.addWidget(choose_model_title)
        model_layout.addWidget(self.model_select)
        model_layout.addSpacing(10)
        model_layout.addWidget(stats_label)
        model_layout.addLayout(self.create_stats())
        model_layout.addStretch()
        return model_layout

    def create_stats(self):
        stats = QVBoxLayout()
        stats.setSpacing(8)
        stats.addLayout(self.create_stat('Name', self.name_label))
        stats.addLayout(self.create_stat('Temps', self.time_label))
        stats.addLayout(self.create_stat('Nb. lignes', self.line_num_label))
        stats.addLayout(self.create_stat('Score', self.score_label))
        return stats

    def create_stat(self, stat_name: str, data):
        layout = QVBoxLayout()
        layout.setSpacing(0)
        name_label = QLabel(f'{stat_name} :')
        name_label.setFont(self.data_font)
        layout.addWidget(name_label)
        layout.addWidget(data)
        return layout

    def update_stats(self):
        self.current_model = self.model_select.currentData()
        self.name_label.setText(self.current_model['nom'])
        self.time_label.setText(str(round(self.current_model['temps_entrainement'], 2)))
        self.line_num_label.setText(str(self.current_model['nb_lignes']))
        self.score_label.setText(str(round(self.current_model['score'] * 100, 2)) + " %")
        self.update_confusion()

    def create_comparison(self):
        comp_layout = QVBoxLayout()
        comp_layout.setSpacing(8)

        comp_title = QLabel('COMPARAISON')
        comp_title.setFont(self.title_font)
        comp_layout.addWidget(comp_title)

        grid = QVBoxLayout()
        grid.setSpacing(10)
        grid.addLayout(self.create_comp_graph())
        grid.addLayout(self.matrice_de_confusion())
        comp_layout.addLayout(grid, 1)
        return comp_layout

    def create_comp_graph(self):
        layout = QVBoxLayout()
        layout.setSpacing(4)

        title = QLabel(f'Comparaison des diférents modèles entraînés')
        title.setFont(self.data_font)

        categories = ['Score', 'Temps d entrainement']

        model_values = {}
        for model in MODELS:
            model_values[model['nom']] = (model['score'], model['temps_entrainement'])
        fig, ax = plt.subplots(layout='constrained')

        res = ax.grouped_bar(model_values, tick_labels=categories, group_spacing=1)

        ax.legend()
        graph = FigureCanvasQTAgg(fig)

        layout.addWidget(title)
        layout.addWidget(graph, 1)
        return layout

    def matrice_de_confusion(self):
        layout = QVBoxLayout()
        layout.setSpacing(4)

        title = QLabel('Matrice de confusion du modèle sélectionné')
        title.setFont(self.data_font)

        self.cm_fig = Figure(layout='constrained')
        self.cm_ax = self.cm_fig.add_subplot()
        self.cm_canvas = FigureCanvasQTAgg(self.cm_fig)

        layout.addWidget(title)
        layout.addWidget(self.cm_canvas, 1)
        return layout

    def update_confusion(self):
        ax = self.cm_ax
        ax.clear()

        matrice = self.current_model.get('matrice_confusion')
        if matrice is None:
            ax.set_axis_off()
            ax.text(0.5, 0.5, 'Matrice indisponible\n(réentraîne le modèle)',
                    ha='center', va='center', transform=ax.transAxes)
        else:
            ax.set_axis_on()
            m = np.array(matrice)
            ax.imshow(m, cmap='Blues')
            ax.set_xticks([0, 1], labels=['B gagne', 'A gagne'])
            ax.set_yticks([0, 1], labels=['B gagne', 'A gagne'])
            ax.set_xlabel('Prédit')
            ax.set_ylabel('Réel')

            seuil = m.max() / 2
            for i in range(2):
                for j in range(2):
                    ax.text(j, i, str(m[i, j]), ha='center', va='center', fontsize=16,
                            color='white' if m[i, j] > seuil else 'black')

        self.cm_canvas.draw_idle()

    def create_train_button(self):
        self.train_button = QPushButton('TRAIN')
        self.train_button.setFont(self.train_font)
        self.train_button.setFixedHeight(120)
        self.train_button.clicked.connect(self.train)
        return self.train_button

    @staticmethod
    def create_train():
        n = random.randint(1, 10)
        head = QPixmap(TRAIN_IMAGES[0])
        body = QPixmap(TRAIN_IMAGES[1])

        train_width = head.width() + n * body.width()
        train_height = max(head.height(), body.height())

        train = QPixmap(train_width, train_height)
        train.fill(Qt.GlobalColor.transparent)

        painter = QPainter(train)
        for i in range(n):
            painter.drawPixmap(i * body.width(), 0, body)
        painter.drawPixmap(n * body.width(), 0, head)
        painter.end()

        return train

    def train(self):
        if self.worker and self.worker.isRunning():
            return

        self.animer_train()
        self.train_button.setEnabled(False)

        self.worker = TrainWorker(self.current_model['nom'], self.current_model['nb_lignes'])
        self.worker.termine.connect(self.on_train_termine)
        self.worker.echec.connect(self.on_train_echec)
        self.worker.start()

    def animer_train(self):
        if self.animation and self.animation.state() == QPropertyAnimation.State.Running:
            return

        button = self.train_button
        pixmap = self.create_train()
        pixmap = pixmap.scaledToHeight(button.height(), Qt.TransformationMode.SmoothTransformation)

        train_label = QLabel(button)
        train_label.setPixmap(pixmap)
        train_label.resize(pixmap.size())
        train_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        y = (button.height() - pixmap.height()) // 2
        train_label.move(-pixmap.width(), y)
        train_label.show()

        self.animation = QPropertyAnimation(train_label, b"pos")
        self.animation.setDuration(3000)
        self.animation.setStartValue(QPoint(-pixmap.width(), y))
        self.animation.setEndValue(QPoint(button.width(), y))
        self.animation.finished.connect(train_label.deleteLater)
        self.animation.start()

    def on_train_termine(self, nom):
        meta = lire_metadonnees(nom)

        i = self.model_select.findText(nom)
        MODELS[i] = meta
        self.model_select.setItemData(i, meta)

        if self.model_select.currentIndex() == i:
            self.update_stats()  # met aussi à jour la matrice
        else:
            self.model_select.setCurrentIndex(i)

        self.train_button.setEnabled(True)

    def on_train_echec(self, message):
        self.train_button.setEnabled(True)
        QMessageBox.critical(self.train_button, 'Erreur d\'entraînement', message)
