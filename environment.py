from abc import ABC, ABCMeta, abstractmethod

class AbstractEnvironmentLayer(ABC, metaclass=ABCMeta):
    SUBSTANCE_NAME: str

    def __init__(self, size):
        self.size = size
    
    @abstractmethod
    def get_level_at_pos(self, pos):
        pass
        
    
class OxygenLayer(AbstractEnvironmentLayer):
    SUBSTANCE_NAME = "oxygen"
    
    def __init__(self, size, oxygen_level=1.0):
        super().__init__(size)
        self.oxygen_level = oxygen_level

    def get_level_at_pos(self, pos):
        return self.oxygen_level