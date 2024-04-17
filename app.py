import sys

from PySide6.QtCore import QRect, QSize, Qt, QTimer
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (QApplication, QDialog, QComboBox, QDoubleSpinBox,
     QFrame, QHBoxLayout, QLabel, QMainWindow, QPushButton, QScrollArea,
    QSizePolicy, QSlider, QSpacerItem, QSpinBox, QVBoxLayout, QWidget)

from cell_type import *
from environment import *
from simulation import Simulation
from visualiser import Visualiser
from graphs import *

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setMinimumSize(QSize(1000, 700))
        self.setWindowTitle("Cell ABM")
        self.central_widget = QWidget()
        
        self.init_model_setup_panel()
        self.init_graphs_panel()
        self.init_playback_panel()

        self.setCentralWidget(self.central_widget)
        
        self.export_data_action = QAction("Export data")
        self.export_data_action.triggered.connect(self.export_data)
        self.export_video_action = QAction("Export video")
        self.export_video_action.triggered.connect(self.export_video)

        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu("File")
        self.file_menu.addAction(self.export_data_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.export_video_action)

        
    def init_model_setup_panel(self):
        self.model_setup_widget = QWidget(self.central_widget)
        self.model_setup_widget.setGeometry(QRect(10, 10, 400, 300))
        self.model_setup_layout = QVBoxLayout(self.model_setup_widget)
        self.model_setup_layout.setContentsMargins(0, 0, 0, 0)
        self.model_setup_top_layout = QHBoxLayout()
        
        self.model_setup_title = QLabel("Model Setup:")
        self.model_setup_top_layout.addWidget(self.model_setup_title)

        self.horizontal_spacer_1 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.model_setup_top_layout.addItem(self.horizontal_spacer_1)

        self.model_reset_button = QPushButton("Reset")
        self.model_reset_button.clicked.connect(self.reset_model)
        self.model_setup_top_layout.addWidget(self.model_reset_button)

        self.model_run_button = QPushButton("Run")
        self.model_run_button.clicked.connect(self.run_model)
        self.model_setup_top_layout.addWidget(self.model_run_button)

        self.model_setup_layout.addLayout(self.model_setup_top_layout)

        self.hline_1 = QFrame(self.model_setup_widget)
        self.hline_1.setFrameShape(QFrame.HLine)
        self.hline_1.setFrameShadow(QFrame.Sunken)
        self.model_setup_layout.addWidget(self.hline_1)

        self.model_setup_scroll_area = QScrollArea(self.model_setup_widget)
        self.model_setup_scroll_area.setWidgetResizable(True)
        self.scroll_area_widget_contents = QWidget()
        self.scroll_area_widget_contents.setGeometry(QRect(0, 0, 400, 255))

        self.init_cell_setup_widget()
        self.init_env_setup_widget()
        self.init_sim_setup_widget()

        self.model_setup_scroll_area.setWidget(self.scroll_area_widget_contents)

        self.model_setup_layout.addWidget(self.model_setup_scroll_area)


    def init_cell_setup_widget(self):
        self.cell_types = AbstractCellType.__subclasses__()
        self.cell_type_names = []
        for cell_type in self.cell_types:
            self.cell_type_names.append(cell_type.__name__)

        self.cell_setup_widget = QWidget(self.scroll_area_widget_contents)
        self.cell_setup_widget.setGeometry(QRect(0, 0, 400, 85))
        self.cell_setup_layout = QVBoxLayout(self.cell_setup_widget)
        self.cell_setup_layout.setContentsMargins(5, 5, 5, 0)
        
        self.cell_setup_title = QLabel("Cells:")
        self.cell_setup_layout.addWidget(self.cell_setup_title)

        self.add_cells_layout = QHBoxLayout()
        
        self.cell_type_combo_box = QComboBox(self.cell_setup_widget)
        self.cell_type_combo_box.addItems(self.cell_type_names)
        self.cell_type_combo_box.currentTextChanged.connect(self.cell_type_changed)
        self.add_cells_layout.addWidget(self.cell_type_combo_box)

        self.cell_num_label = QLabel("Num:")
        self.add_cells_layout.addWidget(self.cell_num_label)

        self.seed_cells_spin_box = QSpinBox(self.cell_setup_widget)
        self.seed_cells_spin_box.setFixedWidth(75)
        self.seed_cells_spin_box.setRange(1, 100)
        self.seed_cells_spin_box.setSingleStep(1)
        self.add_cells_layout.addWidget(self.seed_cells_spin_box)

        self.horizontal_spacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.add_cells_layout.addItem(self.horizontal_spacer_2)

        self.cell_setup_layout.addLayout(self.add_cells_layout)

        self.add_more_cell_types_layout = QHBoxLayout()
        self.add_cell_type_button = QPushButton("+ Cell type")
        self.add_cell_type_button.setEnabled(False)
        self.add_cell_type_button.clicked.connect(self.add_cell_type)
        self.add_more_cell_types_layout.addWidget(self.add_cell_type_button)

        self.horizontal_spacer_3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.add_more_cell_types_layout.addItem(self.horizontal_spacer_3)

        self.cell_setup_layout.addLayout(self.add_more_cell_types_layout)

        self.hline_2 = QFrame(self.cell_setup_widget)
        self.hline_2.setFrameShape(QFrame.HLine)
        self.hline_2.setFrameShadow(QFrame.Sunken)

        self.cell_setup_layout.addWidget(self.hline_2)


    def init_env_setup_widget(self):
        self.env_layers = AbstractEnvironmentLayer.__subclasses__()
        self.env_layer_names = []
        for env_layer in self.env_layers:
            self.env_layer_names.append(env_layer.__name__)

        self.env_setup_widget = QWidget(self.scroll_area_widget_contents)
        self.env_setup_widget.setGeometry(QRect(0, 85, 400, 120))
        self.env_setup_layout = QVBoxLayout(self.env_setup_widget)
        self.env_setup_layout.setContentsMargins(5, 0, 5, 0)
        
        self.env_setup_title = QLabel("Environment:")
        self.env_setup_layout.addWidget(self.env_setup_title)

        self.env_set_width_layout = QHBoxLayout()
        
        self.env_width_label = QLabel("Width:")
        self.env_set_width_layout.addWidget(self.env_width_label)

        self.env_width_double_spin_box = QDoubleSpinBox(self.env_setup_widget)
        self.env_width_double_spin_box.setRange(25.0, 9999999.99)
        self.env_width_double_spin_box.setSingleStep(5.00)
        self.env_width_double_spin_box.setMinimumWidth(130)
        self.env_set_width_layout.addWidget(self.env_width_double_spin_box)

        self.um_label = QLabel("μm")
        self.env_set_width_layout.addWidget(self.um_label)

        self.horizontal_spacer_4 = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.env_set_width_layout.addItem(self.horizontal_spacer_4)

        self.env_setup_layout.addLayout(self.env_set_width_layout)

        self.add_substance_layout = QHBoxLayout()
        
        self.substance_combo_box = QComboBox(self.env_setup_widget)
        self.substance_combo_box.addItem("")
        self.substance_combo_box.addItems(self.env_layer_names)
        self.substance_combo_box.currentTextChanged.connect(self.substance_changed)
        self.add_substance_layout.addWidget(self.substance_combo_box)

        self.substance_level_double_spin_box = QDoubleSpinBox(self.env_setup_widget)
        self.substance_level_double_spin_box.setRange(0.0, 999.99)
        self.substance_level_double_spin_box.setSingleStep(0.1)
        self.substance_level_double_spin_box.setMinimumWidth(110)
        self.substance_level_double_spin_box.setEnabled(False)
        self.add_substance_layout.addWidget(self.substance_level_double_spin_box)

        self.units_label = QLabel("units")
        self.add_substance_layout.addWidget(self.units_label)

        self.horizontal_spacer_5 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.add_substance_layout.addItem(self.horizontal_spacer_5)

        self.env_setup_layout.addLayout(self.add_substance_layout)

        self.add_more_substances_layout = QHBoxLayout()
        self.add_substance_button = QPushButton("+ Substance")
        self.add_substance_button.setEnabled(False)
        self.add_substance_button.clicked.connect(self.add_substance)
        self.add_more_substances_layout.addWidget(self.add_substance_button)

        self.horizontal_spacer_6 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.add_more_substances_layout.addItem(self.horizontal_spacer_6)

        self.env_setup_layout.addLayout(self.add_more_substances_layout)

        self.hline_3 = QFrame(self.env_setup_widget)
        self.hline_3.setFrameShape(QFrame.HLine)
        self.hline_3.setFrameShadow(QFrame.Sunken)
        self.env_setup_layout.addWidget(self.hline_3)


    def init_sim_setup_widget(self):
        self.sim_setup_widget = QWidget(self.scroll_area_widget_contents)
        self.sim_setup_widget.setGeometry(QRect(0, 205, 400, 50))
        self.sim_setup_layout = QVBoxLayout(self.sim_setup_widget)
        self.sim_setup_layout.setContentsMargins(5, 0, 5, 0)
        
        self.sim_setup_title = QLabel("Simulation:")
        self.sim_setup_layout.addWidget(self.sim_setup_title)

        self.sim_iter_and_seed_layout = QHBoxLayout()
        
        self.sim_iter_label = QLabel("Iterations:")
        self.sim_iter_and_seed_layout.addWidget(self.sim_iter_label)

        self.sim_iter_spin_box = QSpinBox(self.sim_setup_widget)
        self.sim_iter_spin_box.setMinimumWidth(100)
        self.sim_iter_spin_box.setRange(1, 9999)
        self.sim_iter_spin_box.setSingleStep(1)
        self.sim_iter_and_seed_layout.addWidget(self.sim_iter_spin_box)

        self.sim_rand_seed_label = QLabel("Random seed:")
        self.sim_iter_and_seed_layout.addWidget(self.sim_rand_seed_label)

        self.sim_rand_seed_spin_box = QSpinBox(self.sim_setup_widget)
        self.sim_rand_seed_spin_box.setMinimumWidth(100)
        self.sim_rand_seed_spin_box.setRange(0, 9999)
        self.sim_rand_seed_spin_box.setSingleStep(1)
        self.sim_iter_and_seed_layout.addWidget(self.sim_rand_seed_spin_box)

        self.horizontal_spacer_7 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.sim_iter_and_seed_layout.addItem(self.horizontal_spacer_7)

        self.sim_setup_layout.addLayout(self.sim_iter_and_seed_layout)


    def init_graphs_panel(self):
        self.graphs_widget = QWidget(self.central_widget)
        self.graphs_widget.setGeometry(QRect(10, 320, 400, 320))
        self.graphs_layout = QVBoxLayout(self.graphs_widget)
        self.graphs_layout.setContentsMargins(0, 0, 0, 0)
        
        self.graphs_title = QLabel("Graphical Analysis:")
        self.graphs_layout.addWidget(self.graphs_title)

        self.hline_4 = QFrame(self.graphs_widget)
        self.hline_4.setFrameShape(QFrame.HLine)
        self.hline_4.setFrameShadow(QFrame.Sunken)
        self.graphs_layout.addWidget(self.hline_4)

        self.graph_canvas = PopulationGraphCanvas("sim_data.csv", self.graphs_widget)
        self.graph_canvas.axes.cla()
        self.graph_canvas.axes.set_axis_off()
        self.graphs_layout.addWidget(self.graph_canvas)


    def init_playback_panel(self):
        self.playback_widget = QWidget(self.central_widget)
        self.playback_widget.setGeometry(QRect(430, 10, 560, 60))
        self.playback_layout = QVBoxLayout(self.playback_widget)
        self.playback_layout.setContentsMargins(0, 0, 0, 0)
        
        self.playback_fps_and_iter_layout = QHBoxLayout()
        
        self.playback_fps_label = QLabel("FPS:")
        self.playback_fps_and_iter_layout.addWidget(self.playback_fps_label)

        self.playback_fps_spin_box = QSpinBox(self.playback_widget)
        self.playback_fps_spin_box.setMinimumWidth(70)
        self.playback_fps_spin_box.setRange(1, 30)
        self.playback_fps_spin_box.setSingleStep(1)
        self.playback_fps_spin_box.valueChanged.connect(self.change_fps)
        self.playback_fps_and_iter_layout.addWidget(self.playback_fps_spin_box)

        self.horizontal_spacer_8 = QSpacerItem(20, 20, QSizePolicy.Fixed, QSizePolicy.Minimum)
        self.playback_fps_and_iter_layout.addItem(self.horizontal_spacer_8)

        self.playback_iter_label = QLabel("ITERATION:")
        self.playback_fps_and_iter_layout.addWidget(self.playback_iter_label)

        self.playback_iter_spin_box = QSpinBox(self.playback_widget)
        self.playback_iter_spin_box.setMinimumWidth(100)
        self.playback_iter_spin_box.setMinimum(0)
        self.playback_iter_spin_box.setSingleStep(1)
        self.playback_iter_spin_box.setEnabled(False)
        self.playback_iter_spin_box.editingFinished.connect(self.playback_iter_changed)
        self.playback_fps_and_iter_layout.addWidget(self.playback_iter_spin_box)

        self.horizontal_spacer_9 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.playback_fps_and_iter_layout.addItem(self.horizontal_spacer_9)

        self.playback_layout.addLayout(self.playback_fps_and_iter_layout)

        self.playback_play_layout = QHBoxLayout()
        
        self.playback_play_pause_button = QPushButton("Play")
        self.playback_play_pause_button.clicked.connect(self.play_pause)
        self.playback_play_pause_button.setEnabled(False)
        self.playback_play_layout.addWidget(self.playback_play_pause_button)

        self.playback_slider = QSlider(self.playback_widget)
        self.playback_slider.setEnabled(False)
        self.playback_slider.setOrientation(Qt.Horizontal)
        self.playback_slider.sliderReleased.connect(self.playback_slider_changed)
        self.playback_play_layout.addWidget(self.playback_slider)

        self.playback_layout.addLayout(self.playback_play_layout)

        self.visualiser = Visualiser(self.central_widget)
        self.visualiser.setGeometry(QRect(430, 80, 560, 560))
        self.visualiser.setVisible(False)

        self.timer = QTimer(self)
        self.timer.setInterval(1000/self.playback_fps_spin_box.value())   # period, in milliseconds
        self.timer.timeout.connect(self.visualiser.update)
        self.timer.timeout.connect(self.play_next_iteration)

        self.current_iteration = 0
        self.max_iteration = 0

    def export_data(self, e):
        pass

    def export_video(self, e):
        pass

    def reset_model(self, e):
        self.timer.stop()
        self.visualiser.setVisible(False)
        
        self.cell_type_combo_box.setCurrentText(self.cell_type_names[0])
        self.seed_cells_spin_box.setValue(1)
        
        self.env_width_double_spin_box.setValue(10.0)
        self.substance_combo_box.setCurrentText("")
        self.substance_level_double_spin_box.setValue(0.0)
        self.substance_level_double_spin_box.setEnabled(False)
        
        self.sim_iter_spin_box.setValue(1)
        self.sim_rand_seed_spin_box.setValue(0)

        self.graph_canvas.clear()

        self.playback_fps_spin_box.setValue(1)
        self.playback_iter_spin_box.setValue(0)
        self.playback_iter_spin_box.setEnabled(False)
        self.playback_play_pause_button.setText("Play")
        self.playback_play_pause_button.setEnabled(False)
        self.playback_slider.setSliderPosition(0)
        self.playback_slider.setEnabled(False)
        
        # remove extra cell type and substance level combos and set plus buttons enabled/disabled accordingly

    def run_model(self, e):
        self.timer.stop()

        input_cell_types = []
        for cell_type in self.cell_types:
            if cell_type.__name__ == self.cell_type_combo_box.currentText():
                input_cell_types.append(cell_type)
        
        initial_cell_num = [self.seed_cells_spin_box.value()]
        
        env_size = self.env_width_double_spin_box.value()
        input_env_layers = []
        for env_layer in self.env_layers:
            if env_layer.__name__ == self.substance_combo_box.currentText():
                input_env_layers.append(env_layer(env_size, self.substance_level_double_spin_box.value()))

        self.max_iteration = self.sim_iter_spin_box.value()
        random_seed = self.sim_rand_seed_spin_box.value()
        
        sim = Simulation("sim_data.csv", input_cell_types, initial_cell_num, env_size, input_env_layers, self.max_iteration, random_seed)
        sim.run_sim()

        self.graph_canvas.plot_data()
        self.graph_canvas.draw()

        self.visualiser.ready_visualisation("sim_data.csv", env_size, self.visualiser.width(), self.visualiser.height())
        self.visualiser.setVisible(True)
        
        self.playback_iter_spin_box.setRange(0, self.max_iteration)
        self.playback_iter_spin_box.setEnabled(True)
        self.playback_play_pause_button.setEnabled(True)
        self.playback_slider.setRange(0, self.max_iteration)
        self.playback_slider.setEnabled(True)


    def cell_type_changed(self, e):
        pass

    def add_cell_type(self, e):
        pass

    def substance_changed(self, new_substance):
        if new_substance == "":
            self.substance_level_double_spin_box.setValue(0.0)
            self.substance_level_double_spin_box.setEnabled(False)
        else:
            self.substance_level_double_spin_box.setEnabled(True)

    def add_substance(self, e):
        pass

    def change_fps(self, new_fps):
        self.timer.setInterval(1000/new_fps)

    def playback_iter_changed(self):
        self.current_iteration = self.playback_iter_spin_box.value()
        self.playback_slider.setValue(self.current_iteration)
        self.visualiser.set_iteration(self.current_iteration)
        self.visualiser.update()

    def play_pause(self, e):
        if self.playback_play_pause_button.text() == "Play":
            if self.current_iteration == self.max_iteration:
                self.current_iteration = 0
                self.set_playback_iter_and_slider()
            self.playback_play_pause_button.setText("Pause")
            self.playback_iter_spin_box.setEnabled(False)
            self.playback_slider.setEnabled(False)
            self.timer.start()
        else:
            self.timer.stop()
            self.playback_play_pause_button.setText("Play")
            self.playback_iter_spin_box.setEnabled(True)
            self.playback_slider.setEnabled(True)

    def playback_slider_changed(self):
        self.current_iteration = self.playback_slider.value()
        self.playback_iter_spin_box.setValue(self.current_iteration)
        self.visualiser.set_iteration(self.current_iteration)
        self.visualiser.update()
    
    def play_next_iteration(self):
        self.current_iteration += 1
        if self.current_iteration > self.max_iteration:
            self.current_iteration = self.max_iteration
            self.timer.stop()
            self.playback_play_pause_button.setText("Play")
        else:
            self.set_playback_iter_and_slider()
            self.visualiser.set_iteration(self.current_iteration)
    
    def set_playback_iter_and_slider(self):
        self.playback_iter_spin_box.setValue(self.current_iteration)
        self.playback_slider.setValue(self.current_iteration)
        

app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()