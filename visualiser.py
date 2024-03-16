import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import math

from data import DataReader

class Visualiser:
    
    cell_colours = {"GenericCell": {"Normal": (0.6, 0.2, 0.2), "Quiescent": (0.8, 0.5, 0.5)}}
    
    # define 12 edges for the environment border
    env_edges = (
        (0,1), (1,2), (2,3), (3,0),
        (4,5), (5,6), (6,7), (7,4),
        (0,4), (1,5), (2,6), (3,7)
    )

    def __init__(self, input_file, max_iteration, env_size):
        self.max_iteration = max_iteration
        self.env_size = env_size
        
        self.env_origin, self.z_near, self.z_far, self.env_vertices = self.get_env_coords()

        self.data_reader = DataReader(input_file)
        self.data_reader.read_data()

    
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


    def get_vis_data(self, iteration):
        cells = self.data_reader.get_iteration(iteration)
        
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
    

    def draw_environment_border(self):
        glDisable(GL_LIGHTING)

        glBegin(GL_LINES)
        glColor4f(0.4, 0.4, 0.4, 1)
        for edge in self.env_edges:
            for vertex in edge:
                glVertex3fv(self.env_vertices[vertex])
        glEnd()


    def display_iteration(self, iteration):
        
        positions, radii, colours = self.get_vis_data(iteration)

        glEnable(GL_LIGHTING)

        glClearColor(1, 1, 1, 1)
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT) #Clear the screen

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
        
        self.draw_environment_border()

        pygame.display.flip() #Update the screen

    def visualise(self):
        pygame.init()
        display = (900, 900)
        screen = pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

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

        glMatrixMode(GL_PROJECTION)
        gluPerspective(20, (display[0]/display[1]), -self.z_near, -self.z_far * 1.05)

        glMatrixMode(GL_MODELVIEW)
        gluLookAt(0, 0, 0, 0, 0, -100, 0, 0, 0)
        viewMatrix = glGetFloatv(GL_MODELVIEW_MATRIX)
        glLoadIdentity()

        iteration = 0
        run = True
        
        self.display_iteration(iteration)

        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                        run = False 
                    elif event.key == pygame.K_LEFT and iteration > 0:
                        iteration -= 1
                        print(iteration)
                        self.display_iteration(iteration)
                    elif event.key == pygame.K_RIGHT and iteration < self.max_iteration:
                        iteration += 1
                        print(iteration)
                        self.display_iteration(iteration)

            # ====== Camera movement ======
            
            #keypress = pygame.key.get_pressed()

            # init model view matrix
            #glLoadIdentity()

            # init the view matrix
            #glPushMatrix()
            #glLoadIdentity()

            # apply the movment 
            #if keypress[pygame.K_w]:
            #    glTranslatef(0,0,0.1)
            #if keypress[pygame.K_s]:
            #    glTranslatef(0,0,-0.1)
            #if keypress[pygame.K_d]:
            #    glTranslatef(-0.1,0,0)
            #if keypress[pygame.K_a]:
            #    glTranslatef(0.1,0,0)

            # multiply the current matrix by the get the new view matrix and store the final view matrix 
            #glMultMatrixf(viewMatrix)
            #viewMatrix = glGetFloatv(GL_MODELVIEW_MATRIX)

            # apply view matrix
            #glPopMatrix()
            #glMultMatrixf(viewMatrix)
                        
            # =============================
            
            pygame.time.wait(10)

        pygame.quit()
