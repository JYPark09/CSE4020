import numpy as np

from OpenGL.GL import *


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
