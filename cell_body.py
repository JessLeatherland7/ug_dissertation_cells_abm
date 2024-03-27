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
        new_pos = self.pos + vel
        max_constraint = self.env_size - self.radius
        min_constraint = self.radius
        
        if max(new_pos) > max_constraint or min(new_pos) < min_constraint:
            if max(new_pos) - max_constraint > min_constraint - min(new_pos):
                max_coord = np.argmax(new_pos)
                vel_multiplier = (max_constraint - self.pos[max_coord]) / vel[max_coord]
            else:
                min_coord = np.argmin(new_pos)
                vel_multiplier = (min_constraint - self.pos[min_coord]) / vel[min_coord]
            
            new_pos = self.pos + vel * vel_multiplier
        
        self.pos = new_pos

    def get_substance_level(self, substance):
        # !!!! implement
        return 1
