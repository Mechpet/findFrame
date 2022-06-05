import cv2

videocapture2 = cv2.VideoCapture("DS_ENTERTAINMENT.mp4")
videocapture1 = cv2.VideoCapture("Opening.mp4")

escape = 27

currentFrameIndex = videocapture2.get(cv2.CAP_PROP_POS_FRAMES)
targetFrameIndex = videocapture1.get(cv2.CAP_PROP_POS_FRAMES)

flag, targetFrame = videocapture1.read()

frameCnt = 0
matched = 0
while videocapture2.isOpened():
    flag, frame = videocapture2.read()
    
    if flag:
        currentFrameIndex = videocapture2.get(cv2.CAP_PROP_POS_FRAMES)
        print(cv2.absdiff(frame, targetFrame))
        if cv2.absdiff(frame, targetFrame).all() == 0:
            print("FOUND SAME FRAME AT ", frameCnt)
            targetFrameIndex = videocapture1.get(cv2.CAP_PROP_POS_FRAMES)
            flag, targetFrame = videocapture1.read()
            matched += 1
        elif matched:
            videocapture1.set(cv2.CAP_PROP_POS_FRAMES, 0)
            flag, targetFrame = videocapture1.read()

            matched = 0
    else:
        break

    if cv2.waitKey(10) == escape:
        break
    if frameCnt == 100:
        break
    frameCnt += 1

print("num matched = ", matched)
videocapture1.release()
videocapture2.release()
cv2.destroyAllWindows()