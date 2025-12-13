# Hand Detection

This document covers the computer vision pipeline for real-time hand tracking.

---

## Overview

The hand detection system uses a fine-tuned YOLO11n model to detect hands in webcam frames. Detected hand positions are normalized and passed to the game engine to control paddle movement.

---

## Model Architecture

**Base Model**: YOLO11n (nano variant)  
**Task**: Single-class object detection (`hand`)  
**Input Size**: 640×640 pixels  
**Output**: Bounding box coordinates + confidence score

### Why YOLO11n?

- Optimized for real-time inference (~10ms per frame)

- Small model size with minimal accuracy trade-off

- Native GPU acceleration via PyTorch/CUDA

---

## Dataset

### EgoHands Dataset

| Split | Images |
|-------|--------|
| Train | ~15,800 |
| Validation | ~2,400 |
| Test | ~1,300 |

**Source**: [EgoHands Dataset](http://vision.soic.indiana.edu/projects/egohands/) (Indiana University)

The dataset contains first-person video frames from Google Glass recordings of people playing cards, chess, puzzles, and Jenga—capturing diverse hand poses and lighting conditions.

### Data Preprocessing

1. **Polygon → Bounding Box**: Original segmentation masks converted to YOLO-format bounding boxes

2. **Normalization**: Coordinates normalized to `[0, 1]` range

3. **Format**: `class_id x_center y_center width height`

```{md}
# Example annotation (hand.txt)
0 0.523438 0.412500 0.156250 0.225000
0 0.734375 0.687500 0.187500 0.250000
```

---

## Training Pipeline

### Configuration

```yaml
task: detect
model: yolo11n.pt
data: datasets/data.yaml
epochs: 100
imgsz: 640
batch: 8
patience: 10  # Early stopping
```

### Training Command

```python
from ultralytics import YOLO

model = YOLO('yolo11n.pt')
model.train(
    data='./datasets/data.yaml',
    epochs=100,
    imgsz=640,
    batch=8,
    name='hand_detection_11n',
    patience=10
)
```

---

## Inference Pipeline

### HandDetector Class

The `HandDetector` class runs in a **separate thread** to prevent blocking the game loop.

```python
class HandDetector:
    def __init__(self, model_path, model_name):
        self.cap = cv2.VideoCapture(0)
        self.model = YOLO(model_path)
        self._lock = threading.Lock()
        
    def detect_hands(self):
        """Continuously process frames and update hand positions."""
        while self._running:
            success, frame = self.cap.read()
            frame = frame[:, ::-1, :]  # Mirror for intuitive control
            
            result = self.model(frame, conf=0.5)
            
            for box in result[0].boxes:
                # Normalize y-coordinate
                y_center = (box.xyxy[0][1] + box.xyxy[0][3]) / 2
                normalized_y = y_center / self.frame_height
                
                # Assign to left or right player
                if x_center < midpoint:
                    self.latest_l_player_norm_y = normalized_y
                else:
                    self.latest_r_player_norm_y = normalized_y
```

### Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Frame mirroring** | Natural mapping—move hand right, paddle moves right |
| **Thread-safe access** | `threading.Lock()` prevents race conditions |
| **Confidence threshold** | `conf=0.5` filters low-confidence detections |
| **Normalized coordinates** | Resolution-independent paddle positioning |

---

## Model Comparison

Three models were trained and evaluated:

| Model | Parameters | mAP50 | Inference (ms) |
|-------|------------|-------|----------------|
| YOLOv8s | 11.2M | High | ~12 |
| YOLO11s | 9.4M | Higher | ~15 |
| **YOLO11n** | 2.6M | High | **~10** |

**Selected**: YOLO11n for optimal speed-accuracy balance in real-time gaming.

---

## Demo

<!-- TODO: Add hand detection visualization -->
<p align="center">
  <em>🖐️ Detection Visualization Coming Soon</em>
</p>

<!-- 
Uncomment when video is available:
<p align="center">
  <video src="../assets/hand_detection_demo.mp4" width="600" controls></video>
</p>
-->

---

## References

```bibtex
@InProceedings{Bambach_2015_ICCV,
  author = {Bambach, Sven and Lee, Stefan and Crandall, David J. and Yu, Chen},
  title = {Lending A Hand: Detecting Hands and Recognizing Activities 
           in Complex Egocentric Interactions},
  booktitle = {IEEE International Conference on Computer Vision (ICCV)},
  year = {2015}
}

@software{yolo11_ultralytics,
  author = {Glenn Jocher and Jing Qiu},
  title = {Ultralytics YOLO11},
  year = {2024},
  url = {https://github.com/ultralytics/ultralytics}
}
```
