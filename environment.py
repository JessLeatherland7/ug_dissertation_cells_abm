# -*- coding: utf-8 -*-

from abc import ABC, ABCMeta, abstractmethod

class AbstractEnvironmentLayer(ABC, metaclass=ABCMeta):
    # All classes implementing this abstract class must define a name for
    # the substance layer
    SUBSTANCE_NAME: str

    def __init__(self, size):
        """Constructs the necessary attributes for the AbstractEnvironmentLayer object.
        
        Parameters
        ----------
        size : float
            the width of the environment
        """
        self.size = size
    
    @abstractmethod
    def get_level_at_pos(self, pos):
        """Get the substance level of the environment layer at the given position.

        This must return a float in all classes that implement this abstract class.
        
        Parameters
        ----------
        pos : numpy.ndarray(3)
            the 3D position in the environment being queried
        """
        pass
        
    
class OxygenLayer(AbstractEnvironmentLayer):
    SUBSTANCE_NAME = "oxygen"
    
    def __init__(self, size, oxygen_level=1.0):
        """Constructs the necessary attributes for the OxygenLayer object.
        
        Parameters
        ----------
        size : float
            the width of the environment
        oxygen_level : float = 1.0
            optional uniform oxygen level that can be set by the user from the GUI,
            but if not set then it takes a default high value
        """
        super().__init__(size)
        self.oxygen_level = oxygen_level

    def get_level_at_pos(self, pos):
        """Gets the oxygen level at the given position.

        As this layer is uniform, the same value is returned for all positions.
        
        Parameters
        ----------
        pos : numpy.ndarray(3)
            the 3D position in the environment being queried
        """
        return self.oxygen_level
