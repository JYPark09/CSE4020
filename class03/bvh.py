from enum import Enum
import numpy as np

class BVHParseStage(Enum):
    NONE = 0
    HIERARCHY = 1
    MOTION = 2

class BVHNode:
    def __init__(self, name='ROOT', props=[]):
        self.name = name
        self.props = props

        self.parent = None
        self.children = []

    def add_child(self, child):
        self.children.append(child)
        child.parent = self

class BVH:
    def __init__(self):
        self.root = BVHNode()

class BVHLoader:
    @staticmethod
    def from_file(filename):
        with open(filename, 'rt') as f:
            return BVHLoader.load(f.read())

    @staticmethod
    def load(obj):
        mode = BVHParseStage.NONE
        bvh = BVH()

        cur_node = None
        node_stack = [bvh.root]

        def _parse_hierarchy(line):
            tokens = line.split()
            key = tokens[0]
            props = [] if len(tokens) == 1 else tokens[1:]

            if key == '{':
                node_stack.append(cur_node)
            elif key == '}':
                node_stack.pop()
            else:
                node = BVHNode(key, props)
                node_stack[-1].add_child(node)


        def _parse_motion(line):
            pass

        for line in obj.splitlines():
            line = line.strip()

            # ignore empty lines
            if len(line) == 0:
                continue

            if line == 'HIERARCHY':
                mode = BVHParseStage.HIERARCHY
                continue
            elif line == 'MOTION':
                mode = BVHParseStage.MOTION
                continue

            if mode == BVHParseStage.HIERARCHY:
                _parse_hierarchy(line)
            elif mode == BVHParseStage.MOTION:
                _parse_motion(line)

