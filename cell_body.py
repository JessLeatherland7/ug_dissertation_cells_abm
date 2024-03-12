import numpy as np

class CellBody:
    
    def __init__(self, pos, seed_radius):
        self.pos = pos
        self.radius = seed_radius
        self.contact_inhibited = False
    
    def set_radius(self, radius):
        self.radius = radius
        
    def grow_radius(self, growth):
        self.radius += growth

    def apply_vel(self, vel):
        self.pos += vel

    def get_substance_level(self, substance):
        # !!!! implement
        return 1
