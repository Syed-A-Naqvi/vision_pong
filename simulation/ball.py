class Ball:
    def __init__(self, x: float, y: float, velocity: list[float, float], DT: float):
        self.original_x = x
        self.original_y = y
        self.original_velocity = velocity
        self.x = x
        self.y = y
        self.velocity = velocity
        self.radius = 10
        self.DT = DT
        
    def update(self):
        # Update position based on velocity
        self.x += self.velocity[0] * self.DT
        self.y += self.velocity[1] * self.DT
        
