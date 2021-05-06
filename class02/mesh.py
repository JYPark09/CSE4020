import ctypes
import numpy as np

from OpenGL.GL import *


class Transform:
    def __init__(self):
        self.translate = np.zeros(3)
        self.rotation = np.zeros(3)
        self.scale = np.ones(3)

    def update(self):
        glScalef(*self.scale)

        glRotatef(self.rotation[2], 1, 0, 0)
        glRotatef(self.rotation[1], 0, 1, 0)
        glRotatef(self.rotation[0], 0, 0, 1)

        glTranslatef(*self.translate)


class Mesh:
    def __init__(self):
        self.clear()

        self.diffuse = np.array([1., 1., 1., 1.])

        self.local_trans = Transform()

        self.children = []
        self.built = False

    def add_vertex(self, pos):
        assert len(pos) == 3
        self.vertices.append(pos)

    def add_normal(self, norm):
        assert len(norm) == 3
        self.normals.append(norm)

    def add_face(self, face, uv, norm):
        if len(face) == 3:
            self.vindices.append(face)
            if len(norm) != 0:
                self.nindices.append(norm)
        else:
            for i in range(1, len(face) - 1):
                self.vindices.append([face[0], face[i], face[i+1]])
                if len(norm) != 0:
                    self.nindices.append([norm[0], norm[i], norm[i+1]])

        self.n_faces += 1
        if len(face) == 3:
            self.face_3 += 1
        elif len(face) == 4:
            self.face_4 += 1
        else:
            self.face_n += 1

    def build(self, **kargs):
        if len(self.vertices) == 0 or len(self.vindices) == 0:
            return

        varr = []

        if len(self.nindices) == 0 or ('force_smooth' in kargs and kargs['force_smooth']):
            normals = [[] for _ in range(len(self.vertices))]

            for face in self.vindices:
                v = np.array([self.vertices[f] for f in face])
                v1 = v[1] - v[0]
                v2 = v[2] - v[0]

                normal = np.cross(v1, v2)
                normal = normal / np.linalg.norm(normal)

                for f in face:
                    normals[f].append(normal)

            for i, norms in enumerate(normals):
                normals[i] = np.sum(np.array(norms), axis=0)
                normals[i] /= np.linalg.norm(normals[i])

            for face in self.vindices:
                for i in face:
                    varr.append(normals[i])
                    varr.append(self.vertices[i])
        else:
            for face in zip(self.vindices, self.nindices):
                for vi, ni in zip(*face):
                    varr.append(self.normals[ni])
                    varr.append(self.vertices[vi])

        self.varr = np.array(varr, dtype=np.float32)

        self.built = True

    def clear(self):
        self.vertices = []
        self.vindices = []
        self.nindices = []
        self.normals = []

        self.n_faces = 0
        self.face_3 = 0
        self.face_4 = 0
        self.face_n = 0

    def update(self, uptime):
        for child in self.children:
            child.update(uptime)

    def render(self):
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, self.diffuse)
        glMaterialfv(GL_FRONT, GL_SHININESS, 10)
        glMaterialfv(GL_FRONT, GL_SPECULAR, (1., 1., 1., 1.))

        glPushMatrix()

        self.local_trans.update()

        if self.built:
            glEnableClientState(GL_VERTEX_ARRAY)
            glEnableClientState(GL_NORMAL_ARRAY)

            glNormalPointer(GL_FLOAT, 6 * self.varr.itemsize, self.varr)
            glVertexPointer(3, GL_FLOAT, 6 * self.varr.itemsize,
                            ctypes.c_void_p(self.varr.ctypes.data + 3*self.varr.itemsize))
            glDrawArrays(GL_TRIANGLES, 0, self.varr.size // 6)

            glDisableClientState(GL_NORMAL_ARRAY)
            glDisableClientState(GL_VERTEX_ARRAY)

        for child in self.children:
            child.render()

        glPopMatrix()


class ObjMeshLoader:
    @staticmethod
    def from_file(filename, **kargs):
        with open(filename, 'rt') as f:
            return ObjMeshLoader.load(f.read(), **kargs)

    @staticmethod
    def from_file_noret(filename, mesh, **kargs):
        with open(filename, 'rt') as f:
            ObjMeshLoader.load_noret(f.read(), mesh, **kargs)

    @staticmethod
    def load(obj, **kargs):
        mesh = Mesh()

        ObjMeshLoader.load_noret(obj, mesh, **kargs)

        return mesh

    @staticmethod
    def load_noret(obj, mesh, **kargs):
        for line in obj.split('\n'):
            line = line.strip()

            # ignore empty or commented line
            if len(line) == 0 or line[0] == '#':
                continue

            cmd, *args = line.split()

            if cmd == 'v':  # vertex
                mesh.add_vertex(list(map(float, args)))
            elif cmd == 'vn':  # normal
                mesh.add_normal(list(map(float, args)))
            elif cmd == 'f':  # face
                face = []
                uv = []
                norm = []

                for arg in args:
                    fun = arg.split('/')

                    if len(fun) >= 1:
                        face.append(int(fun[0]) - 1)
                    if len(fun) >= 3:
                        uv.append(int(fun[1]) - 1 if len(fun[1]) > 0 else 0)
                        norm.append(int(fun[2]) - 1 if len(fun[2]) > 0 else 0)
                    if len(fun) == 2:
                        norm.append(int(fun[1]) - 1 if len(fun[1]) > 0 else 0)

                mesh.add_face(face, uv, norm)

        mesh.build(**kargs)
