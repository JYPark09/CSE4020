import numpy as np

import glfw
from OpenGL.GL import *
from OpenGL.GLU import *

gCamAng = 0
gComposedM = np.identity(4)


def render():
    # enable depth test
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-2, 2, -2, 2, -1, 1)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    drawFrame()
    t = glfw.get_time()

    # blue base transformation
    glPushMatrix()
    glTranslatef(np.sin(t), 0, 0)

    drawFrame()

    # blue base drawing
    glPushMatrix()
    glScalef(.2, .2, .2)
    glColor3ub(0, 0, 255)
    drawBox()
    glPopMatrix()

    # red arm transformation
    glPushMatrix()
    glRotatef(t * (180 / np.pi), 0, 0, 1)
    glTranslatef(.5, 0, .01)

    drawFrame()

    # red arm drawing
    glPushMatrix()
    glScalef(.5, .1, .1)
    glColor3ub(255, 0, 0)
    drawBox()
    glPopMatrix()

    # green arm transformation
    glPushMatrix()
    # translate 0.1 in z axis to avoid collision between green and red
    glTranslatef(0.5, 0, .02)
    glRotatef(t * (180 / np.pi), 0, 0, 1)

    drawFrame()

    # green arm drawing
    glPushMatrix()
    glScalef(.2, .2, .2)
    glColor3ub(0, 255, 0)
    drawBox()
    glPopMatrix()

    glPopMatrix()
    glPopMatrix()
    glPopMatrix()


def drawBox():
    glBegin(GL_QUADS)
    glVertex3fv(np.array([1, 1, 0.]))
    glVertex3fv(np.array([-1, 1, 0.]))
    glVertex3fv(np.array([-1, -1, 0.]))
    glVertex3fv(np.array([1, -1, 0.]))
    glEnd()


def drawFrame():
    # draw coordinate: x in red, y in green, z in blue
    glBegin(GL_LINES)
    glColor3ub(255, 0, 0)
    glVertex3fv(np.array([0., 0., 0.]))
    glVertex3fv(np.array([1., 0., 0.]))
    glColor3ub(0, 255, 0)
    glVertex3fv(np.array([0., 0., 0.]))
    glVertex3fv(np.array([0., 1., 0.]))
    glColor3ub(0, 0, 255)
    glVertex3fv(np.array([0., 0., 0.]))
    glVertex3fv(np.array([0., 0., 1.]))
    glEnd()


def main():
    # Initialize GLFW
    if not glfw.init():
        return

    # Create Window
    window = glfw.create_window(480, 480, "2019064811", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)
    glfw.swap_interval(1)

    # Main Loop
    while not glfw.window_should_close(window):
        glfw.poll_events()

        render()

        glfw.swap_buffers(window)

    glfw.terminate()


if __name__ == '__main__':
    main()
