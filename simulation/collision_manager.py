from itertools import combinations
import heapq
import math

class CollisionManager:
    def __init__(self, balls, restitution=1.0):
        """
        Initialize the collision manager.
        
        Args:
            balls (list): List of ball objects. Each ball must have attributes:
                          x, y, velocity (list/tuple of 2 elements), and radius.
            restitution (float): Restitution coefficient (use 1.0 for fully elastic collisions).
        """
        try:
            self.balls = balls
            self.restitution = restitution
            self.collision_heap = []
            # This attribute stores the next collision event, a tuple:
            # (time_remaining, ball1, ball2, pos1, pos2)
            self.next_event = None
            self.populate_next_events()
        except Exception as e:
            print(f"Error initializing CollisionManager: {e}")
            raise

    def compute_collision_time(self, ball1, ball2):
        """
        Compute the time until collision between two balls using the quadratic formula.
        Returns:
            float: Predicted collision time (a positive number) or math.inf if no collision.
        """
        try:
            dx = ball2.x - ball1.x
            dy = ball2.y - ball1.y
            dvx = ball2.velocity[0] - ball1.velocity[0]
            dvy = ball2.velocity[1] - ball1.velocity[1]
            two_r = ball1.radius + ball2.radius

            a = dvx**2 + dvy**2
            b = 2 * (dx * dvx + dy * dvy)
            c = dx**2 + dy**2 - two_r**2

            if a == 0:
                return math.inf  # Parallel movement.

            disc = b**2 - 4 * a * c
            if disc < 0:
                return math.inf  # No real solution: no collision.

            sqrt_disc = math.sqrt(disc)
            t1 = (-b - sqrt_disc) / (2 * a)
            t2 = (-b + sqrt_disc) / (2 * a)

            # Return the smallest positive time.
            if t1 > 0 and t2 > 0:
                return min(t1, t2)
            elif t1 > 0:
                return t1
            elif t2 > 0:
                return t2
            else:
                return math.inf
        except Exception as e:
            print(f"Error computing collision time: {e}")
            return math.inf
    
    def compute_collision_event(self, ball1, ball2):
        """
        For a given pair of balls, compute an event structure if a collision is predicted.
        The event structure is a tuple: (time_until_collision, ball1, ball2, pos1, pos2)
        Returns:
            tuple or None: The event structure, or None if no collision is predicted.
        """
        try:
            t = self.compute_collision_time(ball1, ball2)
            if t == math.inf:
                return None
            # Predict positions at collision time.
            pos1 = (ball1.x + ball1.velocity[0] * t, ball1.y + ball1.velocity[1] * t)
            pos2 = (ball2.x + ball2.velocity[0] * t, ball2.y + ball2.velocity[1] * t)

            return [t, ball1, ball2, pos1, pos2]
        except Exception as e:
            print(f"Error computing collision event: {e}")
            return None

    def populate_next_events(self):
        """
        Compute collision events for all ball pairs using combinations and store them in a min heap
        prioritized by collision time.
        """
        try:
            # Clear existing heap
            self.collision_heap = []
            
            # Get all possible pairs of ball indices using combinations
            ball_pairs = combinations(range(len(self.balls)), 2)
            
            # Calculate events for each pair and add to heap
            for i, j in ball_pairs:
                event = self.compute_collision_event(self.balls[i], self.balls[j])
                if event is not None:
                    heapq.heappush(self.collision_heap, event)
            
            # The next event will always be at the top of the heap
            self.next_event = self.collision_heap[0] if self.collision_heap else None
        except Exception as e:
            print(f"Error populating next events: {e}")
            self.collision_heap = []
            self.next_event = None

    def process_collisions(self, dt):
        """
        Advance the simulation by dt seconds while accounting for the next predicted collision.
        The method subtracts the dt from the next event's predicted time. When that value falls
        to zero or below, the collision is applied based on the precomputed collision point and the
        collision manager repopulates the next event.
        
        Args:
            dt (float): The time interval to simulate.
        """
        try:
            # No predicted event: simply update positions.
            if self.next_event is not None:
                
                if self.next_event[0] > dt:
                    self.next_event[0] -= dt
                
                elif self.next_event[0] < dt:
                    self.next_event[1].x = self.next_event[3][0]
                    self.next_event[1].y = self.next_event[3][1]
                    self.next_event[2].x = self.next_event[4][0]
                    self.next_event[2].y = self.next_event[4][1]
                    self.handle_ball_ball_collision(self.next_event[1], self.next_event[2])
            
            for ball in self.balls:
                ball.update()
            
            self.populate_next_events() if self.next_event is not None else None
        
        except Exception as e:
            print(f"Error processing collisions: {e}")

    def handle_ball_ball_collision(self, ball1, ball2):
        try:
            # Compute the vector between the ball centers.
            dx = ball2.x - ball1.x
            dy = ball2.y - ball1.y
            distance = math.hypot(dx, dy)
            if distance == 0:
                return  # Avoid division by zero.
            # Unit normal vector from ball1 to ball2.
            nx = dx / distance
            ny = dy / distance

            # Compute relative velocity.
            dvx = ball1.velocity[0] - ball2.velocity[0]
            dvy = ball1.velocity[1] - ball2.velocity[1]
            impact_speed = dvx * nx + dvy * ny

            # Compute the impulse (for equal masses and a fully elastic collision).
            impulse = -(1 + self.restitution) * impact_speed / 2

            # Update velocities.
            ball1.velocity[0] += impulse * nx
            ball1.velocity[1] += impulse * ny
            ball2.velocity[0] -= impulse * nx
            ball2.velocity[1] -= impulse * ny

            # Positional correction.
            # Calculate the penetration depth.
            penetration = (ball1.radius + ball2.radius) - distance
            if penetration > 0:
                correction = penetration / 1.0  # Each ball moves half the penetration.
                ball1.x -= correction * nx
                ball1.y -= correction * ny
                ball2.x += correction * nx
                ball2.y += correction * ny
                
        except Exception as e:
            print(f"Error handling ball-ball collision: {e}")


    def repopulate_next_event(self):
        """
        Public method to repopulate (recompute) the next collision event.
        """
        try:
            self.populate_next_events()
        except Exception as e:
            print(f"Error repopulating next event: {e}")
