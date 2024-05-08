# -*- coding: utf-8 -*-

import cv2
import glfw
import numpy as np
import os
import shutil

from PySide6.QtGui import QOpenGLContext
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import QVBoxLayout

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from data import DataReader
import utils

class Visualiser(QOpenGLWidget):
    
    # Add colours for normal and quiescent states of each implemented cell type class
    cell_colours = {"GenericCell": {"Normal": (0.6, 0.2, 0.2), "Quiescent": (0.7, 0.5, 0.5)},
                    "CancerousCell": {"Normal": (0.2, 0.4, 0.7), "Quiescent": (0.4, 0.6, 0.8)}}
    
    # Define 12 edges for the environment borders
    env_edges = (
        (0,1), (1,2), (2,3), (3,0),
        (4,5), (5,6), (6,7), (7,4),
        (0,4), (1,5), (2,6), (3,7)
    )

    def __init__(self, parent, w, h, input_file, env_size):
        """Constructs the necessary attributes for the Visualiser widget.
        
        Parameters
        ----------
        parent : QWidget
            the parent widget of the visualiser
        w : float
            the width of the visualiser widget
        h : float
            the height of the visualiser widget
        input_file : string
            the name of the data file for the simulation to be visualised
        env_size : float
            the width of the environment to be visualised

        Other defined attributes
        ------------------------
        data_reader : DataReader
            the DataReader object for reading simulation data to visualise
        env_origin : list
            the x, y and z coordinates of the environment origin
        z_near : float
            the z coordinate of the near side of the environment in the world space
        z_far : float
            the z coordinate of the far side of the environment in the world space
        env_vertices : tuple
            a tuple of 8 xyz coordinate tuples of the environment corners
        iteration : int
            the current iteration that should be displayed in the visualiser
        """
        super(Visualiser, self).__init__(parent)

        layout = QVBoxLayout()
        self.setLayout(layout)
    
        self.w = w
        self.h = h

        self.data_reader = DataReader(input_file)
        self.data_reader.read_data()

        self.env_size = env_size
        self.env_origin, self.z_near, self.z_far, self.env_vertices = self.get_env_coords()

        self.iteration = 0

    def get_env_coords(self):
        """Gets coordinates relating to the environment position in the world space.
        
        Returns
        -------
        env_origin : list
            the x, y and z coordinates of the environment origin
        z_near : float
            the z coordinate of the near side of the environment in the world space
        z_far : float
            the z coordinate of the far side of the environment in the world space
        env_vertices : tuple
            a tuple of 8 xyz coordinate tuples of the environment corners
        """
        
        half_env_size = self.env_size / 2.0
        
        # Gets z coordinates to place environment in world space needed 
        # for it to be in full view of the camera
        z_near = -(half_env_size * 1.05) / utils.TAN_10_DEGREES
        z_far = z_near - self.env_size
        
        env_origin = [-half_env_size, -half_env_size, z_near]
        env_vertices = (
            (-half_env_size, -half_env_size, z_near),
            (half_env_size, -half_env_size, z_near),
            (half_env_size, half_env_size, z_near),
            (-half_env_size, half_env_size, z_near),
            (-half_env_size, -half_env_size, z_far),
            (half_env_size, -half_env_size, z_far),
            (half_env_size, half_env_size, z_far),
            (-half_env_size, half_env_size, z_far),
        )

        return env_origin, z_near, z_far, env_vertices

    def get_vis_data(self):
        """Gets the cell data needed to visualise an iteration of the simulation.
        
        Returns
        -------
        positions : list
            a list of the cell agent positions (3D numpy arrays)
        radii : list
            a list of the cell agent radii (floats)
        colours : list
            a list of the colours to apply to each cell agent
        """
        cells = self.data_reader.get_iteration(self.iteration)
        
        positions = []
        radii = []
        colours = []
        
        for cell in cells:
            if not cell["is_dead"]:
                positions.append(cell["pos"])
                radii.append(cell["radius"])
                if cell["current_phase"] == "G0":
                    colours.append(self.cell_colours[cell["cell_type"]]["Quiescent"])
                else:
                    colours.append(self.cell_colours[cell["cell_type"]]["Normal"])
        
        return positions, radii, colours

    def set_iteration(self, iteration):
        """Sets the current iteration that should be displayed.
        
        Parameters
        ----------
        iteration : int
            the current iteration of the simulation to be visualised
        """
        self.iteration = iteration


    def initializeGL(self):
        """Initialises the Visualiser widget, setting up OpenGL functions.
        
        Overrides the QOpenGLWidget initializeGL function. It is called once 
        on initialisation of the widget, sets necessary options and sets up
        the lighting and materials for the scene.
        """
        f = QOpenGLContext.currentContext().functions()
        f.glEnable(GL_DEPTH_TEST)
        f.glDepthFunc(GL_LEQUAL)

        f.glEnable(GL_LIGHTING)

        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, [0.8, 0.8, 0.8, 1.0])

        # Enable light number 0
        f.glEnable(GL_LIGHT0)

        # Set position and intensity of light
        light_z_pos = self.z_near + 2 * self.env_size
        glLightfv(GL_LIGHT0, GL_POSITION, [self.env_size, self.env_size, light_z_pos, 1.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.7, 0.7, 0.7, 1.0])

        # Set up the cell material
        f.glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)
        glShadeModel(GL_SMOOTH)

    def resizeGL(self, w, h):
        """Repositions the camera view when the widget is resized.
        
        Overrides the QOpenGLWidget resizeGL function. It is called on 
        initialisation of the widget and whenever the widget is resized, 
        and sets the camera view to be able to see the environment.
        """
        self.w = w
        self.h = h

        glMatrixMode(GL_PROJECTION)
        gluPerspective(20, (w/h), -self.z_near * 0.95, -self.z_far * 1.05)

        glMatrixMode(GL_MODELVIEW)
        gluLookAt(0, 0, 0, 0, 0, -100, 0, 0, 0)
        viewMatrix = glGetFloatv(GL_MODELVIEW_MATRIX)
        glLoadIdentity()

    def paintGL(self):
        """Draws the current simulation iteration.
        
        Overrides the QOpenGLWidget paintGL function. It is called on 
        initialisation of the widget and whenever the widget is updated, 
        and draws the cells in the current simulation iteration and 
        environment.
        """
        f = QOpenGLContext.currentContext().functions()
        
        # Clear the screen
        f.glClearColor(1, 1, 1, 1)
        f.glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

        # Draw cells and environment
        f.glEnable(GL_LIGHTING)
        self.draw_cells()
        f.glDisable(GL_LIGHTING)
        self.draw_environment_border()

    def draw_cells(self):
        """Draws the cells in the current simulation iteration.
        
        Gets the positions, radii, and colours of the cell agents in
        the current iteration and draws spheres with these attributes.
        """
        positions, radii, colours = self.get_vis_data()
        
        for i in range(len(radii)):
            pos = positions[i]
            colour = colours[i]
            radius = radii[i]
            
            glPushMatrix()
            
            #Create new sphere
            sphere = gluNewQuadric()
            
            # Move to the cell position
            glTranslatef(self.env_origin[0] + pos[0],
                         self.env_origin[1] + pos[1], 
                         self.env_origin[2] - pos[2])
            
            # Put cell color
            glColor4f(colour[0], colour[1], colour[2], 1)
            
            # Draw sphere with cell's radius
            gluSphere(sphere, radius, 32, 16)
            
            glPopMatrix()

    def draw_environment_border(self):
        """Draws the environment.
        
        Draws lines between each of the environment vertices to form the
        environment borders.
        """
        glBegin(GL_LINES)
        glColor4f(0.4, 0.4, 0.4, 1)
        for edge in self.env_edges:
            for vertex in edge:
                glVertex3fv(self.env_vertices[vertex])
        glEnd()
    
    def save_video(self, file_path, max_iteration, frame_rate):
        """Writes a video of the simulation visualisation to the given file location.
        
        Parameters
        ----------
        file_path : string
            name of the file location to save the video in
        max_iteration : int
            the last iteration of the simulation
        frame_rate : int
            the frame rate to save the video with
        """
        # Save current iteration being displayed so this can be returned to
        current_iteration = self.iteration

        # Initialise glfw
        if not glfw.init():
            return
    
        glfw.window_hint(glfw.VISIBLE, False)
        
        # Create a windowed mode window and its OpenGL context
        window = glfw.create_window(self.w, self.h, "hidden window", None, None)
        if not window:
            glfw.terminate()
            return
        
        # Make the window's context current
        glfw.make_context_current(window)

        # Set up visualisation OpenGL options
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)

        glEnable(GL_LIGHTING)
        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, [0.8, 0.8, 0.8, 1.0])

        # Enable light number 0
        glEnable(GL_LIGHT0)

        # Set position and intensity of light
        light_z_pos = self.z_near + 2 * self.env_size
        glLightfv(GL_LIGHT0, GL_POSITION, [self.env_size, self.env_size, light_z_pos, 1.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.7, 0.7, 0.7, 1.0])

        # Set up the cell material
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)
        glShadeModel(GL_SMOOTH)

        # Position the camera to look at the environment
        glMatrixMode(GL_PROJECTION)
        gluPerspective(20, (self.w/self.h), -self.z_near * 0.95, -self.z_far * 1.05)

        glMatrixMode(GL_MODELVIEW)
        gluLookAt(0, 0, 0, 0, 0, -100, 0, 0, 0)
        viewMatrix = glGetFloatv(GL_MODELVIEW_MATRIX)
        glLoadIdentity()

        # Create temporary folder to store video frames
        image_folder = os.getcwd() + "\\" + "images"
        os.mkdir(image_folder)
        
        # Save frames of each iteration
        for i in range(max_iteration + 1):
            self.iteration = i
            
            # Clear the screen
            glClearColor(1, 1, 1, 1)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            # Draw cells and environment
            glEnable(GL_LIGHTING)
            self.draw_cells()
            glDisable(GL_LIGHTING)
            self.draw_environment_border()

            # Read pixels and save frame
            image_buffer = glReadPixels(0, 0, self.w, self.h, OpenGL.GL.GL_BGR, 
                                        OpenGL.GL.GL_UNSIGNED_BYTE)
            image = np.frombuffer(image_buffer, dtype=np.uint8).reshape(self.w, self.h, 3)
            image = np.flip(image, 0)
            num_preceding_zeros = len(str(max_iteration)) - len(str(self.iteration))
            file_name = "images" + "\\" + "0" * num_preceding_zeros + str(self.iteration) + ".png"
            cv2.imwrite(file_name, image)

        glfw.destroy_window(window)
        glfw.terminate()

        
        # Get frames and write video to file location
        images = [img for img in os.listdir(image_folder)]
        frame = cv2.imread(os.path.join(image_folder, images[0]))
        height, width, layers = frame.shape

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video = cv2.VideoWriter(file_path, fourcc, frame_rate, (width, height))

        for image in images:
            video.write(cv2.imread(os.path.join(image_folder, image)))

        # Release resources
        cv2.destroyAllWindows()
        video.release()

        # Delete temporary frames folder
        shutil.rmtree("images")

        # Return to iteration that was originally being displayed
        self.iteration = current_iteration