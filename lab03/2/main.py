import glfw
from OpenGL.GL import *
import numpy as np


g_composed_mat = np.identity(3)

SCALE_MATRIX = np.array([[1., 0., 0.],
                         [0., .9, 0.],
                         [0., 0., 1.]])

SCALE_MATRIX_UNDO = np.array([[1., 0., 0.],
                              [0., 1.1, 0.],
                              [0., 0., 1.]])


def _rotate_matrix(deg):
    rad = np.radians(deg)

    return np.array([[np.cos(rad), -np.sin(rad), 0.],
                     [np.sin(rad), np.cos(rad), 0.],
                     [0., 0., 1.]])


ROTATE_MATRIX = _rotate_matrix(10)
ROTATE_MATRIX_UNDO = _rotate_matrix(-10)

TRANSLATE_MATRIX = np.array([[1., 0., 0.1], [0., 1., 0.], [0., 0., 1.]])
TRANSLATE_MATRIX_UNDO = np.array([[1., 0., -0.1], [0., 1., 0.], [0., 0., 1.]])

REFLECT_MATRIX = np.array([[-1., 0., 0.], [0., -1., 0.], [0., 0., 1.]])


def key_callback(window, key, scancode, action, mods):
    global g_composed_mat

    if action == glfw.PRESS or action == glfw.REPEAT:
        if key == glfw.KEY_W:
            g_composed_mat = SCALE_MATRIX @ g_composed_mat
        elif key == glfw.KEY_E:
            g_composed_mat = SCALE_MATRIX_UNDO @ g_composed_mat
        elif key == glfw.KEY_S:
            g_composed_mat = ROTATE_MATRIX @ g_composed_mat
        elif key == glfw.KEY_D:
            g_composed_mat = ROTATE_MATRIX_UNDO @ g_composed_mat
        elif key == glfw.KEY_X:
            g_composed_mat = TRANSLATE_MATRIX @ g_composed_mat
        elif key == glfw.KEY_C:
            g_composed_mat = TRANSLATE_MATRIX_UNDO @ g_composed_mat
        elif key == glfw.KEY_R:
            g_composed_mat = REFLECT_MATRIX @ g_composed_mat
        elif key == glfw.KEY_1:
            g_composed_mat = np.identity(3)


def render(T):
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    # draw cooridnate
    glBegin(GL_LINES)
    glColor3ub(255, 0, 0)
    glVertex2fv(np.array([0., 0.]))
    glVertex2fv(np.array([1., 0.]))
    glColor3ub(0, 255, 0)
    glVertex2fv(np.array([0., 0.]))
    glVertex2fv(np.array([0., 1.]))
    glEnd()
    # draw triangle
    glBegin(GL_TRIANGLES)
    glColor3ub(255, 255, 255)
    glVertex2fv((T @ np.array([.0, .5, 1.]))[:-1])
    glVertex2fv((T @ np.array([.0, .0, 1.]))[:-1])
    glVertex2fv((T @ np.array([.5, .0, 1.]))[:-1])
    glEnd()


def main():
    # Initialize GLFW
    if not glfw.init():
        return

    window = glfw.create_window(480, 480, "2019064811", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.set_key_callback(window, key_callback)

    glfw.make_context_current(window)

    # Main Loop
    while not glfw.window_should_close(window):
        glfw.poll_events()

        render(g_composed_mat)

        glfw.swap_buffers(window)

    glfw.terminate()


if __name__ == '__main__':
    main()
