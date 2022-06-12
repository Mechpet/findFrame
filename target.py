from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton, QFileDialog, QLabel
from PyQt6.QtCore import QFile, Qt

class target(QWidget):
    """Represents a target video to 'slice' out of the source video"""
    def __init__(self):
        """Initialize an empty target that can be filled out by the user"""
        super().__init__()
        self.initUI()

    def initUI(self):
        """Organize the widgets together"""
        self.layout = QHBoxLayout()

        self.fileEdit = QLineEdit()
        self.fileEdit.textEdited.connect(self.setVideo)
        self.fileBrowse = QPushButton("Browse")
        self.validation = QLabel("Invalid video")

        self.fileBrowse.clicked.connect(self.openFileDialog)

        self.layout.addWidget(self.fileEdit)
        self.layout.addWidget(self.fileBrowse)
        self.layout.addWidget(self.validation)

        self.setLayout(self.layout)

    def openFileDialog(self):
        """Open a fileDialog that prompts the user for a file"""

        # Initialize the file dialog for a single image
        self.dialog = QFileDialog()
        # Set initial filter to image file extensions only
        self.dialog.setNameFilter(self.tr("Videos (*.mp4 *.m4v *.mov *.mkv)"))
        # Accept only one single file
        self.dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        # Instead of 'Open' button, use 'Save' button
        self.dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)

        self.dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.dialog.fileSelected.connect(self.setVideo)
        self.dialog.show()

    def setVideo(self, path):
        self.fileEdit.setText(path)

        if QFile.exists(path):
            self.validation.setText("Valid video")
        else:
            print("NOPE")
            self.validation.setText("Invalid video")

