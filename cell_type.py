from abc import ABC, ABCMeta, abstractmethod
import numpy as np

from cell_body import CellBody

class CellTypeAttributesMeta(ABCMeta):
    cell_type_attributes = [
        'SEED_RADIUS', 
        'MEAN_CYC_LEN', 
        'STD_DEV_CYC_LEN'
    ]

    def __call__(cls, *args, **kwargs):
        instance = super().__call__(*args, **kwargs)
        for attr in cls.cell_type_attributes:
            if not hasattr(instance, attr):
                raise NotImplementedError(f"Missing required class attribute: {attr}")
        return instance
    

class AbstractCellType(ABC, metaclass=CellTypeAttributesMeta):
    SEED_RADIUS: float
    MEAN_CYC_LEN: float
    STD_DEV_CYC_LEN: float

    def __init__(self, sim, id, pos):
        self.id = id
        self.sim = sim
        self.cell_body = CellBody(pos, self.SEED_RADIUS, sim.env_size)
        self.current_phase = "G1"
        self.current_cyc_iteration = 0
        self.is_dead = False

        self.cyc_len = self.get_cyc_len()
        self.g1_len = self.get_g1_len()
        self.growth_rate = self.get_growth_rate()

    def get_cyc_len(self):
        return max(2, int(np.random.normal(loc=self.MEAN_CYC_LEN, scale=self.STD_DEV_CYC_LEN, size=1)))
    
    def get_g1_len(self):
        g1_len_mean = self.cyc_len / 2.0
        return max(1, int(np.random.normal(loc=g1_len_mean, scale=g1_len_mean/10.0, size=1)))
    
    def get_growth_rate(self):
        # radius growth rate required to double volume in G1
        cube_root_2 = 1.259921
        return ((cube_root_2 * self.SEED_RADIUS) - self.SEED_RADIUS) / self.g1_len

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
    SEED_RADIUS = 10.0
    MEAN_CYC_LEN = 24.0
    STD_DEV_CYC_LEN = 1.0
    
    LIFESPAN = 40
    G0_OXY_THRESHOLD = 0.5
    HYPOXIA_THRESHOLD = 0.25

    def __init__(self, sim, id, pos):
        super().__init__(sim, id, pos)
        self.current_age = 0
    
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
            if self.cell_body.get_substance_level("oxygen") < self.G0_OXY_THRESHOLD or self.cell_body.contact_inhibited:
                self.current_phase = "G0"
            else:
                self.current_phase = "S"

    def g0_phase(self):
        if not self.cell_body.contact_inhibited and self.cell_body.get_substance_level("oxygen") > self.G0_OXY_THRESHOLD:
            if self.current_cyc_iteration == self.g1_len:
                self.current_phase = "S"
            else:
                self.current_phase = "M"

    def s_phase(self):
        self.current_cyc_iteration += 1
        if self.current_cyc_iteration == self.cyc_len - 1:
            if self.cell_body.get_substance_level("oxygen") < self.G0_OXY_THRESHOLD or self.cell_body.contact_inhibited:
                self.current_phase = "G0"
            else:
                self.current_phase = "M"

    def g2_phase(self):
        pass

    def m_phase(self):
        self.cell_body.set_radius(self.SEED_RADIUS)
        # !!!! seed new cell where there is space
        direction = np.random.uniform(-1, 1, [3])
        new_cell_pos = self.cell_body.pos + (direction / np.linalg.norm(direction)) * (self.SEED_RADIUS * 2.0)
        new_cell_pos = np.clip(new_cell_pos, self.SEED_RADIUS, self.sim.env_size - self.SEED_RADIUS)
        self.sim.seed_new_cell(GenericCell, new_cell_pos)
        self.current_age += 1
        if self.current_age >= self.LIFESPAN:
            self.is_dead = True
        else:
            self.current_cyc_iteration = 0
            self.current_phase = "G1"
            self.cyc_len = self.get_cyc_len()
            self.g1_len = self.get_g1_len()
            self.growth_rate = self.get_growth_rate()
        
    def migrate(self):
        if not self.cell_body.contact_inhibited:
            direction = np.random.uniform(-1, 1, [3])
            vel = (direction / np.linalg.norm(direction)) * (self.SEED_RADIUS / 2.0)
            self.cell_body.apply_vel(vel)

    def type_specific_processes(self):
        if self.cell_body.get_substance_level("oxygen") < self.HYPOXIA_THRESHOLD:
            self.is_dead = True