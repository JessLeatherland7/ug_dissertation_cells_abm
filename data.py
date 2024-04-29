import csv

class DataWriter:

    def __init__(self, output_file):
        self.output_file = output_file
        self.data = ""

    def save_iteration(self, iteration_num, cells):
        for cell in cells:
            self.data += f"{iteration_num}\t{cell.id}\t{cell.is_dead}\t{type(cell).__name__}\t{cell.current_phase}\t{(cell.cell_body.pos.tolist())}\t{cell.cell_body.radius}\n"

    def write_data(self):
        with open(self.output_file, "w") as f:
            f.write(self.data)
            f.close()


class DataReader:

    def __init__(self, input_file):
        self.input_file = input_file
        self.data = {}

    def read_data(self):
        file = open(self.input_file)
        csvreader = csv.reader(file, delimiter="\t")

        for row in csvreader:
            iteration = int(row[0])
            cell_dict = {"id": int(row[1]), "is_dead": row[2] == "True", "cell_type": row[3], 
                         "current_phase": row[4], "pos": eval(row[5]), "radius": float(row[6])}
            if iteration in self.data:
                self.data[iteration].append(cell_dict)
            else:
                self.data.update({iteration: [cell_dict]})

        file.close()

    def get_iteration(self, iteration):
        return self.data[iteration]
