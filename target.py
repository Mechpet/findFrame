from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton, QFileDialog, QLabel
from PyQt6.QtCore import QFile, Qt
from qtrangeslider import QLabeledRangeSlider

from videoChecker import videoValidity

acceptedExtensions = (
    ".mp4",
    ".m4v",
    ".mov",
    ".mkv"
)

class targetHeader(QWidget):
    """Header that tells the user what each column represents"""
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QHBoxLayout()
        layout.addSpacing(75)
        layout.addWidget(QLabel("Video path"))
        layout.addSpacing(325)
        layout.addWidget(QLabel("Source range"))
        
        self.setLayout(layout)

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
        self.fileEdit.setFixedWidth(200)
        self.fileBrowse = QPushButton("Browse")
        self.validation = QLabel("Invalid video")
        print('INIT')
        self.bounds = QLabeledRangeSlider(Qt.Orientation.Horizontal)
        print('INITED')
        self.bounds.setFixedWidth(200)
        print('SETTED W')
        self.bounds.setMinimum(0)
        print('SETTED MIN')
        #self.bounds.setMaximum(100)
        print('SETTED MAX')
        self.bounds.setValue((0, 100))
        print('SETTED V')

        self.fileBrowse.clicked.connect(self.openFileDialog)

        self.layout.addWidget(self.fileEdit)
        self.layout.addWidget(self.fileBrowse)
        self.layout.addSpacing(25)
        self.layout.addWidget(self.validation)
        self.layout.addSpacing(25)
        self.layout.addWidget(self.bounds)

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
        """Update the input and display whether the video is compatible"""
        self.fileEdit.setText(path)

        # First, check if the file exists and is in video format
        if path is not None and QFile.exists(path) and path.lower().endswith(acceptedExtensions):
            # Then, check if video is corrupt or broken
            if videoValidity(path):
                self.validation.setText("Valid video")
        else:
            print("NOPE")
            self.validation.setText("Invalid video")

