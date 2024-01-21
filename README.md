<img src="https://github.com/nkr38/Autonomous_Cat_Deterrence/assets/69133832/7a802287-cad0-42df-8e41-28bd945d1995" alt="render" width="50%">
# Autonomous Cat Deterrence

Welcome to the repository for the Autonomous Cat Deterrence senior design group project.

## Project Overview

The project aims to autonomously detect and deter cats using the YOLOv8 object detection model.

## Features

- Real-time cat detection using YOLOv8
- Displaying confidence scores and center coordinates of detected cats
- Visualizing detection results on video frames

## Project Structure

```plaintext
/
|-- src/
|   |-- yolov8_webcam.py
|-- models/
|   |-- yolov8n.pt
|-- images/
|   |-- render.png
|   |-- kitchenrender.png
|-- README.txt
```

## Getting Started

### Prerequisites

- Python 3.x
- OpenCV (`pip install opencv-python`)
- Ultralytics (`pip install ultralytics`)

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/Autonomous_Cat_Deterrence.git
   ```
2. Navigate to the project directory:
   ```bash
   Copy code
   cd Autonomous_Cat_Deterrence
   ```
3. Run the script:
   ```bash
   Copy code
   python src/main.py
   ```
## Dependencies
- YOLOv8: Ultralytics YOLO

## Acknowledgments
Ultralytics YOLO for providing the YOLOv8 model

## Contact Information
For any inquiries, please contact:
Email: nkr38@drexel.edu
