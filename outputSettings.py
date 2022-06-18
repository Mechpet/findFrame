from PyQt6.QtWidgets import QWidget, QLineEdit, QLabel, QRadioButton, QButtonGroup, QFileDialog, QPushButton, QGridLayout
from PyQt6.QtCore import Qt, pyqtSlot

import os

class outputSettings(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        layout = QGridLayout()

        outputLabel = QLabel("Output directory:")
        self.outputDirectoryEdit = QLineEdit()
        self.outputDirectoryBrowse = QPushButton("Browse")

        outputCustomizationLabel = QLabel("Output customization:")
        self.appendBtns = QButtonGroup()
        self.beforeBtn = QRadioButton("Before", self)
        self.afterBtn = QRadioButton("After", self)
        self.appendBtns.addButton(self.beforeBtn, 1)
        self.appendBtns.addButton(self.afterBtn, 0)
        self.afterBtn.setChecked(True)

        self.outputTemplate = QLineEdit("")
        outputPreviewLabel = QLabel("Preview of output slices:")
        self.outputPreview = QLabel("0.mp4")

        self.outputTemplate.textChanged.connect(self.updatePreview)
        self.outputDirectoryEdit.editingFinished.connect(self.updatePreview)
        self.outputDirectoryBrowse.clicked.connect(self.openDirectoryDialog)
        self.beforeBtn.clicked.connect(self.updatePreview)
        self.afterBtn.clicked.connect(self.updatePreview)

        layout.addWidget(outputLabel, 0, 0, 1, 1)
        layout.addWidget(self.outputDirectoryEdit, 0, 1, 1, 3)
        layout.addWidget(self.outputDirectoryBrowse, 0, 4, 1, 1)
        layout.addWidget(self.outputDirectoryEdit, 0, 1, 1, 3)
        layout.addWidget(outputCustomizationLabel, 1, 0, 1, 1)
        layout.addWidget(self.beforeBtn, 2, 0, 1, 1)
        layout.addWidget(self.outputTemplate, 2, 1, 1, 3)
        layout.addWidget(self.afterBtn, 2, 4, 1, 1)
        layout.addWidget(outputPreviewLabel, 3, 0, 1, 1)
        layout.addWidget(self.outputPreview, 4, 0, 1, -1)

        self.setLayout(layout)
    
    @pyqtSlot()
    def openDirectoryDialog(self):
        dir = QFileDialog.getExistingDirectory(self, self.tr("Open Directory"), "", QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontResolveSymlinks)
        if dir:
            self.outputDirectoryEdit.setText(dir)
            self.updatePreview()

    @pyqtSlot()
    def updatePreview(self):
        """Update the preview of the 0th slice filename"""
        if self.beforeBtn.isChecked():
            self.outputPreview.setText(f"{self.getOutputDirectory()}0{self.outputTemplate.text()}.mp4")
        elif self.afterBtn.isChecked():
            self.outputPreview.setText(f"{self.getOutputDirectory()}{self.outputTemplate.text()}0.mp4")

    def getOutputDirectory(self):
        """Return the user-inputted output directory if it is valid"""
        if self.outputDirectoryEdit.text():
            if os.path.isdir(self.outputDirectoryEdit.text()):
                if self.outputDirectoryEdit.text()[-1] == '/':
                    return self.outputDirectoryEdit.text()
                else:
                    return self.outputDirectoryEdit.text() + '/'
        return ''
        