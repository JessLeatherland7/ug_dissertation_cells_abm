# -*- coding: utf-8 -*-

import csv

class DataWriter:

    def __init__(self, output_file):
        """Constructs the necessary attributes for the DataWriter object.
        
        Parameters
        ----------
        output_file : string
            the name of the file for the simulation data to be saved to

        Other defined attributes
        ------------------------
        data : str
            the accumulated data from the simulation formatted as a string
        """
        self.output_file = output_file
        self.data = ""

    def save_iteration(self, iteration_num, cells):
        """Appends the cell data for the current iteration to the data string."""
        for cell in cells:
            self.data += f"{iteration_num}\t{cell.id}\t{cell.is_dead}" \
                + f"\t{type(cell).__name__}\t{cell.current_phase}" \
                + f"\t{(cell.cell_body.pos.tolist())}\t{cell.cell_body.radius}\n"

    def write_data(self):
        """Writes the data string to the output file location."""
        with open(self.output_file, "w") as f:
            f.write(self.data)
            f.close()


class DataReader:

    def __init__(self, input_file):
        """Constructs the necessary attributes for the DataReader object.
        
        Parameters
        ----------
        input_file : string
            the name of the file to read the simulation data from

        Other defined attributes
        ------------------------
        data : dict
            the data from the input file in a dictionary format
        """
        self.input_file = input_file
        self.data = {}

    def read_data(self):
        """Reads the simulation data from the input file into the data dictionary."""
        file = open(self.input_file)
        csvreader = csv.reader(file, delimiter="\t")

        for row in csvreader:
            iteration = int(row[0])
            cell_dict = {"id": int(row[1]), "is_dead": row[2] == "True",
                         "cell_type": row[3], "current_phase": row[4],
                         "pos": eval(row[5]), "radius": float(row[6])}
            if iteration in self.data:
                self.data[iteration].append(cell_dict)
            else:
                self.data.update({iteration: [cell_dict]})

        file.close()

    def get_iteration(self, iteration):
        """Gets the cell data for the given iteration.
        
        Returns
        -------
        dictionary entry for given simulation iteration
        """
        return self.data[iteration]
