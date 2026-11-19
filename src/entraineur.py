import random
from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
                               QComboBox, QPushButton, QFrame, QWidget)
from PySide6.QtCore import Qt, QPropertyAnimation, QPoint
from PySide6.QtGui import QPixmap, QFont, QPainter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib import category

import modele
from donnees import *
from config import TRAIN_IMAGES
from modele import RegressionLineaire, lister_modeles, lire_metadonnees
import qt_themes

MODELS = []
mod_temp = modele.lister_modeles()
for mod in mod_temp:
    MODELS.append(lire_metadonnees(mod))

class Entraineur(QVBoxLayout):
    def __init__(self):
        super().__init__()
        qt_themes.set_theme('one_dark_two')
        self.current_model = MODELS[0]
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
        self.time_label.setText(str(self.current_model['temps_entrainement']))
        self.line_num_label.setText(str(self.current_model['nb_lignes']))
        self.score_label.setText(str(self.current_model['score']))

    def create_comparison(self):
        comp_layout = QVBoxLayout()
        comp_layout.setSpacing(8)

        comp_title = QLabel('COMPARAISON')
        comp_title.setFont(self.title_font)
        comp_layout.addWidget(comp_title)

        grid = QGridLayout()
        grid.setSpacing(10)
        others = [m for m in MODELS if m != self.model_select.currentData()]
        for i, model in enumerate(others):
            grid.addLayout(self.create_comp_graph(model), i // 2, i % 2)
        comp_layout.addLayout(grid, 1)
        return comp_layout

    def create_comp_graph(self, model):
        layout = QVBoxLayout()
        layout.setSpacing(4)

        title = QLabel(f'{self.model_select.currentText()} \\ {model['nom']}')
        title.setFont(self.data_font)


        categories = ['Score', 'Temps d entrainement']

        model_values = {}
        for mod in MODELS:
            model_values[mod['nom']] = (mod['score'], mod['temps_entrainement'])
        fig, ax = plt.subplots(layout='constrained')

        res = ax.grouped_bar(model_values, tick_labels=categories, group_spacing=1)

        ax.legend()
        graph = FigureCanvasQTAgg(fig)
#        graph.setFrameShape(QFrame.Shape.Box)
#        graph.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(title)
        layout.addWidget(graph, 1)
        return layout

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
