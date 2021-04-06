import numpy as np
import glfw
from OpenGL.GL import *
from OpenGL.GLU import *


def drawFrame():
    glBegin(GL_LINES)
    glColor3ub(255, 0, 0)
    glVertex2fv(np.array([0., 0.]))
    glVertex2fv(np.array([1., 0.]))
    glColor3ub(0, 255, 0)
    glVertex2fv(np.array([0., 0.]))
    glVertex2fv(np.array([0., 1.]))
    glEnd()


def drawTriangle():
    glBegin(GL_TRIANGLES)
    glVertex2fv(np.array([0., .5]))
    glVertex2fv(np.array([0., 0.]))
    glVertex2fv(np.array([.5, 0.]))
    glEnd()


def draw_white():
    glLoadIdentity()

    drawFrame()
    glColor3ub(255, 255, 255)
    drawTriangle()

def draw_blue():
    glLoadIdentity()

    glTranslatef(0.6, 0, 0)
    glRotatef(30, 0, 0, 1)

    drawFrame()
    glColor3ub(0, 0, 255)
    drawTriangle()

def draw_red():
    glLoadIdentity()

    glRotatef(30, 0, 0, 1)
    glTranslatef(0.6, 0, 0)

    drawFrame()
    glColor3ub(255, 0, 0)
    drawTriangle()


def main():
    # Initialize GLFW
    if not glfw.init():
        return

    window = glfw.create_window(480, 480, "2019064811", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)

    # Main Loop
    while not glfw.window_should_close(window):
        glfw.poll_events()

        draw_white()
        draw_blue()
        draw_red()

        glfw.swap_buffers(window)

    glfw.terminate()


if __name__ == '__main__':
    main()
