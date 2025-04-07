class Ball:
    def __init__(self, x: float, y: float, velocity: list[float, float], DT: float):
        self.x = x
        self.y = y
        self.velocity = velocity
        self.radius = 15
        self.DT = DT
        
    def update(self):
        # Update position based on velocity
        self.x += self.velocity[0] * self.DT
        self.y += self.velocity[1] * self.DT
        
