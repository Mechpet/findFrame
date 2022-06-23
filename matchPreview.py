from PyQt6.QtWidgets import QWidget, QLabel, QProgressBar, QGridLayout, QStackedWidget
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QImage, QPixmap

class matchPreview(QWidget):
    def __init__(self):
        super().__init__()
        
        self.initUI()

    def initUI(self):
        layout = QGridLayout()
        self.status = QLabel("IDLE.")
        self.sourceImage = QLabel("")
        self.sourceImage.resize(320, 240)
        self.targetImage = QLabel("")
        self.targetImage.resize(320, 240)
        self.progress = QProgressBar()
        self.progress.setMaximum(100)
        self.progress.setValue(0)
        self.matchStatus = QStackedWidget()
        matchSuccess = QLabel("<font color = 'green'>Matched frames.</font>")
        matchFailure = QLabel("<font color = 'red'>Not a match.</font>")

        self.matchStatus.addWidget(matchFailure)
        self.matchStatus.addWidget(matchSuccess)
        self.matchStatus.setCurrentIndex(0)

        layout.addWidget(self.status, 0, 0, 1, -1)
        layout.addWidget(self.sourceImage, 1, 0, 4, 5)
        layout.addWidget(self.targetImage, 1, 5, 4, 5)
        layout.addWidget(self.matchStatus, 5, 0, 1, -1, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.progress, 6, 0, 1, -1)
        self.setLayout(layout)

    @pyqtSlot(float)
    def updateValue(self, value):
        self.progress.setValue(int(value))

    @pyqtSlot(str)
    def updateStatus(self, newStatus):
        self.status.setText(newStatus)

    @pyqtSlot(QImage)
    def setSource(self, image):
        self.sourceImage.setPixmap(QPixmap.fromImage(image))

    @pyqtSlot(QImage)
    def setTarget(self, image):
        self.targetImage.setPixmap(QPixmap.fromImage(image))

    @pyqtSlot()
    def success(self):
        self.matchStatus.setCurrentIndex(1)

    @pyqtSlot()
    def fail(self):
        self.matchStatus.setCurrentIndex(0)
