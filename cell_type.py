# -*- coding: utf-8 -*-

from abc import ABC, ABCMeta, abstractmethod
import numpy as np

from cell_body import CellBody
import utils

class AbstractCellType(ABC, metaclass=ABCMeta):
    # All classes implementing this abstract class must define these constants
    SEED_RADIUS: float
    MEAN_CYC_LEN: float
    STD_DEV_CYC_LEN: float

    def __init__(self, sim, id, pos):
        """Constructs the necessary attributes for the AbstractCellType object.
        
        Parameters
        ----------
        sim : Simulation
            the simulation object that the cell is in
        id : int
            the ID of the cell agent
        pos : np.ndarray(3)
            the initial 3D position of the cell agent in the environment

        Other defined attributes
        ------------------------
        cell_body : CellBody
            the body that this cell has holding its physical attributes
        current_phase : string
            the current phase of the cell cycle that the cell is in
        current_cycle_iteration : int
            the current iteration of the cell cycle that the cell is in
        is_dead : bool
            whether the cell is dead or not
        cyc_len : int
            the length of the cell's cycle in iterations
        g1_len : int
            the length of the cell's G1 phase in iterations
        growth_rate : float
            the amount that the cell's radius need to grow in each iteration
            of G1 in order to double in volume
        """
        self.id = id
        self.sim = sim
        self.cell_body = CellBody(sim, pos, self.SEED_RADIUS)
        self.current_phase = "G1"
        self.current_cyc_iteration = 0
        self.is_dead = False

        self.cyc_len = self.get_cyc_len()
        self.g1_len = self.get_g1_len()
        self.growth_rate = self.get_growth_rate()

    def get_cyc_len(self):
        """Gets a random cycle length for the cell based on a normal distribution.

        Returns
        -------
        int
            cell cycle length in iterations (min 2 iterations)
        """
        rand_cyc_len = np.random.normal(loc=self.MEAN_CYC_LEN, scale=self.STD_DEV_CYC_LEN, size=1)
        return max(2, int(rand_cyc_len))
    
    def get_g1_len(self):
        """Gets a random G1 length for the cell based on a normal distribution.

        Returns
        -------
        int
            G1 phase length in iterations (min 1 iteration)
        """
        g1_len_mean = self.cyc_len / 2.0
        rand_g1_len = np.random.normal(loc=g1_len_mean, scale=g1_len_mean/10.0, size=1)
        return max(1, int(rand_g1_len))
    
    def get_growth_rate(self):
        """Gets the radius growth rate required for the cell to double in volume in G1.

        Returns
        -------
        float
            radius growth rate throughout G1 phase
        """
        return ((utils.CUBE_ROOT_2 * self.SEED_RADIUS) - self.SEED_RADIUS) / self.g1_len

    def do_cell_cycle(self):
        """Calls the relevant cycle phase function based on the current phase the cell is in."""
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
        """G1 phase behaviour.

        This must be defined in all classes that implement this abstract class.
        """
        pass

    @abstractmethod
    def g0_phase():
        """G0 phase behaviour.

        This must be defined in all classes that implement this abstract class.
        """
        pass

    @abstractmethod
    def s_phase():
        """S phase behaviour.

        This must be defined in all classes that implement this abstract class.
        """
        pass

    @abstractmethod
    def g2_phase():
        """G2 phase behaviour.

        This must be defined in all classes that implement this abstract class.
        """
        pass

    @abstractmethod
    def m_phase():
        """M phase behaviour.

        This must be defined in all classes that implement this abstract class.
        """
        pass

    @abstractmethod
    def migrate():
        """Cell migratory behaviour.

        This must be defined in all classes that implement this abstract class.
        """
        pass

    @abstractmethod
    def type_specific_processes():
        """Other cell behaviours specific to this cell type.

        This must be defined in all classes that implement this abstract class.
        """
        pass


class GenericCell(AbstractCellType):
    SEED_RADIUS = 10.0
    MEAN_CYC_LEN = 24.0
    STD_DEV_CYC_LEN = 1.0
    
    LIFESPAN = 40
    G0_OXY_THRESHOLD = 0.5
    HYPOXIA_THRESHOLD = 0.25

    def __init__(self, sim, id, pos):
        """Constructs the necessary attributes for the GenericCell object.
        
        Parameters
        ----------
        sim : Simulation
            the simulation object that the cell is in
        id : int
            the ID of the cell agent
        pos : np.ndarray(3)
            the initial 3D position of the cell agent in the environment

        Other defined attributes
        ------------------------
        current_age : int
            the current age of the cell (how many times it has divided)
        """
        super().__init__(sim, id, pos)
        self.current_age = 0
    
    def do_cell_cycle(self):
        """Overrides the AbstractCellType behaviour to call the relevant cycle phase
        function based on the current phase the cell is in.

        The GenericCell class has no G2 phase as S and G2 are considered to be merged.
        """
        if self.current_phase == "G0":
            self.g0_phase()
        elif self.current_phase == "G1":
            self.g1_phase()
        elif self.current_phase == "S":
            self.s_phase()
        else:
            self.m_phase()

    def g1_phase(self):
        """G1 phase behaviour.

        The cell grows until it reaches the final G1 iteration, if it is in low
        oxygen or is contact inhibited then it becomes quiescent and goes to G0,
        otherwise it goes to the S phase.
        """
        if self.current_cyc_iteration == self.g1_len:
            oxy_level = self.cell_body.get_substance_level("oxygen")
            if  oxy_level < self.G0_OXY_THRESHOLD or self.cell_body.contact_inhibited:
                self.current_phase = "G0"
            else:
                self.current_phase = "S"
        else:
            self.cell_body.grow_radius(self.growth_rate)
        
        self.current_cyc_iteration += 1

    def g0_phase(self):
        """G0 phase behaviour.

        If the oxygen is high enough and the cell is not contact inhibited,
        the cell returns to its cycle at either the start of S phase or at
        the M phase.
        """
        oxy_level = self.cell_body.get_substance_level("oxygen")
        if not self.cell_body.contact_inhibited and oxy_level > self.G0_OXY_THRESHOLD:
            if self.current_cyc_iteration == self.g1_len:
                self.current_phase = "S"
            else:
                self.current_phase = "M"

    def s_phase(self):
        """S phase behaviour.

        At the end of the cycle iterations, if the cell is in low oxygen or is 
        contact inhibited then it becomes quiescent and goes to G0, otherwise it 
        goes to the M phase.
        """
        if self.current_cyc_iteration == self.cyc_len - 1:
            oxy_level = self.cell_body.get_substance_level("oxygen")
            if oxy_level < self.G0_OXY_THRESHOLD or self.cell_body.contact_inhibited:
                self.current_phase = "G0"
            else:
                self.current_phase = "M"
        
        self.current_cyc_iteration += 1

    def g2_phase(self):
        """G2 phase behaviour.

        The GenericCell class has no G2 behaviour because this is considered
        to be merged with the S phase.
        """
        pass

    def m_phase(self):
        """M phase behaviour.

        The cell returns to its original size, seeds a new cell at a random
        location next to it, ages, and either dies of old age, or goes to the
        start of its next cycle, generating a new cycle length.
        """
        self.cell_body.set_radius(self.SEED_RADIUS)
        new_cell_pos = self.cell_body.pos + utils.rand_unit_vec() * self.SEED_RADIUS * 2.0
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
        """Cell migratory behaviour.

        If the cell is not contact inhibited, it moves a distance equal to
        half its radius in a random direction.
        """
        if not self.cell_body.contact_inhibited:
            vel = utils.rand_unit_vec * (self.SEED_RADIUS / 2.0)
            self.cell_body.apply_vel(vel)

    def type_specific_processes(self):
        """Other cell behaviours specific to this cell type.

        The cell dies of hypoxia if the oxygen level at its location is too low.
        """
        oxy_level = self.cell_body.get_substance_level("oxygen")
        if oxy_level < self.HYPOXIA_THRESHOLD:
            self.is_dead = True


class CancerousCell(AbstractCellType):
    SEED_RADIUS = 10.0
    MEAN_CYC_LEN = 12.0
    STD_DEV_CYC_LEN = 1.0

    def __init__(self, sim, id, pos):
        """Constructs the necessary attributes for the CancerousCell object.
        
        Parameters
        ----------
        sim : Simulation
            the simulation object that the cell is in
        id : int
            the ID of the cell agent
        pos : np.ndarray(3)
            the initial 3D position of the cell agent in the environment
        """
        super().__init__(sim, id, pos)
    
    def do_cell_cycle(self):
        """Overrides the AbstractCellType behaviour to call the relevant cycle phase
        function based on the current phase the cell is in.

        The CancerousCell class has no G2 phase as S and G2 are considered to be merged,
        and it cannot enter the G0 phase.
        """
        if self.current_phase == "G1":
            self.g1_phase()
        elif self.current_phase == "S":
            self.s_phase()
        else:
            self.m_phase()

    def g1_phase(self):
        """G1 phase behaviour.

        The cell grows until it reaches the final G1 iteration, and then goes to
        the S phase.
        """
        self.current_cyc_iteration += 1
        
        self.cell_body.grow_radius(self.growth_rate)
        
        if self.current_cyc_iteration == self.g1_len:
            self.current_phase = "S"

    def g0_phase(self):
        """G0 phase behaviour.

        The CancerousCell class has no G0 behaviour because it cannot become quiescent.
        """
        pass

    def s_phase(self):
        """S phase behaviour.

        At the end of the cycle iterations the cell goes to the M phase.
        """
        self.current_cyc_iteration += 1
        if self.current_cyc_iteration == self.cyc_len - 1:
            self.current_phase = "M"

    def g2_phase(self):
        """G2 phase behaviour.

        The CancerousCell class has no G2 behaviour because this is considered
        to be merged with the S phase.
        """
        pass

    def m_phase(self):
        """M phase behaviour.

        The cell returns to its original size, seeds a new cell at a random
        location next to it, and goes to the start of its next cycle, generating 
        a new cycle length.
        """
        self.cell_body.set_radius(self.SEED_RADIUS)
        
        new_cell_pos = self.cell_body.pos + utils.rand_unit_vec() * (self.SEED_RADIUS * 2.0)
        new_cell_pos = np.clip(new_cell_pos, self.SEED_RADIUS, self.sim.env_size - self.SEED_RADIUS)
        self.sim.seed_new_cell(CancerousCell, new_cell_pos)
        
        self.current_cyc_iteration = 0
        self.current_phase = "G1"
        self.cyc_len = self.get_cyc_len()
        self.g1_len = self.get_g1_len()
        self.growth_rate = self.get_growth_rate()
        
    def migrate(self):
        """Cell migratory behaviour.

        The cell moves a distance equal to half its radius in a random direction.
        """
        vel = utils.rand_unit_vec() * (self.SEED_RADIUS / 2.0)
        self.cell_body.apply_vel(vel)

    def type_specific_processes(self):
        """Other cell behaviours specific to this cell type.

        The CancerousCell class has no other type specific behaviours.
        """
        pass