import cv2
import mediapipe as mp
import time
import numpy as np
import HandTrackingModule as htm
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume 

wCam, hCam = 640, 489

cap = cv2.VideoCapture(0)  # Use camera index 0
cap.set(3, wCam)  # Set width
cap.set(4, hCam)  # Set height
pTime = 0

detector = htm.handDetector(maxHands=2, detectionCon=0.7, trackCon=0.7)
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))  # Get the audio endpoint volume interface
volumeRange = volume.GetVolumeRange()  # Get the volume range
minVol = volumeRange[0]  # Minimum volume level
maxVol = volumeRange[1]  # Maximum volume level


while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)
    if len(lmList) != 0:
        # print(lmList[4], lmList[8])  # Print coordinates of thumb and index finger

        x1, y1 = lmList[4][1], lmList[4][2]  # Thumb coordinates
        x2, y2 = lmList[8][1], lmList[8][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        
        cv2.circle(img, (x1, y1), 15, (255, 0, 0), cv2.FILLED)
        cv2.circle(img, (x2, y2), 15, (255, 0, 0), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0), 3)
        cv2.circle(img, (cx, cy), 15, (0, 255, 0), cv2.FILLED)


        length = math.hypot(x2 - x1, y2 - y1)  # Length of the line between thumb and index finger
        # print(length)

        vol = np.interp(length, [35, 200], [-65.25, 0])  # Volume range
        print(length, vol)
        volume.SetMasterVolumeLevel(vol, None)

        if length < 35:
            cv2.circle(img, (cx, cy), 15, (0, 0, 255), cv2.FILLED)

    # Replace the incorrect usage of 'volume' with the current volume level
    currentVol = volume.GetMasterVolumeLevel()  # Retrieve the current volume level

    # Draw the volume bar
    cv2.rectangle(img, (50, 150), (85, 400), (0, 255, 0), 3)  # Volume bar outline
    cv2.rectangle(img, (50, int(np.interp(currentVol, [-65.25, 0], [400, 150]))), (85, 400), (0, 255, 0), cv2.FILLED)

    cTime = time.time()
    fps = 1 / (cTime - pTime) if 'pTime' in locals() else 0
    pTime = cTime

    cv2.putText(img, f'FPS: {int(fps)}', (5, 70), cv2.FONT_HERSHEY_PLAIN,
                2, (255, 0, 0), 3)
    

    if not success:
        print("Failed to access the webcam.")
        break

    cv2.imshow("Image", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):  # Exit on pressing 'q'
        break

cap.release()
cv2.destroyAllWindows()


