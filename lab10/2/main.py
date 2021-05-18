import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
from OpenGL.arrays import vbo

gCamAng = 0.
gCamHeight = 1.

frameCnt = 0
frames = [
    [0, np.radians(np.array((20, 30, 30))),
     np.radians(np.array((15, 30, 25)))],
    [20, np.radians(np.array((45, 60, 40))),
     np.radians(np.array((25, 40, 40)))],
    [40, np.radians(np.array((60, 70, 50))),
     np.radians(np.array((40, 60, 50)))],
    [60, np.radians(np.array((80, 85, 70))),
     np.radians(np.array((55, 80, 65)))]
]


def l2norm(v):
    return np.sqrt(np.dot(v, v))


def normalized(v):
    l = l2norm(v)
    return 1/l * np.array(v)


def exp(rv):
    theta = l2norm(rv)
    x, y, z = normalized(rv)

    M = np.zeros((3, 3))
    M[0, 0] = np.cos(theta) + (x ** 2) * (1 - np.cos(theta))
    M[0, 1] = x * y * (1 - np.cos(theta)) - z * np.sin(theta)
    M[0, 2] = x * z * (1 - np.cos(theta)) + y * np.sin(theta)

    M[1, 0] = y * x * (1 - np.cos(theta)) + z * np.sin(theta)
    M[1, 1] = np.cos(theta) + (y ** 2) * (1 - np.cos(theta))
    M[1, 2] = y * z * (1 - np.cos(theta)) - x * np.sin(theta)

    M[2, 0] = z * x * (1 - np.cos(theta)) - y * np.sin(theta)
    M[2, 1] = z * y * (1 - np.cos(theta)) + x * np.sin(theta)
    M[2, 2] = np.cos(theta) + (z ** 2) * (1 - np.cos(theta))

    return M


def log(R):
    theta = np.arccos((R[0, 0] + R[1, 1] + R[2, 2] - 1) / 2)
    denom = 2 * np.sin(theta)

    v1 = (R[2, 1] - R[1, 2]) / denom
    v2 = (R[0, 2] - R[2, 0]) / denom
    v3 = (R[1, 0] - R[0, 1]) / denom

    return np.array([v1, v2, v3]) * theta


def slerp(R1, R2, t):
    return R1 @ exp(t * log(R1.T @ R2))


def createVertexAndIndexArrayIndexed():
    varr = np.array([
        (-0.5773502691896258, 0.5773502691896258,  0.5773502691896258),
        (-1,  1,  1),  # v0
        (0.8164965809277261, 0.4082482904638631,  0.4082482904638631),
        (1,  1,  1),  # v1
        (0.4082482904638631, -0.4082482904638631,  0.8164965809277261),
        (1, -1,  1),  # v2
        (-0.4082482904638631, -0.8164965809277261,  0.4082482904638631),
        (-1, -1,  1),  # v3
        (-0.4082482904638631, 0.4082482904638631, -0.8164965809277261),
        (-1,  1, -1),  # v4
        (0.4082482904638631, 0.8164965809277261, -0.4082482904638631),
        (1,  1, -1),  # v5
        (0.5773502691896258, -0.5773502691896258, -0.5773502691896258),
        (1, -1, -1),  # v6
        (-0.8164965809277261, -0.4082482904638631, -0.4082482904638631),
        (-1, -1, -1),  # v7
    ], 'float32')
    iarr = np.array([
        (0, 2, 1),
        (0, 3, 2),
        (4, 5, 6),
        (4, 6, 7),
        (0, 1, 5),
        (0, 5, 4),
        (3, 6, 2),
        (3, 7, 6),
        (1, 2, 6),
        (1, 6, 5),
        (0, 7, 3),
        (0, 4, 7),
    ])
    return varr, iarr


def drawCube_glDrawElements():
    global gVertexArrayIndexed, gIndexArray
    varr = gVertexArrayIndexed
    iarr = gIndexArray
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_NORMAL_ARRAY)
    glNormalPointer(GL_FLOAT, 6*varr.itemsize, varr)
    glVertexPointer(3, GL_FLOAT, 6*varr.itemsize,
                    ctypes.c_void_p(varr.ctypes.data + 3*varr.itemsize))
    glDrawElements(GL_TRIANGLES, iarr.size, GL_UNSIGNED_INT, iarr)


def drawFrame():
    glBegin(GL_LINES)
    glColor3ub(255, 0, 0)
    glVertex3fv(np.array([0., 0., 0.]))
    glVertex3fv(np.array([3., 0., 0.]))
    glColor3ub(0, 255, 0)
    glVertex3fv(np.array([0., 0., 0.]))
    glVertex3fv(np.array([0., 3., 0.]))
    glColor3ub(0, 0, 255)
    glVertex3fv(np.array([0., 0., 0]))
    glVertex3fv(np.array([0., 0., 3.]))
    glEnd()


def XYZEulerToRotMat(euler):
    xang, yang, zang = euler

    Rx = np.array([
        [1, 0, 0],
        [0, np.cos(xang), -np.sin(xang)],
        [0, np.sin(xang), np.cos(xang)]
    ])

    Ry = np.array([
        [np.cos(yang), 0, np.sin(yang)],
        [0, 1, 0],
        [-np.sin(yang), 0, np.cos(yang)]
    ])

    Rz = np.array([
        [np.cos(zang), -np.sin(zang), 0],
        [np.sin(zang), np.cos(zang), 0],
        [0, 0, 1]
    ])

    return Rx @ Ry @ Rz


def draw_arm(objectColor, R1, R2):
    specularObjectColor = (1., 1., 1., 1.)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, objectColor)
    glMaterialfv(GL_FRONT, GL_SHININESS, 10)
    glMaterialfv(GL_FRONT, GL_SPECULAR, specularObjectColor)

    J1 = R1

    glPushMatrix()
    glMultMatrixf(J1.T)
    glPushMatrix()
    glTranslatef(0.5, 0, 0)
    glScalef(0.5, 0.05, 0.05)
    drawCube_glDrawElements()
    glPopMatrix()
    glPopMatrix()

    T1 = np.identity(4)
    T1[0][3] = 1.

    J2 = R1 @ T1 @ R2

    glPushMatrix()
    glMultMatrixf(J2.T)
    glPushMatrix()
    glTranslatef(0.5, 0, 0)
    glScalef(0.5, 0.05, 0.05)
    drawCube_glDrawElements()
    glPopMatrix()
    glPopMatrix()


def draw_arm_static(objectColor, euler1, euler2):
    R1 = np.identity(4)
    R1[:3, :3] = XYZEulerToRotMat(euler1)

    R2 = np.identity(4)
    R2[:3, :3] = XYZEulerToRotMat(euler2)

    draw_arm(objectColor, R1, R2)


def draw_arm_dynamic(objectColor, euler11, euler12, euler21, euler22, portion):
    R11 = XYZEulerToRotMat(euler11)
    R12 = XYZEulerToRotMat(euler12)
    R21 = XYZEulerToRotMat(euler21)
    R22 = XYZEulerToRotMat(euler22)

    R1 = np.identity(4)
    R1[:3, :3] = slerp(R11, R12, portion)
    R2 = np.identity(4)
    R2[:3, :3] = slerp(R21, R22, portion)

    draw_arm(objectColor, R1, R2)


def render(t):
    global gCamAng, gCamHeight, frameCnt
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 1, 1, 10)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(5*np.sin(gCamAng), gCamHeight, 5 *
              np.cos(gCamAng), 0, 0, 0, 0, 1, 0)

    # draw global frame
    drawFrame()

    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)

    glEnable(GL_RESCALE_NORMAL)

    lightPos = (3., 4., 5., 1.)
    glLightfv(GL_LIGHT0, GL_POSITION, lightPos)

    lightColor = (1., 1., 1., 1.)
    ambientLightColor = (.1, .1, .1, 1.)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, lightColor)
    glLightfv(GL_LIGHT0, GL_SPECULAR, lightColor)
    glLightfv(GL_LIGHT0, GL_AMBIENT, ambientLightColor)

    # Draw 0 frame
    draw_arm_static((1., 0., 0., 1.), *frames[0][1:])

    # Draw 20 frame
    draw_arm_static((1., 1., 0., 1.), *frames[1][1:])

    # Draw 40 frame
    draw_arm_static((0., 1., 0., 1.), *frames[2][1:])

    # Draw 60 frame
    draw_arm_static((0., 0., 1., 1.), *frames[3][1:])

    for i in range(1, len(frames)):
        if frames[i][0] >= frameCnt:
            break

    portion = (frames[i][0] - frameCnt) / (frames[i][0] - frames[i-1][0])

    draw_arm_dynamic((1., 1., 1., 1.), frames[i][1], frames[i-1]
                     [1], frames[i][2], frames[i-1][2], portion)

    glDisable(GL_LIGHTING)

    frameCnt = (frameCnt + 1) % 60


def key_callback(window, key, scancode, action, mods):
    global gCamAng, gCamHeight
    # rotate the camera when 1 or 3 key is pressed or repeated
    if action == glfw.PRESS or action == glfw.REPEAT:
        if key == glfw.KEY_1:
            gCamAng += np.radians(-10)
        elif key == glfw.KEY_3:
            gCamAng += np.radians(10)
        elif key == glfw.KEY_2:
            gCamHeight += .1
        elif key == glfw.KEY_W:
            gCamHeight += -.1


gVertexArrayIndexed = None
gIndexArray = None


def main():
    global gVertexArrayIndexed, gIndexArray
    if not glfw.init():
        return
    window = glfw.create_window(640, 640, '2019064811', None, None)
    if not window:
        glfw.terminate()
        return
    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)
    glfw.swap_interval(1)

    gVertexArrayIndexed, gIndexArray = createVertexAndIndexArrayIndexed()

    while not glfw.window_should_close(window):
        glfw.poll_events()
        t = glfw.get_time()
        render(t)

        glfw.swap_buffers(window)

    glfw.terminate()


if __name__ == "__main__":
    main()
