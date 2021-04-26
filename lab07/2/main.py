import numpy as np

import glfw
from OpenGL.GL import *
from OpenGL.GLU import *

gCamAng = 0.
gCamHeight = 1.
gObjectColor = np.array((0., 0., 0., 1.))


def createVertexAndIndexArrayIndexed():
    varr = np.array([
        (-1., 1., 1.),  # v0
        (1., 1., 1.),  # v1
        (1., -1., 1.),  # v2
        (-1., -1., 1.),  # v3
        (-1., 1., -1.),  # v4
        (1., 1., -1.),  # v5
        (1., -1., -1.),  # v6
        (-1., -1., -1.),  # v7
    ], 'float32')

    narr = np.array([
        (-0.5773502691896258, 0.5773502691896258, 0.5773502691896258),   # v0
        (0.8164965809277261, 0.4082482904638631, 0.4082482904638631),    # v1
        (0.4082482904638631, -0.4082482904638631, 0.8164965809277261),   # v2
        (-0.4082482904638631, -0.8164965809277261, 0.4082482904638631),  # v3
        (-0.4082482904638631, 0.4082482904638631, -0.8164965809277261),  # v4
        (0.4082482904638631, 0.8164965809277261, -0.4082482904638631),   # v5
        (0.5773502691896258, -0.5773502691896258, -0.5773502691896258),  # v6
        (-0.8164965809277261, -0.4082482904638631, -0.4082482904638631),  # v7
    ], 'float32')

    iarr = np.array([
        (0, 2, 1),
        (0, 3, 2),
        (4, 5, 6),
        (4, 6, 7),
        (0, 1, 5),
        (0, 5, 4),
        (3, 6, 2),
        (3, 7, 6),
        (1, 2, 6),
        (1, 6, 5),
        (0, 7, 3),
        (0, 4, 7),
    ])

    return varr, narr, iarr


def drawCube_glDrawElements():
    global gVertexArrayIndexed, gNormalArray, gIndexArray
    varr = gVertexArrayIndexed
    narr = gNormalArray
    iarr = gIndexArray

    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_NORMAL_ARRAY)
    glVertexPointer(3, GL_FLOAT, 3*varr.itemsize, varr)
    glNormalPointer(GL_FLOAT, 3*narr.itemsize, narr)
    glDrawElements(GL_TRIANGLES, iarr.size, GL_UNSIGNED_INT, iarr)


def render():
    global gCamAng, gCamHeight
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 1, 1, 10)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(5*np.sin(gCamAng), gCamHeight, 5 *
              np.cos(gCamAng), 0, 0, 0, 0, 1, 0)

    drawFrame()

    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)

    glEnable(GL_NORMALIZE)

    glPushMatrix()

    t = glfw.get_time()

    lightPos = (3., 4., 5., 1.)
    glLightfv(GL_LIGHT0, GL_POSITION, lightPos)
    glPopMatrix()

    # light intensity for each color channel
    lightColor = (1., 1., 1., 1.)
    ambientLightColor = (.1, .1, .1, 1.)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, lightColor)
    glLightfv(GL_LIGHT0, GL_SPECULAR, lightColor)
    glLightfv(GL_LIGHT0, GL_AMBIENT, ambientLightColor)

    specularObjectColor = (1., 1., 1., 1.)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, gObjectColor)
    glMaterialfv(GL_FRONT, GL_SHININESS, 10)
    glMaterialfv(GL_FRONT, GL_SPECULAR, specularObjectColor)

    glPushMatrix()

    drawCube_glDrawElements()
    glPopMatrix()

    glDisable(GL_LIGHTING)


def drawFrame():
    glBegin(GL_LINES)
    glColor3ub(255, 0, 0)
    glVertex3fv(np.array([0., 0., 0.]))
    glVertex3fv(np.array([1., 0., 0.]))
    glColor3ub(0, 255, 0)
    glVertex3fv(np.array([0., 0., 0.]))
    glVertex3fv(np.array([0., 1., 0.]))
    glColor3ub(0, 0, 255)
    glVertex3fv(np.array([0., 0., 0]))
    glVertex3fv(np.array([0., 0., 1.]))
    glEnd()


def key_callback(window, key, scancode, action, mods):
    global gCamAng, gCamHeight, gObjectColor
    if action == glfw.PRESS or action == glfw.REPEAT:
        if key == glfw.KEY_1:
            gCamAng += np.radians(-10)
        elif key == glfw.KEY_3:
            gCamAng += np.radians(10)
        elif key == glfw.KEY_2:
            gCamHeight += .1
        elif key == glfw.KEY_W:
            gCamHeight += -.1
        elif key == glfw.KEY_R:
            gObjectColor[0] = 1. - gObjectColor[0]
        elif key == glfw.KEY_G:
            gObjectColor[1] = 1. - gObjectColor[1]
        elif key == glfw.KEY_B:
            gObjectColor[2] = 1. - gObjectColor[2]


gVertexArrayIndexed = None
gNormalArray = None
gIndexArray = None


def main():
    global gVertexArrayIndexed, gNormalArray, gIndexArray

    # Initialize GLFW
    if not glfw.init():
        return

    # Create Window
    window = glfw.create_window(480, 480, "2019064811", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)
    glfw.swap_interval(1)

    gVertexArrayIndexed, gNormalArray, gIndexArray = createVertexAndIndexArrayIndexed()

    # Main Loop
    while not glfw.window_should_close(window):
        glfw.poll_events()

        render()

        glfw.swap_buffers(window)

    glfw.terminate()


if __name__ == '__main__':
    main()
