import cv2
import numpy as np
from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator, colors
from mss import mss
from ultralytics import YOLO
import numpy as np
import cv2


# Replace the relative path to your weight file
model_path = 'D://py_code_workspace//weights//custom_yolov8.pt'

model = YOLO(model_path)

#model = YOLO("yolov8n.pt")
names = model.model.names
import time
with mss() as sct:
    monitor = sct.monitors[1]
    while True:
        #time.sleep(2)
        screenshot = sct.grab(monitor)
        frame = np.array(screenshot)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
        if monitor:
            results = model.track(frame, persist=True, verbose=False)
            boxes = results[0].boxes.xyxy.cpu()

            if results[0].boxes.id is not None:

                # Extract prediction results
                clss = results[0].boxes.cls.cpu().tolist()
                track_ids = results[0].boxes.id.int().cpu().tolist()
                confs = results[0].boxes.conf.float().cpu().tolist()

                # Annotator Init
                annotator = Annotator(frame, line_width=2)
                print("annotating")
                for box, cls, track_id in zip(boxes, clss, track_ids):
                    annotator.box_label(box, color=colors(int(cls), True), label=names[int(cls)])
            cv2.imshow('Frame', frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        else:
            break
    cv2.destroyAllWindows()