import numpy as np

class CellBody:
    
    def __init__(self, pos, seed_radius):
        self.pos = pos        
        self.radii = [seed_radius, seed_radius, seed_radius]
        self.rot = [0, 0, 0]

    def get_seed_vol(self):
        return 4/3.0 * np.pi * self.ct.seed_radius**3
    
    def get_substance_level(self, substance):
        # !!!! implement
        return 0
    
    def is_contact_inhibited(self):
        # !!!! implement
        return False
    
    def calc_vol(self):
        return 4.0/3.0 * np.pi * np.prod(self.radii)        
    
    def change_vol(self, new_vol):
        new_radius = np.cbrt((new_vol * 3.0) / (4.0 * np.pi))
        self.radii = [new_radius, new_radius, new_radius]

    def change_position(self, vel):
        # !!!! implement
        pass

    def squash(self, dir):
        # !!!! implement
        pass

    def round(self):
        # !!!! change to more sophisticated (rounding as much as possible in the space available)
        round_radius = np.cbrt(np.prod(self.radii))
        self.radii = [round_radius, round_radius, round_radius]