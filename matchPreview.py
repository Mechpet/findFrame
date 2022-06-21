from PyQt6.QtWidgets import QWidget, QLabel, QProgressBar, QGridLayout, QSizePolicy
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QImage, QPixmap

class matchPreview(QWidget):
    def __init__(self):
        super().__init__()
        
        self.initUI()

    def initUI(self):
        layout = QGridLayout()
        self.status = QLabel("Matching video captures...")
        self.sourceImage = QLabel("")
        self.sourceImage.resize(320, 240)
        self.targetImage = QLabel("")
        self.targetImage.resize(320, 240)
        self.progress = QProgressBar()
        self.progress.setMaximum(100)
        self.progress.setValue(0)
        layout.addWidget(self.status, 0, 0, 1, -1)
        layout.addWidget(self.sourceImage, 1, 0, 4, 5)
        layout.addWidget(self.targetImage, 1, 5, 4, 5)
        layout.addWidget(self.progress, 5, 0, 1, -1)
        self.setLayout(layout)

    @pyqtSlot(float)
    def updateValue(self, value):
        print("UPDATE VALUE")
        self.progress.setValue(value)

    @pyqtSlot(str)
    def updateStatus(self, newStatus):
        self.status.setText(newStatus)

    @pyqtSlot(QImage)
    def setSource(self, image):
        print("UPDATE SOURCE")
        self.sourceImage.setPixmap(QPixmap.fromImage(image))
        print("DONE")

    @pyqtSlot(QImage)
    def setTarget(self, image):
        print("UPDATE TARGET")
        self.targetImage.setPixmap(QPixmap.fromImage(image))
        print("DONE")
