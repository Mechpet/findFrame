from PyQt6.QtWidgets import QWidget, QGridLayout, QLabel, QLineEdit, QPushButton, QScrollArea
from PyQt6.QtCore import Qt

from target import targetHeader
from targetList import targetList

# Constants:
sourceLabelColumnSpan = 3
sourceInputColumnSpan = 6

class captureEditor(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.layout = QGridLayout()

        self.sourceLabel = QLabel("Source file")
        self.sourceLabel.setToolTip("Primary video file to take slices out of.")
        self.sourceInput = QLineEdit()
        self.sourceBrowser = QPushButton("Browse")
        self.targetList = targetList()

        self.targetHeader = targetHeader()

        self.targetListScroll = QScrollArea()
        self.targetListScroll.setWidget(self.targetList)
        self.targetListScroll.setWidgetResizable(True)
        self.targetListScroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.targetListScroll.horizontalScrollBar().setDisabled(True)

        self.layout.addWidget(self.sourceLabel, 0, 0, 1, sourceLabelColumnSpan)
        self.layout.addWidget(self.sourceInput, 0, sourceLabelColumnSpan + 1, 1, sourceInputColumnSpan)
        self.layout.addWidget(self.sourceBrowser, 0, sourceLabelColumnSpan + sourceInputColumnSpan + 2, 1, 1)
        self.layout.addWidget(self.targetHeader, 1, 0, 1, -1)
        self.layout.addWidget(self.targetListScroll, 2, 0, 4, -1)

        self.setLayout(self.layout)