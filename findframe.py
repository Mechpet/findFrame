import cv2
import ffmpeg
from skimage.metrics import structural_similarity as ssim
import numpy as np

# Open video captures:
sourceCapture = cv2.VideoCapture("DS_ENTERTAINMENT.mp4")
targetCapture = cv2.VideoCapture("Opening.mp4")

# Constants:
escape = 27
space = 32

# Adjustables:
similarityThreshold = 0.95
frameCnt = 0
matched = 0
maxFrames = -1
desiredDim = (400, 225)
sourcePercentStart = 0.0
targetPercentStart = 0.0

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
targetFrameImg = cv2.cvtColor(targetFrameImg, cv2.COLOR_BGR2GRAY)
targetFrameImgResized = cv2.resize(targetFrameImg, desiredDim)

# Start the main loop of iterating through frames of the source footage
while sourceCapture.isOpened():
    # Read the next frame of the sourceCapture (colored)
    sourceFlag, sourceFrameImg = sourceCapture.read()
    
    if sourceFlag:
        sourceFrameImg = cv2.cvtColor(sourceFrameImg, cv2.COLOR_BGR2GRAY)
        sourceFrameImgResized = cv2.resize(sourceFrameImg, desiredDim)

        cv2.imshow("Source capture", sourceFrameImgResized)
        cv2.imshow("Target capture", targetFrameImgResized)

        # Calculate the Structural Similarity Index between the two grayscale images
        ssimFloat = ssim(sourceFrameImg, targetFrameImg)

        if ssimFloat >= similarityThreshold:
            sourceTime = sourceFrameIndex / sourceFPS
            targetTime = targetFrameIndex / targetFPS
            print("FOUND SAME FRAME AT FRAME #: ", frameCnt)
            print("@ source time: ", sourceTime)
            print("@ target time", targetTime)

            # Read the next frame of the targetCapture
            targetFrameIndex = targetCapture.get(cv2.CAP_PROP_POS_FRAMES)
            targetFlag, targetFrameImg = targetCapture.read()
            if targetFlag:
                targetFrameImg = cv2.cvtColor(targetFrameImg, cv2.COLOR_BGR2GRAY)
                targetFrameImgResized = cv2.resize(targetFrameImg, desiredDim)
            else:
                break
            matched += 1
        elif matched:
            targetCapture.set(cv2.CAP_PROP_POS_FRAMES, 0)
            targetFlag, targetFrameImg = targetCapture.read()

            matched = 0
        
        sourceFrameIndex = sourceCapture.get(cv2.CAP_PROP_POS_FRAMES)
    # Something failed while trying to read the next frame; end
    else:
        break

    key = cv2.waitKey(10)
    # Holding the 'Esc' key will end the loop
    if key == escape:
        break
    # Pressing the 'Space' key will advance to the next frame, if any
    elif key == space:
        pass
    else:
        cv2.waitKey(5000)

    if frameCnt == maxFrames:
        break
    frameCnt += 1

print("num matched = ", matched)
sourceCapture.release()
targetCapture.release()
cv2.destroyAllWindows()