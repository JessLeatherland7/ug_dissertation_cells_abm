from PySide6.QtCore import QRect, QSize, Qt, QTimer
from PySide6.QtGui import QAction
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import (QApplication, QProgressDialog, QFileDialog, QComboBox,
    QDoubleSpinBox, QFrame, QHBoxLayout, QLabel, QMainWindow, QPushButton, QScrollArea,
    QMessageBox, QSizePolicy, QSlider, QSpacerItem, QSpinBox, QVBoxLayout, QWidget)

from cell_type import *
from environment import *
from simulation import Simulation
from visualiser import Visualiser
from graphs import *

import yappi

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
        self.model_setup_widget.setGeometry(QRect(10, 10, 400, 320))
        self.model_setup_layout = QVBoxLayout(self.model_setup_widget)
        self.model_setup_layout.setContentsMargins(0, 0, 0, 0)
        self.model_setup_top_layout = QHBoxLayout()
        
        self.model_setup_title = QLabel("Model Setup:")
        self.model_setup_top_layout.addWidget(self.model_setup_title)

        self.horizontal_spacer_1 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
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
        self.model_setup_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.model_setup_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.model_setup_scroll_area.setWidgetResizable(True)
        
        self.scroll_area_widget_contents = QWidget()
        self.scroll_area_widget_contents.setFixedWidth(400)
        self.scroll_area_layout = QVBoxLayout()
        self.scroll_area_widget_contents.setLayout(self.scroll_area_layout)

        self.init_cell_setup_widget()
        self.init_env_setup_widget()
        self.init_sim_setup_widget()

        self.model_setup_scroll_area.setWidget(self.scroll_area_widget_contents)

        self.model_setup_layout.addWidget(self.model_setup_scroll_area)


    def init_cell_setup_widget(self):
        self.cell_types = self.get_all_subclasses(AbstractCellType)
        self.cell_type_names = []
        for cell_type in self.cell_types:
            self.cell_type_names.append(cell_type.__name__)

        self.cell_setup_widget = QWidget(self.scroll_area_widget_contents)
        self.cell_setup_widget.setMinimumHeight(80)
        self.cell_setup_layout = QVBoxLayout(self.cell_setup_widget)
        self.cell_setup_layout.setContentsMargins(0, 0, 0, 0)
        
        self.cell_setup_title = QLabel("Cells:")
        self.cell_setup_layout.addWidget(self.cell_setup_title)

        self.add_initial_cells_widget = QWidget(self.cell_setup_widget)
        self.add_initial_cells_widget.setMinimumHeight(28)
        self.add_initial_cells_layout = QVBoxLayout()
        self.add_initial_cells_layout.setContentsMargins(0, 0, 0, 0)
        self.add_initial_cells_widget.setLayout(self.add_initial_cells_layout)
        self.add_cell_type_layouts = []
        self.cell_type_combo_boxes = []
        self.seed_cells_spin_boxes = []

        self.add_cell_type_widget()
        
        self.cell_setup_layout.addWidget(self.add_initial_cells_widget)

        self.add_more_cell_types_widget = QWidget()
        self.add_more_cell_types_widget.setMinimumHeight(28)
        self.add_more_cell_types_layout = QHBoxLayout()
        self.add_more_cell_types_layout.setContentsMargins(0, 0, 0, 0)
        self.add_more_cell_types_widget.setLayout(self.add_more_cell_types_layout)
        self.add_cell_type_button = QPushButton("+ Cell type")
        self.add_cell_type_button.clicked.connect(self.add_cell_type_widget)
        self.add_more_cell_types_layout.addWidget(self.add_cell_type_button)

        self.horizontal_spacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.add_more_cell_types_layout.addItem(self.horizontal_spacer_3)

        self.cell_setup_layout.addWidget(self.add_more_cell_types_widget)

        self.scroll_area_layout.addWidget(self.cell_setup_widget)


    def init_env_setup_widget(self):
        self.env_layers = self.get_all_subclasses(AbstractEnvironmentLayer)
        self.env_layer_names = []
        for env_layer in self.env_layers:
            self.env_layer_names.append(env_layer.__name__)

        self.env_setup_widget = QWidget(self.scroll_area_widget_contents)
        self.env_setup_widget.setMinimumHeight(110)
        self.env_setup_layout = QVBoxLayout(self.env_setup_widget)
        self.env_setup_layout.setContentsMargins(0, 0, 0, 0)
        
        self.env_setup_title = QLabel("Environment:")
        self.env_setup_title.setStyleSheet("border-top-width: 1px; border-top-style: solid; border-radius: 0px;")
        self.env_setup_layout.addWidget(self.env_setup_title)

        self.env_set_width_layout = QHBoxLayout()
        
        self.env_width_label = QLabel("Width:")
        self.env_set_width_layout.addWidget(self.env_width_label)

        self.env_width_double_spin_box = QDoubleSpinBox(self.env_setup_widget)
        self.env_width_double_spin_box.setRange(25.0, 9999.99)
        self.env_width_double_spin_box.setSingleStep(5.00)
        self.env_width_double_spin_box.setMinimumWidth(130)
        self.env_set_width_layout.addWidget(self.env_width_double_spin_box)

        self.um_label = QLabel("μm")
        self.env_set_width_layout.addWidget(self.um_label)

        self.horizontal_spacer_4 = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.env_set_width_layout.addItem(self.horizontal_spacer_4)

        self.env_setup_layout.addLayout(self.env_set_width_layout)

        self.add_substances_widget = QWidget(self.cell_setup_widget)
        self.add_substances_widget.setMinimumHeight(28)
        self.add_substances_layout = QVBoxLayout()
        self.add_substances_layout.setContentsMargins(0, 0, 0, 0)
        self.add_substances_widget.setLayout(self.add_substances_layout)
        self.add_substance_layouts = []
        self.substance_combo_boxes = []
        self.substance_level_double_spin_boxes = []
        
        self.add_substance_widget()

        self.env_setup_layout.addWidget(self.add_substances_widget)

        self.add_more_substances_layout = QHBoxLayout()
        self.add_substance_button = QPushButton("+ Substance")
        self.add_substance_button.clicked.connect(self.add_substance_widget)
        self.add_more_substances_layout.addWidget(self.add_substance_button)

        self.horizontal_spacer_6 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.add_more_substances_layout.addItem(self.horizontal_spacer_6)

        self.env_setup_layout.addLayout(self.add_more_substances_layout)

        self.scroll_area_layout.addWidget(self.env_setup_widget)


    def init_sim_setup_widget(self):
        self.sim_setup_widget = QWidget(self.scroll_area_widget_contents)
        self.sim_setup_widget.setMinimumHeight(50)
        self.sim_setup_layout = QVBoxLayout(self.sim_setup_widget)
        self.sim_setup_layout.setContentsMargins(0, 0, 0, 0)
        
        self.sim_setup_title = QLabel("Simulation:")
        self.sim_setup_title.setStyleSheet("border-top-width: 1px; border-top-style: solid; border-radius: 0px;")
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

        self.horizontal_spacer_7 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.sim_iter_and_seed_layout.addItem(self.horizontal_spacer_7)

        self.sim_setup_layout.addLayout(self.sim_iter_and_seed_layout)

        self.scroll_area_layout.addWidget(self.sim_setup_widget)


    def init_graphs_panel(self):
        self.graphs_widget = QWidget(self.central_widget)
        self.graphs_widget.setGeometry(QRect(10, 340, 400, 300))
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

        self.horizontal_spacer_8 = QSpacerItem(20, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
        self.playback_fps_and_iter_layout.addItem(self.horizontal_spacer_8)

        self.playback_iter_label = QLabel("ITERATION:")
        self.playback_fps_and_iter_layout.addWidget(self.playback_iter_label)

        self.playback_iter_spin_box = QSpinBox(self.playback_widget)
        self.playback_iter_spin_box.setMinimumWidth(100)
        self.playback_iter_spin_box.setMinimum(0)
        self.playback_iter_spin_box.setSingleStep(1)
        self.playback_iter_spin_box.setEnabled(False)
        self.playback_iter_spin_box.valueChanged.connect(self.playback_iter_changed)
        self.playback_fps_and_iter_layout.addWidget(self.playback_iter_spin_box)

        self.horizontal_spacer_9 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.playback_fps_and_iter_layout.addItem(self.horizontal_spacer_9)

        self.playback_layout.addLayout(self.playback_fps_and_iter_layout)

        self.playback_play_layout = QHBoxLayout()
        
        self.playback_play_pause_button = QPushButton("Play")
        self.playback_play_pause_button.clicked.connect(self.play_pause)
        self.playback_play_pause_button.setEnabled(False)
        self.playback_play_layout.addWidget(self.playback_play_pause_button)
        self.playing = False

        self.playback_slider = QSlider(self.playback_widget)
        self.playback_slider.setEnabled(False)
        self.playback_slider.setOrientation(Qt.Horizontal)
        self.playback_slider.sliderReleased.connect(self.playback_slider_changed)
        self.playback_play_layout.addWidget(self.playback_slider)

        self.playback_layout.addLayout(self.playback_play_layout)

        self.visualiser_widget = QWidget(self.central_widget)
        self.visualiser_widget.setGeometry(QRect(430, 80, 560, 560))
        self.visualiser_layout = QVBoxLayout()
        self.visualiser_widget.setLayout(self.visualiser_layout)
        self.visualiser = QOpenGLWidget(self.visualiser_widget)
        self.visualiser_layout.addWidget(self.visualiser)

        self.timer = QTimer(self)
        self.timer.setInterval(1000/self.playback_fps_spin_box.value())   # period, in milliseconds
        self.timer.timeout.connect(self.visualiser.update)
        self.timer.timeout.connect(self.play_next_iteration)

        self.visualiser.deleteLater()
        self.visualiser = None

        self.current_iteration = 0
        self.max_iteration = 0

    def add_cell_type_widget(self, e=None):
        widget = QWidget()
        widget.setMinimumHeight(28)
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(layout)
        
        cell_type_combo_box = QComboBox(self.cell_setup_widget)
        cell_type_combo_box.addItems(self.cell_type_names)
        layout.addWidget(cell_type_combo_box)

        cell_num_label = QLabel("Num:")
        layout.addWidget(cell_num_label)

        seed_cells_spin_box = QSpinBox(self.cell_setup_widget)
        seed_cells_spin_box.setFixedWidth(75)
        seed_cells_spin_box.setRange(1, 100)
        seed_cells_spin_box.setSingleStep(1)
        layout.addWidget(seed_cells_spin_box)

        horizontal_spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        layout.addItem(horizontal_spacer)

        self.add_cell_type_layouts.append(layout)
        self.cell_type_combo_boxes.append(cell_type_combo_box)
        self.seed_cells_spin_boxes.append(seed_cells_spin_box)
        self.add_initial_cells_layout.addWidget(widget)
        self.add_initial_cells_widget.setMinimumHeight(28 * len(self.add_cell_type_layouts))
        self.cell_setup_widget.setMinimumHeight(self.add_initial_cells_widget.height() + 52)


    def substance_changed(self, new_substance, substance_combo_box):
        spin_box_index = None
        for i in range(len(self.substance_combo_boxes)):
            if substance_combo_box == self.substance_combo_boxes[i]:
                spin_box_index = i
                break
        
        if spin_box_index != None:
            substance_level_double_spin_box = self.substance_level_double_spin_boxes[i]
            if new_substance == "":
                substance_level_double_spin_box.setValue(0.0)
                substance_level_double_spin_box.setEnabled(False)
            else:
                substance_level_double_spin_box.setEnabled(True)

    def add_substance_widget(self, e=None):
        widget = QWidget()
        widget.setMinimumHeight(28)
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(layout)
        
        substance_combo_box = QComboBox(self.env_setup_widget)
        substance_combo_box.addItem("")
        substance_combo_box.addItems(self.env_layer_names)
        substance_combo_box.currentTextChanged.connect(lambda e: self.substance_changed(e, substance_combo_box))
        layout.addWidget(substance_combo_box)

        substance_level_double_spin_box = QDoubleSpinBox(self.env_setup_widget)
        substance_level_double_spin_box.setRange(0.0, 999.99)
        substance_level_double_spin_box.setSingleStep(0.1)
        substance_level_double_spin_box.setMinimumWidth(110)
        substance_level_double_spin_box.setEnabled(False)
        layout.addWidget(substance_level_double_spin_box)

        units_label = QLabel("units")
        layout.addWidget(units_label)

        horizontal_spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        layout.addItem(horizontal_spacer)

        self.add_substance_layouts.append(layout)
        self.substance_combo_boxes.append(substance_combo_box)
        self.substance_level_double_spin_boxes.append(substance_level_double_spin_box)
        self.add_substances_layout.addWidget(widget)
        self.add_substances_widget.setMinimumHeight(28 * len(self.add_substance_layouts))
        self.env_setup_widget.setMinimumHeight(self.add_substances_widget.height() + 82)

    def export_data(self, e):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        save_file_name, _ = QFileDialog.getSaveFileName(self, 
            "Save File", "", "All Files(*)", options = options)
        if save_file_name:
            if save_file_name[-4:] != ".csv":
                save_file_name += ".csv"
            with open("sim_data.csv", 'r') as data_file:
                with open(save_file_name, 'w') as save_file:
                    for line in data_file:
                        save_file.write(line)
            data_file.close()
            save_file.close()

    def export_video(self, e):
        if self.visualiser != None:
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            save_file_name, _ = QFileDialog.getSaveFileName(self, 
                "Save File", "", "All Files(*)", options = options)
            if save_file_name:
                if save_file_name[-4:] != ".mp4":
                    save_file_name += ".mp4"
                self.visualiser.save_video(save_file_name, self.max_iteration, self.playback_fps_spin_box.value())
        else:
            QMessageBox.critical(self, "Alert", "No visualisation to export!", buttons=QMessageBox.Ok)

    def reset_model(self, e):
        self.timer.stop()
        
        if self.visualiser != None:
            self.visualiser.deleteLater()
            self.visualiser = None
        
        if len(self.add_cell_type_layouts) > 1:
            for i in reversed(range(1, len(self.add_cell_type_layouts))):
                layout: QHBoxLayout = self.add_cell_type_layouts[i]
                layout_item = self.add_initial_cells_layout.itemAt(i)
                
                self.remove_layout_widgets(layout)
                self.add_initial_cells_layout.removeItem(layout_item)
            
            self.add_cell_type_layouts = [self.add_cell_type_layouts[0]]
            self.cell_type_combo_boxes = [self.cell_type_combo_boxes[0]]
            self.seed_cells_spin_boxes = [self.seed_cells_spin_boxes[0]]
            self.add_initial_cells_widget.setMinimumHeight(28)
            self.cell_setup_widget.setMinimumHeight(80)

        first_cell_type_combo_box: QComboBox = self.cell_type_combo_boxes[0]
        first_seed_cells_spin_box: QSpinBox = self.seed_cells_spin_boxes[0]
        first_cell_type_combo_box.setCurrentText(self.cell_type_names[0])
        first_seed_cells_spin_box.setValue(1)
        
        if len(self.add_substance_layouts) > 1:
            for i in reversed(range(1, len(self.add_substance_layouts))):
                layout: QHBoxLayout = self.add_substance_layouts[i]
                layout_item = self.add_substances_layout.itemAt(i)
                
                self.remove_layout_widgets(layout)
                self.add_substances_layout.removeItem(layout_item)
            
            self.add_substance_layouts = [self.add_substance_layouts[0]]
            self.substance_combo_boxes = [self.substance_combo_boxes[0]]
            self.substance_level_double_spin_boxes = [self.substance_level_double_spin_boxes[0]]
            self.add_substances_widget.setMinimumHeight(28)
            self.env_setup_widget.setMinimumHeight(110)

        first_substance_combo_box: QComboBox = self.substance_combo_boxes[0]
        first_substance_level_double_spin_box: QSpinBox = self.substance_level_double_spin_boxes[0]
        first_substance_combo_box.setCurrentText("")
        first_substance_level_double_spin_box.setValue(0.0)
        first_substance_level_double_spin_box.setEnabled(False)

        self.env_width_double_spin_box.setValue(10.0)
        
        self.sim_iter_spin_box.setValue(1)
        self.sim_rand_seed_spin_box.setValue(0)

        self.graph_canvas.clear()
        self.graph_canvas.draw()

        self.playback_fps_spin_box.setValue(1)
        self.reset_playback_iteration()
    
    def remove_layout_widgets(self, layout):
        for i in reversed(range(layout.count())):
            widget = layout.itemAt(i).widget()
            if widget is not None:
                layout.removeWidget(widget)
                widget.setParent(None)

    def reset_playback_iteration(self):
        self.current_iteration = 0
        self.playback_iter_spin_box.setValue(0)
        self.playback_iter_spin_box.setEnabled(False)
        self.playback_play_pause_button.setText("Play")
        self.playback_play_pause_button.setEnabled(False)
        self.playback_slider.setSliderPosition(0)
        self.playback_slider.setEnabled(False)

    def run_model(self, e):
        # ====== Uncomment yappi lines for profiling ======
        #yappi.set_clock_type("wall")
        #yappi.start()

        self.timer.stop()

        self.reset_playback_iteration()

        input_cell_types = []
        cell_type_combo_box: QComboBox
        for cell_type in self.cell_types:
            for cell_type_combo_box in self.cell_type_combo_boxes:
                if cell_type.__name__ == cell_type_combo_box.currentText():
                    input_cell_types.append(cell_type)
        
        input_cell_nums = []
        seed_cells_spin_box : QSpinBox
        for seed_cells_spin_box in self.seed_cells_spin_boxes:
            input_cell_nums.append(seed_cells_spin_box.value())
        
        self.env_size = self.env_width_double_spin_box.value()
        
        input_env_layers = []
        for env_layer in self.env_layers:
            for i in range(len(self.substance_combo_boxes)):
                if env_layer.__name__ == self.substance_combo_boxes[i].currentText():
                    input_env_layers.append(env_layer(self.env_size, self.substance_level_double_spin_boxes[i].value()))
                    break

        self.max_iteration = self.sim_iter_spin_box.value()
        random_seed = self.sim_rand_seed_spin_box.value()
        
        progress_dialog = QProgressDialog("Running simulation...", "Cancel", 0, self.max_iteration, self)
        progress_dialog.setWindowModality(Qt.WindowModal)
        progress_dialog.setWindowTitle("Run Model")
        progress_dialog.setMinimumDuration(0)

        self.sim = Simulation("sim_data.csv", input_cell_types, input_cell_nums, self.env_size, input_env_layers, self.max_iteration, random_seed)

        cancelled = False
        for i in range(1, self.max_iteration+1):
            if progress_dialog.wasCanceled():
                cancelled = True
                break

            self.sim.run_iteration()
            progress_dialog.setValue(i)

        if not cancelled:
            self.sim.write_simulation()

            self.graph_canvas.plot_data(input_cell_types)
            self.graph_canvas.draw()

            if self.visualiser != None:
                self.visualiser.deleteLater()
                self.visualiser = None

            width, height = self.visualiser_widget.width(), self.visualiser_widget.height()
            self.visualiser = Visualiser(self.visualiser_widget, width, height, "sim_data.csv", self.env_size)
            self.visualiser_layout.addWidget(self.visualiser)
            
            self.playback_iter_spin_box.setRange(0, self.max_iteration)
            self.playback_iter_spin_box.setEnabled(True)
            self.playback_play_pause_button.setEnabled(True)
            self.playback_slider.setRange(0, self.max_iteration)
            self.playback_slider.setEnabled(True)

        else:
            self.sim = None
            if self.visualiser != None:
                self.visualiser.deleteLater()
                self.visualiser = None
            self.graph_canvas.clear()
            self.graph_canvas.draw()

        # ====== Uncomment yappi lines for profiling ======
        #yappi.stop()
        #yappi.get_func_stats().print_all()
        #yappi.get_thread_stats().print_all()
        #yappi.clear_stats()
        

    def change_fps(self, new_fps):
        if self.timer != None:
            self.timer.setInterval(1000/new_fps)

    def playback_iter_changed(self):
        if not self.playing:
            self.current_iteration = self.playback_iter_spin_box.value()
            self.playback_slider.setValue(self.current_iteration)
            self.update_visualiser()

    def play_pause(self, e):
        if not self.playing:
            if self.current_iteration == self.max_iteration:
                self.current_iteration = 0
                self.set_playback_iter_and_slider()
            self.playback_play_pause_button.setText("Pause")
            self.playback_iter_spin_box.setEnabled(False)
            self.playback_slider.setEnabled(False)
            self.timer.start()
            self.playing = True
        else:
            self.timer.stop()
            self.playback_play_pause_button.setText("Play")
            self.playback_iter_spin_box.setEnabled(True)
            self.playback_slider.setEnabled(True)
            self.playing = False

    def playback_slider_changed(self):
        if not self.playing:
            self.current_iteration = self.playback_slider.value()
            self.playback_iter_spin_box.setValue(self.current_iteration)
            self.update_visualiser()
    
    def play_next_iteration(self):
        self.current_iteration += 1
        if self.current_iteration > self.max_iteration:
            self.current_iteration = self.max_iteration
            self.timer.stop()
            self.playback_play_pause_button.setText("Play")
            self.playback_iter_spin_box.setEnabled(True)
            self.playback_slider.setEnabled(True)
            self.playing = False
        else:
            self.set_playback_iter_and_slider()
            self.update_visualiser()
    
    def set_playback_iter_and_slider(self):
        self.playback_iter_spin_box.setValue(self.current_iteration)
        self.playback_slider.setValue(self.current_iteration)
    
    def update_visualiser(self):
        if self.visualiser != None:
            self.visualiser.set_iteration(self.current_iteration)
            self.visualiser.update()

    def get_all_subclasses(self, parent_class):
        subclasses = []
        classes_to_check = [parent_class]
        while classes_to_check:
            parent = classes_to_check.pop()
            for child in parent.__subclasses__():
                if child not in subclasses:
                    subclasses.append(child)
                    classes_to_check.append(child)
        return subclasses


app = QApplication([])

window = MainWindow()
window.show()

app.exec()