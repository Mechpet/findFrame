import cv2
import ffmpeg
import os
import subprocess
from skimage.metrics import structural_similarity as ssim
import numpy as np

from timeit import default_timer as timer

showStatus = False

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
sourceDuration = sourceFrameCnt / sourceFPS

targetFrameIndex = targetCapture.get(cv2.CAP_PROP_POS_FRAMES)
targetFrameCnt = targetCapture.get(cv2.CAP_PROP_FRAME_COUNT)
targetFPS = targetCapture.get(cv2.CAP_PROP_FPS)
targetDuration = targetFrameCnt / targetFPS

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

matchStartFrame = -1

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
            if matchStartFrame < 0:
                matchStartFrame = sourceFrameIndex
            sourceTime = sourceFrameIndex / sourceFPS
            targetTime = targetFrameIndex / targetFPS
            if showStatus:
                print("FOUND SAME FRAME AT FRAME #: ", frameCnt)
                print("@ source time: ", sourceTime)
                print("@ target time", targetTime)

            # Read the next frame of the targetCapture
            targetFrameIndex = targetCapture.get(cv2.CAP_PROP_POS_FRAMES)
            targetFlag, targetFrameImg = targetCapture.read()
            if showStatus:
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
            matchStartFrame = -1

            matched = 0
        
        sourceFrameIndex = sourceCapture.get(cv2.CAP_PROP_POS_FRAMES)
        if showStatus:
            print("Index = ", sourceFrameIndex)
    # Something failed while trying to read the next frame; end
    else:
        break

    if cv2.waitKey(10) == escape:
        break

    if frameCnt == maxFrames:
        break
    frameCnt += 1

matchStartTime = matchStartFrame / sourceFPS
matchEndTime = (matchStartFrame + matched) / sourceFPS
matchEndFrame = matchStartFrame + matched + 1

useTime = True
index = 1
if useTime:
    sampling = 't'
    length = 60
    matchStart = matchStartTime
    matchEnd = matchEndTime
    max = int(sourceFrameCnt / sourceFPS)
else:
    sampling = 'n'
    length = int(sourceFPS * 60)
    matchStart = matchStartFrame
    matchEnd = matchEndFrame
    max = sourceFrameCnt

start = 0
end = length
if matched == targetFrameCnt and targetFrameIndex == targetFrameCnt:
    # Matched the exact number of frames in the target sequence
    # The target sequence has finished reading through
    # Safe to trim the video out:
    executing = True
    while executing:
        file = open("log.txt", "a")
        if matchStart >= start and matchStart <= end:
            if matchEnd + (length - (matchStart - start)) > max:
                ffmpegCmdSlow = f"C:/ffmpeg/bin/ffmpeg.exe -y -i {sourceFile} "\
                    f"-filter_complex \"select = "\
                    f"'between({sampling}, {start}, {matchStart}) + "\
                    f"between({sampling}, {matchEnd}, {max})', "\
                    "setpts = N/FRAME_RATE/TB\" "\
                    f"-af \"aselect = "\
                    f"'between({sampling}, {start}, {matchStart}) + "\
                    f"between({sampling}, {matchEnd}, {max})', "\
                    "asetpts = N/SR/TB\" "\
                    "-map 0 "\
                    f"{index}.mp4"
                executing = False
            else:
                ffmpegCmdSlow = f"C:/ffmpeg/bin/ffmpeg.exe -y -i {sourceFile} "\
                    f"-filter_complex \"select = "\
                    f"'between({sampling}, {start}, {matchStart}) + "\
                    f"between({sampling}, {matchEnd}, {matchEnd + (length - (matchStart - start))})', "\
                    "setpts = N/FRAME_RATE/TB\" "\
                    f"-af \"aselect = "\
                    f"'between({sampling}, {start}, {matchStart}) + "\
                    f"between({sampling}, {matchEnd}, {matchEnd + (length - (matchStart - start))})', "\
                    "asetpts = N/SR/TB\" "\
                    "-map 0 "\
                    f"{index}.mp4"

            start = matchEnd + (length - (matchStart - start))
        elif end > max:
            ffmpegCmdSlow = f"C:/ffmpeg/bin/ffmpeg.exe -y -i {sourceFile} "\
                "-filter_complex \"select = "\
                f"'between({sampling}, {start}, {max})', "\
                "setpts = N/FRAME_RATE/TB\" "\
                f"-af \"aselect = "\
                f"'between({sampling}, {start}, {max})', "\
                "asetpts = N/SR/TB\" "\
                "-map 0 "\
                f"{index}.mp4"
            executing = False
        else:
            ffmpegCmdSlow = f"C:/ffmpeg/bin/ffmpeg.exe -y -i {sourceFile} "\
                "-filter_complex \"select = "\
                f"'between({sampling}, {start}, {end})', "\
                "setpts = N/FRAME_RATE/TB\" "\
                f"-af \"aselect = "\
                f"'between({sampling}, {start}, {end})', "\
                "asetpts = N/SR/TB\" "\
                "-map 0 "\
                f"{index}.mp4"

            start = end
        
        end = start + length
        file.write(ffmpegCmdSlow + "\n")
        file.close()
        subprocess.call(ffmpegCmdSlow, shell = True)

        index += 1

def copyTrim():
    ffmpegCmd = f"C:/ffmpeg/bin/ffmpeg.exe -y -i {sourceFile} "\
        f"-vf \"select = "\
        f"'between(n, 0, {int(matchStartFrame)}) + "\
        f"between(n, {int(matchStartFrame + matched)}, {int(sourceFrameCnt)})', "\
        "setpts = N/FRAME_RATE/TB\" "\
        f"-af \"aselect = "\
        f"'between(n, 0, {int(matchStartFrame)}) + "\
        f"between(n, {int(matchStartFrame + matched)}, {int(sourceFrameCnt)})', "\
        "asetpts = N/SR/TB\" "\
        "output.mp4"
    subprocess.call(ffmpegCmd, shell = True)

print("num matched = ", matched)
sourceCapture.release()
targetCapture.release()
cv2.destroyAllWindows()
end = timer()
print(f"Took {end - start}")