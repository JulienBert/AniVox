import numpy as np

class Bone():
    #    tP0 = (x, y, z)
    def __init__(self, name, tP0, tP1, tLimRot, tColor):
        
        # Control points
        #                          z
        #       + p0             /
        #      /                +--- x
        #     /                 |
        #    + p1               y
        #
        #
        # Diamond drawing
        #
        #        + p0
        #      /   \
        #  pm +--+--+ pp
        #     \   p /
        #     \     /
        #      \   /
        #      \   /
        #       \ /
        #        + p1
        #
        #
        
        d = 10 # width and height of the diamond head
        
        ## Compute p

        p0 = np.array([tP0[0], tP0[1], tP0[2]])
        p1 = np.array([tP1[0], tP1[1], tP1[2]])

        # get vector p1p0
        p1p0 = p1-p0
        p1p0 = p1p0 / np.linalg.norm(p1p0) 

        p = p0 + d*p1p0

        ## From p get pp (on xy-plan)

        # express p0 according to p
        p0p = p0 - p
        # rotate -pi/2   ->  [[0, -1], [1, 0]]
        pp = np.array([-p0p[1], p0p[0], 1])
        # move back pp to global frame
        pp = p + pp

        ## From p get pm (on xy-plan)

        # express p0 according to p
        p0p = p0 - p
        # rotate pi/2   ->  [[0, 1], [-1, 0]]
        pm = np.array([p0p[1], -p0p[0], 1])
        # move back pp to global frame
        pm = p + pm

        self.sBoneName = name
        #                                0   1   2  3   4
        self.aRestPoseVertex = np.array([p0, p1, p, pp, pm], 'float32')

        self.aRestPoseEdges = np.array([[0, 3], [0, 4], [3, 4], [4, 1], [3, 1]], 'int16')

        self.aLocalRotation = np.eye(3)
        self.aLocalTranslation = np.zeros(3)
        self.aAngles = np.zeros(3)
        self.aLimitAngles = np.array([tLimRot[0], tLimRot[1], tLimRot[2]])

        self.tColor = tColor

    def getDrawLines(self):
        allLines = []
        for i in range(len(self.aRestPoseEdges)):
            iP1 = self.aRestPoseEdges[i][0]
            iP2 = self.aRestPoseEdges[i][1]

            P1 = (self.aRestPoseVertex[iP1][0], self.aRestPoseVertex[iP1][1], self.aRestPoseVertex[iP1][2])
            P2 = (self.aRestPoseVertex[iP2][0], self.aRestPoseVertex[iP2][1], self.aRestPoseVertex[iP2][2])
            aLine = (P1, P2)
            allLines.append(aLine)

        return allLines

    def getDrawColor(self):
        return self.tColor

class Skeleton():
    def __init__(self):
        self.lBones = []

    def addSerialBone(self, name, tP0, tP1, tLimRot, color):
       aBone = Bone(name, tP0, tP1, tLimRot, color)
       self.lBones.append(aBone)

    def getNbBones(self):
        return len(self.lBones)

    def getBone(self, id):
        return self.lBones[id]
