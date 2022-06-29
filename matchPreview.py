from PyQt6.QtWidgets import QWidget, QLabel, QGridLayout, QStackedWidget, QCheckBox, QLineEdit, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QImage, QPixmap, QIntValidator

import config
from SSIMBar import SSIMBar

class matchPreview(QWidget):
    def __init__(self):
        super().__init__()
        
        self.initUI()

    def initUI(self):
        layout = QGridLayout()
        self.sourceImage = QLabel("")
        self.sourceImage.resize(320, 240)
        self.targetImage = QLabel("")
        self.targetImage.resize(320, 240)
        self.matchStatus = QStackedWidget()
        matchSuccess = QLabel("<font color = 'green'>Matched frames.</font>")
        matchFailure = QLabel("<font color = 'red'>Not a match.</font>")

        self.matchStatus.addWidget(matchFailure)
        self.matchStatus.addWidget(matchSuccess)
        self.matchStatus.setCurrentIndex(0)

        self.SSIM = SSIMBar()

        slowHBox = QHBoxLayout()
        self.slowEnable = QCheckBox("Enable slow mode (ms):")
        self.slowEnable.clicked.connect(self.changeSlowMode)

        self.slowModeEdit = QLineEdit(str("0"))
        self.slowModeEdit.setValidator(QIntValidator())
        self.slowModeEdit.textChanged.connect(self.changeSlowDuration)
        slowHBox.addWidget(self.slowEnable)
        slowHBox.addWidget(self.slowModeEdit)

        layout.addWidget(self.sourceImage, 0, 0, 4, 5)
        layout.addWidget(self.targetImage, 0, 5, 4, 5)
        layout.addWidget(self.SSIM, 4, 0, 1, -1)
        layout.addLayout(slowHBox, 5, 0, 1, -1)
        layout.addWidget(self.matchStatus, 6, 0, 1, -1, Qt.AlignmentFlag.AlignHCenter)
        self.setLayout(layout)

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

    @pyqtSlot(float)
    def initSSIM(self, threshold):
        self.SSIM.initUI(threshold)

    @pyqtSlot()
    def changeSlowMode(self):
        config.slowOn = self.slowEnable.isChecked()

    @pyqtSlot(str)
    def changeSlowDuration(self, str):
        config.slowDuration = int(self.slowModeEdit.text())
    