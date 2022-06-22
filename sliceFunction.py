import cv2
import ffmpeg
import os
import subprocess
from skimage.metrics import structural_similarity as ssim
import numpy as np

from PyQt6.QtCore import Qt, QObject, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QImage, QPixmap
from timeit import default_timer as timer

from target import target
import config

showStatus = False
DEFAULT_SSIM = 0.95
DEFAULT_SLICE_LENGTH = 60

class sliceWorker(QObject):
    ready = pyqtSignal()
    slicing = pyqtSignal()
    finished = pyqtSignal()
    matched = pyqtSignal()
    sourceImageChanged = pyqtSignal(QImage)
    targetImageChanged = pyqtSignal(QImage)
    progressChanged = pyqtSignal(float)
    def __init__(self, sourceFile, targetFiles, targetSSIMs, sourceRanges, sliceDuration, dimensions, directory, template, prefix, slowOn):
        super().__init__()
        self.sourceFile = sourceFile
        self.targetFiles = targetFiles
        self.targetSSIMs = targetSSIMs
        self.sourceRanges = sourceRanges
        self.sliceDuration = sliceDuration
        self.dimensions = dimensions
        self.directory = directory
        self.template = template
        self.prefix = prefix
        self.slowOn = slowOn
        self.ready.connect(self.run)

    @pyqtSlot()
    def run(self):
        """Start the slicing operation"""
        config.executingFlag = True
        self.slice(self.sourceFile, self.targetFiles, self.targetSSIMs, self.sourceRanges, self.sliceDuration, self.dimensions, self.directory, self.template, self.prefix, self.slowOn)
    
    def match(self, sourceFile, targetFiles, targetSSIMs, sourceRanges, dimensions, slowOn):
        sourceCapture = cv2.VideoCapture(sourceFile)

        sourceFrameCnt = sourceCapture.get(cv2.CAP_PROP_FRAME_COUNT)
        matchStarts = []

        for i in range(len(targetFiles)):
            matchStarts.append(-1)
            targetCapture = cv2.VideoCapture(targetFiles[i])
            sourceRange = np.dot(sourceRanges[i], sourceFrameCnt / 100).astype(int)

            sourceCapture.set(cv2.CAP_PROP_POS_FRAMES, sourceRange[0])
            sourceFrameIndex = sourceCapture.get(cv2.CAP_PROP_POS_FRAMES)

            # Get the first frame of the target capture
            targetFlag, targetFrameImg = targetCapture.read()
            targetFrameImgResized = cv2.resize(targetFrameImg, dimensions)
            targetFrameImgResized = cv2.cvtColor(targetFrameImgResized, cv2.COLOR_BGR2GRAY)
            targetFrameCnt = targetCapture.get(cv2.CAP_PROP_FRAME_COUNT)
            targetFrameIndex = targetCapture.get(cv2.CAP_PROP_POS_FRAMES)

            # Display the image 
            h, w = targetFrameImgResized.shape
            p = QImage(targetFrameImgResized.data, w, h, QImage.Format.Format_Grayscale8)
            p = p.scaled(320, 240)
            self.targetImageChanged.emit(p)

            while sourceCapture.isOpened() and config.executingFlag:
                # Read the next frame of the sourceCapture
                sourceFlag, sourceFrameImg = sourceCapture.read()
    
                if sourceFlag:
                    sourceFrameImgResized = cv2.resize(sourceFrameImg, dimensions)
                    sourceFrameImgResized = cv2.cvtColor(sourceFrameImgResized, cv2.COLOR_BGR2GRAY)
                    
                    if config.onPreview:
                        h, w = sourceFrameImgResized.shape
                        p = QImage(sourceFrameImgResized.data, w, h, QImage.Format.Format_Grayscale8)
                        p = p.scaled(320, 240)
                        self.sourceImageChanged.emit(p)

                    # Calculate the Structural Similarity Index between the two grayscale images
                    ssimFloat = ssim(sourceFrameImgResized, targetFrameImgResized)
                    print(f"SSIM: {ssimFloat}")

                    if ssimFloat >= targetSSIMs[i]:
                        if matchStarts[i] < 0:
                            matchStarts[i] = sourceFrameIndex
                        self.progressChanged.emit(((matchStarts[i] - sourceRange[0]) / sourceRange[1] + (1 - (matchStarts[i] - sourceRange[0]) / sourceRange[1]) / targetFrameCnt * targetFrameIndex) * 100)
                        self.matched.emit()
                        # Read the next frame of the targetCapture
                        targetFlag, targetFrameImg = targetCapture.read()
                        if targetFlag:
                            targetFrameImg = cv2.cvtColor(targetFrameImg, cv2.COLOR_BGR2GRAY)
                            targetFrameImgResized = cv2.resize(targetFrameImg, dimensions)
                            targetFrameIndex = targetCapture.get(cv2.CAP_PROP_POS_FRAMES)
                            if config.onPreview:
                                h, w = targetFrameImgResized.shape
                                p = QImage(targetFrameImgResized.data, w, h, QImage.Format.Format_Grayscale8)
                                p = p.scaled(320, 240)
                                self.targetImageChanged.emit(p)
                        else:
                            break
                    elif matchStarts[i]:
                        print("BROKE")
                        targetCapture.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        targetFlag, targetFrameImg = targetCapture.read()
                        targetFrameIndex = targetCapture.get(cv2.CAP_PROP_POS_FRAMES)
                        targetFrameImgResized = cv2.resize(targetFrameImg, dimensions)
                        targetFrameImgResized = cv2.cvtColor(targetFrameImgResized, cv2.COLOR_BGR2GRAY)
                        targetFrameIndex = targetCapture.get(cv2.CAP_PROP_POS_FRAMES)
                        matchStarts[i] = -1
                        self.progressChanged.emit((sourceFrameIndex - sourceRange[0]) / sourceRange[1] * 100)
                    else:
                        self.progressChanged.emit((sourceFrameIndex - sourceRange[0]) / sourceRange[1] * 100)
            
                    sourceFrameIndex = sourceCapture.get(cv2.CAP_PROP_POS_FRAMES)
                # Something failed while trying to read the next frame - safe to end the search
                else:
                    break

                # Didn't find a suitable match within the given range
                if sourceFrameIndex == sourceRange[1] and matchStarts[i] == -1:
                    break

                if slowOn:
                    cv2.waitKey(slowOn)

        return matchStarts

    def slice(self, sourceFile, targetFiles, targetSSIMs, sourceRanges, sliceDuration, dimensions, directory = "", name = "", prefix = False, slowOn = False):
        matchingFrames = self.match(sourceFile, targetFiles, targetSSIMs, sourceRanges, dimensions, slowOn)

        sourceProps = captureAttributes(sourceFile)
        targetsProps = [captureAttributes(targetFile) for targetFile in targetFiles]
        targetMatches = [(matchingFrames[i], matchingFrames[i] + targetsProps[i].frameCnt) for i in range(len(matchingFrames))]
        # Convert the targetMatches to seconds
        targetMatches = [(targetMatches[i][0] / targetsProps[i].FPS, targetMatches[i][1] / targetsProps[i].FPS) for i in range(len(targetMatches))]

        sampling = 't'
        sliceIndex = 1
        targetIndex = 0
        if sampling == 'n':
            start = 0
            length = int(sourceProps.FPS * sliceDuration)
            max = sourceProps.frameCnt
        elif sampling == 't':
            start = 0
            length = sliceDuration
            max = sourceProps.frameCnt / sourceProps.FPS
        end = length
        sliceRange = [[start, end]]

        matchStart = targetMatches[targetIndex][0]
        matchEnd = targetMatches[targetIndex][1]

        self.slicing.emit()
        while config.executingFlag:
            file = open("log.txt", "a")
            if matchStart >= start and matchStart <= end:
                file.write("Case 1:\n")
                sliceRange = [[start, end]]
                # Found a match within the current slice
                while matchStart >= sliceRange[-1][0] and matchStart <= sliceRange[-1][1]:
                    sliceRange[-1][1] = matchStart + 1
                    sliceRange.append([matchEnd, matchEnd + (length - (matchStart - start))])
                    targetIndex += 1
                    if targetIndex < len(targetMatches):
                        matchStart = targetMatches[targetIndex][0]
                        matchEnd = targetMatches[targetIndex][1]
                    else:
                        break

                betweenStringArgs = betweenString(sliceRange, sampling, max)

                ffmpegCmdSlow = f"C:/ffmpeg/bin/ffmpeg.exe -y -i {sourceFile} "\
                    f"-filter_complex \"select = "\
                    f"'{betweenStringArgs}', "\
                    "setpts = N/FRAME_RATE/TB\" "\
                    f"-af \"aselect = "\
                    f"'{betweenStringArgs}', "\
                    "asetpts = N/SR/TB\" "\
                    "-map 0 "\
                    f"{getFileName(directory, name, prefix, sliceIndex)}"

                start = sliceRange[-1][1]
                if start >= max:
                    config.executingFlag = False
            elif end > max:
                file.write("Case 2:\n")
                ffmpegCmdSlow = f"C:/ffmpeg/bin/ffmpeg.exe -y -i {sourceFile} "\
                    "-filter_complex \"select = "\
                    f"'between({sampling}, {start}, {max})', "\
                    "setpts = N/FRAME_RATE/TB\" "\
                    f"-af \"aselect = "\
                    f"'between({sampling}, {start}, {max})', "\
                    "asetpts = N/SR/TB\" "\
                    "-map 0 "\
                    f"{getFileName(directory, name, prefix, sliceIndex)}"
                config.executingFlag = False
            else:
                file.write("Case 3:\n")
                ffmpegCmdSlow = f"C:/ffmpeg/bin/ffmpeg.exe -y -i {sourceFile} "\
                    "-filter_complex \"select = "\
                    f"'between({sampling}, {start}, {end})', "\
                    "setpts = N/FRAME_RATE/TB\" "\
                    f"-af \"aselect = "\
                    f"'between({sampling}, {start}, {end})', "\
                    "asetpts = N/SR/TB\" "\
                    "-map 0 "\
                    f"{getFileName(directory, name, prefix, sliceIndex)}"

                start = end
        
            file.write(ffmpegCmdSlow + "\n")
            end = start + length
            file.close()
            subprocess.call(ffmpegCmdSlow, shell = True)

            sliceIndex += 1
    
        self.finished.emit()

class captureAttributes:
    def __init__(self, fileName):
        capture = cv2.VideoCapture(fileName)
        self.frameCnt = capture.get(cv2.CAP_PROP_FRAME_COUNT)
        self.FPS = capture.get(cv2.CAP_PROP_FPS)

def betweenString(ranges, sampling, max):
    """Return the string of betweens"""
    strings = []
    for range in ranges:
        # If the end is before the start, the first range is useless
        if range[1] < range[0]:
            pass
        else:
            strings.append(f"between({sampling}, {range[0]}, {min(max, range[1])})")
    
    return " + ".join(strings)

def getFileName(directory, name, prefix, index):
    """Get the file name given the template, index, and whether the index is the prefix or suffix"""
    if prefix:
        return f"{directory}{index}{name}.mp4"
    else:
        return f"{directory}{name}{index}.mp4"
