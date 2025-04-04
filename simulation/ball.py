from typing import Tuple

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