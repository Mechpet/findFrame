import cv2
import ffmpeg
import os
import subprocess
from skimage.metrics import structural_similarity as ssim
import numpy as np

from timeit import default_timer as timer

from target import target

showStatus = False
DEFAULT_SSIM = 0.95
DEFAULT_SLICE_LENGTH = 60

class captureAttributes:
    def __init__(self, fileName):
        capture = cv2.VideoCapture(fileName)
        self.frameCnt = capture.get(cv2.CAP_PROP_FRAME_COUNT)
        self.FPS = capture.get(cv2.CAP_PROP_FPS)

def slice(sourceFile, targetFiles, targetSSIMs, sourceRanges, sliceDuration, dimensions):
    global executingFlag
    matchingFrames = match(sourceFile, targetFiles, targetSSIMs, sourceRanges, dimensions)
    print(matchingFrames)

    sourceProps = captureAttributes(sourceFile)
    targetsProps = [captureAttributes(targetFile) for targetFile in targetFiles]
    targetMatches = [(matchingFrames[i], matchingFrames[i] + targetsProps[i].frameCnt) for i in range(len(matchingFrames))]
    # Convert the targetMatches to seconds
    targetMatches = [(targetMatches[i][0] / targetsProps[i].FPS, targetMatches[i][1] / targetsProps[i].FPS) for i in range(len(targetMatches))]

    # match = [(start, end), (start, end), ...]
    # Get the list of the matches from above -> Sorted (lower the index, the lower the starting frame index)
    # Start slicing the source capture
    # While the lowest match is IN the slice (start, end):
    #   Trim it out and work around it 
    #   Calculate the new slice (start, end)
    #   Look at the next lowest match from now on
    # Matched the exact number of frames in the target sequence
    # The target sequence has finished reading through
    # Safe to trim the video out:
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
    while executingFlag:
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
                f"{sliceIndex}.mp4"

            start = sliceRange[-1][1]
            if start >= max:
                executingFlag = False
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
                f"{sliceIndex}.mp4"
            executingFlag = False
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
                f"{sliceIndex}.mp4"

            start = end
        
        file.write(ffmpegCmdSlow + "\n")
        end = start + length
        file.close()
        subprocess.call(ffmpegCmdSlow, shell = True)

        sliceIndex += 1
    
    print('Finished')

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


def match(sourceFile, targetFiles, targetSSIMs, sourceRanges, dimensions):
    global executingFlag
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

        while sourceCapture.isOpened() and executingFlag:
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
