import cv2
import numpy as np
import time

print("Connecting Camera...")
capture = cv2.VideoCapture('http://BRUKER@169.254.8.94:10/0')

if not capture.isOpened():
    print("Can't open camera")
    exit()


while(True):
    ret, frame = capture.read()
    if not ret:
        print("Can't receive frame")
    cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

capture.release()
cv2.destroyAllWindows()
