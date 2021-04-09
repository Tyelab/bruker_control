import cv2
import numpy as np

print("Connecting Camera...")
capture = cv2.VideoCapture('rtsp://S1148323@169.254.8.94')
print("Camera Captured")

while(True):
    ret, frame = capture.read()
    cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

capture.release()
cv2.destroyAllWindows()
