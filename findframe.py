import cv2
import ffmpeg
import numpy as np

sourceCapture = cv2.VideoCapture("DS_ENTERTAINMENT.mp4")
targetCapture = cv2.VideoCapture("Ending.mp4")

escape = 27

sourceFrameIndex = sourceCapture.get(cv2.CAP_PROP_POS_FRAMES)
sourceFrameCnt = sourceCapture.get(cv2.CAP_PROP_FRAME_COUNT)
sourceFPS = sourceCapture.get(cv2.CAP_PROP_FPS)

sourceStart = sourceFrameCnt * 0.912

targetFrameIndex = targetCapture.get(cv2.CAP_PROP_POS_FRAMES)
targetFrameCnt = targetCapture.get(cv2.CAP_PROP_FRAME_COUNT)
targetFPS = targetCapture.get(cv2.CAP_PROP_FPS)

if sourceFPS != targetFPS:
    print(f"EXCEPTION: Source FPS {sourceFPS} != Target FPS {targetFPS}")
    quit()

targetFlag, targetFrameImg = targetCapture.read()

frameCnt = 0
matched = 0
maxFrames = -1

sourceCapture.set(cv2.CAP_PROP_POS_FRAMES, sourceStart)
while sourceCapture.isOpened():
    sourceFlag, sourceFrameImg = sourceCapture.read()
    
    if sourceFlag:
        cv2.imshow("Source capture", sourceFrameImg)
        print(cv2.absdiff(sourceFrameImg, targetFrameImg).shape)
        if np.sum(cv2.absdiff(sourceFrameImg, targetFrameImg)) < 1000000:
            sourceTime = sourceFrameIndex / sourceFPS
            targetTime = targetFrameIndex / targetFPS
            print("FOUND SAME FRAME AT FRAME #: ", frameCnt)
            print("@ source time: ", sourceTime)
            print("@ target time", targetTime)
            targetFrameIndex = targetCapture.get(cv2.CAP_PROP_POS_FRAMES)
            targetFlag, targetFrameImg = targetCapture.read()
            matched += 1
        elif matched:
            targetCapture.set(cv2.CAP_PROP_POS_FRAMES, 0)
            targetFlag, targetFrameImg = targetCapture.read()

            matched = 0
        else:
            print("Diff sum = ", np.sum(cv2.absdiff(sourceFrameImg, targetFrameImg)))
        
        sourceFrameIndex = sourceCapture.get(cv2.CAP_PROP_POS_FRAMES)
    else:
        break

    if cv2.waitKey(10) == escape:
        break
    if frameCnt == maxFrames:
        break
    frameCnt += 1

print("num matched = ", matched)
sourceCapture.release()
targetCapture.release()
cv2.destroyAllWindows()