import math
import numpy as np

class PhysicalModel:
    FORCE_MULTIPLIER = 0.125
    TARGET_SEPARATION = 0.125
    MAX_ITERATIONS = 100
    MIN_STABLE_OVERLAP_CUTOFF = 5.0
    MIN_STABLE_OVERLAP_DIFF = 0.025
    MIN_CONTACTS_FOR_INHIBITION = 6
    CONTACT_INHIBITION_RADIUS = 1

    def __init__(self, env_size):
        self.env_size = env_size
    
    def solve_overlap(self, cells):
        solve_iteration = 0
        previous_overlap = self.MIN_STABLE_OVERLAP_DIFF + 1
        current_overlap = 0

        while solve_iteration < self.MAX_ITERATIONS and not (abs(previous_overlap - current_overlap) < self.MIN_STABLE_OVERLAP_DIFF and current_overlap > self.MIN_STABLE_OVERLAP_CUTOFF):

            previous_overlap = current_overlap
            
            current_overlap, cell_forces_dict = self.get_total_overlap_and_forces(cells)

            if not current_overlap:
                #print("finished", solve_iteration)
                break
            #elif (abs(previous_overlap - current_overlap) < self.MIN_STABLE_OVERLAP_DIFF and current_overlap > self.MIN_STABLE_OVERLAP_CUTOFF):
                #print("minimised", solve_iteration, previous_overlap, current_overlap)
            else:
                for i, force_list in cell_forces_dict.items():
                    cells[i].cell_body.apply_vel(self.FORCE_MULTIPLIER * np.sum(force_list, axis=0))

            solve_iteration += 1

        total_overlap, cell_forces_dict = self.get_total_overlap_and_forces(cells, extra_overlap_radius=self.CONTACT_INHIBITION_RADIUS)
        self.set_contact_inhibited_flags(cells, cell_forces_dict)

        return total_overlap
    

    def get_overlap_and_force(self, cell_i_pos, cell_i_radius, cell_j_pos, cell_j_radius, extra_overlap_radius):
        diff_vector = (cell_i_pos - cell_j_pos)
        dist = np.linalg.norm(diff_vector)
        
        if dist <= cell_i_radius + cell_j_radius + extra_overlap_radius:
            overlap = cell_i_radius + cell_j_radius + extra_overlap_radius - dist
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


    def get_total_overlap_and_forces(self, cells, extra_overlap_radius=0):
        total_overlap = 0
        cell_forces_dict = {}
        
        for i in range(len(cells) - 1):
            if not cells[i].is_dead:
                cell_i_body = cells[i].cell_body
                cell_i_pos = cell_i_body.pos
                cell_i_radius = cell_i_body.radius
                
                for j in range(i+1, len(cells)):
                    if not cells[j].is_dead:
                        cell_j_body = cells[j].cell_body
                        overlap, force = self.get_overlap_and_force(cell_i_pos, cell_i_radius, cell_j_body.pos, cell_j_body.radius, extra_overlap_radius)

                        if overlap > 0:
                            total_overlap += overlap

                            if i in cell_forces_dict:
                                cell_forces_dict[i].append(force)
                            else:
                                cell_forces_dict[i] = [force]
                            
                            if j in cell_forces_dict:
                                cell_forces_dict[j].append(-force)
                            else:
                                cell_forces_dict[j] = [-force]
        
        return total_overlap, cell_forces_dict
    
    
    def set_contact_inhibited_flags(self, cells, cell_forces_dict):
        for i in range(len(cells)):
            cell_body = cells[i].cell_body
            if i in cell_forces_dict and len(cell_forces_dict[i]) + cell_body.get_num_border_contacts() >= self.MIN_CONTACTS_FOR_INHIBITION:
                cell_body.contact_inhibited = True
            else:
                cell_body.contact_inhibited = False


class PhysicalModelWithLocals(PhysicalModel):

    def __init__(self, env_size, max_cell_radius):
        super().__init__(env_size)
        self.grid_cells_per_side = min(int(self.env_size / (max_cell_radius * 4)), 20)
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
    
    def get_total_overlap_and_forces(self, cells, extra_overlap_radius=0):
        local_envs = self.add_cells_to_local_environments(cells)

        total_overlap = 0
        cell_forces_dict = {}
        
        cell_pairs_checked_matrix = np.array([[False for _ in range(len(cells))] for _ in range(len(cells))])
        
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
                        if not current_cells[k].is_dead and not cell_pairs_checked_matrix[cell_j_id, cell_k_id]:
                            cell_k_body = current_cells[k].cell_body
                            overlap, force = self.get_overlap_and_force(cell_j_pos, cell_j_radius, cell_k_body.pos, cell_k_body.radius, extra_overlap_radius)

                            if overlap > 0:
                                total_overlap += overlap
                                if cell_j_id in cell_forces_dict:
                                    cell_forces_dict[cell_j_id].append(force)
                                else:
                                    cell_forces_dict[cell_j_id] = [force]
                                
                                if cell_k_id in cell_forces_dict:
                                    cell_forces_dict[cell_k_id].append(-force)
                                else:
                                    cell_forces_dict[cell_k_id] = [-force]
                                
                            cell_pairs_checked_matrix[cell_j_id, cell_k_id] = True
                            cell_pairs_checked_matrix[cell_k_id, cell_j_id] = True
        
        return total_overlap, cell_forces_dict
    