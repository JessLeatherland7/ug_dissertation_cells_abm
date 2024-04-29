from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtGui import QOpenGLContext
from PySide6.QtWidgets import QVBoxLayout

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import os
import shutil
import cv2
import glfw
import numpy as np

from data import DataReader

class Visualiser(QOpenGLWidget):
    
    cell_colours = {"GenericCell": {"Normal": (0.6, 0.2, 0.2), "Quiescent": (0.7, 0.5, 0.5)},
                    "CancerousCell": {"Normal": (0.2, 0.4, 0.7), "Quiescent": (0.4, 0.6, 0.8)}}
    
    # define 12 edges for the environment border
    env_edges = (
        (0,1), (1,2), (2,3), (3,0),
        (4,5), (5,6), (6,7), (7,4),
        (0,4), (1,5), (2,6), (3,7)
    )

    def __init__(self, parent, w, h, input_file, env_size):
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
        tan_10_degrees = 0.176327
        half_env_size = self.env_size / 2.0
        
        z_near = -(half_env_size * 1.05) / tan_10_degrees
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
        self.iteration = iteration


    def initializeGL(self):
        f = QOpenGLContext.currentContext().functions()
        f.glEnable(GL_DEPTH_TEST)
        f.glDepthFunc(GL_LEQUAL)

        f.glEnable(GL_LIGHTING)

        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, [0.8, 0.8, 0.8, 1.0])

        # Enable light number 0
        f.glEnable(GL_LIGHT0)

        # Set position and intensity of light
        glLightfv(GL_LIGHT0, GL_POSITION, [self.env_size, self.env_size, self.z_near + 2 * self.env_size, 1.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.7, 0.7, 0.7, 1.0])

        # Setup the cell material
        f.glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)
        glShadeModel(GL_SMOOTH)
        

    def resizeGL(self, w, h):
        self.w = w
        self.h = h

        glMatrixMode(GL_PROJECTION)
        gluPerspective(20, (w/h), -self.z_near * 0.95, -self.z_far * 1.05)

        glMatrixMode(GL_MODELVIEW)
        gluLookAt(0, 0, 0, 0, 0, -100, 0, 0, 0)
        viewMatrix = glGetFloatv(GL_MODELVIEW_MATRIX)
        glLoadIdentity()


    def paintGL(self):
        f = QOpenGLContext.currentContext().functions()
        f.glClearColor(1, 1, 1, 1)
        f.glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT) #Clear the screen

        f.glEnable(GL_LIGHTING)

        positions, radii, colours = self.get_vis_data()
        
        for i in range(len(radii)):
            pos = positions[i]
            colour = colours[i]
            radius = radii[i]
            
            glPushMatrix()
            
            sphere = gluNewQuadric() #Create new sphere
            glTranslatef(self.env_origin[0] + pos[0], self.env_origin[1] + pos[1], self.env_origin[2] - pos[2]) # Move to the cell pos
            glColor4f(colour[0], colour[1], colour[2], 1) # Put cell color
            gluSphere(sphere, radius, 32, 16) # Draw sphere with cell's radius
            
            glPopMatrix()
        
        # Draw environment border
        f.glDisable(GL_LIGHTING)

        glBegin(GL_LINES)
        glColor4f(0.4, 0.4, 0.4, 1)
        for edge in self.env_edges:
            for vertex in edge:
                glVertex3fv(self.env_vertices[vertex])
        glEnd()
    
    def save_video(self, file_path, max_iteration, frame_rate):
        current_iteration = self.iteration

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
        
        glMatrixMode(GL_PROJECTION)
        gluPerspective(20, (self.w/self.h), -self.z_near * 0.95, -self.z_far * 1.05)

        glMatrixMode(GL_MODELVIEW)
        gluLookAt(0, 0, 0, 0, 0, -100, 0, 0, 0)
        viewMatrix = glGetFloatv(GL_MODELVIEW_MATRIX)
        glLoadIdentity()

        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)

        glEnable(GL_LIGHTING)

        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, [0.8, 0.8, 0.8, 1.0])

        # Enable light number 0
        glEnable(GL_LIGHT0)

        # Set position and intensity of light
        glLightfv(GL_LIGHT0, GL_POSITION, [self.env_size, self.env_size, self.z_near + 2 * self.env_size, 1.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.7, 0.7, 0.7, 1.0])

        # Setup the cell material
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)
        glShadeModel(GL_SMOOTH)

        image_folder = os.getcwd() + "\\" + "images"
        os.mkdir(image_folder)
        
        for i in range(max_iteration + 1):
            self.iteration = i

            glClearColor(1, 1, 1, 1)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glEnable(GL_LIGHTING)

            positions, radii, colours = self.get_vis_data()
            
            for i in range(len(radii)):
                pos = positions[i]
                colour = colours[i]
                radius = radii[i]
                
                glPushMatrix()
                
                sphere = gluNewQuadric() #Create new sphere
                glTranslatef(self.env_origin[0] + pos[0], self.env_origin[1] + pos[1], self.env_origin[2] - pos[2]) # Move to the cell pos
                glColor4f(colour[0], colour[1], colour[2], 1) # Put cell color
                gluSphere(sphere, radius, 32, 16) # Draw sphere with cell's radius
                
                glPopMatrix()
            
            # Draw environment border
            glDisable(GL_LIGHTING)

            glBegin(GL_LINES)
            glColor4f(0.4, 0.4, 0.4, 1)
            for edge in self.env_edges:
                for vertex in edge:
                    glVertex3fv(self.env_vertices[vertex])
            glEnd()

            image_buffer = glReadPixels(0, 0, self.w, self.h, OpenGL.GL.GL_BGR, OpenGL.GL.GL_UNSIGNED_BYTE)
            image = np.frombuffer(image_buffer, dtype=np.uint8).reshape(self.w, self.h, 3)
            image = np.flip(image, 0)
            file_name = "images" + "\\" + "0" * (len(str(max_iteration)) - len(str(self.iteration))) + str(self.iteration) + ".png"
            cv2.imwrite(file_name, image)

        glfw.destroy_window(window)
        glfw.terminate()

        images = [img for img in os.listdir(image_folder)]
        frame = cv2.imread(os.path.join(image_folder, images[0]))
        height, width, layers = frame.shape

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video = cv2.VideoWriter(file_path, fourcc, frame_rate, (width, height))

        for image in images:
            video.write(cv2.imread(os.path.join(image_folder, image)))

        cv2.destroyAllWindows()
        video.release()

        shutil.rmtree("images")


        self.iteration = current_iteration