from abc import ABC, ABCMeta, abstractmethod
import numpy as np

from cell_body import CellBody

class CellTypeAttributesMeta(ABCMeta):
    cell_type_attributes = [
        'seed_radius', 
        'mean_cyc_len', 
        'std_dev_cyc_len'
    ]

    def __call__(cls, *args, **kwargs):
        instance = super().__call__(*args, **kwargs)
        for attr in cls.cell_type_attributes:
            if not hasattr(instance, attr):
                raise NotImplementedError(f"Missing required class attribute: {attr}")
        return instance
    

class AbstractCellType(ABC, metaclass=CellTypeAttributesMeta):
    seed_radius: float
    mean_cyc_len: float
    std_dev_cyc_len: float

    def __init__(cls, self, id, pos):
        self.id = id
        self.cell_body = CellBody(pos, cls.seed_radius)
        self.current_phase = "G1"
        self.current_cyc_iteration = 0
        self.is_dead = False

        self.cyc_len = self.get_cyc_len()
        self.g1_len = self.get_g1_len()
        self.growth_rate = self.get_growth_rate()

    def get_cyc_len(cls, self):
        return int(np.random.normal(loc=cls.mean_cyc_len, scale=cls.std_dev_cyc_len, size=1))
    
    def get_g1_len(self):
        g1_len_mean = self.cyc_len / 2.0
        return int(np.random.normal(loc=g1_len_mean, scale=g1_len_mean/10.0, size=1))
    
    def get_growth_rate(cls, self):
        # radius growth rate required to double volume in G1
        # cube root of 2 = 1.259921
        return 1.259921 * cls.seed_radius / self.g1_len

    def do_cell_cycle(self):
        if self.current_phase == "G0":
            self.g0_phase()
        elif self.current_phase == "G1":
            self.g1_phase()
        elif self.current_phase == "S":
            self.s_phase()
        elif self.current_phase == "G2":
            self.g2_phase()
        else:
            self.m_phase()

    @abstractmethod
    def g1_phase():
        pass

    @abstractmethod
    def g0_phase():
        pass

    @abstractmethod
    def s_phase():
        pass

    @abstractmethod
    def g2_phase():
        pass

    @abstractmethod
    def m_phase():
        pass

    @abstractmethod
    def migrate():
        pass

    @abstractmethod
    def type_specific_processes():
        pass


class GenericCell(AbstractCellType):
    seed_radius = 10.0
    mean_cyc_len = 24.0
    std_dev_cyc_len = 1.0
    
    lifespan = 40
    g0_oxy_threshold = 0.5
    hypoxia_theshold = 0.25

    def __init__(self):
        super().__init__()
        self.current_age = 0

    @property
    def min_radius(self):
        return self.cell_body.rounded_radius / 2.0
    
    def do_cell_cycle(self):
        if self.current_phase == "G0":
            self.g0_phase()
        elif self.current_phase == "G1":
            self.g1_phase()
        elif self.current_phase == "S":
            self.s_phase()
        else:
            self.m_phase()

    def g1_phase(self):
        self.current_cyc_iteration += 1
        
        self.cell_body.grow_radius(self.growth_rate)
        
        if self.current_cyc_iteration == self.g1_len:
            if self.cell_body.get_substance_level("oxygen") < self.g0_oxy_threshold or self.cell_body.contact_inhibited():
                self.current_phase = "G0"
            else:
                self.current_phase = "S"

    def g0_phase(self):
        if not self.cell_body.contact_inhibited() and self.cell_body.get_substance_level("oxygen") > self.g0_oxy_threshold:
            if self.current_cyc_iteration == self.g1_len:
                self.current_phase = "S"
            else:
                self.current_phase = "M"

    def s_phase(self):
        self.current_cyc_iteration += 1
        if self.current_cyc_iteration == self.cyc_len - 1:
            if self.cell_body.get_substance_level("oxygen") < self.g0_oxy_threshold or self.cell_body.contact_inhibited:
                self.current_phase = "G0"
            else:
                self.current_phase = "M"

    def g2_phase(self):
        pass

    def m_phase(cls, self):
        self.cell_body.set_radius(cls.seed_radius)
        # !!!! seed new cell where there is space
        self.current_age += 1
        if self.current_age > cls.lifespan:
            self.is_dead = True
        else:
            self.current_cyc_iteration = 0
            self.cyc_len = self.get_cyc_len()
            self.g1_len = self.get_g1_len()
            self.growth_rate = self.get_growth_rate()
        
    def migrate(self):
        pass

    def type_specific_processes(self):
        if self.cell_body.get_substance_level("oxygen") < self.hypoxia_theshold:
            self.is_dead = True