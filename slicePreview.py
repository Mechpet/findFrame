from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit
from PyQt6.QtCore import Qt, pyqtSlot, QFileSystemWatcher

import config

class slicePreview(QWidget):
    def __init__(self):
        super().__init__()
        
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.fileWatcher = QFileSystemWatcher()
        self.fileWatcher.addPath("output.txt")
        self.fileWatcher.fileChanged.connect(self.updateStatus)

        self.statusDisplay = QTextEdit()
        self.statusDisplay.setReadOnly(True)

        layout.addWidget(self.statusDisplay)

        self.setLayout(layout)

    def updateStatus(self):
        if config.onPreview:
            newText = open(self.fileWatcher.files()[0]).read()
            self.statusDisplay.setPlainText(newText)
