import math
import numpy as np

class PhysicalModel:
    
    LAMBDA = 0.125
    TARGET_SEPARATION = 0.125
    MAX_ITERATIONS = 50

    def __init__(self, env_size):
        self.env_size = env_size

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
    
    def get_overlap(self, cell, other_cell):
        sq_dist = np.sum((cell.cell_body.pos - other_cell.cell_body.pos) ** 2)
        if sq_dist <= (cell.cell_body.radius + other_cell.cell_body.radius) ** 2:
            return cell.cell_body.radius + other_cell.cell_body.radius - np.sqrt(sq_dist)
        else:
            return 0

    def get_overlapping_cells(self, cells):
        overlapping_cells = []
        overlapping_cell_matrix = np.array([[False for _ in range(len(cells))] for _ in range(len(cells))])
        #total_overlap = 0
        for i in range(len(cells) - 1):
            if not cells[i].is_dead:
                for j in range(i+1, len(cells)):
                    if not cells[j].is_dead:
                        overlap = self.get_overlap(cells[i], cells[j])
                        if overlap > 0:
                            #total_overlap += overlap
                            overlapping_cell_matrix[i, j] = True
                            overlapping_cell_matrix[j, i] = True
                            overlapping_cells.append((cells[i], cells[j]))

        return overlapping_cell_matrix, overlapping_cells#, total_overlap

    def get_force(self, cell_pos, cell_radius, other_cell_pos, other_cell_radius):
        diff_vector = (other_cell_pos - cell_pos)
        dist = np.linalg.norm(diff_vector)
        if dist == 0:
            unit_vector = np.random.uniform(-1, 1, [3])
            unit_vector /= np.linalg.norm(unit_vector)
        else:
            unit_vector = diff_vector / dist
        
        return unit_vector * (dist - cell_radius - other_cell_radius - self.TARGET_SEPARATION)

    def apply_forces(self, cells, overlapping_cell_matrix):
        for i in range(np.shape(overlapping_cell_matrix)[0]):
            if np.any(overlapping_cell_matrix[i]):
                force = np.array([0.0, 0.0, 0.0])
                cell_i_body = cells[i].cell_body
                cell_i_pos = cell_i_body.pos
                cell_i_radius = cell_i_body.radius
                
                for j in range(np.shape(overlapping_cell_matrix)[1]):
                    if overlapping_cell_matrix[i, j]:
                        cell_j_body = cells[j].cell_body
                        force += self.get_force(cell_i_pos, cell_i_radius, cell_j_body.pos, cell_j_body.radius)
                
                cell_i_body.apply_vel(self.LAMBDA * force)

    def is_cell_contact_inhibited(self, cells):
        pass

class PhysicalModelWithLocals(PhysicalModel):
    
    def __init__(self, env_size, max_cell_radius):
        super().__init__(env_size)
        self.grid_cells_per_side = int(self.env_size / (max_cell_radius * 4))
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
                if not current_cells[i].is_dead:
                    for j in range(i+1, len(current_cells)):
                        if not current_cells[j].is_dead and not overlapping_cell_matrix[current_cells[i].id, current_cells[j].id]:
                            if self.get_overlap(current_cells[i], current_cells[j]) > 0:
                                overlapping_cell_matrix[current_cells[i].id, current_cells[j].id] = True
                                overlapping_cell_matrix[current_cells[j].id, current_cells[i].id] = True
                                overlapping_cells.append((current_cells[i], current_cells[j]))
        
        return overlapping_cell_matrix, overlapping_cells

class NewPhysicalModel:
    LAMBDA = 0.125
    TARGET_SEPARATION = 0.125
    MAX_ITERATIONS = 100
    MIN_STABLE_OVERLAP_CUTOFF = 5.0
    MIN_STABLE_OVERLAP_DIFF = 0.025

    def __init__(self, env_size):
        self.env_size = env_size
    
    def solve_overlap(self, cells):
        solve_iteration = 0
        previous_overlap = self.MIN_STABLE_OVERLAP_DIFF + 1
        current_overlap = 0

        while solve_iteration < self.MAX_ITERATIONS and not (abs(previous_overlap - current_overlap) < self.MIN_STABLE_OVERLAP_DIFF and current_overlap > self.MIN_STABLE_OVERLAP_CUTOFF):

            previous_overlap = current_overlap
            
            current_overlap, cell_forces_dict, overlapping_cells = self.get_total_overlap_and_forces(cells)

            if not current_overlap:
                print("finished", solve_iteration)
                break
            elif (abs(previous_overlap - current_overlap) < self.MIN_STABLE_OVERLAP_DIFF and current_overlap > self.MIN_STABLE_OVERLAP_CUTOFF):
                print("minimised", solve_iteration, previous_overlap, current_overlap)
            else:
                for i, force_list in cell_forces_dict.items():
                    cells[i].cell_body.apply_vel(self.LAMBDA * np.sum(force_list, axis=0))

            solve_iteration += 1

        total_overlap, cell_forces_dict, overlapping_cells = self.get_total_overlap_and_forces(cells)

        return total_overlap, overlapping_cells
    

    def get_overlap_and_force(self, cell_i_pos, cell_i_radius, cell_j_pos, cell_j_radius):
        diff_vector = (cell_i_pos - cell_j_pos)
        dist = np.linalg.norm(diff_vector)
        
        if dist <= cell_i_radius + cell_j_radius:
            overlap = cell_i_radius + cell_j_radius - dist
        else:
            overlap = 0
    
        if overlap > 0:
            if dist == 0:
                unit_vector = np.random.uniform(-1, 1, [3])
                unit_vector /= np.linalg.norm(unit_vector)
            else:
                unit_vector = diff_vector / dist
            
            force = unit_vector * (overlap + self.TARGET_SEPARATION)

            return overlap, force
        else:
            return overlap, 0


    def get_total_overlap_and_forces(self, cells):
        total_overlap = 0
        cell_forces_dict = {}
        overlapping_cells = []
        
        for i in range(len(cells) - 1):
            if not cells[i].is_dead:
                cell_i_body = cells[i].cell_body
                cell_i_pos = cell_i_body.pos
                cell_i_radius = cell_i_body.radius
                
                for j in range(i+1, len(cells)):
                    if not cells[j].is_dead:
                        cell_j_body = cells[j].cell_body
                        overlap, force = self.get_overlap_and_force(cell_i_pos, cell_i_radius, cell_j_body.pos, cell_j_body.radius)

                        if overlap > 0:
                            total_overlap += overlap
                            overlapping_cells.append((cells[i], cells[j]))

                            if i in cell_forces_dict:
                                cell_forces_dict[i].append(force)
                            else:
                                cell_forces_dict[i] = [force]
                            
                            if j in cell_forces_dict:
                                cell_forces_dict[j].append(-force)
                            else:
                                cell_forces_dict[j] = [-force]
        
        return total_overlap, cell_forces_dict, overlapping_cells


class NewPhysicalModelWithLocals(NewPhysicalModel):

    def __init__(self, env_size, max_cell_radius):
        super().__init__(env_size)
        self.grid_cells_per_side = int(self.env_size / (max_cell_radius * 4))
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
    
    def get_total_overlap_and_forces(self, cells):
        local_envs = self.add_cells_to_local_environments(cells)

        total_overlap = 0
        cell_forces_dict = {}
        overlapping_cells = []
        
        overlapping_cell_matrix = np.array([[False for _ in range(len(cells))] for _ in range(len(cells))])
        
        for i in range(self.num_connected_environments):
            current_cells = local_envs[i] + local_envs[i+1]
            current_cells += local_envs[i+self.y_offset] + local_envs[i+self.y_offset+1]
            current_cells += local_envs[i+self.z_offset] + local_envs[i+self.z_offset+1]
            current_cells += local_envs[i+self.y_offset+self.z_offset] + local_envs[i+self.y_offset+self.z_offset+1]

            for j in range(len(current_cells) - 1):
                if not current_cells[j].is_dead:
                    cell_j_id = current_cells[j].id
                    cell_j_body = current_cells[j].cell_body
                    cell_j_pos = cell_j_body.pos
                    cell_j_radius = cell_j_body.radius
                    
                    for k in range(j+1, len(current_cells)):
                        cell_k_id = current_cells[k].id
                        if not current_cells[k].is_dead and not overlapping_cell_matrix[cell_j_id, cell_k_id]:
                            cell_k_body = current_cells[k].cell_body
                            overlap, force = self.get_overlap_and_force(cell_j_pos, cell_j_radius, cell_k_body.pos, cell_k_body.radius)

                            if overlap > 0:
                                total_overlap += overlap
                                overlapping_cells.append((current_cells[j], current_cells[k]))
                                if cell_j_id in cell_forces_dict:
                                    cell_forces_dict[cell_j_id].append(force)
                                else:
                                    cell_forces_dict[cell_j_id] = [force]
                                
                                if cell_k_id in cell_forces_dict:
                                    cell_forces_dict[cell_k_id].append(-force)
                                else:
                                    cell_forces_dict[cell_k_id] = [-force]
                                
                                overlapping_cell_matrix[cell_j_id, cell_k_id] = True
                                overlapping_cell_matrix[cell_k_id, cell_j_id] = True
        
        return total_overlap, cell_forces_dict, overlapping_cells
    