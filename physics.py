import math
import numpy as np

class PhysicalModel:
    
    LAMBDA = 0.1
    TARGET_SEPARATION = 0.05
    MAX_ITERATIONS = 50

    def __init__(self, env_size, max_cell_radius):
        self.env_size = env_size
        self.max_cell_radius = max_cell_radius

    def overlapping(self, cell, other_cell):
        sq_dist = np.sum((cell.cell_body.pos - other_cell.cell_body.pos) ** 2)
        return sq_dist + self.TARGET_SEPARATION <= (cell.cell_body.radius + other_cell.cell_body.radius) ** 2

    def get_overlapping_cells(self, cells):
        overlapping_cells = []
        overlapping_cell_matrix = np.array([[False for _ in range(len(cells))] for _ in range(len(cells))])
        for i in range(len(cells) - 1):
            for j in range(i+1, len(cells)):
                if self.overlapping(cells[i], cells[j]):
                    overlapping_cell_matrix[cells[i].id, cells[j].id] = True
                    overlapping_cell_matrix[cells[j].id, cells[i].id] = True
                    overlapping_cells.append((cells[i], cells[j]))

        return overlapping_cell_matrix, overlapping_cells

    def get_overlapping_volumes(self, overlapping_cell_matrix):
        pass

    def apply_forces(self, cells, overlapping_cell_matrix):
        for i in range(len(overlapping_cell_matrix)):
            force = np.array([0.0, 0.0, 0.0])
            cell_i_body = cells[i].cell_body
            cell_i_pos = cell_i_body.pos
            cell_i_radius = cell_i_body.radius
            
            for j in range(len(overlapping_cell_matrix)):
                if overlapping_cell_matrix[i, j]:
                    cell_j_body = cells[j].cell_body
                    vector_ij = (cell_j_body.pos - cell_i_pos)
                    dist_ij = np.linalg.norm(vector_ij)
                    if dist_ij == 0:
                        unit_ij = np.random.uniform(-1, 1, [3])
                        unit_ij /= np.linalg.norm(unit_ij)
                    else:
                        unit_ij = vector_ij / (dist_ij)
                    force += unit_ij * (dist_ij - cell_i_radius - cell_j_body.radius - (self.TARGET_SEPARATION * 2))
            
            if np.any(force):
                cell_i_body.apply_vel(self.LAMBDA * force)    

    def is_cell_contact_inhibited(self, cells):
        pass

    def solve_overlap(self, cells):
        solve_iteration = 0
        while solve_iteration < self.MAX_ITERATIONS:
            overlapping_cell_matrix, overlapping_cells = self.get_overlapping_cells(cells)
            if not np.any(overlapping_cell_matrix):
                break
            else:
                self.apply_forces(cells, overlapping_cell_matrix)
            solve_iteration += 1
        
        return self.get_overlapping_cells(cells)



class PhysicalModelWithLocals(PhysicalModel):
    
    def __init__(self, env_size, max_cell_radius):
        super().__init__(env_size, max_cell_radius)
        self.grid_cells_per_side = int(self.env_size / (self.max_cell_radius * 4))
        self.y_offset = self.grid_cells_per_side
        self.z_offset = self.y_offset ** 2
        self.inv_grid_cell_size = self.grid_cells_per_side / self.env_size
        self.num_local_environments = self.grid_cells_per_side ** 3
        self.num_connected_environments = self.num_local_environments - self.y_offset - self.z_offset - 1

    def add_cells_to_local_environments(self, cells):
        local_environments = [[] for _ in range(self.num_local_environments)]
        for cell in cells:
            pos = cell.cell_body.pos
            pos_indices = np.clip((pos * self.inv_grid_cell_size).astype(np.int32), 0, self.grid_cells_per_side-1)
            index = np.sum([1, self.y_offset, self.z_offset] * pos_indices)
            local_environments[index].append(cell)

        return local_environments

    def get_overlapping_cells(self, cells):
        local_envs = self.add_cells_to_local_environments(cells)
        
        overlapping_cells = []
        overlapping_cell_matrix = np.array([[False for _ in range(len(cells))] for _ in range(len(cells))])
        
        for i in range(self.num_connected_environments):
            current_cells = local_envs[i] + local_envs[i+1]
            current_cells += local_envs[i+self.y_offset] + local_envs[i+self.y_offset+1]
            current_cells += local_envs[i+self.z_offset] + local_envs[i+self.z_offset+1]
            current_cells += local_envs[i+self.y_offset+self.z_offset] + local_envs[i+self.y_offset+self.z_offset+1]
            
            for i in range(len(current_cells) - 1):
                for j in range(i+1, len(current_cells)):
                    if not overlapping_cell_matrix[current_cells[i].id, current_cells[j].id]:
                        if self.overlapping(current_cells[i], current_cells[j]):
                            overlapping_cell_matrix[current_cells[i].id, current_cells[j].id] = True
                            overlapping_cell_matrix[current_cells[j].id, current_cells[i].id] = True
                            overlapping_cells.append((current_cells[i], current_cells[j]))
        
        return overlapping_cell_matrix, overlapping_cells
