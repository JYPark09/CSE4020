import numpy as np

import glfw
from OpenGL.GL import *
from OpenGL.GLU import *

VERBOSE = True
GRID_SIZE = 2.5

VIEWER_STATE = {
    'projection': True,

    'button': {
        'orbit': False,
        'panning': False
    },

    'cam': {
        'speed': 0.1,
        'distance': 7.,
        'azimuth': np.pi/4.,
        'elevation': np.pi/4.,

        'eye': None,
        'lookat': np.array([0., 0., 0.]),
        'up': np.array([0., 1., 0.]),
    }
}


class Mesh:
    def __init__(self):
        self.clear()

    def add_vertex(self, pos):
        if len(self.vertices) > 0:
            assert len(pos) == len(self.vertices[0])

        self.vertices.append(pos)

    def add_face(self, face):
        if len(self.indices) > 0:
            assert len(face) == len(self.indices[0])

        self.indices.append(face)

    def build(self):
        assert len(self.vertices) != 0 and len(self.indices) != 0

        self.vertices = np.array(self.vertices, dtype=np.float32)
        self.indices = np.array(self.indices, dtype=np.uint32)
        self.colors = np.array(self.colors, dtype=np.uint32)

        self.vertex_dim = len(self.vertices[0])
        self.mode = GL_TRIANGLES if len(self.indices[0]) == 3 else GL_QUADS

    def clear(self):
        self.vertices = []
        self.indices = []
        self.colors = []

        self.vertex_dim = 0
        self.mode = None

    def render(self):
        vertex_dim = len(self.vertices[0])

        glEnableClientState(GL_VERTEX_ARRAY)
        glColorPointer(3, GL_UNSIGNED_BYTE, 0, self.colors)
        glVertexPointer(self.vertex_dim, GL_FLOAT,
                        self.vertex_dim * self.vertices.itemsize, self.vertices)
        glDrawElements(self.mode, self.indices.size,
                       GL_UNSIGNED_INT, self.indices)


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
        gluPerspective(45, 1, 3, 10+VIEWER_STATE['cam']['distance'])
    else:
        v = 3 * np.tan(np.pi/4 / 2)
        glOrtho(-v, v, -v, v, 3, 10+VIEWER_STATE['cam']['distance'])

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
            diff_x * VIEWER_STATE['cam']['speed'] * VIEWER_STATE['cam']['distance'])
        VIEWER_STATE['cam']['elevation'] += np.radians(
            -diff_y * VIEWER_STATE['cam']['speed'] * VIEWER_STATE['cam']['distance'])

        verbose("azimuth: {}, elevation: {}".format(
            VIEWER_STATE['cam']['azimuth'], VIEWER_STATE['cam']['elevation']))

    if VIEWER_STATE['button']['panning']:
        eye = VIEWER_STATE['cam']['eye']
        lookat = VIEWER_STATE['cam']['lookat']
        up = VIEWER_STATE['cam']['up']

        vec_forward = normalize(eye - lookat)
        vec_right = np.cross(up, vec_forward)
        vec_up = np.cross(vec_forward, vec_right)

        vec_delta = diff_x * vec_right * \
            VIEWER_STATE['cam']['speed'] + -diff_y * \
            vec_up * VIEWER_STATE['cam']['speed']

        VIEWER_STATE['cam']['eye'] += vec_delta
        VIEWER_STATE['cam']['lookat'] += vec_delta

    prev_cursor_xpos = xpos
    prev_cursor_ypos = ypos


def scroll_callback(window, xoffset, yoffset):
    VIEWER_STATE['cam']['distance'] += np.sign(
        yoffset) * VIEWER_STATE['cam']['speed']

    verbose('Changed VIEWER_STATE(cam.distance) to',
            VIEWER_STATE['cam']['distance'])


def key_callback(window, key, scancode, action, mods):
    if key == glfw.KEY_V and action == glfw.PRESS:
        VIEWER_STATE['projection'] = not VIEWER_STATE['projection']
        verbose('Changed VIEWER_STATE(projection) to',
                VIEWER_STATE['projection'])


def main():
    # Initialize GLFW
    if not glfw.init():
        raise Exception("GLFW initialization failed.")

    window = glfw.create_window(680, 480, "Basic OpenGL Viewer", None, None)
    if not window:
        glfw.terminate()
        raise Exception("Cannot create window.")

    glfw.set_mouse_button_callback(window, mouse_button_callback)
    glfw.set_cursor_pos_callback(window, cursor_pos_callback)
    glfw.set_scroll_callback(window, scroll_callback)
    glfw.set_key_callback(window, key_callback)

    glfw.make_context_current(window)

    box_mesh = Mesh()

    box_mesh.add_vertex((-1., 1., 1.))
    box_mesh.add_vertex((1., 1., 1.))
    box_mesh.add_vertex((1., -1., 1.))
    box_mesh.add_vertex((-1., -1., 1.))
    box_mesh.add_vertex((-1., 1., -1.))
    box_mesh.add_vertex((1., 1., -1.))
    box_mesh.add_vertex((1., -1., -1.))
    box_mesh.add_vertex((-1., -1., -1.))

    box_mesh.add_face((0, 1, 5, 4))
    box_mesh.add_face((0, 3, 2, 1))
    box_mesh.add_face((0, 4, 7, 3))
    box_mesh.add_face((2, 3, 7, 6))
    box_mesh.add_face((4, 5, 6, 7))
    box_mesh.add_face((1, 2, 6, 5))

    box_mesh.build()

    # Main Loop
    while not glfw.window_should_close(window):
        glfw.poll_events()

        render()
        box_mesh.render()

        glfw.swap_buffers(window)

    glfw.terminate()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print('<Exception>')
        print(e)

        raise
