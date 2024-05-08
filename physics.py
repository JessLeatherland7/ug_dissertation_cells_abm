# -*- coding: utf-8 -*-

import numpy as np

import utils

class PhysicalModel:
    MAX_ITERATIONS = 100
    FORCE_MULTIPLIER = 0.125
    TARGET_SEPARATION = 0.125
    MIN_STABLE_OVERLAP_CUTOFF = 5.0
    MIN_STABLE_OVERLAP_DIFF = 0.025
    MIN_CONTACTS_FOR_INHIBITION = 6
    CONTACT_INHIBITION_RADIUS = 0.5

    def __init__(self, env_size):
        """Constructs the necessary attributes for the PhysicalModel object.
        
        Parameters
        ----------
        env_size : float
            the width of the environment
        """
        self.env_size = env_size

    
    def solve_overlap(self, sim_iteration, cells):
        """Minimises the cell overlap between the given cells.
        
        Parameters
        ----------
        sim_iteration : int
            the current simulation iteration being solved
        cells : list
            the cell agent objects in the simulation
        """
        solve_iteration = 0
        previous_overlap = self.MIN_STABLE_OVERLAP_DIFF + 1
        current_overlap = 0

        # Attempt to solve the overlap within MAX_ITERATIONS
        while solve_iteration < self.MAX_ITERATIONS:

            previous_overlap = current_overlap
            
            # Get the total overlap and the forces to apply to each cell
            current_overlap, cell_forces_dict = self.get_total_overlap_and_forces(cells)

            # Stop solver if there is no overlap or it has stabilised
            if not current_overlap or self.overlap_stabilised(previous_overlap, current_overlap):
                break
            else:
                # Apply the sum of each cell's forces to their positions
                for i, force_list in cell_forces_dict.items():
                    sum_forces = np.sum(force_list, axis=0)
                    cells[i].cell_body.apply_vel(self.FORCE_MULTIPLIER * sum_forces)

            solve_iteration += 1

        # Get the cell forces that apply to the cells within the contact inhibition radius
        total_overlap, cell_forces_dict = self.get_total_overlap_and_forces(
            cells, extra_overlap_radius=self.CONTACT_INHIBITION_RADIUS)
        
        # Set whether the cells are contact inhibited or not
        self.set_contact_inhibited_flags(cells, cell_forces_dict)

        # ================= Uncomment to track overlap =====================
        #total_overlap, _ = self.get_total_overlap_and_forces(cells)
        #if total_overlap > 0:
        #    print("Iteration:", sim_iteration, "  Overlap:", total_overlap)
        # ==================================================================

    def overlap_stabilised(self, previous_overlap, current_overlap):
        """Returns whether the current overlap has stabilised.
        
        Parameters
        ----------
        previous_overlap : float
            the overlap from the previous solve iteration
        current_overlap : float
            the overlap from the current solve iteration

        Returns
        -------
        bool
            whether the difference in the current and previous overlap is
            low enough and the current overlap is high enough to consider
            it stabilised
        """
        diff_below_thresh = abs(previous_overlap - current_overlap) < self.MIN_STABLE_OVERLAP_DIFF
        overlap_above_cutoff = current_overlap > self.MIN_STABLE_OVERLAP_CUTOFF
        return diff_below_thresh and overlap_above_cutoff

    def get_overlap_and_force(self, cell_i_pos, cell_i_radius, 
                              cell_j_pos, cell_j_radius, extra_overlap_radius=0):
        """Gets the overlap between cells i and j, and if there is overlap,
        computes the force that cell j exerts on cell i.
        
        Parameters
        ----------
        cell_i_pos : numpy.ndarray(3)
            the position of cell i
        cell_i_radius : float
            the radius of cell i
        cell_j_pos : numpy.ndarray(3)
            the position of cell j
        cell_j_radius : float
            the radius of cell j
        extra_overlap_radius : float = 0
            optional extra distance between cells where they can be considered 
            overlapping

        Returns
        -------
        overlap : float
            the overlapping distance between cell i and cell j
        force : float
            the force that cell j exerts on cell i
        """
        diff_vector = cell_i_pos - cell_j_pos
        dist = np.linalg.norm(diff_vector)
        
        if dist <= cell_i_radius + cell_j_radius + extra_overlap_radius:
            overlap = cell_i_radius + cell_j_radius + extra_overlap_radius - dist
        else:
            overlap = 0
    
        if overlap > 0:
            if dist == 0:
                # If cells directly on top of each other, separate in random direction
                unit_vector = utils.rand_unit_vec()
            else:
                unit_vector = diff_vector / dist
            
            force = unit_vector * (overlap + self.TARGET_SEPARATION)

            return overlap, force
        else:
            return overlap, 0.0

    def get_total_overlap_and_forces(self, cells, extra_overlap_radius=0):
        """Gets the total overlap between all cell pairs, and gets the forces
        exerted on each cell.
        
        Parameters
        ----------
        cells : list
            the cell agent objects in the simulation
        extra_overlap_radius : float = 0
            optional extra distance between cells where they can be considered 
            overlapping

        Returns
        -------
        total_overlap : float
            the sum of all overlap between cell pairs in the simulation
        cell_forces_dict : dict
            a dictionary relating the cell ids to a list of the forces
            that are exerted on them
        """
        total_overlap = 0.0
        cell_forces_dict = {}
        
        for i in range(len(cells) - 1):
            if not cells[i].is_dead:
                cell_i_body = cells[i].cell_body
                cell_i_pos = cell_i_body.pos
                cell_i_radius = cell_i_body.radius
                
                for j in range(i+1, len(cells)):
                    if not cells[j].is_dead:
                        cell_j_body = cells[j].cell_body
                        
                        # Get overlap between cells i and j and force that j exerts on i
                        overlap, force = self.get_overlap_and_force(
                            cell_i_pos, cell_i_radius, 
                            cell_j_body.pos, cell_j_body.radius, extra_overlap_radius)

                        if overlap > 0:
                            total_overlap += overlap
                            
                            # Add force that cell j exerts on cell i to cell i's force list
                            if i in cell_forces_dict:
                                cell_forces_dict[i].append(force)
                            else:
                                cell_forces_dict[i] = [force]
                            
                            # Add equal and opposite force that cell i exerts on cell j
                            # to cell j's force list
                            if j in cell_forces_dict:
                                cell_forces_dict[j].append(-force)
                            else:
                                cell_forces_dict[j] = [-force]
        
        return total_overlap, cell_forces_dict
    
    def set_contact_inhibited_flags(self, cells, cell_forces_dict):
        """Sets the contact inhibited flags for all cells in the simulation.
        
        The number of contacts a cell has is given by the number of environment
        borders it is touching plus the number of forces that are being applied to
        it by other cells. If this is above MIN_CONTACTS_FOR_INHIBITION, the
        cell is contact inhibited.

        Parameters
        ----------
        cells : list
            the cell agent objects in the simulation
        cell_forces_dict : dict
            the dictionary relating cell ids to the list of forces being applied
            to them
        """
        for i in range(len(cells)):
            cell_body = cells[i].cell_body
            if i in cell_forces_dict:
                contacts = len(cell_forces_dict[i]) + cell_body.get_num_border_contacts() 
                if contacts >= self.MIN_CONTACTS_FOR_INHIBITION:
                    cell_body.contact_inhibited = True
            else:
                contacts = cell_body.get_num_border_contacts()
                if contacts >= self.MIN_CONTACTS_FOR_INHIBITION:
                    cell_body.contact_inhibited = True
                else:
                    cell_body.contact_inhibited = False


class PhysicalModelWithLocals(PhysicalModel):

    def __init__(self, env_size, max_cell_radius):
        """Constructs the necessary attributes for the PhysicalModelWithLocals object.
        
        This class extends the PhysicalModel to split the environment into chunks
        (local environments), and uses a windowing algorithm to only check for overlapping
        cells in neighbouring environments.

        Parameters
        ----------
        env_size : float
            the width of the environment
        max_cell_radius: float
            the maximum radius that a cell in the simulation can have

        Other defined attributes
        ------------------------
        local_envs_per_side : int
            the number of local environments that fit along a side of the environment
        y_offset : int
            the offset for the y index of the local environments
        z_offset : int
            the offset for the z index of the local environments
        inv_local_env_size : float
            1 / the width of each local environment
        num_local_environments : int
            the total number of local environments
        num_window_positions : int
            the number of positions the 2x2x2 window can be in
        """
        super().__init__(env_size)
        
        """
        The number of local environments per side is the maximum number with
        width greater than two cell diameters that can fit along a side of the 
        environment, capped at 20
        """
        self.local_envs_per_side = min(int(self.env_size / (max_cell_radius * 4)), 20)
        
        self.y_offset = self.local_envs_per_side
        self.z_offset = self.y_offset ** 2
        self.inv_local_env_size = self.local_envs_per_side / self.env_size
        self.num_local_environments = self.local_envs_per_side ** 3
        self.num_window_positions = self.num_local_environments - self.y_offset - self.z_offset - 1

    def add_cells_to_local_environments(self, cells):
        """Sets up a list for each local environment containing the cells that fall within them.
        
        The positions of each cell are converted into the indices of the local environments
        they fall within, and they are each added to the corresponding local environment list.

        Parameters
        ----------
        cells : list
            the cell agent objects in the simulation

        Returns
        -------
        local_environments : list
            list of local environment lists containing the cells that fall within them
        """
        local_environments = [[] for _ in range(self.num_local_environments)]
        for cell in cells:
            pos = cell.cell_body.pos
            pos_indices = (pos * self.inv_local_env_size).astype(np.int32)
            pos_indices = np.clip(pos_indices, 0, self.local_envs_per_side-1)
            env_index = np.sum([1, self.y_offset, self.z_offset] * pos_indices)
            local_environments[env_index].append(cell)

        return local_environments
    
    def get_total_overlap_and_forces(self, cells, extra_overlap_radius=0):
        """Overrides the PhysicalModel behaviour to get the total overlap between
        cell pairs that fall within a marching window, and gets the forces
        exerted on each cell.
        
        Parameters
        ----------
        cells : list
            the cell agent objects in the simulation
        extra_overlap_radius : float = 0
            optional extra distance between cells where they can be considered 
            overlapping

        Returns
        -------
        total_overlap : float
            the sum of all overlap between cell pairs in the simulation
        cell_forces_dict : dict
            a dictionary relating the cell ids to a list of the forces
            that are exerted on them
        """
        local_envs = self.add_cells_to_local_environments(cells)

        total_overlap = 0
        cell_forces_dict = {}
        
        # Used so that cell pairs that fall into multiple positions of the marching
        # window are not checked more than once
        cell_pairs_checked_matrix = np.array(
            [[False for _ in range(len(cells))] for _ in range(len(cells))]
        )
        
        for i in range(self.num_window_positions):
            # Collect cells within current window
            current_cells = local_envs[i] + local_envs[i+1]
            current_cells += local_envs[i+self.y_offset] + local_envs[i+self.y_offset+1]
            current_cells += local_envs[i+self.z_offset] + local_envs[i+self.z_offset+1]
            current_cells += local_envs[i+self.y_offset+self.z_offset] 
            current_cells += local_envs[i+self.y_offset+self.z_offset+1]

            # Check all cell pairs within current window for overlap
            for j in range(len(current_cells) - 1):
                if not current_cells[j].is_dead:
                    cell_j_id = current_cells[j].id
                    cell_j_body = current_cells[j].cell_body
                    cell_j_pos = cell_j_body.pos
                    cell_j_radius = cell_j_body.radius
                    
                    for k in range(j+1, len(current_cells)):
                        if not current_cells[k].is_dead:
                            cell_k_id = current_cells[k].id
                            if not cell_pairs_checked_matrix[cell_j_id, cell_k_id]:
                                cell_k_body = current_cells[k].cell_body
                                cell_k_pos = cell_k_body.pos
                                cell_k_radius = cell_k_body.radius
                                
                                # Get overlap between cells j and k and force that k exerts on j
                                overlap, force = self.get_overlap_and_force(
                                    cell_j_pos, cell_j_radius, 
                                    cell_k_pos, cell_k_radius, extra_overlap_radius)

                                if overlap > 0:
                                    total_overlap += overlap

                                    # Add force that cell k exerts on cell j to cell j's force list
                                    if cell_j_id in cell_forces_dict:
                                        cell_forces_dict[cell_j_id].append(force)
                                    else:
                                        cell_forces_dict[cell_j_id] = [force]
                                    
                                    # Add equal and opposite force that cell j exerts on cell k
                                    # to cell k's force list
                                    if cell_k_id in cell_forces_dict:
                                        cell_forces_dict[cell_k_id].append(-force)
                                    else:
                                        cell_forces_dict[cell_k_id] = [-force]
                                
                                # Track that the cell pair has been checked
                                cell_pairs_checked_matrix[cell_j_id, cell_k_id] = True
                                cell_pairs_checked_matrix[cell_k_id, cell_j_id] = True
        
        return total_overlap, cell_forces_dict
    