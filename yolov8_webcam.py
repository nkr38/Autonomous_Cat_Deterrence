# 1/20/2024
# nkr38@drexel.edu

import cv2
from ultralytics import YOLO

# Load the YOLOv8 model
model = YOLO('yolov8n.pt')

# Open the video file
video_path = "C:/Users/noakr/Downloads/cat.mp4"
#cap = cv2.VideoCapture(video_path)  # For video testing
cap = cv2.VideoCapture(0) # For webcam

# Loop through the video frames
while cap.isOpened():
    # Read a frame from the video
    success, frame = cap.read()
    
    if success:
        # Run YOLOv8 inference on the frame
        results = model(frame, verbose= False, conf = .80)

        # Gather results
        boxes = results[0].boxes.xywh.cpu()
        clss = results[0].boxes.cls.cpu().tolist()
        confs = results[0].boxes.conf.float().cpu().tolist()

        # Find index of cat in list of class detections
        cat_index = clss.index(15) if 15 in clss else None

        if cat_index is not None:
            # Get information for the detected cat at the specific index
            cat_box = boxes[cat_index]
            cat_conf = confs[cat_index]

            # Calculate center coordinates
            x_center = (cat_box[0] + cat_box[2]) / 2
            y_center = (cat_box[1] + cat_box[3]) / 2

            print(f"Cat detected, Confidence Score: {cat_conf:.2f}, Center Coordinates: ({x_center:.2f}, {y_center:.2f})")
        
        # Visualize the results on the frame
        annotated_frame = results[0].plot()

        # Display the annotated frame
        cv2.imshow("YOLOv8 Inference", annotated_frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    else:
        break

cap.release()
cv2.destroyAllWindows()
