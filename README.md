# 🎮 Vision Pong

**Real-Time Gesture-Controlled Pong Using Computer Vision**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![YOLO](https://img.shields.io/badge/YOLO-v11-green.svg)](https://github.com/ultralytics/ultralytics)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.x-red.svg)](https://opencv.org)
[![Pygame](https://img.shields.io/badge/Pygame-2.x-yellow.svg)](https://pygame.org)

---

## 🎯 Overview

Vision Pong transforms the classic Pong game into an immersive experience by replacing keyboard controls with **real-time hand tracking**. Using a fine-tuned YOLO model and your webcam, simply move your hands to control the paddles.

The system combines:

- **Computer Vision**: Custom-trained YOLO11n for robust hand detection

- **Physics Simulation**: Event-driven collision detection with elastic ball dynamics

- **Multithreading**: Parallel vision and game loops for low-latency gameplay

---

## 🎬 Demo

<!-- TODO: Add gameplay demo video -->
<p align="center">
  <em>🎥 Gameplay Demo Coming Soon</em>
</p>

<!-- 
Uncomment and replace with actual video path:
<p align="center">
  <video src="assets/demo_gameplay.mp4" width="700" controls></video>
</p>
-->

<!-- TODO: Add hand detection demo -->
<p align="center">
  <em>🖐️ Hand Detection Demo Coming Soon</em>
</p>

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| **🖐️ Hand Tracking** | Real-time hand detection using fine-tuned YOLO11n |
| **⚡ Low Latency** | Multithreaded architecture separates vision from game logic |
| **🎱 Physics Engine** | Predictive collision detection for ball-ball interactions |
| **📈 Progressive Difficulty** | Multiple balls spawn as gameplay continues |
| **🎯 Two-Player** | Left/right hand positioning maps to Player 1/2 |

---

## 🏗️ Architecture

```{md}
┌─────────────────────┐     ┌─────────────────────┐
│   Webcam Feed       │────▶   Hand Detector     │
│   (OpenCV)          │     │   (YOLO11n)         │
└─────────────────────┘     └──────────┬──────────┘
                                       │
                                       │  normalized y-coords
┌─────────────────────┐      ┌──────── ▼ ──────────┐
│   Collision Manager │◀──▶│   Game Engine       │
│   (Physics)         │      │   (Pygame)          │
└─────────────────────┘      └─────────────────────┘
```

---

## 🛠️ Tech Stack

- **Python 3.8+** – Core language
- **Ultralytics YOLO** – Hand detection model
- **OpenCV** – Webcam capture and frame processing
- **Pygame** – Game rendering and display
- **NumPy** – Physics calculations
- **Threading** – Parallel processing

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+

- Webcam

- CUDA-capable GPU *(recommended)*

### Installation

```bash
# Clone the repository
git clone https://github.com/Syed-A-Naqvi/air_paddle.git
cd air_paddle

# Install dependencies
pip install -r requirements.txt

# Run the game
python simulation/main.py
```

### Controls

| Action | Input |
|--------|-------|
| Move Player 1 paddle | Left-side hand (vertical movement) |
| Move Player 2 paddle | Right-side hand (vertical movement) |
| Pause | `P` key |
| Quit | `Q` key |

---

## 📁 Project Structure

```{md}
air_paddle/
├── simulation/           # Game source code
│   ├── main.py          # Entry point
│   ├── game.py          # Game loop and rendering
│   ├── hand_detector.py # YOLO-based hand tracking
│   ├── paddle.py        # Paddle entity
│   ├── ball.py          # Ball entity
│   └── collision_manager.py  # Physics engine
├── model_training/       # ML training pipeline
│   ├── training.ipynb   # Model fine-tuning
│   ├── testing.ipynb    # Evaluation & analysis
│   ├── datasets/        # YOLO-format dataset
│   └── runs/            # Training outputs
├── docs/                 # Documentation
└── requirements.txt
```

---

## 📊 Model Performance

Fine-tuned on the [EgoHands Dataset](http://vision.soic.indiana.edu/projects/egohands/) (~15,000+ training images).

| Model | mAP50 | Inference Time | Use Case |
|-------|-------|----------------|----------|
| **YOLO11n** | High | ~10ms | ✅ Production (balanced) |
| YOLO11s | Higher | ~15ms | Accuracy priority |
| YOLOv8s | High | ~12ms | Alternative |

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [Hand Detection](docs/hand_detection.md) | YOLO model training and inference pipeline |
| [Physics Engine](docs/physics_engine.md) | Collision detection and ball dynamics |
| [Game Architecture](docs/game_architecture.md) | Multithreaded design and game loop |

---

## 🔮 Future Improvements

- [ ] Single-player mode with AI opponent
- [ ] Gesture-based game controls (start, pause, restart)
- [ ] Sound effects and visual polish
- [ ] Configurable difficulty settings
- [ ] Web-based version using TensorFlow.js

---

## 📖 References

- [Ultralytics YOLO11](https://github.com/ultralytics/ultralytics)
- [EgoHands Dataset](http://vision.soic.indiana.edu/projects/egohands/) – Bambach et al., ICCV 2015
- [Oxford Hands Dataset](http://www.robots.ox.ac.uk/~vgg/data/hands/) – Mittal et al., BMVC 2011

---

## 📄 License

This project is for educational purposes.

---

<p align="center">
  <strong>Built by <a href="https://github.com/Syed-A-Naqvi">Arham Naqvi</a></strong>
</p>
