import numpy as np

import glfw
from OpenGL.GL import *
from OpenGL.GLU import *


gCamAng = 0.
gCamHeight = 1.


def key_callback(window, key, scancode, action, mods):
    global gCamAng, gCamHeight
    if action == glfw.PRESS or action == glfw.REPEAT:
        if key == glfw.KEY_1:
            gCamAng += np.radians(-10)
        elif key == glfw.KEY_3:
            gCamAng += np.radians(10)
        elif key == glfw.KEY_2:
            gCamHeight += .1
        elif key == glfw.KEY_W:
            gCamHeight += -.1


def createVertexAndIndexArrayIndexed():
    varr = np.array([
        (-.75, .75, .75),  # v0
        (.75, .75, .75),  # v1
        (.75, -.75, .75),  # v2
        (-.75, -.75, .75),  # v3
        (-.75, .75, -.75),  # v4
        (.75, .75, -.75),  # v5
        (.75, -.75, -.75),  # v6
        (-.75, -.75, -.75),  # v7
    ], 'float32')

    iarr = np.array([
        (0, 1, 5, 4),
        (0, 3, 2, 1),
        (0, 4, 7, 3),
        (2, 3, 7, 6),
        (4, 5, 6, 7),
        (1, 2, 6, 5)
    ])

    return varr, iarr


def drawFrame():
    trans_vec = np.array([-.75, -.75, -.75])

    glBegin(GL_LINES)
    glColor3ub(255, 0, 0)
    glVertex3fv(np.array([0., 0., 0.]) + trans_vec)
    glVertex3fv(np.array([1., 0., 0.]) + trans_vec)
    glColor3ub(0, 255, 0)
    glVertex3fv(np.array([0., 0., 0.]) + trans_vec)
    glVertex3fv(np.array([0., 1., 0.]) + trans_vec)
    glColor3ub(0, 0, 255)
    glVertex3fv(np.array([0., 0., 0.]) + trans_vec)
    glVertex3fv(np.array([0., 0., 1.]) + trans_vec)
    glEnd()


def render():
    global gCamAng, gCamHeight
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)
    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    glLoadIdentity()

    gluPerspective(45, 1, 1, 10)

    gluLookAt(5*np.sin(gCamAng), gCamHeight, 5 *
              np.cos(gCamAng), 0, 0, 0, 0, 1, 0)

    drawFrame()

    glColor3ub(255, 255, 255)
    drawCube_glDrawElements()


def drawCube_glDrawElements():
    global gVertexArrayIndexed, gIndexArray
    varr = gVertexArrayIndexed
    iarr = gIndexArray

    glEnableClientState(GL_VERTEX_ARRAY)
    glVertexPointer(3, GL_FLOAT, 3*varr.itemsize, varr)
    glDrawElements(GL_QUADS, iarr.size, GL_UNSIGNED_INT, iarr)


gVertexArrayIndexed = None
gIndexArray = None


def main():
    # Initialize GLFW
    if not glfw.init():
        return

    window = glfw.create_window(480, 480, "2019064811", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)

    global gVertexArrayIndexed, gIndexArray
    gVertexArrayIndexed, gIndexArray = createVertexAndIndexArrayIndexed()

    # Main Loop
    while not glfw.window_should_close(window):
        glfw.poll_events()

        render()

        glfw.swap_buffers(window)

    glfw.terminate()


if __name__ == '__main__':
    main()
