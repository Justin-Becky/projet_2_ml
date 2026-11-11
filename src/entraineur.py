from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QGraphicsOpacityEffect, QFrame, QWidget, \
    QComboBox, QPushButton
from PySide6.QtCore import Signal
from PySide6.QtGui import QPixmap, Qt, QIcon, QFont
from config import MODELS

class Entraineur(QVBoxLayout):
    def __init__(self):
        super().__init__()
        self.current_model = None

        self.time_label = QLabel()
        self.line_num_label = QLabel()
        self.score_label = QLabel()
        self.name_label = QLabel()
        self.model_select = QComboBox()

        self.train_font = QFont()
        self.train_font.setPointSize(50)

        self.data_font = QFont()
        self.data_font.setPointSize(15)

        self.time_label.setFont(self.data_font)
        self.line_num_label.setFont(self.data_font)
        self.score_label.setFont(self.data_font)
        self.name_label.setFont(self.data_font)

        self.top_layout = QHBoxLayout()
        self.top_layout.addLayout(self.create_model_layout())
        self.top_layout.addLayout(self.create_comparison())
        self.addLayout(self.top_layout)
        self.addWidget(self.create_train_button())
        self.model_select.currentIndexChanged.connect(self.update_stats)


    def create_model_layout(self):
        model_layout = QVBoxLayout()
        for model in MODELS:
            self.model_select.addItem(model)


        font = QFont()
        font.setBold(True)
        font.setPointSize(20)

        self.model_select.setFixedSize(200, 60)
        self.model_select.setFont(font)

        choose_model_title = QLabel('CHOSE MODEL')
        stats_label = QLabel('STATS')

        choose_model_title.setFont(font)
        stats_label.setFont(font)

        model_layout.addWidget(choose_model_title)
        model_layout.addWidget(self.model_select)
        model_layout.addWidget(stats_label)
        model_layout.addLayout(self.create_stats())
        return model_layout

    def create_stats(self):
        stats = QVBoxLayout()
        stats.addLayout(self.create_stat('Name', self.name_label))
        stats.addLayout(self.create_stat('Temps', self.time_label))
        stats.addLayout(self.create_stat('Nb. lignes', self.line_num_label))
        stats.addLayout(self.create_stat('Score', self.score_label))
        return stats

    def create_stat(self, stat_name:str, data):
        layout = QVBoxLayout()
        name_label = QLabel(f'{stat_name} :')
        name_label.setFont(self.data_font)
        layout.addWidget(name_label)
        layout.addWidget(data)
        return layout

    def update_stats(self):
        self.name_label.setText(self.model_select.currentText())
        self.time_label.setText('4')
        self.line_num_label.setText('5')
        self.score_label.setText('0')

    def create_comparison(self):
        comp_layout = QGridLayout()
        for model in MODELS:
            if model != self.model_select.currentText():
                comp_layout.addWidget(self.create_comp_graph(model))

        return comp_layout

    def create_comp_graph(self, model):
        return QLabel('graphic interessant')

    def create_train_button(self):
        train_button = QPushButton('TRAIN')
        train_button.setFont(self.train_font)
        train_button.setFixedHeight(120)

        return train_button