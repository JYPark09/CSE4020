from enum import Enum
import numpy as np
import os

import glfw
from OpenGL.GL import *
from OpenGL.GLU import *

class BVHParserState(Enum):
    NONE = 0,
    HIERARCHY = 1,
    MOTION = 2

class BVHNode:
    def __init__(self, name, parent=None, is_end=False):
        self.name = name
        self.parent = parent
        self.is_end = is_end

        self.offset = np.zeros(3)
        self.channels = []
        self.frames = []

        self.children = []

    def render(self, frame):
        glPushMatrix()
        glTranslatef(*self.offset)

        glBegin(GL_LINES)
        glVertex3fv(np.zeros(3))
        glVertex3fv(-self.offset)
        glEnd()

        if not self.is_end:
            for c in self.children:
                c.render(frame)

        glPopMatrix()

class BVH:
    def __init__(self):
        self.root = BVHNode('ROOT')

        self.joints = []
        self.num_of_frames = 0
        self.fps = 0

    def render(self, frame=-1):
        self.root.render(frame)

    def __repr__(self):
        def _make_str(level, msg):
            return '  ' * level + msg + os.linesep

        result = ''

        node_stack = [(self.root, 0)]

        while node_stack:
            node, level = node_stack[-1]
            node_stack.pop()

            result += _make_str(level, '<{}>'.format(node.name))
            result += _make_str(level, 'offset: ' + str(node.offset))
            result += _make_str(level, 'channel: ' + ', '.join(node.channels))
            result += _make_str(level, 'is endpoint: {}'.format(node.is_end))

            if not node.is_end:
                result += _make_str(level, 'first frame: ' + str(node.frames[0]))
                result += _make_str(level, 'last frame: ' + str(node.frames[-1]))

                for c in node.children:
                    node_stack.append((c, level+1))

        return result


def parse_bvh(lines):
    state = BVHParserState.NONE

    bvh = BVH()
    cur_node = None
    node_stack = [bvh.root]

    tot_num_of_channels = 0
    channels = []
    frames = []

    for line in lines:
        line = line.strip()
        key, *args = line.split()
        key = key.upper()

        if key == 'HIERARCHY':
            state = BVHParserState.HIERARCHY
            continue
        elif key == 'MOTION':
            state = BVHParserState.MOTION
            continue

        if state == BVHParserState.HIERARCHY:
            if key == 'JOINT' or key == 'ROOT':
                bvh.joints.append(args[0])

            if key == '{':
                node_stack.append(cur_node)
            elif key == '}':
                node_stack.pop()
            elif key == 'ROOT':
                cur_node = bvh.root
                cur_node.name = args[0]
            elif key == 'JOINT':
                cur_node = BVHNode(args[0], node_stack[-1], False)
                node_stack[-1].children.append(cur_node)
            elif key == 'END':
                cur_node = BVHNode(args[0], True)
                node_stack[-1].children.append(cur_node)
            elif key == 'OFFSET':
                cur_node.offset = np.fromiter(map(float, args), dtype=float)
            elif key == 'CHANNELS':
                cur_node.channels.extend(list(map(lambda x: x.upper(), args[1:])))
                channels.append([cur_node, int(args[0])])
                tot_num_of_channels += int(args[0])

        elif state == BVHParserState.MOTION:
            if line.upper().startswith('FRAMES:'):
                bvh.num_of_frames = int(args[-1])
            elif line.upper().startswith('FRAME TIME:'):
                bvh.fps = 1 / float(args[-1])
            else:
                frames.append(np.fromiter(map(float, line.split()), dtype=float))

    # build frames
    print(tot_num_of_channels)
    for frame_idx in range(bvh.num_of_frames):
        ch_idx = 0

        for node, cnt in channels:
            node.frames.append(frames[frame_idx][ch_idx:ch_idx+cnt])
            ch_idx += cnt

    return bvh

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

    if VIEWER_STATE['bvh'] is not None:
        VIEWER_STATE['bvh'].render()


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
        

def drop_callback(window, cbfun):
    fname = cbfun[0]

    with open(fname, 'rt') as f:
        bvh = VIEWER_STATE['bvh'] = parse_bvh(f.readlines())

    print('[Open BVH]')
    print('File name:', fname)
    print('Num of frames:', bvh.num_of_frames)
    print('FPS:', bvh.fps)
    print('Num of joints:', len(bvh.joints))
    print('Joint list:', ', '.join(bvh.joints))
    print(flush=True)


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
