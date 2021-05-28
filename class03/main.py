from enum import Enum
import numpy as np

import glfw
from OpenGL.GL import *
from OpenGL.GLU import *

class BVHParserState(Enum):
    NONE = 0,
    HIERARCHY = 1,
    MOTION = 2

class BVHNode:
    def __init__(self):
        self.offset = np.zeros(3)


class BVH:
    def __init__(self):
        self.channels = []

'''
*******************************
* Main Program                *
*******************************
'''

VERBOSE = False
GRID_SIZE = 2.5

VIEWER_STATE = {
    'projection': True,

    'button': {
        'orbit': False,
        'panning': False
    },

    'cam': {
        'speed': 0.8,
        'distance': 7.,
        'azimuth': np.pi/4.,
        'elevation': np.pi/4.,

        'eye': None,
        'lookat': np.array([0., 0., 0.]),
        'up': np.array([0., 1., 0.]),
    },

    'bvh': None
}


def verbose(*args, **kargs):
    if VERBOSE:
        print(*args, **kargs)


def draw_grid():
    glBegin(GL_LINES)

    for i in np.arange(-GRID_SIZE, GRID_SIZE+1e-10, 0.5):
        if -1e-10 < i < 1e-10:
            glColor3ub(135, 65, 74)
        else:
            glColor3ub(195, 195, 195)

        glVertex3f(-GRID_SIZE, 0, i)
        glVertex3f(+GRID_SIZE, 0, i)

        if -1e-10 < i < 1e-10:
            glColor3ub(107, 145, 47)
        else:
            glColor3ub(195, 195, 195)

        glVertex3f(i, 0, -GRID_SIZE)
        glVertex3f(i, 0, +GRID_SIZE)

    glEnd()


def process_camera():
    distance = VIEWER_STATE['cam']['distance']
    azimuth = VIEWER_STATE['cam']['azimuth']
    elevation = VIEWER_STATE['cam']['elevation']

    VIEWER_STATE['cam']['eye'] = VIEWER_STATE['cam']['lookat'] + np.array(
        [distance * np.cos(azimuth) * np.sin(elevation), distance * np.cos(elevation), distance * np.sin(azimuth) * np.sin(elevation)])

    gluLookAt(*VIEWER_STATE['cam']['eye'], *
              VIEWER_STATE['cam']['lookat'], *VIEWER_STATE['cam']['up'])


def render():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)

    glLoadIdentity()

    if VIEWER_STATE['projection']:
        gluPerspective(45, 1, .1, 1000.)
    else:
        v = 6 * np.tan(np.pi/4 / 2)
        glOrtho(-v, v, -v, v, -1000., 1000.)

    process_camera()

    draw_grid()


prev_cursor_xpos = 0
prev_cursor_ypos = 0


def mouse_button_callback(window, button, action, mod):
    global prev_cursor_xpos, prev_cursor_ypos

    if button == glfw.MOUSE_BUTTON_LEFT:
        if action == glfw.PRESS:
            VIEWER_STATE['button']['orbit'] = True
            prev_cursor_xpos, prev_cursor_ypos = None, None
        elif action == glfw.RELEASE:
            VIEWER_STATE['button']['orbit'] = False

        verbose('Changed VIEWER_STATE(orbit) to',
                VIEWER_STATE['button']['orbit'])

    elif button == glfw.MOUSE_BUTTON_RIGHT:
        if action == glfw.PRESS:
            VIEWER_STATE['button']['panning'] = True
            prev_cursor_xpos, prev_cursor_ypos = None, None
        elif action == glfw.RELEASE:
            VIEWER_STATE['button']['panning'] = False

        verbose('Changed VIEWER_STATE(panning) to',
                VIEWER_STATE['button']['panning'])


def normalize(v):
    return v / np.sqrt(np.dot(v, v))


def cursor_pos_callback(window, xpos, ypos):
    global prev_cursor_xpos, prev_cursor_ypos

    if prev_cursor_xpos is None:
        prev_cursor_xpos = xpos

    if prev_cursor_ypos is None:
        prev_cursor_ypos = ypos

    diff_x = np.sign(xpos - prev_cursor_xpos)
    diff_y = np.sign(ypos - prev_cursor_ypos)

    if VIEWER_STATE['button']['orbit']:
        VIEWER_STATE['cam']['azimuth'] += np.radians(
            diff_x * VIEWER_STATE['cam']['speed'] * VIEWER_STATE['cam']['distance'] * 0.5)
        VIEWER_STATE['cam']['elevation'] += np.radians(
            -diff_y * VIEWER_STATE['cam']['speed'] * VIEWER_STATE['cam']['distance'] * 0.5)

        verbose("azimuth: {}, elevation: {}".format(
            VIEWER_STATE['cam']['azimuth'], VIEWER_STATE['cam']['elevation']))

    if VIEWER_STATE['button']['panning']:
        eye = VIEWER_STATE['cam']['eye']
        lookat = VIEWER_STATE['cam']['lookat']
        up = VIEWER_STATE['cam']['up']

        vec_forward = normalize(eye - lookat)
        vec_right = np.cross(up, vec_forward)
        vec_up = np.cross(vec_forward, vec_right)

        vec_delta = -diff_x * vec_right * \
            VIEWER_STATE['cam']['speed'] * 0.3 + diff_y * \
            vec_up * VIEWER_STATE['cam']['speed'] * 0.3

        VIEWER_STATE['cam']['eye'] += vec_delta
        VIEWER_STATE['cam']['lookat'] += vec_delta

    prev_cursor_xpos = xpos
    prev_cursor_ypos = ypos


def scroll_callback(window, xoffset, yoffset):
    VIEWER_STATE['cam']['distance'] += np.sign(
        -yoffset) * VIEWER_STATE['cam']['speed']

    verbose('Changed VIEWER_STATE(cam.distance) to',
            VIEWER_STATE['cam']['distance'])


def key_callback(window, key, scancode, action, mods):
    if key == glfw.KEY_V and action == glfw.PRESS:
        VIEWER_STATE['projection'] = not VIEWER_STATE['projection']
        verbose('Changed VIEWER_STATE(projection) to',
                VIEWER_STATE['projection'])


def parse_bvh(lines):
    state = BVHParserState.NONE

    

    for line in lines:
        line = line.strip().upper()

        if line == 'HIERARCHY':
            state = BVHParserState.HIERARCHY
            continue
        elif line == 'MOTION':
            state = BVHParserState.MOTION
            continue

        

def drop_callback(window, cbfun):
    fname = cbfun[0]

    with open(fname, 'rt') as f:
        VIEWER_STATE['bvh'] = parse_bvh(f.readlines())


def main():
    # Initialize GLFW
    if not glfw.init():
        raise Exception("GLFW initialization failed.")

    window = glfw.create_window(680, 480, "BVH Viewer", None, None)
    if not window:
        glfw.terminate()
        raise Exception("Cannot create window.")

    glfw.set_mouse_button_callback(window, mouse_button_callback)
    glfw.set_cursor_pos_callback(window, cursor_pos_callback)
    glfw.set_scroll_callback(window, scroll_callback)
    glfw.set_key_callback(window, key_callback)
    glfw.set_drop_callback(window, drop_callback)

    glfw.make_context_current(window)
    glfw.swap_interval(1)

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
