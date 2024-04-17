from data import DataReader

import matplotlib
matplotlib.use('Qt5Agg')

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class PopulationGraphCanvas(FigureCanvas):
    def __init__(self, input_file, parent=None, width=5, height=4, dpi=100):
        self.input_file = input_file
        self.parent = parent
        
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        
        super(PopulationGraphCanvas, self).__init__(self.fig)

    def get_population_data(self):
        data_reader = DataReader(self.input_file)
        data_reader.read_data()

        iterations = []
        population_data = []

        for iteration, cell_dict_list in data_reader.data.items():
            iterations.append(iteration)
            alive_cell_count = 0
            for cell_dict in cell_dict_list:
                if not cell_dict["is_dead"]:
                    alive_cell_count += 1

            population_data.append(alive_cell_count)
        
        return iterations, population_data

    def plot_data(self):
        iterations, population_data = self.get_population_data()
        self.axes.plot(iterations, population_data)
        self.axes.set_axis_on()
        self.axes.set_xlabel("Iteration")
        self.axes.set_ylabel("Alive cell population")
        self.axes.set_title("Cell population over time")
        self.fig.tight_layout()

    def clear(self):
        self.axes.cla()
        self.axes.set_axis_off()