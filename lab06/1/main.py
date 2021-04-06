import numpy as np

import glfw
from OpenGL.GL import *
from OpenGL.GLU import *


def drawUnitCube():
    glBegin(GL_QUADS)
    glVertex3f(0.5, 0.5, -0.5)
    glVertex3f(-0.5, 0.5, -0.5)
    glVertex3f(-0.5, 0.5, 0.5)
    glVertex3f(0.5, 0.5, 0.5)

    glVertex3f(0.5, -0.5, 0.5)
    glVertex3f(-0.5, -0.5, 0.5)
    glVertex3f(-0.5, -0.5, -0.5)
    glVertex3f(0.5, -0.5, -0.5)

    glVertex3f(0.5, 0.5, 0.5)
    glVertex3f(-0.5, 0.5, 0.5)
    glVertex3f(-0.5, -0.5, 0.5)
    glVertex3f(0.5, -0.5, 0.5)

    glVertex3f(0.5, -0.5, -0.5)
    glVertex3f(-0.5, -0.5, -0.5)
    glVertex3f(-0.5, 0.5, -0.5)
    glVertex3f(0.5, 0.5, -0.5)

    glVertex3f(-0.5, 0.5, 0.5)
    glVertex3f(-0.5, 0.5, -0.5)
    glVertex3f(-0.5, -0.5, -0.5)
    glVertex3f(-0.5, -0.5, 0.5)

    glVertex3f(0.5, 0.5, -0.5)
    glVertex3f(0.5, 0.5, 0.5)
    glVertex3f(0.5, -0.5, 0.5)
    glVertex3f(0.5, -0.5, -0.5)
    glEnd()


def drawCubeArray():
    for i in range(5):
        for j in range(5):
            for k in range(5):
                glPushMatrix()
                glTranslatef(i, j, -k-1)
                glScalef(.5, .5, .5)
                drawUnitCube()
                glPopMatrix()


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


def render():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)
    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    glLoadIdentity()

    myFrustum(-1, 1, -1, 1, 1, 10)
    myLookAt(np.array([5, 3, 5]), np.array([1, 1, -1]), np.array([0, 1, 0]))

    # Above two lines must behave exactly same as the below two lines

    #glFrustum(-1, 1, -1, 1, 1, 10)
    #gluLookAt(5, 3, 5, 1, 1, -1, 0, 1, 0)

    drawFrame()

    glColor3ub(255, 255, 255)
    drawCubeArray()


def normalize(vec):
    return vec / np.sqrt(np.dot(vec, vec))


def myLookAt(eye, at, up):
    vec_w = normalize(eye - at)
    vec_u = np.cross(up, vec_w)
    vec_v = np.cross(vec_w, vec_u)

    M = np.eye(4)
    M[0, :3] = vec_u
    M[1, :3] = vec_v
    M[2, :3] = vec_w
    
    M[0, 3] = -np.dot(vec_u, eye)
    M[1, 3] = -np.dot(vec_v, eye)
    M[2, 3] = -np.dot(vec_w, eye)

    glMultMatrixf(M.T)


def myFrustum(left, right, bottom, top, near, far):
    mat_orth = np.eye(4)
    mat_orth[0, 0] = 2. / (right - left)
    mat_orth[1, 1] = 2. / (top - bottom)
    mat_orth[2, 2] = -2. / (far - near)
    mat_orth[0, 3] = -(right + left) / (right - left)
    mat_orth[1, 3] = -(top + bottom) / (top - bottom)
    mat_orth[2, 3] = -(far + near) / (far - near)

    P = np.eye(4) * near
    P[2, 2] += far
    P[2, 3] = near * far
    P[3, 3] = 0
    P[3, 2] = -1

    mat_pers = mat_orth @ P

    glMultMatrixf(mat_pers.T)


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

        render()

        glfw.swap_buffers(window)

    glfw.terminate()

if __name__ == '__main__':
    main()
