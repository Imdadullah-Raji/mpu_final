import serial
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math

# Serial configuration
SERIAL_PORT = '/dev/ttyACM0'
BAUD_RATE = 115200
TIMEOUT = 0.1

# Initialize serial connection
ser = serial.Serial(port=SERIAL_PORT, baudrate=BAUD_RATE, timeout=TIMEOUT)

# Cube vertices
vertices = (
    (1, -1, -1), (1, 1, -1), (-1, 1, -1), (-1, -1, -1),
    (1, -1, 1), (1, 1, 1), (-1, -1, 1), (-1, 1, 1)
)

# Cube edges
edges = (
    (0,1), (0,3), (0,4), (2,1), (2,3), (2,7),
    (6,3), (6,4), (6,7), (5,1), (5,4), (5,7)
)

# Cube faces
surfaces = (
    (0,1,2,3), (3,2,7,6), (6,7,5,4),
    (4,5,1,0), (1,5,7,2), (4,0,3,6)
)

# Face colors
colors = (
    (1,0,0), (0,1,0), (0,0,1),
    (1,1,0), (1,0,1), (0,1,1)
)

def draw_cube():
    glBegin(GL_QUADS)
    for i, surface in enumerate(surfaces):
        glColor3fv(colors[i])
        for vertex in surface:
            glVertex3fv(vertices[vertex])
    glEnd()
    
    glBegin(GL_LINES)
    glColor3fv((0,0,0))
    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()

def main():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL)
    pygame.display.set_caption("MPU6050 Orientation Visualizer")
    
    gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)
    glTranslatef(0.0, 0.0, -5)
    
    yaw, pitch, roll = 0, 0, 0
    
    print("Connected. Reading data...")
    clock = pygame.time.Clock()
    
    try:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    ser.close()
                    return
            
            # Read serial data
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                print(line)
                
                # Parse ypr data
                if line.startswith('ypr'):
                    parts = line.split('\t')
                    if len(parts) == 4:
                        try:
                            yaw = float(parts[1])
                            pitch = float(parts[2])
                            roll = float(parts[3])
                        except ValueError:
                            pass
            
            # Clear screen
            glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
            
            glPushMatrix()
            
            # Apply rotations (order matters: yaw, pitch, roll)
            glRotatef(yaw, 0, 0, 1)      # Yaw around Z axis
            glRotatef(pitch, 0, 1, 0)    # Pitch around Y axis
            glRotatef(roll, 1, 0, 0)     # Roll around X axis
            
            draw_cube()
            
            glPopMatrix()
            
            pygame.display.flip()
            clock.tick(60)
            
    except KeyboardInterrupt:
        print("Stopping.")
    finally:
        ser.close()
        pygame.quit()

if __name__ == "__main__":
    main()