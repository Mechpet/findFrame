from PyQt6.QtWidgets import QWidget, QLineEdit, QLabel, QRadioButton, QButtonGroup, QFileDialog, QPushButton, QGridLayout
from PyQt6.QtCore import Qt

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
        self.afterBtn.setChecked(True)

        self.outputTemplate = QLineEdit("")
        outputPreviewLabel = QLabel("Preview of output slices:")
        self.outputPreview = QLabel("0.mp4")

        self.outputTemplate.textChanged.connect(self.updatePreview)
        self.outputDirectoryBrowse.clicked.connect(self.openDirectoryDialog)

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

    def openDirectoryDialog(self):
        self.dialog = QFileDialog()
        
        # Show only directories
        self.dialog.setOption(QFileDialog.Option.ShowDirsOnly, True)
        # Set initial filter to any
        self.dialog.setNameFilter(self.tr("Any directory (*)"))
        # Accept only one directory
        self.dialog.setFileMode(QFileDialog.FileMode.Directory)
        # Instead of 'Open' button, use 'Save' button
        self.dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)

        self.dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.dialog.fileSelected.connect(self.outputDirectoryEdit.setText)
        self.dialog.show()

    def updatePreview(self):
        if self.beforeBtn.isChecked():
            self.outputPreview.setText(f"0{self.outputTemplate.text()}.mp4")
        elif self.afterBtn.isChecked():
            self.outputPreview.setText(f"{self.outputTemplate.text()}0.mp4")
