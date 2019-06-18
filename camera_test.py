import time
import cv2
from imutils.video import VideoStream


vs = VideoStream(usePiCamera=True).start()
time.sleep(2.0)

while 1:
	frame = vs.read()
	cv2.imshow('Cam Test', frame)
	cv2.waitKey(1)

