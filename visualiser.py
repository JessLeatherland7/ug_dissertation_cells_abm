import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *

import math

from data import DataReader

class Visualiser:
    
    cell_colours = {"GenericCell": (0.5, 0.2, 0.2), "Quiescent": (0.5, 0.5, 0.2)}
    
    vertices=( 
        (50, -50, -412),
        (50, 50, -412),
        (-50, 50, -412),
        (-50, -50, -412),
        (50, -50, -310),
        (50, 50, -310),
        (-50, -50, -310),
        (-50, 50, -310)
    )
    ##define 12 edges for the body
    edges = (
        (0,1),
        (0,3),
        (0,4),
        (2,1),
        (2,3),
        (2,7),
        (6,3),
        (6,4),
        (6,7),
        (5,1),
        (5,4),
        (5,7)
    )

    def __init__(self, input_file, max_iteration):
        self.max_iteration = max_iteration
        self.data_reader = DataReader(input_file)
        self.data_reader.read_data()

        
    def get_vis_data(self, iteration):
        cells = self.data_reader.get_iteration(iteration)
        
        positions = []
        radii = []
        colours = []
        
        for cell in cells:
            positions.append(cell["pos"])
            radii.append(cell["radius"])
            if cell["current_phase"] == "G0":
                colours.append(self.cell_colours["Quiescent"])
            else:
                colours.append(self.cell_colours[cell["cell_type"]])
        
        return positions, radii, colours
    
    def draw_cube(self):
        glBegin(GL_LINES)
        glColor4f(1, 1, 1, 1)
        for edge in self.edges:
            for index in edge:
                glVertex3fv(self.vertices[index])
        glEnd()


    def display_iteration(self, iteration):
        
        positions, radii, colours = self.get_vis_data(iteration)
        
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT) #Clear the screen
        
        

        for i in range(len(radii)):
            pos = positions[i]
            colour = colours[i]
            radius = radii[i]
            glPushMatrix()
            sphere = gluNewQuadric() #Create new sphere
            glTranslatef(pos[0], pos[1], -362-pos[2]) #Move to the place
            glColor4f(colour[0], colour[1], colour[2], 1) #Put color
            gluSphere(sphere, radius, 32, 16) #Draw sphere
            glPopMatrix()

        self.draw_cube()

        pygame.display.flip() #Update the screen

    def visualise(self):
        pygame.init()
        display = (900, 900)
        screen = pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)

        glEnable(GL_LIGHTING)

        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, [0.3, 0.3, 0.3, 1.0])

        # Enable light number 0
        glEnable(GL_LIGHT0)

        # Set position and intensity of light
        glLightfv(GL_LIGHT0, GL_POSITION, [50.0, 50.0, -1.0, 1.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.7, 0.7, 0.7, 1.0])

        # Setup the material
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)

        glShadeModel(GL_SMOOTH)

        glMatrixMode(GL_PROJECTION)
        gluPerspective(20, (display[0]/display[1]), 310.0, 417.0)

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

            # multiply the current matrix by the get the new view matrix and store the final vie matrix 
            #glMultMatrixf(viewMatrix)
            #viewMatrix = glGetFloatv(GL_MODELVIEW_MATRIX)

            # apply view matrix
            #glPopMatrix()
            #glMultMatrixf(viewMatrix)
                        
            # =============================
            
            pygame.time.wait(10)

        pygame.quit()
