import cv2
import ffmpeg
import os
import subprocess
from skimage.metrics import structural_similarity as ssim
import numpy as np

from timeit import default_timer as timer

start = timer()

# Open video captures:
sourceFile = "DS_ENTERTAINMENT.mp4"
targetFile = "Opening.mp4"
sourceCapture = cv2.VideoCapture(sourceFile)
targetCapture = cv2.VideoCapture(targetFile)

# Constants:
escape = 27
space = 32

# Adjustables:
similarityThreshold = 0.95
frameCnt = 0
matched = 0
maxFrames = -1
desiredDim = (160, 90)
sourcePercentStart = 0.10
targetPercentStart = 0.00

# Setup data about the source capture and target capture
sourceFrameIndex = sourceCapture.get(cv2.CAP_PROP_POS_FRAMES)
sourceFrameCnt = sourceCapture.get(cv2.CAP_PROP_FRAME_COUNT)
sourceFPS = sourceCapture.get(cv2.CAP_PROP_FPS)

targetFrameIndex = targetCapture.get(cv2.CAP_PROP_POS_FRAMES)
targetFrameCnt = targetCapture.get(cv2.CAP_PROP_FRAME_COUNT)
targetFPS = targetCapture.get(cv2.CAP_PROP_FPS)

# If the two videos differ in frame rate, the application won't function correctly; just quit
if sourceFPS != targetFPS:
    print(f"EXCEPTION: Source FPS {sourceFPS} != Target FPS {targetFPS}")
    quit()

# Set the starting frame of both the source and target 
sourceStart = int(sourcePercentStart * sourceFrameCnt)
targetStart = int(targetPercentStart * targetFrameCnt)

sourceCapture.set(cv2.CAP_PROP_POS_FRAMES, sourceStart)
targetCapture.set(cv2.CAP_PROP_POS_FRAMES, targetStart)

# Read the 1st frame of the targetCapture (grayscale)
targetFlag, targetFrameImg = targetCapture.read()
targetFrameImgResized = cv2.resize(targetFrameImg, desiredDim)
targetFrameImgResized = cv2.cvtColor(targetFrameImgResized, cv2.COLOR_BGR2GRAY)

sourceMatch = -1

# Start the main loop of iterating through frames of the source footage
while sourceCapture.isOpened():
    # Read the next frame of the sourceCapture (colored)
    sourceFlag, sourceFrameImg = sourceCapture.read()
    
    if sourceFlag:
        sourceFrameImgResized = cv2.resize(sourceFrameImg, desiredDim)
        sourceFrameImgResized = cv2.cvtColor(sourceFrameImgResized, cv2.COLOR_BGR2GRAY)

        cv2.imshow("Source capture", sourceFrameImgResized)
        cv2.imshow("Target capture", targetFrameImgResized)

        # Calculate the Structural Similarity Index between the two grayscale images
        ssimFloat = ssim(sourceFrameImgResized, targetFrameImgResized)
        print(f"SSIM: {ssimFloat}")

        if ssimFloat >= similarityThreshold:
            matched += 1
            if sourceMatch < 0:
                sourceMatch = sourceFrameIndex
            sourceTime = sourceFrameIndex / sourceFPS
            targetTime = targetFrameIndex / targetFPS
            print("FOUND SAME FRAME AT FRAME #: ", frameCnt)
            print("@ source time: ", sourceTime)
            print("@ target time", targetTime)

            # Read the next frame of the targetCapture
            targetFrameIndex = targetCapture.get(cv2.CAP_PROP_POS_FRAMES)
            targetFlag, targetFrameImg = targetCapture.read()
            print(f"Target frame index = {targetFrameIndex} / {targetFrameCnt}")
            if targetFlag:
                targetFrameImg = cv2.cvtColor(targetFrameImg, cv2.COLOR_BGR2GRAY)
                targetFrameImgResized = cv2.resize(targetFrameImg, desiredDim)
            else:
                print("Ended the target sequence")
                break
        elif matched:
            targetCapture.set(cv2.CAP_PROP_POS_FRAMES, 0)
            targetFlag, targetFrameImg = targetCapture.read()
            sourceMatch = -1

            matched = 0
        
        sourceFrameIndex = sourceCapture.get(cv2.CAP_PROP_POS_FRAMES)
        print("Index = ", sourceFrameIndex)
    # Something failed while trying to read the next frame; end
    else:
        break

    if cv2.waitKey(10) == escape:
        break

    if frameCnt == maxFrames:
        break
    frameCnt += 1

if matched == targetFrameCnt and targetFrameIndex == targetFrameCnt:
    # Matched the exact number of frames in the target sequence
    # The target sequence has finished reading through
    # Safe to trim the video out:
    ffmpegCmd = f"ffmpeg -i {sourceFile} "\
        f"-vf \"select = "\
        f"'between(n, 0, {sourceMatch}) + "\
        f"between({sourceMatch + matched}, {sourceFrameCnt})', "\
        "setpts = N/FRAME_RATE/TB\""\
        f"-af \"aselect = "\
        f"'between(n, 0, {sourceMatch}) + "\
        f"between({sourceMatch + matched}, {sourceFrameCnt})', "\
        "asetpts = N/SR/TB\""\
        "output.mp4"
    subprocess.call(ffmpegCmd, shell = True)
    print("Finished CMD")

print("num matched = ", matched)
sourceCapture.release()
targetCapture.release()
cv2.destroyAllWindows()
end = timer()
print(f"Took {end - start}")