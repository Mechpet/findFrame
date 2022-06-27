import sys

from PyQt6.QtWidgets import QApplication, QWidget, QGridLayout, QPushButton, QTabWidget, QStackedWidget
from PyQt6.QtCore import Qt, QObject, QThread, pyqtSignal, pyqtSlot
from cv2 import threshold

from captureEditor import captureEditor
from videoSettings import videoSettings
from outputSettings import outputSettings
from progressPreview import progressPreview
from sliceFunction import sliceWorker, DEFAULT_SLICE_LENGTH, DEFAULT_SSIM
import config
import os

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
        self.tabWidget.currentChanged.connect(self.updateConfig)

        self.executeBtn = QPushButton("Execute")
        self.executeBtn.clicked.connect(self.startSliceWorker)
        self.stopBtn = QPushButton("Stop")
        self.stopBtn.clicked.connect(self.stopSlicing)

        self.mainBtn = QStackedWidget()
        self.mainBtn.addWidget(self.executeBtn)
        self.mainBtn.addWidget(self.stopBtn)
        self.mainBtn.setCurrentWidget(self.executeBtn)

        self.layout = QGridLayout()
        self.layout.addWidget(self.tabWidget, 1, 0, 5, 2)
        self.layout.addWidget(self.mainBtn, 7, 0, 1, -1, Qt.AlignmentFlag.AlignVCenter)
        self.setLayout(self.layout)
        
        self.show()

    @pyqtSlot()
    def startSliceWorker(self):
        """Lock important widgets and create a new worker"""
        self.createSliceWorker()

    @pyqtSlot()
    def stopSlicing(self):
        """Stop the slicing operation of the current worker"""
        self.closeThread()
        config.executingFlag = False
        os.system("taskkill /f /im ffmpeg.exe")
        self.progress.updateStatus("IDLE.")
        self.progress.stack.setCurrentWidget(self.progress.match)
        self.mainBtn.setCurrentWidget(self.executeBtn)

    def createSliceWorker(self):
        """Get all of the information the user inputted"""
        sourceFile = self.captureEditor.sourceInput.text()
        targetFiles = []
        targetSSIMs = []
        sourceRanges = []
        dimensions = (int(self.videoSettings.compareWidth.text()), int(self.videoSettings.compareHeight.text()))
        thresholdSSIM = self.videoSettings.thresholdEdit.text()
        if thresholdSSIM:
            targetSSIM = float(thresholdSSIM) / 100.0
            print("targetSSIM = ", targetSSIM)
        else:
            targetSSIM = DEFAULT_SSIM
            print("targetSSIM = ", targetSSIM)
        for i in range(self.captureEditor.targetList.layout.count() - 1):
            targetFiles.append(self.captureEditor.targetList.layout.itemAt(i).widget().fileEdit.text())
            targetSSIMs.append(targetSSIM)
            sourceRanges.append(self.captureEditor.targetList.layout.itemAt(i).widget().bounds.value())

        if self.videoSettings.sliceDurationEdit.text():
            sliceDuration = float(self.videoSettings.sliceDurationEdit.text())
        else:
            sliceDuration = DEFAULT_SLICE_LENGTH

        directory = self.outputSettings.getOutputDirectory()
        template = self.outputSettings.outputTemplate.text()
        prefix = self.outputSettings.appendBtns.checkedId()
        slowEnabled = self.videoSettings.slowModeEdit.text()
        if slowEnabled:
            slowEnabled = int(slowEnabled)

        self.worker = sliceWorker(sourceFile, targetFiles, targetSSIMs, sourceRanges, sliceDuration, dimensions, directory, template, prefix, slowEnabled)
        self.worker.slicing.connect(self.startSlicing)
        self.worker.finished.connect(self.stopSlicing)
        self.worker.progressChanged.connect(self.progress.updateValue)
        self.worker.sourceImageChanged.connect(self.progress.match.setSource)
        self.worker.targetImageChanged.connect(self.progress.match.setTarget)
        self.worker.newSSIM.connect(self.progress.match.SSIM.displaySSIM)
        self.worker.matched.connect(self.progress.match.success)
        self.worker.notmatched.connect(self.progress.match.fail)
        self.worker.moveToThread(self.thread)

        self.progress.updateStatus("MATCHING VIDEOS.")
        self.progress.stack.setCurrentWidget(self.progress.match)
        self.progress.match.initSSIM(targetSSIM * 100)

        self.thread.start()
        self.mainBtn.setCurrentWidget(self.stopBtn)
        self.worker.ready.emit()

    def closeEvent(self, event):
        """Quit all running threads and exit the app"""
        self.closeThread()
        event.accept()

    def closeThread(self):
        self.thread.quit()
        self.worker = None

    @pyqtSlot()
    def startSlicing(self):
        self.progress.updateStatus("SLICING VIDEOS.")
        self.progress.stack.setCurrentWidget(self.progress.slice)

    @pyqtSlot(int)
    def updateConfig(self, newIndex):
        if newIndex == 3:
            config.onPreview = True
        else:
            config.onPreview = False

def main():
    global executingFlag
    executingFlag = False
    window = mainWindow()

    sys.exit(app.exec())

if __name__ == '__main__':
    main()