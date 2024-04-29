from cell_type import *
from environment import *
from data import DataWriter
from visualiser import Visualiser
from physics import *

class Simulation():
    
    def __init__(self, save_file, cell_types, initial_cell_nums, env_size, env_layers, max_iteration, random_seed=None):        
        self.save_file = save_file
        self.data_writer = DataWriter(self.save_file)
        
        self.cell_types = cell_types
        self.initial_cell_nums = initial_cell_nums
        self.env_size = env_size
        self.env_layers = env_layers
        
        for env_layer in AbstractEnvironmentLayer.__subclasses__():
            if env_layer not in self.env_layers:
                self.env_layers.append(env_layer(self.env_size))

        self.max_iteration = max_iteration
        
        if random_seed:
            np.random.seed(random_seed)
        
        self.sim_iteration = 0
        self.cells = []
        self.new_cell_buffer = []

        for i in range(len(self.cell_types)):
            cell_type = self.cell_types[i]
            for j in range(self.initial_cell_nums[i]):
                pos = np.random.uniform(10, self.env_size - 10, [3])
                self.seed_new_cell(cell_type, pos)

        self.add_buffer_cells()

        max_cell_radius = GenericCell.SEED_RADIUS * 1.259921
        if int(self.env_size / (max_cell_radius * 4)) < 4:
            self.physics_model = PhysicalModel(self.env_size)
        else:
            self.physics_model = PhysicalModelWithLocals(self.env_size, max_cell_radius)

        total_overlap = self.physics_model.solve_overlap(self.cells)

        #if total_overlap > 0:
        #    print(self.sim_iteration, total_overlap)

        self.data_writer.save_iteration(self.sim_iteration, self.cells)


    def seed_new_cell(self, cell_type, pos):
        new_cell_id = len(self.cells) + len(self.new_cell_buffer)
        self.new_cell_buffer.append(cell_type(self, new_cell_id, pos))


    def add_buffer_cells(self):
        self.cells += self.new_cell_buffer
        self.new_cell_buffer = []


    def get_env_layer(self, substance_name):
        for env_layer in self.env_layers:
            if env_layer.SUBSTANCE_NAME == substance_name:
                return env_layer
        return None


    def run_iteration(self):
        self.sim_iteration += 1

        for cell in self.cells:
            if not cell.is_dead:
                cell.do_cell_cycle()
                cell.migrate()
                cell.type_specific_processes()
        
        self.add_buffer_cells()
        
        total_overlap = self.physics_model.solve_overlap(self.cells)

        #if total_overlap > 0:
        #    print(self.sim_iteration, total_overlap)
        
        self.data_writer.save_iteration(self.sim_iteration, self.cells)
        

    def write_simulation(self):
        self.data_writer.write_data()
