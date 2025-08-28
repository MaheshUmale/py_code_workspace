import cv2
import numpy as np
import mss
from ultralytics import YOLO
import time
# Load the YOLOv8 modelq
# model = YOLO("./weights/custom_yolov8.pt")  # You can choose a different YOLOv8 model here Original model here 
model = YOLO('foduucom/stockmarket-future-prediction/best.pt')
# Set up screen capture
with mss.mss() as sct:
    monitor = sct.monitors[1]  # Capture the primary monitor
    while True:
        # Capture the screen
        img = np.array(sct.grab(monitor))
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)  # Convert to BGR for OpenCV

        # Perform object detection
        results = model(img)

        # Visualize results
        annotated_frame = results[0].plot()
        cv2.imshow("Screen Detection", annotated_frame)

        if cv2.waitKey(1) == ord("q"):
            break

        time.sleep(2)

cv2.destroyAllWindows()