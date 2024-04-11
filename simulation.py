from cell_type import *
from data import DataWriter
from visualiser import Visualiser
from physics import *

class Simulation:

    def __init__(self, save_file, initial_cell_num, env_size, max_iteration, random_seed=None):
        self.save_file = save_file
        self.data_writer = DataWriter(self.save_file)

        self.initial_cell_num = initial_cell_num
        self.env_size = env_size
        self.max_iteration = max_iteration
        
        if random_seed:
            np.random.seed(random_seed)
        
        self.sim_iteration = 0
        self.cells = []
        self.new_cell_buffer = []

        #x_pos = [190, 200, 210]
        #y_pos = [200, 200, 200]
        #z_pos = [200, 200, 200]

        for i in range(self.initial_cell_num):
            pos = np.random.uniform(20, self.env_size - 20, [3])
            #pos = np.array([x_pos[i], y_pos[i], z_pos[i]])
            self.seed_new_cell(GenericCell, pos)

        self.add_buffer_cells()

        max_cell_radius = GenericCell.SEED_RADIUS * 1.259921
        if int(self.env_size / (max_cell_radius * 4)) < 4:
            self.physics_model = NewPhysicalModel(self.env_size)
        else:
            self.physics_model = NewPhysicalModelWithLocals(self.env_size, max_cell_radius)

        for cell in self.cells:
            cell.cell_body.contact_inhibited = False

        total_overlap, overlapping_cells = self.physics_model.solve_overlap(self.cells)

        if total_overlap > 0:
            print(self.sim_iteration, total_overlap)

        for cell_pair in overlapping_cells:
            cell_pair[0].cell_body.contact_inhibited = True
            cell_pair[1].cell_body.contact_inhibited = True

        self.data_writer.save_iteration(self.sim_iteration, self.cells)

        self.sim_iteration += 1


    def seed_new_cell(self, cell_type, pos):
        new_cell_id = len(self.cells) + len(self.new_cell_buffer)
        self.new_cell_buffer.append(cell_type(self, new_cell_id, pos))

    def add_buffer_cells(self):
        self.cells += self.new_cell_buffer
        self.new_cell_buffer = []

    def run_sim(self):
        while self.sim_iteration <= self.max_iteration:
            for cell in self.cells:
                cell.cell_body.contact_inhibited = False

            for cell in self.cells:
                if not cell.is_dead:
                    cell.do_cell_cycle()
                    cell.migrate()
                    cell.type_specific_processes()
            
            self.add_buffer_cells()
            
            total_overlap, overlapping_cells = self.physics_model.solve_overlap(self.cells)

            if total_overlap > 0:
                print(self.sim_iteration, total_overlap)
            
            for cell_pair in overlapping_cells:
                cell_pair[0].cell_body.contact_inhibited = True
                cell_pair[1].cell_body.contact_inhibited = True
            
            self.data_writer.save_iteration(self.sim_iteration, self.cells)

            self.sim_iteration += 1

        self.data_writer.write_data()

    def visualise_sim(self):
        visualiser = Visualiser(self.save_file, self.max_iteration, self.env_size)
        visualiser.visualise()

#while sim_iteration < 50:
#    for cell in cells:
#        cell.cell_body.contact_inhibited = False
        
#    total_overlap, overlapping_cells = physics_model.solve_overlap(cells)

#overlapping_cell_matrix, overlapping_cells = physics_model.get_overlapping_cells(cells)
        
#    for cell_pair in overlapping_cells:
#        cell_pair[0].cell_body.contact_inhibited = True
#        cell_pair[1].cell_body.contact_inhibited = True

#    data_writer.save_iteration(sim_iteration, cells)

#    sim_iteration += 1

sim = Simulation("sim_data.csv", initial_cell_num=100, env_size=100, max_iteration=20)
sim.run_sim()
sim.visualise_sim()