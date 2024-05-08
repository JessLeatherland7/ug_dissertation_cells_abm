# -*- coding: utf-8 -*-

from cell_type import *
from data import DataWriter
from environment import *
from physics import *
import utils

class Simulation():
    
    def __init__(self, save_file, cell_types, initial_cell_nums, 
                 env_size, env_layers, max_iteration, random_seed=None):
        """Constructs the necessary attributes for the Simulation object.
        
        Parameters
        ----------
        save_file : string
            the name of the data file where the simulation data should be saved
        cell_types : list
            a list of the cell type classes to add to the simulation
        initial_cell_nums : list
            a list of the counts of each cell type to initialise in the simulation
        env_size : float
            the width of the environment
        env_layers : list
            a list of the environment layer objects that the user has added to 
            the simulation
        max_iteration : int
            the number of iterations the user has chosen to simulate
        random_seed : int
            an optional random seed that the user can set for the simulation

        Other defined attributes
        ------------------------
        data_writer : DataWriter
            the DataWriter object for writing simulation data
        sim_iteration : int
            the current iteration being simulated
        cells : list
            a list of the current cells in the simulation
        new_cell_buffer : list
            a list of the cells that have been seeded in an iteration to 
            be added to the cells list
        physics_model : PhysicsModel / PhysicsModelWithLocals
            the physical model used to solve cell overlap
        """      
        self.data_writer = DataWriter(save_file)
        self.cell_types = cell_types
        self.initial_cell_nums = initial_cell_nums
        self.env_size = env_size
        self.env_layers = env_layers
        
        # Add default environment layers for any layers that the user did not add
        for env_layer in AbstractEnvironmentLayer.__subclasses__():
            if env_layer not in self.env_layers:
                self.env_layers.append(env_layer(self.env_size))

        self.max_iteration = max_iteration
        
        if random_seed:
            np.random.seed(random_seed)
        
        self.sim_iteration = 0
        self.cells = []
        self.new_cell_buffer = []
        
        # Seed new cells at random locations
        for i in range(len(self.cell_types)):
            cell_type = self.cell_types[i]
            for j in range(self.initial_cell_nums[i]):
                pos = np.random.uniform(
                    cell_type.SEED_RADIUS, self.env_size - cell_type.SEED_RADIUS, [3])
                self.seed_new_cell(cell_type, pos)
        
        # Add the seeded cells to the cells list
        self.add_buffer_cells()

        # Choose which physical model implementation to use
        max_cell_radius = self.get_max_cell_radius()
        if int(self.env_size / (max_cell_radius * 4)) < 4:
            self.physics_model = PhysicalModel(self.env_size)
        else:
            self.physics_model = PhysicalModelWithLocals(self.env_size, max_cell_radius)

        # Solve any overlap resulting from the random initial cell positions
        self.physics_model.solve_overlap(self.sim_iteration, self.cells)

        # Save iteration 0
        self.data_writer.save_iteration(self.sim_iteration, self.cells)

    def get_max_cell_radius(self):
        """Gets the fully grown radius of the largest cell type in the simulation.

        Returns
        ----------
        float
            fully grown radius of largest cell type
        """
        max_cell_seed_radius = max([cell_type.SEED_RADIUS for cell_type in self.cell_types])
        return max_cell_seed_radius * utils.CUBE_ROOT_2

    def seed_new_cell(self, cell_type, pos):
        """Adds a new cell object with the given type and position to the new cell buffer.
        
        Parameters
        ----------
        cell_type : AbtractCellType subclass
            the cell type class to initialise
        pos : np.ndarray(3)
            the initial 3D position of the new cell
        """
        new_cell_id = len(self.cells) + len(self.new_cell_buffer)
        self.new_cell_buffer.append(cell_type(self, new_cell_id, pos))

    def add_buffer_cells(self):
        """Adds the cells that have been seeded in the buffer to the cells list."""
        self.cells += self.new_cell_buffer
        self.new_cell_buffer = []

    def get_env_layer(self, substance_name):
        """Gets the environment layer object with the given substance name.
        
        Parameters
        ----------
        substance_name : string
            the name of the substance in the environment layer that needs 
            to be returned
        
        Returns
        -------
        env_layer : AbstractEnvironmentLayer subclass
            the environment layer object with the given substance
        """
        for env_layer in self.env_layers:
            if env_layer.SUBSTANCE_NAME == substance_name:
                return env_layer
        return None

    def run_iteration(self):
        """Run an iteration of the simulation.

        Applies the cell behaviours to each of the cells, adds any cells that
        have been seeded to the cells list, calls the physical solver to resolve
        overlap, and saves the iteration data.
        """
        self.sim_iteration += 1

        for cell in self.cells:
            if not cell.is_dead:
                cell.do_cell_cycle()
                cell.migrate()
                cell.type_specific_processes()
        
        self.add_buffer_cells()
        
        self.physics_model.solve_overlap(self.sim_iteration, self.cells)
        
        self.data_writer.save_iteration(self.sim_iteration, self.cells)

    def write_simulation(self):
        """Calls the DataWriter to save all of the simulation data to a file."""
        self.data_writer.write_data()
