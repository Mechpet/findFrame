import sys

from PyQt6.QtWidgets import QApplication, QWidget, QGridLayout, QPushButton, QTabWidget
from PyQt6.QtCore import Qt, QObject, QThread, pyqtSignal, pyqtSlot

from captureEditor import captureEditor
from videoSettings import videoSettings
from outputSettings import outputSettings
from progressPreview import progressPreview
from sliceFunction import sliceWorker, DEFAULT_SLICE_LENGTH, DEFAULT_SSIM
import config

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
        self.progress = progressPreview()
        self.captureEditor.sourceInput.textChanged.connect(self.videoSettings.setAspectRatio)

        self.tabWidget = QTabWidget()
        self.tabWidget.addTab(self.captureEditor, "Input settings")
        self.tabWidget.addTab(self.videoSettings, "Slice settings")
        self.tabWidget.addTab(self.outputSettings, "Output settings")
        self.tabWidget.addTab(self.progress, "Progress")
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

    @pyqtSlot()
    def startSlice(self):
        """Lock important widgets and create a new worker"""
        self.createSliceWorker()

    @pyqtSlot()
    def stopSlicing(self):
        """Stop the slicing operation of the current worker"""
        config.executingFlag = False

    def createSliceWorker(self):
        """Get all of the information the user inputted"""
        sourceFile = self.captureEditor.sourceInput.text()
        targetFiles = []
        targetSSIMs = []
        sourceRanges = []
        dimensions = (int(self.videoSettings.compareWidth.text()), int(self.videoSettings.compareHeight.text()))
        for i in range(self.captureEditor.targetList.layout.count() - 1):
            targetFiles.append(self.captureEditor.targetList.layout.itemAt(i).widget().fileEdit.text())
            targetSSIMs.append(DEFAULT_SSIM)
            sourceRanges.append(self.captureEditor.targetList.layout.itemAt(i).widget().bounds.value())

        if self.videoSettings.sliceDurationEdit.text():
            sliceDuration = float(self.videoSettings.sliceDurationEdit.text())
        else:
            sliceDuration = DEFAULT_SLICE_LENGTH

        directory = self.outputSettings.getOutputDirectory()
        template = self.outputSettings.outputTemplate.text()
        prefix = self.outputSettings.appendBtns.checkedId()

        self.worker = sliceWorker(sourceFile, targetFiles, targetSSIMs, sourceRanges, sliceDuration, dimensions, directory, template, prefix)
        self.worker.progressChanged.connect(self.progress.updateValue)
        self.worker.moveToThread(self.thread)
        self.thread.start()
        self.worker.ready.emit()

    def closeEvent(self, event):
        """Quit all running threads and exit the app"""
        self.thread.quit()
        self.worker = None
        event.accept()

def main():
    global executingFlag
    executingFlag = False
    window = mainWindow()

    sys.exit(app.exec())

if __name__ == '__main__':
    main()