# UG Dissertation Project - Development of a generic agent-based cell model in Python

This is my UG dissertation project for my BSc Computer Science (AI) degree at the University of Sheffield. Biological cell models are often specialised to fit the specific objectives of a research project, which has resulted in a lack of generic models to build on, with researchers typically required to program their models from scratch. My project aimed to create a 3D agent-based cell model in Python, encoding generic cell behaviours to facilitate efficient extension for future biological research. I achieved this, implementing: cell agents with their essential biological behaviours; a physical model keeping the agents from overlapping; a GUI to set up simulations; and useful features for research including graph generation of the cell population sizes, 3D visualisation of the agents, and data export options. I taught myself how to use Python bindings of C++ libraries for the GUI and 3D visualisation, which I had no prior experience of. I developed strong research and analysis skills through composing a detailed literature review, and improved my time management and feature prioritisation abilities by closely tracking my progress on the project requirements and managing where I spent my efforts effectively. The project was a success and is going to be adapted for further biological studies.

Referee: Dr Dawn Walker - d.c.walker@sheffield.ac.uk

## Intstructions for using the project

Install the following libraries with these pip commands:
- pip install glfw
- pip install matplotlib
- pip install numpy
- pip install opencv-python
- pip install PyOpenGL
- pip install PySide6
- pip install yappi

To run the application, run app.py

To add a new cell type, do the following:
1. Extend the AbstractCellType class in cell_type.py
2. Define the class constants (SEED_RADIUS, MEAN_CYC_LEN and STD_DEV_CYC_LEN)
3. Define the cell behaviour methods (all cell phase functions, migrate() and type_specific_processes())
4. Override any other behaviour necessary
5. Add a dictionary entry to cell_colours in visualiser.py of the form - ClassName: {Normal: (R, G, B), Quiescent: (R, G, B)}

To add a new substance layer, do the following:
1. Extend the AbstractEnvironmentLayer class in environment.py
2. Define the constant for the name of the substance (SUBSTANCE_NAME)
3. Define the get_level_at_pos() function, making sure it returns a float for the substance level at the given position
