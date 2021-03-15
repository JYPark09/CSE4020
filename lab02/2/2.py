import numpy as np
import glfw
from OpenGL.GL import *

now_clock = 9
CLOCK_KEY_LIST = [
    glfw.KEY_3, glfw.KEY_4, glfw.KEY_5, glfw.KEY_6,
    glfw.KEY_7, glfw.KEY_8, glfw.KEY_9, glfw.KEY_0,
    glfw.KEY_Q, glfw.KEY_W, glfw.KEY_1, glfw.KEY_2,
]


def key_callback(window, key, scancode, action, mods):
    global now_clock

    try:
        idx = CLOCK_KEY_LIST.index(key)
        now_clock = idx
    except:
        pass

def draw_clock():
    rad = np.linspace(0, -2 * np.pi, 13)
    x_pos = np.cos(rad)
    y_pos = np.sin(rad)

    # draw border
    glBegin(GL_LINE_LOOP)
    for x, y in zip(x_pos, y_pos):
        glVertex2f(x, y)
    glEnd()

    # draw time bar
    glBegin(GL_LINES)
    glVertex2f(0, 0)
    glVertex2f(x_pos[now_clock], y_pos[now_clock])
    glEnd()

def render():
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()

    draw_clock()

def main():
    # Initialize glfw
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

if __name__ == '__main__':
    main()
