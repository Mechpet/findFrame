from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton, QFileDialog, QLabel, QSlider, QVBoxLayout
from PyQt6.QtCore import QFile, Qt, pyqtSlot
from PyQt6.QtGui import QDoubleValidator
from qtrangeslider import QLabeledRangeSlider

from videoChecker import videoValidity

acceptedExtensions = (
    ".mp4",
    ".m4v",
    ".mov",
    ".mkv"
)

MINIMUM_THRESHOLD = "0.0"

class targetHeader(QWidget):
    """Header that tells the user what each column represents"""
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QHBoxLayout()
        layout.addSpacing(75)
        layout.addWidget(QLabel("Video path"))
        layout.addSpacing(270)
        layout.addWidget(QLabel("Source range"))
        layout.addSpacing(80)
        layout.addWidget(QLabel("SSIM Threshold"))
        
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
        self.bounds = QLabeledRangeSlider(Qt.Orientation.Horizontal)
        self.bounds.setFixedWidth(200)
        self.bounds.setMinimum(0)
        self.bounds.setValue((0, 100))

        self.fileBrowse.clicked.connect(self.openFileDialog)

        thresholdVBox = QVBoxLayout()
        self.thresholdEdit = QLineEdit()
        self.thresholdEdit.setPlaceholderText("95")
        self.thresholdEdit.setValidator(QDoubleValidator())
        self.thresholdEdit.editingFinished.connect(self.updateThresholdEdit)
        self.thresholdSlider = QSlider(Qt.Orientation.Horizontal)
        self.thresholdSlider.setMinimum(0)
        self.thresholdSlider.setMaximum(100)
        self.thresholdSlider.valueChanged.connect(lambda: self.thresholdEdit.setText(str(self.thresholdSlider.value())))


        thresholdVBox.addWidget(self.thresholdSlider)
        thresholdVBox.addWidget(self.thresholdEdit)

        self.layout.addWidget(self.fileEdit)
        self.layout.addWidget(self.fileBrowse)
        self.layout.addSpacing(10)
        self.layout.addWidget(self.validation)
        self.layout.addSpacing(10)
        self.layout.addWidget(self.bounds)
        self.layout.addLayout(thresholdVBox)

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

    @pyqtSlot()
    def updateThresholdEdit(self):
        if not self.thresholdEdit.text() or float(self.thresholdEdit.text()) < float(MINIMUM_THRESHOLD):
            self.thresholdEdit.setText(MINIMUM_THRESHOLD)
        self.thresholdSlider.setValue(int(self.thresholdEdit.text()))