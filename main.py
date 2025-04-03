import pygame
import cv2
from ultralytics import YOLO
import numpy as np
from typing import List, Tuple
import time

class HandDetector:
    def __init__(self, model_path: str = './model_training/runs/detect/hand_detection_11n/weights/best.pt'):
        self.model = YOLO(model_path)
        self.cap = cv2.VideoCapture(0)
        
    def get_hand_position(self) -> float:
        ret, frame = self.cap.read()
        if not ret:
            return 0.0
            
        results = self.model(frame)
        # Placeholder for hand detection logic
        # Will be implemented when we have the actual model
        return 0.0
        
    def release(self):
        self.cap.release()

class Ball:
    def __init__(self, x: float, y: float, velocity: Tuple[float, float]):
        self.x = x
        self.y = y
        self.velocity = velocity
        self.radius = 10
        
    def update(self, screen_width: int, screen_height: int) -> bool:
        # Update position based on velocity
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        
        # Handle collisions with walls
        if self.x - self.radius <= 0 or self.x + self.radius >= screen_width:
            self.velocity = (-self.velocity[0], self.velocity[1])
            
        if self.y - self.radius <= 0:
            self.velocity = (self.velocity[0], -self.velocity[1])
            
        # Check if ball fell off screen
        return self.y <= screen_height

class Paddle:
    def __init__(self, x: float, y: float, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
    def update(self, hand_x: float, screen_width: int):
        # Update paddle position based on hand position
        self.x = max(0, min(screen_width - self.width, hand_x - self.width/2))

class Game:
    def __init__(self):
        pygame.init()
        self.screen_width = 800
        self.screen_height = 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Air Paddle")
        
        self.hand_detector = HandDetector()
        self.paddle = Paddle(self.screen_width/2, self.screen_height - 50, 100, 20)
        self.balls: List[Ball] = []
        self.score = 0
        self.start_time = time.time()
        self.last_ball_add = time.time()
        
    def add_new_ball(self):
        x = np.random.randint(0, self.screen_width)
        y = np.random.randint(0, self.screen_height/2)
        velocity = (np.random.uniform(-5, 5), np.random.uniform(-5, 5))
        self.balls.append(Ball(x, y, velocity))
        
    def run(self):
        running = True
        clock = pygame.time.Clock()
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
            # Update game state
            hand_x = self.hand_detector.get_hand_position()
            self.paddle.update(hand_x, self.screen_width)
            
            # Update balls
            self.balls = [ball for ball in self.balls if ball.update(self.screen_width, self.screen_height)]
            
            # Add new balls periodically
            if time.time() - self.last_ball_add > 5:  # Add new ball every 5 seconds
                self.add_new_ball()
                self.last_ball_add = time.time()
                
            # Update score
            self.score = int(time.time() - self.start_time)
            
            # Draw everything
            self.screen.fill((0, 0, 0))
            
            # Draw paddle
            pygame.draw.rect(self.screen, (255, 255, 255), 
                           (self.paddle.x, self.paddle.y, self.paddle.width, self.paddle.height))
            
            # Draw balls
            for ball in self.balls:
                pygame.draw.circle(self.screen, (255, 255, 255), 
                                 (int(ball.x), int(ball.y)), ball.radius)
                
            # Draw score
            font = pygame.font.Font(None, 36)
            score_text = font.render(f"Score: {self.score}", True, (255, 255, 255))
            self.screen.blit(score_text, (10, 10))
            
            pygame.display.flip()
            clock.tick(60)
            
        pygame.quit()
        self.hand_detector.release()

if __name__ == "__main__":
    game = Game()
    game.run()
