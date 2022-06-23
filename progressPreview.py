from PyQt6.QtWidgets import QWidget, QGridLayout, QLabel, QStackedWidget
from PyQt6.QtCore import Qt, pyqtSlot

from matchPreview import matchPreview
from slicePreview import slicePreview

class progressPreview(QWidget):
    def __init__(self):
        super().__init__()
        
        self.initUI()

    def initUI(self):
        layout = QGridLayout()

        self.status = QLabel("IDLE.")

        self.stack = QStackedWidget()

        self.match = matchPreview()
        self.slice = slicePreview()
        self.stack.addWidget(self.match)
        self.stack.addWidget(self.slice)
        self.stack.setCurrentWidget(self.match)

        layout.addWidget(self.status, 0, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.stack, 1, 0)
        self.setLayout(layout)

    @pyqtSlot(str)
    def updateStatus(self, newStatus):
        self.status.setText(newStatus)