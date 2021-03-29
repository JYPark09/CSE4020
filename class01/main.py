import numpy as np

import glfw
from OpenGL.GL import *
from OpenGL.GLU import *

VERBOSE = True
GRID_SIZE = 10

VIEWER_STATE = {
    'projection': True,

    'button': {
        'orbit': False,
        'panning': False
    },

    'cam': {
        'eye': np.array([.25, 0.5, .25]),
        'lookat': np.array([0., 0., 0.]),
        'up': np.array([0., 1., 0.])
    }
}


def verbose(*args, **kargs):
    if VERBOSE:
        print(*args, **kargs)


def draw_grid():
    glBegin(GL_LINES)

    glColor3ub(195, 195, 195)

    for i in np.arange(-GRID_SIZE, GRID_SIZE, 0.5):
        glVertex3f(-GRID_SIZE, 0, i)
        glVertex3f(+GRID_SIZE, 0, i)

        glVertex3f(i, 0, -GRID_SIZE)
        glVertex3f(i, 0, +GRID_SIZE)

    glEnd()


def draw_unit_cube():
    glBegin(GL_QUADS)

    glVertex3f(0.5,  0.5, -0.5)
    glVertex3f(-0.5,  0.5, -0.5)
    glVertex3f(-0.5,  0.5,  0.5)
    glVertex3f(0.5,  0.5,  0.5)

    glVertex3f(0.5, -0.5,  0.5)
    glVertex3f(-0.5, -0.5,  0.5)
    glVertex3f(-0.5, -0.5, -0.5)
    glVertex3f(0.5, -0.5, -0.5)

    glVertex3f(0.5,  0.5,  0.5)
    glVertex3f(-0.5,  0.5,  0.5)
    glVertex3f(-0.5, -0.5,  0.5)
    glVertex3f(0.5, -0.5,  0.5)

    glVertex3f(0.5, -0.5, -0.5)
    glVertex3f(-0.5, -0.5, -0.5)
    glVertex3f(-0.5,  0.5, -0.5)
    glVertex3f(0.5,  0.5, -0.5)

    glVertex3f(-0.5,  0.5,  0.5)
    glVertex3f(-0.5,  0.5, -0.5)
    glVertex3f(-0.5, -0.5, -0.5)
    glVertex3f(-0.5, -0.5,  0.5)

    glVertex3f(0.5,  0.5, -0.5)
    glVertex3f(0.5,  0.5,  0.5)
    glVertex3f(0.5, -0.5,  0.5)
    glVertex3f(0.5, -0.5, -0.5)

    glEnd()


def render():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)

    glLoadIdentity()

    if not VIEWER_STATE['projection']:
        glOrtho(-5, 5, -5, 5, -10, 10)

    gluLookAt(*VIEWER_STATE['cam']['eye'], *VIEWER_STATE['cam']
              ['lookat'], *VIEWER_STATE['cam']['up'])

    draw_grid()

    draw_unit_cube()


def mouse_button_callback(window, button, action, mod):
    if button == glfw.MOUSE_BUTTON_LEFT:
        if action == glfw.PRESS:
            VIEWER_STATE['button']['orbit'] = True
        elif action == glfw.RELEASE:
            VIEWER_STATE['button']['orbit'] = False

        verbose('Changed VIEWER_STATE(orbit) to',
                VIEWER_STATE['button']['orbit'])

    elif button == glfw.MOUSE_BUTTON_RIGHT:
        if action == glfw.PRESS:
            VIEWER_STATE['button']['panning'] = True
        elif action == glfw.RELEASE:
            VIEWER_STATE['button']['panning'] = False

        verbose('Changed VIEWER_STATE(panning) to',
                VIEWER_STATE['button']['panning'])


def cursor_pos_callback(window, xpos, ypos):
    pass


def scroll_callback(window, xoffset, yoffset):
    verbose('Zomming scroll offset ({}, {})'.format(xoffset, yoffset))


def key_callback(window, key, scancode, action, mods):
    if key == glfw.KEY_V and action == glfw.PRESS:
        VIEWER_STATE['projection'] = not VIEWER_STATE['projection']
        verbose('Changed VIEWER_STATE(projection) to',
                VIEWER_STATE['projection'])


def main():
    # Initialize GLFW
    if not glfw.init():
        raise Exception("GLFW initialization failed.")

    window = glfw.create_window(1080, 680, "Basic OpenGL Viewer", None, None)
    if not window:
        glfw.terminate()
        raise Exception("Cannot create window.")

    glfw.set_mouse_button_callback(window, mouse_button_callback)
    glfw.set_cursor_pos_callback(window, cursor_pos_callback)
    glfw.set_scroll_callback(window, scroll_callback)
    glfw.set_key_callback(window, key_callback)

    glfw.make_context_current(window)

    # Main Loop
    while not glfw.window_should_close(window):
        glfw.poll_events()

        render()

        glfw.swap_buffers(window)

    glfw.terminate()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print('<Exception>')
        print(e)

        raise
