import pygame
import numpy as np
import time
from typing import List
from hand_detector import HandDetector
from paddle import Paddle
from ball import Ball
import threading

class Game:
    def __init__(self):

        pygame.init()
        
        self.hand_detector = HandDetector(model_path='./model_training/runs/detect/hand_detection_11n/weights/best.pt', name="yolo11n")
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
    
    def update(self):
        for ball in self.balls:
            
            l_edge = ball.x - ball.radius
            r_edge = ball.x + ball.radius
            t_edge = ball.y - ball.radius
            b_edge = ball.y + ball.radius
            
            if t_edge <= 0:
                ball.velocity[1] = -ball.velocity[1]
            if b_edge >= self.screen_height:
                ball.velocity[1] = -ball.velocity[1]
                
            if r_edge <= 0:
                self.playerB["score"] += 1
                self.balls.remove(ball)
                self.add_new_ball(ball.DT)
            if l_edge >= self.screen_width:
                self.playerA["score"] += 1
                self.balls.remove(ball)
                self.add_new_ball(ball.DT)

            if ball.velocity[0] > 0:
                if r_edge >= self.playerB["paddle"].x and ball.y >= self.playerB["paddle"].y and ball.y <= self.playerB["paddle"].y + self.playerB["paddle"].height:
                    ball.velocity[0] = -ball.velocity[0]
            if ball.velocity[0] < 0:
                if l_edge <= self.playerA["paddle"].x + self.playerA["paddle"].width and ball.y >= self.playerA["paddle"].y and ball.y <= self.playerA["paddle"].y + self.playerA["paddle"].height:
                    ball.velocity[0] = -ball.velocity[0]
            
            self.playerA["paddle"].update(self.hand_detector.get_latest_left_player_y(), self.screen_height)
            self.playerB["paddle"].update(self.hand_detector.get_latest_right_player_y(), self.screen_height)
            
            ball.update()
               

    def add_new_ball(self, DT):
        x = np.random.randint(self.screen_width//4, 3*self.screen_width//4)
        y = np.random.randint(0, self.screen_height)
        velocity = [(-1 if np.random.uniform(-1, 1) < 0 else 1)*np.random.uniform(250, 300),
                    (-1 if np.random.uniform(-1, 1) < 0 else 1)*np.random.uniform(100, 200)]
        self.balls.append(Ball(x, y, velocity, DT))
        
    # # visualize collision boundaries
    # def draw_debug_boxes(self, ball):
    #     # Draw ball boundaries
    #     pygame.draw.rect(self.screen, (255, 0, 0), (
    #         ball.x - ball.radius,
    #         ball.y - ball.radius,
    #         ball.radius * 2,
    #         ball.radius * 2
    #     ), 1)  # The last parameter 1 means draw outline only
    
    # def remove_ball(self):
    #     self.balls.pop()
    
    # def speed_up_balls(self):
    #     for ball in self.balls:
    #         if np.abs(ball.velocity[0]) < 20:
    #             ball.velocity[0] = ball.velocity[0] * 1.5
    #         if np.abs(ball.velocity[1]) < 20:
    #             ball.velocity[1] = ball.velocity[1] * 1.5
        
    # def slow_down_balls(self):
    #     for ball in self.balls:
    #         if np.abs(ball.velocity[0]) > 0:
    #             ball.velocity[0] = ball.velocity[0] * 0.5
    #         if np.abs(ball.velocity[1]) > 0:
    #             ball.velocity[1] = ball.velocity[1] * 0.5
        
    def run(self):
        np.random.seed(int(time.time()))
        paused = False
        running = True
        clock = pygame.time.Clock()
        FPS = 60
        DT = (1/FPS)
        
        self.add_new_ball(DT)
        
        for i in range(10, 0, -1):
            time.sleep(1)
            print(f"{i}...")
        
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
                
                if not paused:
                    
                    self.update()

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
            
            pygame.quit()  # Clean up pygame