import numpy as np

class CellBody:
    
    def __init__(self, pos, seed_radius, env_size):
        self.pos = pos
        self.radius = seed_radius
        self.env_size = env_size
        self.contact_inhibited = False
    
    def set_radius(self, radius):
        self.radius = radius
        
    def grow_radius(self, growth):
        self.radius += growth

    def apply_vel(self, vel):
        self.pos = np.clip(self.pos + vel, self.radius, self.env_size - self.radius)

    def get_substance_level(self, substance):
        # !!!! implement
        return 1
