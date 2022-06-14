import sys

from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QGridLayout, QLineEdit, QPushButton, QScrollArea, QTabWidget
from PyQt6.QtCore import Qt

from captureEditor import captureEditor
from videoSettings import videoSettings

app = QApplication(sys.argv)

sourceLabelColumnSpan = 3
sourceInputColumnSpan = 6

class mainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setFixedSize(750, 600)

        self.captureEditor = captureEditor()
        self.videoSettings = videoSettings()
        self.captureEditor.sourceInput.textChanged.connect(self.videoSettings.setAspectRatio)

        self.tabWidget = QTabWidget()
        self.tabWidget.addTab(self.captureEditor, "Videos")
        self.tabWidget.addTab(self.videoSettings, "Settings")
        self.executeBtn = QPushButton("Execute")

        self.layout = QGridLayout()
        self.layout.addWidget(self.tabWidget, 1, 0)
        self.layout.addWidget(self.executeBtn, 10, 0, 2, 2)
        self.setLayout(self.layout)
        
        self.show()

def main():
    window = mainWindow()

    sys.exit(app.exec())

if __name__ == '__main__':
    main()