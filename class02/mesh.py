import numpy as np

from OpenGL.GL import *


class Mesh:
    def __init__(self):
        self.clear()

    def add_vertex(self, pos):
        if len(self.vertices) > 0:
            assert len(pos) == len(self.vertices[0])

        self.vertices.append(pos)

    def add_normal(self, norm):
        if len(self.normals) > 0:
            assert len(norm) == len(self.normals[0])

        self.normals.append(norm)

    def add_face(self, face):
        if len(self.indices) > 0:
            assert len(face) == len(self.indices[0])

        self.indices.append(face)

    def build(self):
        assert len(self.vertices) != 0 and len(self.indices) != 0

        self.vertices = np.array(self.vertices, dtype=np.float32)
        self.normals = np.array(self.normals, dtype=np.float32)
        self.indices = np.array(self.indices, dtype=np.uint32)
        self.colors = np.array(self.colors, dtype=np.uint32)

        self.vertex_dim = len(self.vertices[0])
        self.mode = GL_TRIANGLES if len(self.indices[0]) == 3 else GL_QUADS

    def clear(self):
        self.vertices = []
        self.indices = []
        self.normals = []
        self.colors = []

        self.vertex_dim = 0
        self.mode = None

    def render(self):
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_NORMAL_ARRAY)
        glColorPointer(3, GL_UNSIGNED_BYTE, 0, self.colors)
        glVertexPointer(self.vertex_dim, GL_FLOAT,
                        self.vertex_dim * self.vertices.itemsize, self.vertices)
        glNormalPointer(GL_FLOAT, 3*self.normals.itemsize, self.normals)
        glDrawElements(self.mode, self.indices.size,
                       GL_UNSIGNED_INT, self.indices)


class ObjMeshLoader:
    @staticmethod
    def from_file(filename):
        with open(filename, 'rt') as f:
            return ObjMeshLoader.load(f.read())

    @staticmethod
    def load(obj):
        mesh = Mesh()

        for line in obj.split('\n'):
            line = line.strip()

            # ignore empty or commented line
            if len(line) == 0 or line[0] == '#':
                continue

            cmd, *args = line.split()

            if cmd == 'v':  # vertex
                mesh.add_vertex(args)
            elif cmd == 'vn':  # normal
                mesh.add_normal(args)
            elif cmd == 'f': # face
                pass

        return mesh
