import numpy as np
from pyglet import gl
import pyglet

class Bone():
    def __init__(self, name, length, limRx, limRy, limRz):
        self.sBoneName = name
        self.fBoneLength = length

        # Build vertex
        #         + 0
        #         |
        #     1+ 3|4 +2 
        #         |                  / z
        #         |       in 3D      - x
        #         |                 | y
        #         + 5
        bt = 20 # bone thickness
        self.aRestPoseVertex = np.array([[  0,    0,    0],
                                         [-bt,  -bt,    0],
                                         [ bt,  -bt,    0],
                                         [  0,  -bt,  -bt],
                                         [  0,  -bt,   bt],
                                         [  0, -length,   0]], 'float32')
        self.aRestPoseEdges = (0, 2, 4, 0, 4, 1, 0, 1, 3, 0, 3, 2,
                               2, 5, 4, 4, 5, 1, 1, 5, 3, 3, 5, 2)

        self.aLocalRotation = np.eye(3)
        self.aLocalTranslation = np.zeros(3)
        self.aAngles = np.zeros(3)
        self.aLimitAngles = np.array([limRx, limRy, limRz])

    def draw(self):
        gl.glColor3f(0, 1, 0)
        bt = 20 # bone thickness
        length = self.fBoneLength
        # Triangles
        # pyglet.graphics.draw_indexed(6, pyglet.gl.GL_TRIANGLES,
        #                             self.aRestPoseEdges,
        #                             ('v3f', self.aRestPoseVertex.flatten())
        #                             )
        # Lines
        pyglet.graphics.draw_indexed(6, pyglet.gl.GL_LINES,
                                    (0, 2, 0, 4, 0, 1, 0, 3, 2, 5, 4, 5, 1, 5, 3, 5, 2, 4, 4, 1, 1, 3, 3, 2),
                                    ('v3f', self.aRestPoseVertex.flatten())
                                    )

class Skeleton():
    def __init__(self):
        self.dictRigging = {}
        self.lBones = []

        # Build skeleton
        self.dictRigging['LeftArm'] = {'parent': 'root', 'childs': []}
        self.lBones.append(Bone('LeftArm', 200, 0, 0, 0))

    def draw(self):
        for bone in self.lBones:
            bone.draw()
