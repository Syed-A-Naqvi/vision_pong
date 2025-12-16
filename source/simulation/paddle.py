class Paddle:
    def __init__(self, x: float, y: float, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
    def update(self, hand_y_norm: float, screen_height: int):
        
        y = (hand_y_norm * screen_height) - (self.height/2)
        
        # Update paddle position based on hand position
        self.y = max(0, min(screen_height - self.height, y))
