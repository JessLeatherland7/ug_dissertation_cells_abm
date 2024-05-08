# -*- coding: utf-8 -*-

import matplotlib
matplotlib.use('Qt5Agg')

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from data import DataReader
from visualiser import Visualiser

class PopulationGraphCanvas(FigureCanvas):
    def __init__(self, input_file, parent=None, width=5, height=4, dpi=100):
        """Constructs the necessary attributes for the PopulationGraphCanvas object.
        
        Parameters
        ----------
        input_file : string
            the name of the data file for the simulation to be visualised
        parent : QWidget
            the parent widget of the graph canvas
        width : int
            the width of the graph canvas
        height : int
            the height of the graph canvas
        dpi : int
            the dpi of the graph canvas figure
        """
        self.input_file = input_file
        self.parent = parent
        
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        
        super(PopulationGraphCanvas, self).__init__(self.fig)

    def get_population_data(self, cell_types):
        """Gets the data from the simulation to plot in the graph.
        
        Parameters
        ----------
        cell_types : list
            a list of the cell type classes that are present in the simulation
        
        Returns
        -------
        iterations : int
            the number of iterations to plot on the x axis
        population_data : dict
            a dictionary relating each cell type name to a list of their alive
            population counts at each iteration to plot on the y axis
        """
        data_reader = DataReader(self.input_file)
        data_reader.read_data()

        iterations = []
        
        population_data = {}
        for cell_type in cell_types:
            population_data[cell_type.__name__] = []

        for iteration, cell_dict_list in data_reader.data.items():
            iterations.append(iteration)
            
            alive_cell_count = {}
            for cell_type in cell_types:
                alive_cell_count[cell_type.__name__] = 0

            for cell_dict in cell_dict_list:
                if not cell_dict["is_dead"]:
                    cell_type = cell_dict["cell_type"]
                    alive_cell_count[cell_type] += 1
            
            for cell_type in alive_cell_count:
                population_data[cell_type].append(alive_cell_count[cell_type])
        
        return iterations, population_data

    def plot_data(self, cell_types):
        """Plots the cell population data from the simulation on the graph canvas.
        
        Parameters
        ----------
        cell_types : list
            a list of the cell type classes that are present in the simulation
        """
        self.clear()
        
        iterations, population_data = self.get_population_data(cell_types)
        for cell_type in population_data:
            self.axes.plot(iterations, population_data[cell_type], 
                           color=Visualiser.cell_colours[cell_type]["Normal"], label=cell_type)
        
        self.axes.set_axis_on()
        self.axes.set_xlabel("Iteration")
        self.axes.set_ylabel("Alive cell population")
        self.axes.set_title("Cell population over time")
        self.axes.grid()
        
        if len(population_data) > 1:
            self.axes.legend()
        
        self.fig.tight_layout()

    def clear(self):
        """Clears the graph canvas."""
        self.axes.cla()
        self.axes.set_axis_off()