import numpy as np

class CellBody:
    
    def __init__(self, sim, pos, seed_radius):
        self.pos = pos
        self.radius = seed_radius
        self.sim = sim
        self.env_size = sim.env_size
        self.contact_inhibited = False
    
    def set_radius(self, radius):
        self.radius = radius
        
    def grow_radius(self, growth):
        self.radius += growth

    def apply_vel(self, vel):
        self.pos = np.clip(self.pos + vel, self.radius, self.env_size - self.radius)

    def get_substance_level(self, substance):
        env_layer = self.sim.get_env_layer(substance)
        return env_layer.get_level_at_pos(self.pos)
    
    def get_num_border_contacts(self, extra_contact_radius=0.1):
        border_contacts = (self.pos <= self.radius + extra_contact_radius).sum()
        border_contacts += (self.pos >= self.env_size - self.radius - extra_contact_radius).sum()
        return border_contacts
