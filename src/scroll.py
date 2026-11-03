from PySide6.QtWidgets import QScrollArea, QWidget, QVBoxLayout
from PySide6.QtGui import Qt

def scroll_area(layout=None):
    if layout is None:
        layout = QVBoxLayout()
    # ── ScrollArea ──
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setHorizontalScrollBarPolicy(
        Qt.ScrollBarPolicy.ScrollBarAlwaysOff
    )
    scroll.setVerticalScrollBarPolicy(
        Qt.ScrollBarPolicy.ScrollBarAsNeeded
    )
    scroll.setFrameShape(QScrollArea.Shape.NoFrame)
    scroll.setStyleSheet("""
        QScrollArea {
            border: none; background: transparent;
            margin: 0px; padding: 0px;
        }
        QScrollArea > QWidget > QWidget { background: transparent; }
        QScrollBar:vertical {
            background: transparent;
            width: 6px;
            margin: 0px;
        }
        QScrollBar::handle:vertical {
            background: #FE6F88FF;
            border-radius: 3px;
            min-height: 20px;
        }
        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical { height: 0px; }
    """)
    scroll.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
    scroll.viewport().setAutoFillBackground(False)

    contenu = QWidget()
    contenu.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
    contenu.setAutoFillBackground(False)
    contenu_layout = layout
    contenu.setLayout(contenu_layout)
    contenu_layout.setContentsMargins(6, 0, 6, 10)
    contenu_layout.setSpacing(4)
    contenu_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
    scroll.setWidget(contenu)

    return scroll, contenu_layout
