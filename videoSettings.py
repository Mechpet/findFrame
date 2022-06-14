from PyQt6.QtWidgets import QWidget, QSlider, QLineEdit, QGridLayout, QLabel
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QDoubleValidator
import cv2

from videoChecker import videoValidity

class videoSettings(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QLineEdit#dimensions {
                color: blue;
            }
        """)

        self.capWidth = 0
        self.capHeight = 0

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

        self.compareWidth.editingFinished.connect(self.updateHeight)
        self.compareHeight.editingFinished.connect(self.updateWidth)

        self.thresholdSlider.valueChanged.connect(lambda: self.thresholdEdit.setText(str(self.thresholdSlider.value())))

        self.layout.addWidget(self.thresholdLabel, 0, 0, 1, 1)
        self.layout.addWidget(self.thresholdEdit, 0, 1, 1, 1)
        self.layout.addWidget(self.thresholdSlider, 0, 2, 1, 3)
        self.layout.addWidget(self.sliceDurationLabel, 1, 0, 1, 1)
        self.layout.addWidget(self.sliceDurationEdit, 1, 1, 1, 1)
        self.layout.addWidget(self.compareLabel, 2, 0, 2, 1, Qt.AlignmentFlag.AlignVCenter)
        self.layout.addWidget(self.compareWidth, 2, 1, 1, 1)
        self.layout.addWidget(self.compareHeight, 3, 1, 1, 1)

        self.setLayout(self.layout)

    @pyqtSlot(str)
    def setAspectRatio(self, path):
        """Sets the aspect ratio connected by the two dimensions given the path to a video file"""
        if videoValidity(path):
            # cv2 method:
            temp = cv2.VideoCapture(path)
            if temp.isOpened():
                self.capWidth = temp.get(cv2.CAP_PROP_FRAME_WIDTH)
                self.capHeight = temp.get(cv2.CAP_PROP_FRAME_HEIGHT)
            temp.release()

    def updateWidth(self):
        if self.capHeight and self.capWidth:
            if self.compareHeight.text():
                ratio = self.capWidth / self.capHeight
                self.compareWidth.setText(str(int(ratio * int(self.compareHeight.text()))))

    def updateHeight(self):
        if self.capHeight and self.capWidth:
            if self.compareWidth.text():
                ratio = self.capHeight / self.capWidth
                self.compareHeight.setText(str(int(ratio * int(self.compareWidth.text()))))