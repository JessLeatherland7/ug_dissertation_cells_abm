# cells_abm

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
