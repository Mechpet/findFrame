import sys

from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QGridLayout, QLineEdit, QPushButton
from PyQt6.QtCore import Qt

from target import target

app = QApplication(sys.argv)

sourceLabelColumnSpan = 3
sourceInputColumnSpan = 6

class mainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setFixedSize(750, 500)
        self.layout = QGridLayout()

        self.sourceLabel = QLabel("Source file")
        self.sourceLabel.setToolTip("Primary video file to take slices out of.")
        self.sourceInput = QLineEdit()
        self.sourceBrowser = QPushButton("Browse")
        self.target = target()

        self.layout.addWidget(self.sourceLabel, 0, 0, 1, sourceLabelColumnSpan)
        self.layout.addWidget(self.sourceInput, 0, sourceLabelColumnSpan + 1, 1, sourceInputColumnSpan)
        self.layout.addWidget(self.sourceBrowser, 0, sourceLabelColumnSpan + sourceInputColumnSpan + 1, 1, 1)
        self.layout.addWidget(self.target, 1, 0)

        self.setLayout(self.layout)
        self.show()

def main():
    window = mainWindow()

    sys.exit(app.exec())

if __name__ == '__main__':
    main()