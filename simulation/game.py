import pygame
import numpy as np
import time
from typing import List
from hand_detector import HandDetector
from paddle import Paddle
from ball import Ball
import threading
from collision_manager import CollisionManager

class Game:
    def __init__(self):

        pygame.init()
        
        self.hand_detector = HandDetector(model_path='./model_training/runs/detect/hand_detection_11n/weights/best.pt', model_name="yolo11n")
        self.detector_thread = threading.Thread(target=self.hand_detector.detect_hands,
                                                daemon=True)
        self.detector_thread.start()

        self.screen_width = 800
        self.screen_height = 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Vision Pong")
        
        self.playerA = {
            "paddle": Paddle(50, self.screen_height//2 - 50, 10, 100),  
            "score": 0
            }
        self.playerB = {
            "paddle": Paddle(self.screen_width - 50, self.screen_height//2 - 50, 10, 100),
            "score": 0
            }
        
        self.balls: List[Ball] = []
        
        self.collision_manager = CollisionManager(self.balls)
        
    def add_new_ball(self, DT):
        x = np.random.randint(self.screen_width//4, 3*self.screen_width//4)
        y = np.random.randint(0, self.screen_height)
        velocity = [(-1 if np.random.uniform(-1, 1) < 0 else 1)*np.random.uniform(150, 200),
                    (-1 if np.random.uniform(-1, 1) < 0 else 1)*np.random.uniform(50, 100)]
        self.balls.append(Ball(x, y, velocity, DT))
                
    def update(self, buffer_time_elapsed, DT):
        
        A = self.playerA["paddle"]
        B = self.playerB["paddle"]

        collision_occurred = False

        # Handle boundary collisions (top/bottom) and scoring.
        for ball in self.balls[:]:
            top_edge = ball.y - ball.radius
            bot_edge = ball.y + ball.radius
            if top_edge <= 0 or bot_edge >= self.screen_height:
                ball.velocity[1] = -ball.velocity[1]
                collision_occurred = True

            # Check scoring.
            if ball.x - ball.radius <= 0:
                self.playerB["score"] += 1
                self.balls.remove(ball)
                collision_occurred = True
            elif ball.x + ball.radius >= self.screen_width:
                self.playerA["score"] += 1
                self.balls.remove(ball)
                collision_occurred = True
            
            # Optional: Handle paddle collisions.
            left_edge = ball.x - ball.radius
            right_edge = ball.x + ball.radius
            if(buffer_time_elapsed < 5):
                if (left_edge < self.screen_width//5 or right_edge > 4*self.screen_width//5):
                    ball.velocity[0] = -ball.velocity[0]
                    collision_occurred = True
            else:
                if ((left_edge < A.x + A.width and left_edge > A.x and A.y < ball.y < A.y + A.height) or 
                    (right_edge > B.x and right_edge < B.x + B.width and B.y < ball.y < B.y + B.height)):
                    ball.velocity[0] = -1.1*ball.velocity[0]
                    collision_occurred = True

        # If any changes occurred (including removals), repopulate the next event.
        if collision_occurred:
            self.collision_manager.repopulate_next_event()

        # Update paddles based on hand detection.
        self.playerA["paddle"].update(self.hand_detector.get_latest_left_player_y(), self.screen_height)
        self.playerB["paddle"].update(self.hand_detector.get_latest_right_player_y(), self.screen_height)

        # Process ball–ball collisions (and advance simulation) over DT seconds.
        self.collision_manager.process_collisions(DT)

  
        
    def run(self):
        np.random.seed(int(time.time()))
        paused = False
        running = True
        clock = pygame.time.Clock()
        FPS = 60
        DT = (1/FPS)
        
        self.add_new_ball(DT)
        self.add_new_ball(DT)
        self.add_new_ball(DT)
        self.add_new_ball(DT)
        
        for i in range(3, 0, -1):
            time.sleep(1)
            print(f"{i}...")
        
        buffer_start_time = time.time()
        
        try:
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_q:
                            running = False
                        if event.key == pygame.K_p:
                            paused = not paused
                
                if not self.hand_detector._running:
                    print("Hand tracking not running. exiting game.")
                    break
                
                if len(self.balls) == 0:
                    print("No balls left. exiting game.")
                    break
                
                if not paused:
                    
                    buffer_time_elapsed = time.time() - buffer_start_time
                    
                    self.update(buffer_time_elapsed, DT)

                    # Draw everything
                    self.screen.fill((0, 0, 0))

                    # Draw paddles
                    pygame.draw.rect(self.screen, (255, 255, 255), 
                                   (self.playerA["paddle"].x, self.playerA["paddle"].y, 
                                    self.playerA["paddle"].width, self.playerA["paddle"].height))
                    pygame.draw.rect(self.screen, (255, 255, 255), 
                                   (self.playerB["paddle"].x, self.playerB["paddle"].y, 
                                    self.playerB["paddle"].width, self.playerB["paddle"].height))

                    # Draw balls
                    for ball in self.balls:
                        pygame.draw.circle(self.screen, (255, 255, 255), 
                                         (int(ball.x), int(ball.y)), ball.radius)

                    # Draw dotted center line
                    for y in range(0, self.screen_height, 20):
                        pygame.draw.line(self.screen, (255, 255, 255), 
                                       (self.screen_width//2, y), 
                                       (self.screen_width//2, y+10))
                    
                    # initial buffer period lines
                    if(buffer_time_elapsed < 5):
                        pygame.draw.line(self.screen, (255, 0, 0),
                                       (self.screen_width//5, 0),
                                       (self.screen_width//5, self.screen_height))
                        pygame.draw.line(self.screen, (255, 0, 0),
                                       (4*self.screen_width//5, 0), 
                                       (4*self.screen_width//5, self.screen_height))

                    # Draw title
                    title_font = pygame.font.Font(None, 48)
                    title_text = title_font.render("Vision Pong", False, (255, 255, 255))
                    self.screen.blit(title_text, (self.screen_width//2 - title_text.get_width()//2, 10))
                    
                    # Draw score
                    font = pygame.font.Font(None, 24)
                    score_text_a = font.render(f"Player 1: {self.playerA['score']}", 
                                            False, (255, 255, 255))
                    score_text_b = font.render(f"Player 2: {self.playerB['score']}", 
                                            False, (255, 255, 255))
                    self.screen.blit(score_text_a, (self.screen_width//4, 50))
                    self.screen.blit(score_text_b, (3*self.screen_width//4 - score_text_b.get_width(), 50))

                    pygame.display.flip()
                    clock.tick(FPS)
        
        except Exception as e:
            print(f"Error in game loop: {e}")
        
        finally:
            # Clean up resources in the correct order
            if hasattr(self, 'hand_detector'):
                self.hand_detector.release()  # Signal thread to stop and release CV2 resources
            
            if hasattr(self, 'detector_thread') and self.detector_thread.is_alive():
                self.detector_thread.join(timeout=1.0)  # Wait for thread to finish
            
            # Clear screen and show winner
            self.screen.fill((0, 0, 0))
            winner_font = pygame.font.Font(None, 74)
            winner_text = winner_font.render(
                f"Player {1 if self.playerA['score'] > self.playerB['score'] else 2} Wins!", 
                False, 
                (255, 255, 255)
            )
            text_rect = winner_text.get_rect(center=(self.screen_width//2, self.screen_height//2))
            self.screen.blit(winner_text, text_rect)
            pygame.display.flip()
            pygame.time.wait(2000)  # Show winner for 2 seconds
                
            
            pygame.quit()  # Clean up pygame