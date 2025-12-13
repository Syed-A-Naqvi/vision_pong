# Game Architecture

This document covers the multithreaded design and game loop structure.

---

## Overview

The game uses a **two-thread architecture** to decouple computer vision from game rendering:

```
┌─────────────────────────────────────────────────────────┐
│                      Main Thread                        │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐ │
│  │  Game Loop  │───▶│   Update    │───▶│   Render    │ │
│  │   (60 FPS)  │    │   Physics   │    │   Pygame    │ │
│  └─────────────┘    └─────────────┘    └─────────────┘ │
│         ▲                                               │
│         │ read normalized y-coords                      │
│         │                                               │
│  ┌──────┴──────────────────────────────────────────┐   │
│  │              Thread-Safe Interface               │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                          ▲
                          │
┌─────────────────────────┴───────────────────────────────┐
│                    Detector Thread                       │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │
│  │   Webcam    │───▶│   YOLO      │───▶│   Update    │  │
│  │   Capture   │    │  Inference  │    │  Positions  │  │
│  └─────────────┘    └─────────────┘    └─────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## Thread Design

### Why Multithreading?

| Single-threaded | Multithreaded |
|-----------------|---------------|
| Vision blocks game loop | Vision runs independently |
| Frame drops during inference | Consistent 60 FPS |
| ~30 FPS max | 60+ FPS achievable |

### Thread Communication

Threads communicate via **shared state with locking**:

```python
class HandDetector:
    def __init__(self):
        self._lock = threading.Lock()
        self.latest_l_player_norm_y = 0
        self.latest_r_player_norm_y = 0
    
    def detect_hands(self):
        # Producer: writes positions
        with self._lock:
            self.latest_l_player_norm_y = normalized_y
    
    def get_latest_left_player_y(self):
        # Consumer: reads positions
        with self._lock:
            return self.latest_l_player_norm_y
```

### Thread Lifecycle

```python
# Game initialization
self.hand_detector = HandDetector(model_path='...')
self.detector_thread = threading.Thread(
    target=self.hand_detector.detect_hands,
    daemon=True  # Auto-terminates with main thread
)
self.detector_thread.start()
```

---

## Game Loop

### Main Loop Structure

```python
def run(self):
    clock = pygame.time.Clock()
    FPS = 60
    DT = 1/FPS
    
    while running:
        # 1. Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # 2. Update game state
        self.update(buffer_time_elapsed, DT)
        
        # 3. Render
        self.draw()
        
        # 4. Cap framerate
        clock.tick(FPS)
```

### Update Phase

The update phase handles:
1. **Paddle positions** – Read from detector thread
2. **Ball physics** – Wall/paddle/ball collisions
3. **Scoring** – Boundary exits

```python
def update(self, buffer_time_elapsed, DT):
    # Update paddles from hand detection
    self.playerA["paddle"].update(
        self.hand_detector.get_latest_left_player_y(), 
        self.screen_height
    )
    
    # Process collisions and physics
    for ball in self.balls:
        # Wall collisions
        # Paddle collisions
        # Scoring
    
    # Ball-ball collisions
    self.collision_manager.process_collisions(DT)
```

---

## Game Entities

### Paddle

Maps normalized hand position to screen coordinates:

```python
class Paddle:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
    
    def update(self, hand_y_norm, screen_height):
        # Convert normalized [0,1] to screen coordinates
        y = (hand_y_norm * screen_height) - (self.height/2)
        # Clamp to screen bounds
        self.y = max(0, min(screen_height - self.height, y))
```

### Player State

Players are represented as dictionaries:

```python
self.playerA = {
    "paddle": Paddle(50, screen_height//2, 10, 100),
    "score": 0
}
self.playerB = {
    "paddle": Paddle(screen_width - 50, screen_height//2, 10, 100),
    "score": 0
}
```

---

## Buffer Period

A 5-second buffer at game start allows players to position hands:

```python
buffer_start_time = time.time()

# In update loop:
buffer_time_elapsed = time.time() - buffer_start_time

if buffer_time_elapsed < 5:
    # Balls bounce off inner boundaries (safety zone)
    if ball_left < screen_width/5 or ball_right > 4*screen_width/5:
        ball.velocity[0] = -ball.velocity[0]
else:
    # Normal paddle collision detection
    ...
```

Visual indicator shows buffer zone with red lines.

---

## Rendering

### Draw Order

1. Clear screen (black background)
2. Draw paddles (white rectangles)
3. Draw balls (white circles)
4. Draw center line (dotted)
5. Draw buffer zone lines (if active)
6. Draw UI (title, scores)

```python
# Paddles
pygame.draw.rect(screen, WHITE, (paddle.x, paddle.y, paddle.width, paddle.height))

# Balls
pygame.draw.circle(screen, WHITE, (int(ball.x), int(ball.y)), ball.radius)

# Center line (dotted)
for y in range(0, screen_height, 20):
    pygame.draw.line(screen, WHITE, (screen_width//2, y), (screen_width//2, y+10))
```

---

## Cleanup

Proper resource cleanup on exit:

```python
finally:
    # Stop detector thread
    self.hand_detector.release()
    
    # Wait for thread to finish
    self.detector_thread.join(timeout=1.0)
    
    # Show winner
    display_winner()
    
    # Cleanup pygame
    pygame.quit()
```

---

## Game Flow

```
┌─────────────┐
│    Start    │
└──────┬──────┘
       ▼
┌─────────────┐
│  Initialize │  Spawn 4 balls
│   Game      │  Start detector thread
└──────┬──────┘
       ▼
┌─────────────┐
│  Countdown  │  3... 2... 1...
│  (3 sec)    │
└──────┬──────┘
       ▼
┌─────────────┐
│   Buffer    │  5-second safety period
│   Period    │
└──────┬──────┘
       ▼
┌─────────────┐
│  Game Loop  │◀─────┐
└──────┬──────┘      │
       │             │
       ▼             │
   ┌───────┐    ┌────┴────┐
   │ Balls │ No │  Update  │
   │ left? ├───▶│ & Render │
   └───┬───┘    └──────────┘
       │ Yes
       ▼
┌─────────────┐
│  Game Over  │  Display winner
└──────┬──────┘
       ▼
┌─────────────┐
│   Cleanup   │  Release resources
└─────────────┘
```

---

## Configuration

Key configurable parameters:

| Parameter | Value | Location |
|-----------|-------|----------|
| Screen size | 800×600 | `game.py` |
| FPS | 60 | `game.py` |
| Paddle size | 10×100 | `game.py` |
| Ball radius | 15 | `ball.py` |
| Initial balls | 4 | `game.py` |
| Buffer duration | 5 sec | `game.py` |
| Confidence threshold | 0.5 | `hand_detector.py` |
