from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from target import target

class targetList(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.adder = QPushButton("Add new target")
        self.adder.clicked.connect(self.append)

        self.layout = QVBoxLayout()
        self.layout.addWidget(target())
        self.layout.addWidget(self.adder)

        self.setLayout(self.layout)

    def append(self):
        self.layout.insertWidget(self.layout.count() - 1, target())