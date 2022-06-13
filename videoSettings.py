from PyQt6.QtWidgets import QWidget, QSlider, QLineEdit, QGridLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDoubleValidator

class videoSettings(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QLineEdit#dimensions {
                border: none;
                background: transparent;
                color: blue;
            }
        """)

        self.initUI()

    def initUI(self):
        self.layout = QGridLayout()

        self.thresholdLabel = QLabel("Similarity threshold:")
        self.thresholdEdit = QLineEdit()
        self.thresholdEdit.setPlaceholderText("0.00 - 100.00")
        self.thresholdEdit.setValidator(QDoubleValidator())
        self.thresholdSlider = QSlider(Qt.Orientation.Horizontal)
        self.thresholdSlider.setMinimum(0.00)
        self.thresholdSlider.setMaximum(100.00)

        self.sliceDurationLabel = QLabel("Slice duration:")
        self.sliceDurationEdit = QLineEdit()
        self.sliceDurationEdit.setPlaceholderText("seconds")

        self.compareLabel = QLabel("Comparison dimensions:")
        self.compareWidth = QLineEdit("1920")
        self.compareWidth.setObjectName("dimensions")
        self.compareHeight = QLineEdit("1080")
        self.compareHeight.setObjectName("dimensions")

        self.layout.addWidget(self.thresholdLabel, 0, 0, 1, 1)
        self.layout.addWidget(self.thresholdEdit, 0, 1, 1, 1)
        self.layout.addWidget(self.thresholdSlider, 0, 2, 1, 3)
        self.layout.addWidget(self.sliceDurationLabel, 1, 0, 1, 1)
        self.layout.addWidget(self.sliceDurationEdit, 1, 1, 1, 1)
        self.layout.addWidget(self.compareLabel, 2, 0, 2, 1, Qt.AlignmentFlag.AlignVCenter)
        self.layout.addWidget(self.compareWidth, 2, 1, 1, 1)
        self.layout.addWidget(self.compareHeight, 3, 1, 1, 1)

        self.setLayout(self.layout)



        