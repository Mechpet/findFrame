import sys

from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QGridLayout, QLineEdit, QPushButton, QScrollArea, QTabWidget
from PyQt6.QtCore import Qt, QObject, QThread, pyqtSignal, pyqtSlot

from captureEditor import captureEditor
from videoSettings import videoSettings
from outputSettings import outputSettings
import sliceFunction as slicer

app = QApplication(sys.argv)

sourceLabelColumnSpan = 3
sourceInputColumnSpan = 6

class mainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.thread = QThread()

        self.initUI()

    def initUI(self):
        self.setFixedSize(750, 600)

        self.captureEditor = captureEditor()
        self.videoSettings = videoSettings()
        self.outputSettings = outputSettings()
        self.captureEditor.sourceInput.textChanged.connect(self.videoSettings.setAspectRatio)

        self.tabWidget = QTabWidget()
        self.tabWidget.addTab(self.captureEditor, "Input settings")
        self.tabWidget.addTab(self.videoSettings, "Slice settings")
        self.tabWidget.addTab(self.outputSettings, "Output settings")
        self.executeBtn = QPushButton("Execute")
        self.executeBtn.clicked.connect(self.startSlice)
        self.stopBtn = QPushButton("Stop")
        self.stopBtn.clicked.connect(self.stopSlicing)

        self.layout = QGridLayout()
        self.layout.addWidget(self.tabWidget, 1, 0, 5, 2)
        self.layout.addWidget(self.executeBtn, 10, 0, 1, 1)
        self.layout.addWidget(self.stopBtn, 10, 1, 1, 1)
        self.setLayout(self.layout)
        
        self.show()

    def startSlice(self):
        """Lock important widgets and create a new worker"""
        self.createSliceWorker()

    def stopSlicing(self):
        slicer.executingFlag = False

    def createSliceWorker(self):
        """Get all of the information the user inputted"""
        sourceFile = self.captureEditor.sourceInput.text()
        targetFiles = []
        targetSSIMs = []
        sourceRanges = []
        dimensions = (int(self.videoSettings.compareWidth.text()), int(self.videoSettings.compareHeight.text()))
        for i in range(self.captureEditor.targetList.layout.count() - 1):
            targetFiles.append(self.captureEditor.targetList.layout.itemAt(i).widget().fileEdit.text())
            targetSSIMs.append(slicer.DEFAULT_SSIM)
            sourceRanges.append(self.captureEditor.targetList.layout.itemAt(i).widget().bounds.value())

        self.worker = sliceWorker(sourceFile, targetFiles, targetSSIMs, sourceRanges, slicer.DEFAULT_SLICE_LENGTH, dimensions)
        self.worker.moveToThread(self.thread)
        self.thread.start()
        self.worker.ready.emit()

    def closeEvent(self, event):
        self.thread.quit()
        self.worker = None
        event.accept()

class sliceWorker(QObject):
    ready = pyqtSignal()
    def __init__(self, sourceFile, targetFiles, targetSSIMs, sourceRanges, sliceLength, dimensions):
        super().__init__()
        self.sourceFile = sourceFile
        self.targetFiles = targetFiles
        self.targetSSIMs = targetSSIMs
        self.sourceRanges = sourceRanges
        self.sliceLength = sliceLength
        self.dimensions = dimensions
        self.ready.connect(self.run)

    @pyqtSlot()
    def run(self):
        slicer.executingFlag = True
        slicer.slice(self.sourceFile, self.targetFiles, self.targetSSIMs, self.sourceRanges, slicer.DEFAULT_SLICE_LENGTH, self.dimensions)

def main():
    slicer.executingFlag = False
    window = mainWindow()

    sys.exit(app.exec())

if __name__ == '__main__':
    main()