from cell_type import *
from data import DataWriter, DataReader
from visualiser import Visualiser

data_writer = DataWriter("sim_data.csv")

initial_cell_num = 4
cells = []

#x_pos = [-40.0, -20.0, 0.0, 20.0, 40.0, -40.0, -20.0, 0.0, 20.0, 40.0]
#x_pos = [-37.5, -12.5, 12.5, 37.5]
#y_pos = [-10.0, -10.0, -10.0, -10.0, -10.0, 10.0, 10.0, 10.0, 10.0, 10.0]

for i in range(initial_cell_num):
    pos = np.random.uniform(-20,20,[3])
    cells.append(GenericCell(id=i, pos=pos))

max_iteration = 30

sim_iteration = 0
data_writer.save_iteration(sim_iteration, cells)
sim_iteration += 1

while sim_iteration <= max_iteration:
    
    for cell in cells:
        if not cell.is_dead:
            cell.do_cell_cycle()
            cell.migrate()
            cell.type_specific_processes()
    
    # !!!! call physical solver

    data_writer.save_iteration(sim_iteration, cells)
        
    sim_iteration += 1

data_writer.write_data()

visualiser = Visualiser("sim_data.csv", max_iteration)
visualiser.visualise()