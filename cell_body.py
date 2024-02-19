import numpy as np

class CellBody:
    
    def __init__(self, pos, seed_radius):
        self.pos = pos
        self.rounded_radius = seed_radius
        self.radii = np.array([seed_radius, seed_radius, seed_radius])
        self.rot = [0, 0, 0]
    
    def set_radius(self, radius):
        self.radii = np.ones(3) * radius
        
    def grow_radii(self, growth):
        self.rounded_radius += growth
        self.round()
        # !!!! change to work for growth while squashed

    def apply_vel(self, vel):
        # !!!! implement
        pass

    def get_substance_level(self, substance):
        # !!!! implement
        return 0
    
    def is_contact_inhibited(self):
        # !!!! implement
        return False
    
    def squash(self, dir):
        # !!!! implement
        pass

    def round(self):
        # !!!! change to more sophisticated (rounding as much as possible in the space available)
        self.radii = np.array([self.rounded_radius, self.rounded_radius, self.rounded_radius])