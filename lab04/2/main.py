import glfw
from OpenGL.GL import *
import numpy as np

def render(th):
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()

    # draw cooridnates
    glBegin(GL_LINES)
    glColor3ub(255, 0, 0)
    glVertex2fv(np.array([0., 0.]))
    glVertex2fv(np.array([1., 0.]))
    glColor3ub(0, 255, 0)
    glVertex2fv(np.array([0., 0.]))
    glVertex2fv(np.array([0., 1.]))
    glEnd()

    glColor3ub(255, 255, 255)

    # calculate matrix M1, M2 using th
    R = np.identity(3)
    R[0, :2] = np.array([np.cos(-th), -np.sin(-th)])
    R[1, :2] = np.array([np.sin(-th), np.cos(-th)])

    T1 = np.identity(3)
    T1[0, 2] = .5

    M1 = R @ T1

    T2 = np.identity(3)
    T2[1, 2] = .5

    M2 = R @ T2

    # draw point p
    glBegin(GL_POINTS)
    glVertex2fv((M1 @ np.array([.5, 0., 1.]))[:-1]) # p1
    glVertex2fv((M2 @ np.array([0., .5, 1.]))[:-1]) # p2
    glEnd()

    # draw vector v
    glBegin(GL_LINES)
    # v1
    glVertex2fv((M1 @ np.array([0., 0., 0.]))[:-1])
    glVertex2fv((M1 @ np.array([.5, 0., 0.]))[:-1])

    # v2
    glVertex2fv((M2 @ np.array([0., 0., 0.]))[:-1])
    glVertex2fv((M2 @ np.array([0., .5, 0.]))[:-1])
    glEnd()


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

        t = glfw.get_time()
        render(t)

        glfw.swap_buffers(window)

    glfw.terminate()


if __name__ == "__main__":
    main()
