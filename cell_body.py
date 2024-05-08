# -*- coding: utf-8 -*-

import numpy as np

class CellBody:
    
    def __init__(self, sim, pos, seed_radius):
        """Constructs the necessary attributes for the CellBody object.
        
        Parameters
        ----------
        sim : Simulation
            the simulation object that the cell is in
        pos : numpy.ndarray(3)
            the 3D position of the cell in the environment
        seed_radius : float
            the initial radius of the cell

        Other defined attributes
        ------------------------
        env_size : float
            the width of the environment that the cell is in
        contact_inhibited : bool
            whether the cell body is contact inhibited
        """
        self.pos = pos
        self.radius = seed_radius
        self.sim = sim
        self.env_size = sim.env_size
        self.contact_inhibited = False
    
    def set_radius(self, radius):
        """Sets the radius of the cell body.
        
        Parameters
        ----------
        radius : float
            the new cell radius
        """
        self.radius = radius
        
    def grow_radius(self, growth):
        """Increases the radius of the cell body.
        
        Parameters
        ----------
        growth : float
            how much to increase the radius by
        """
        self.radius += growth

    def apply_vel(self, vel):
        """Applies the velocity to the cell body's position.
        
        The velocity is added to the cell's position and then the
        position is clipped to remain within the environment boundary.

        Parameters
        ----------
        vel : numpy.ndarray(3)
            the velocity to add to the cell's position
        """
        self.pos = np.clip(self.pos + vel, self.radius, self.env_size - self.radius)

    def get_substance_level(self, substance):
        """Gets the level of the given substance layer at the cell's position.
        
        Parameters
        ----------
        substance : string
            the name of the substance layer to get the level of
        """
        env_layer = self.sim.get_env_layer(substance)
        return env_layer.get_level_at_pos(self.pos)
    
    def get_num_border_contacts(self, extra_contact_radius=0.5):
        """Gets the number of environment borders that the cell is contacting.
        
        Parameters
        ----------
        extra_contact_radius : float
            how close the cell needs to be to a border to be considered
            in contact with it
        """
        border_contacts = (self.pos <= self.radius + extra_contact_radius).sum()
        border_contacts += (self.pos >= self.env_size - self.radius - extra_contact_radius).sum()
        return border_contacts
