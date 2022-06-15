import cv2
import ffmpeg
import os
import subprocess
from skimage.metrics import structural_similarity as ssim
import numpy as np

from timeit import default_timer as timer

showStatus = False
DEFAULT_SSIM = 0.95
DEFAULT_SLICE_LENGTH = 60

def slice(sourceFile, targetFiles, targetSSIMs, sourceRanges, sliceDuration, dimensions):
    matchingFrames = match(sourceFile, targetFiles, targetSSIMs, sourceRanges, dimensions)
    print(matchingFrames)


def match(sourceFile, targetFiles, targetSSIMs, sourceRanges, dimensions):
    sourceCapture = cv2.VideoCapture(sourceFile)

    sourceFrameCnt = sourceCapture.get(cv2.CAP_PROP_FRAME_COUNT)
    matchStarts = []

    for i in range(len(targetFiles)):
        matchStarts.append(-1)
        targetCapture = cv2.VideoCapture(targetFiles[i])
        print(f"sourceRanges = {sourceRanges}")
        sourceRange = np.dot(sourceRanges[i], sourceFrameCnt / 100).astype(int)

        print(f"Source range = {sourceRange}")
        sourceCapture.set(cv2.CAP_PROP_POS_FRAMES, sourceRange[0])
        sourceFrameIndex = sourceCapture.get(cv2.CAP_PROP_POS_FRAMES)

        # Get the first frame of the target capture
        targetFlag, targetFrameImg = targetCapture.read()
        targetFrameImgResized = cv2.resize(targetFrameImg, dimensions)
        targetFrameImgResized = cv2.cvtColor(targetFrameImgResized, cv2.COLOR_BGR2GRAY)

        while sourceCapture.isOpened():
            # Read the next frame of the sourceCapture
            sourceFlag, sourceFrameImg = sourceCapture.read()
    
            if sourceFlag:
                sourceFrameImgResized = cv2.resize(sourceFrameImg, dimensions)
                sourceFrameImgResized = cv2.cvtColor(sourceFrameImgResized, cv2.COLOR_BGR2GRAY)

                # Calculate the Structural Similarity Index between the two grayscale images
                ssimFloat = ssim(sourceFrameImgResized, targetFrameImgResized)
                print(f"SSIM: {ssimFloat}")

                if ssimFloat >= targetSSIMs[i]:
                    if matchStarts[i] < 0:
                        matchStarts[i] = sourceFrameIndex

                    # Read the next frame of the targetCapture
                    targetFlag, targetFrameImg = targetCapture.read()
                    if targetFlag:
                        targetFrameImg = cv2.cvtColor(targetFrameImg, cv2.COLOR_BGR2GRAY)
                        targetFrameImgResized = cv2.resize(targetFrameImg, dimensions)
                    else:
                        break
                elif matchStarts[i]:
                    targetCapture.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    targetFlag, targetFrameImg = targetCapture.read()
                    matchStarts[i] = -1
            
                sourceFrameIndex = sourceCapture.get(cv2.CAP_PROP_POS_FRAMES)
            # Something failed while trying to read the next frame - safe to end the search
            else:
                break

            # Didn't find a suitable match within the given range
            if sourceFrameIndex == sourceRange[1] and matchStarts[i] == -1:
                break

    return matchStarts
