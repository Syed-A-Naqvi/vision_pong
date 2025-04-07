# VisionPong: Vision-Based Interactive Ball Simulation

## Interactive Hand-Controlled Pong Game

### Overview
VisionPong is an interactive, computer vision-based Pong game where two players control paddles using real-time hand tracking. By combining robust hand detection with physics-based ball simulation, the game delivers a dynamic and engaging experience reminiscent of classic Pong. The system employs lightweight YOLO models for precise hand tracking and an event-driven collision manager for realistic ball dynamics.

### Table of Contents
1. [Features](#features)
2. [Technology Stack](#technology-stack)
3. [Installation](#installation)
4. [Directory Structure](#directory-structure)
5. [Usage](#usage)
6. [How It Works](#how-it-works)
7. [Challenges and Solutions](#challenges-and-solutions)
8. [Future Improvements](#future-improvements)
9. [License](#license)

### Features
- **Real-Time Hand Detection:** Utilizes a webcam feed to track hand positions with fine-tuned YOLO models.
- **Physics-Based Simulation:** Implements realistic ball bounces based on Newtonian mechanics.
- **Responsive Paddle Control:** Hand movements are mapped directly to paddle position.
- **Scoring & Difficulty:** Tracks scores and supports multiple balls for increased challenge.
- **Low Latency:** Achieves fast, responsive gameplay through optimized algorithms and multithreading.

### Technology Stack
- **Python**: Main programming language.
- **OpenCV**: For real-time hand detection and image processing.
- **YOLO Models**: Fine-tuned YOLO11n, YOLO11s, and YOLOv8s for hand detection.
- **Pygame**: For game visualization and graphics.
- **NumPy**: For efficient numerical computations.
- **Multithreading**: Ensures real-time performance by parallelizing vision and simulation processes.

### Installation
1. **Clone this repository:**
   ```bash
   git clone https://github.com/yourusername/VisionPong.git
   cd VisionPong
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run main python file:**
   ```bash
   python Simulation/main.py
   ```

**NOTE:** A webcam is required for hand tracking.

4. **Directory Structure:**
    ```bash
   VisionPong/
   ├── main.py              # Entry point of the game
   ├── README.md            # Project documentation (this file)
   ├── requirements.txt     # Python package requirements
   ├── src/                 # Source code for game logic
   │   ├── detection/       # Computer vision scripts for hand detection
   │   ├── physics/         # Physics and collision modules
   │   └── utils/           # Utility functions and helpers
   ├── assets/              # Images, sounds, and other assets
   └── LICENSE              # Project license (MIT)
   ```

5. **Usage:*
   - Ensure your hand is clearly visible on the webcame.
   - Keep your hand on the left or right side of the frame. (Left side is player 1, right side is player 2)
   - Move your hand up and down to stop balls from crossing your side of the screen.
   - As the game progresses, multiple balls may start appearing, at varying speeds.
  
6. **How it Workds:**
  - 

   

