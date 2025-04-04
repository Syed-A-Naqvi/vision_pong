class Paddle:
    def __init__(self, x: float, y: float, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
    def update(self, hand_x: float, screen_width: int):
        # Update paddle position based on hand position
        self.x = max(0, min(screen_width - self.width, hand_x - self.width/2))