import cv2
from ultralytics import YOLO
import matplotlib.pyplot as plt
from collections import defaultdict

# Load YOLO model
model = YOLO('yolov8n.pt')  # Choose the appropriate YOLOv8 model - original model 
# foduucom/stockmarket-future-prediction
#model = YOLO('foduucom/stockmarket-future-prediction/best.pt')  # Choose the appropriate YOLOv8 model

# Access screen capture
screen_width = 1920  # Adjust to your screen resolution
screen_height = 1080
cap = cv2.VideoCapture(0)  # 0 for default camera, or provide video file path
cap.set(cv2.CAP_PROP_FRAME_WIDTH, screen_width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, screen_height)

# Initialize chart
class_counts = defaultdict(int)
plt.ion()  # Turn on interactive mode for live updates
fig, ax = plt.subplots()

while True:
    # Read frame from capture
    ret, frame = cap.read()
    if not ret:
        break

    # Detect objects
    results = model(frame)  

    # Process results
    for result in results:
        boxes = result.boxes
        for box in boxes:
            class_id = result.names[int(box.cls[0])]
            class_counts[class_id] += 1

            # Draw bounding boxes and labels
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f"{class_id}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    # Update chart
    classes, counts = zip(*class_counts.items())
    ax.clear()
    ax.bar(classes, counts)
    plt.draw()
    plt.pause(0.001)  # Allow time for chart to update

    # Display frame
    cv2.imshow("YOLO Object Detection", frame)
    if cv2.waitKey(1) == ord('q'):  # Press 'q' to exit
        break

cap.release()
cv2.destroyAllWindows()