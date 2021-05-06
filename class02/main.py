import numpy as np

import glfw
from OpenGL.GL import *
from OpenGL.GLU import *

from mesh import ObjMeshLoader

VERBOSE = False
GRID_SIZE = 2.5

VIEWER_STATE = {
    'projection': True,
    'wireframe': False,
    'force_smooth': False,

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

    'mesh': None
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

    if VIEWER_STATE['wireframe']:
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    else:
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    if VIEWER_STATE['projection']:
        gluPerspective(45, 1, .1, 1000.)
    else:
        v = 6 * np.tan(np.pi/4 / 2)
        glOrtho(-v, v, -v, v, -1000., 1000.)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    process_camera()

    # Render meshes
    draw_grid()

    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHT1)
    glEnable(GL_LIGHT2)

    glEnable(GL_NORMALIZE)

    '''
    Setup Light 0
    '''
    glPushMatrix()

    lightColor = (1., 0., 0., 1.)
    ambientLightColor = (.1, .1, .1, 1.)
    lightPos = (5., 5., 5., 1.)
    glLightfv(GL_LIGHT0, GL_POSITION, lightPos)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, lightColor)
    glLightfv(GL_LIGHT0, GL_SPECULAR, lightColor)
    glLightfv(GL_LIGHT0, GL_AMBIENT, ambientLightColor)

    glPopMatrix()

    '''
    Setup Light 1
    '''
    glPushMatrix()

    lightColor = (0., 1., 0., 1.)
    ambientLightColor = (.1, .1, .1, 1.)
    lightPos = (-5., 5., 5., 1.)
    glLightfv(GL_LIGHT1, GL_POSITION, lightPos)
    glLightfv(GL_LIGHT1, GL_DIFFUSE, lightColor)
    glLightfv(GL_LIGHT1, GL_SPECULAR, lightColor)
    glLightfv(GL_LIGHT1, GL_AMBIENT, ambientLightColor)

    glPopMatrix()

    '''
    Setup Light 2
    '''
    glPushMatrix()

    lightColor = (0., 0., 1., 1.)
    ambientLightColor = (.1, .1, .1, 1.)
    lightPos = (0., 5., -5., 1.)
    glLightfv(GL_LIGHT2, GL_POSITION, lightPos)
    glLightfv(GL_LIGHT2, GL_DIFFUSE, lightColor)
    glLightfv(GL_LIGHT2, GL_SPECULAR, lightColor)
    glLightfv(GL_LIGHT2, GL_AMBIENT, ambientLightColor)

    glPopMatrix()

    objectColor = (1., 1., 1., 1.)
    specularObjectColor = (1., 1., 1., 1.)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, objectColor)
    glMaterialfv(GL_FRONT, GL_SHININESS, 10)
    glMaterialfv(GL_FRONT, GL_SPECULAR, specularObjectColor)

    if VIEWER_STATE['mesh'] is not None:
        VIEWER_STATE['mesh'].render()

    glDisable(GL_LIGHTING)


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
    if action == glfw.PRESS or action == glfw.REPEAT:
        if key == glfw.KEY_V:
            VIEWER_STATE['projection'] = not VIEWER_STATE['projection']
            verbose('Changed VIEWER_STATE(projection) to',
                    VIEWER_STATE['projection'])
        elif key == glfw.KEY_Z:
            VIEWER_STATE['wireframe'] = not VIEWER_STATE['wireframe']
        elif key == glfw.KEY_S:
            VIEWER_STATE['force_smooth'] = not VIEWER_STATE['force_smooth']
            if VIEWER_STATE['mesh'] is not None:
                VIEWER_STATE['mesh'].build(force_smooth=VIEWER_STATE['force_smooth'])

def drop_callback(window, cbfun):
    fname = cbfun[0]

    mesh = ObjMeshLoader.from_file(fname, force_smooth=VIEWER_STATE['force_smooth'])

    print('[Load OBJ]')
    print('Filename: %s' % fname)
    print('Total number of faces: %d' % mesh.n_faces)
    print('Number of faces with 3 vertices: %d' % mesh.face_3)
    print('Number of faces with 4 vertices: %d' % mesh.face_4)
    print('Number of faces with more than 4 vertices: %d' % mesh.face_n)

    VIEWER_STATE['mesh'] = mesh


def main():
    # Initialize GLFW
    if not glfw.init():
        raise Exception("GLFW initialization failed.")

    window = glfw.create_window(680, 480, "Obj Viewer", None, None)
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
