import sys
import cv2


def videoValidity(filename):
    """Check if a given file is a valid video"""
    try:
        video = cv2.VideoCapture(filename)
        if not video.isOpened():
            raise NameError("Video is incompatible")
    except cv2.error as e:
        print("ERROR: ", e)
        return False
    except Exception as e:
        print("EXCEPTION: ", e)
        return False
    else:
        print("Valid")
        return True
