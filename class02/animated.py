import numpy as np

from mesh import Mesh, ObjMeshLoader


class Door(Mesh):
    def __init__(self, **kargs):
        super(Door, self).__init__()

        ObjMeshLoader.from_file_noret('./animated/door.obj', self, **kargs)

        self.local_trans.translate = np.array([20., -17., -3])
        self.local_trans.scale = np.full((3,), 0.5)
        self.local_trans.rotation[0] = 90

    def update(self, uptime):
        self.local_trans.rotation[2] = np.sin(uptime / 3) * 30

        super(Door, self).update(uptime)


class RobotArm(Mesh):
    def __init__(self, **kargs):
        super(RobotArm, self).__init__()

        ObjMeshLoader.from_file_noret(
            './animated/robot_arm.obj', self, **kargs)

        self.local_trans.translate[1] = 5
        self.local_trans.scale = np.full((3,), 3)
        self.local_trans.scale[0] = 2
        self.diffuse = np.array([0.25, 0.25, 0.25, 1.])

        self.children.append(Door(**kargs))

    def update(self, uptime):
        self.local_trans.rotation[1] = (uptime * 30) % 360

        super(RobotArm, self).update(uptime)

class AnimatedMesh(Mesh):
    def __init__(self, **kargs):
        super(AnimatedMesh, self).__init__()

        ObjMeshLoader.from_file_noret('./animated/flat_bed.obj', self, **kargs)

        self.local_trans.scale = np.full((3,), 0.05)
        self.local_trans.scale[0] = 0.075
        self.diffuse = np.array([1., 1., 1., 1.])

        self.children.append(RobotArm(**kargs))

    def update(self, uptime):
        self.local_trans.translate[2] = np.sin(uptime) * 50

        super(AnimatedMesh, self).update(uptime)
