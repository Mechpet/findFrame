from PyQt6.QtWidgets import QWidget, QGridLayout, QLabel, QStackedWidget
from PyQt6.QtCore import pyqtSlot

from matchPreview import matchPreview

class progressPreview(QWidget):
    def __init__(self):
        super().__init__()
        
        self.initUI()

    def initUI(self):
        layout = QGridLayout()

        self.stack = QStackedWidget()

        self.match = matchPreview()
        self.stack.addWidget(self.match)
        self.stack.setCurrentWidget(self.match)

        layout.addWidget(self.stack, 0, 0)
        self.setLayout(layout)
