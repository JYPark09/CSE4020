import glfw
from OpenGL.GL import *
import numpy as np

move_info = []

transform_map = {
    glfw.KEY_Q: lambda: glTranslate(-0.1, 0, 0),
    glfw.KEY_E: lambda: glTranslate(+0.1, 0, 0),
    glfw.KEY_A: lambda: glRotate(+10, 0, 0, 1),
    glfw.KEY_D: lambda: glRotate(-10, 0, 0, 1),
}

def key_callback(window, key, scancode, action, mods):
    if action == glfw.PRESS or action == glfw.REPEAT:
        if key == glfw.KEY_Q or key == glfw.KEY_E or key == glfw.KEY_A or key == glfw.KEY_D:
            move_info.append(key)
        elif key == glfw.KEY_1:
            move_info.clear()


def render():
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

    for info in move_info[::-1]:
        transform_map[info]()

    drawTriangle()


def drawTriangle():
    glBegin(GL_TRIANGLES)
    glVertex2fv(np.array([0., .5]))
    glVertex2fv(np.array([0., 0.]))
    glVertex2fv(np.array([.5, 0.]))
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

        render()

        glfw.swap_buffers(window)

    glfw.terminate()


if __name__ == "__main__":
    main()
