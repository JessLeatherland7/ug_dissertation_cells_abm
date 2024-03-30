from cell_type import *
from data import DataWriter, DataReader
from visualiser import Visualiser
from physics import *

data_writer = DataWriter("sim_data.csv")

initial_cell_num = 100
env_size = 100
max_iteration = 50
sim_iteration = 0
cells = []

#x_pos = [200, 200, 200]
#y_pos = [200, 200, 200]
#z_pos = [200, 200, 200]

for i in range(initial_cell_num):
    pos = np.random.uniform(20, env_size * 0.9, [3])
    #pos = np.array([x_pos[i], y_pos[i], z_pos[i]])
    cells.append(GenericCell(i, pos, env_size))

max_cell_radius = GenericCell.SEED_RADIUS * 1.259921
if int(env_size / (max_cell_radius * 4)) < 3:
    physics_model = PhysicalModel(env_size, max_cell_radius)
else:
    physics_model = PhysicalModelWithLocals(env_size, max_cell_radius)

overlapping_cell_matrix, overlapping_cells = physics_model.get_overlapping_cells(cells)
        
for cell_pair in overlapping_cells:
    cell_pair[0].cell_body.contact_inhibited = True
    cell_pair[1].cell_body.contact_inhibited = True

data_writer.save_iteration(sim_iteration, cells)

sim_iteration += 1

while sim_iteration <= max_iteration:
    for cell in cells:
        cell.cell_body.contact_inhibited = False
    
    for cell in cells:
        if not cell.is_dead:
            cell.do_cell_cycle()
            cell.migrate()
            cell.type_specific_processes()
        
    overlapping_cell_matrix, overlapping_cells = physics_model.solve_overlap(cells)
    
    for cell_pair in overlapping_cells:
        cell_pair[0].cell_body.contact_inhibited = True
        cell_pair[1].cell_body.contact_inhibited = True

    data_writer.save_iteration(sim_iteration, cells)

    sim_iteration += 1

data_writer.write_data()


visualiser = Visualiser("sim_data.csv", max_iteration, env_size)
visualiser.visualise()