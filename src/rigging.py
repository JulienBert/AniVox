import numpy as np

class Bone():
    def __init__(self, name, adp0, adp1, tColor):
        
        # Control points
        #                          z
        #       + p1             /
        #      /                +--- x
        #     /                 |
        #    + p0               y
        #
        #
        # Diamond drawing
        #
        #        + p0                  + pq
        #      /   \                 p/
        #  pm +--+--+ pp      pm +---+---+ pp
        #     \   p /               / 
        #     \     /              + pr
        #      \   /
        #      \   /
        #       \ /
        #        + p1
        #
        #
        
        d = 10 # width and height of the diamond head
        
        self.aAngles = np.zeros(3)
        self.tColor = tColor

        # p0 is org

        self.mLocalTranslation = np.matrix([[1, 0, 0, adp0[0]],
                                            [0, 1, 0, adp0[1]],
                                            [0, 0, 1, adp0[2]],
                                            [0, 0, 0,       1]])

        self.mLocalRotation = np.matrix(np.eye(4))

        self.mLocalTransformation = self.mLocalTranslation*self.mLocalRotation

        self.mGlobalTransformation = np.matrix(np.eye(4)) 

        p0 = np.array([0, 0, 0])
        p1 = np.array([adp1[0], adp1[1], adp1[2]])

        ## Compute p

        # get vector p1p0
        p1p0 = p1-p0
        p1p0 = p1p0 / np.linalg.norm(p1p0) 

        p = p0 + d*p1p0

        ## From p get pp (on xy-plan)

        # express p0 according to p
        p0p = p0 - p
        
        # rotate -pi/2   ->  [[0, -1], [1, 0]]
        pp = np.array([-p0p[1], p0p[0], p0p[2]])
        # rotate pi/2   ->  [[0, 1], [-1, 0]]
        pm = np.array([p0p[1], -p0p[0], p0p[2]])

        # the same for z-axis
        pq = np.array([p0p[0], -p0p[2],  p0p[1]])
        pr = np.array([p0p[0],  p0p[2], -p0p[1]])

        # move back pp to global frame
        pp = p + pp
        pm = p + pm
        pq = p + pq
        pr = p + pr

        self.sBoneName = name

        #                                  0      1      2     3      4      5      6
        self.mRestPoseVertex = np.matrix([[p0[0], p1[0], p[0], pp[0], pm[0], pq[0], pr[0]],
                                          [p0[1], p1[1], p[1], pp[1], pm[1], pq[1], pr[1]],  
                                          [p0[2], p1[2], p[2], pp[2], pm[2], pq[2], pr[2]],
                                          [    1,     1,    1,     1,     1,     1,     1]], 'float32')

        self.aDrawEdges = np.array([[0, 3], [0, 4], [3, 4], [4, 1], [3, 1],
                                    [0, 6], [0, 5], [6, 1], [5, 1], [5, 6]], 'int16')

        self.mPoseVertex = self.mGlobalTransformation * self.mRestPoseVertex

    def setOrientation(self, rx, ry, rz):
        self.aAngles[0] = rx
        self.aAngles[1] = ry
        self.aAngles[2] = rz

    def setOrientationRx(self, rx):
        self.aAngles[0] = rx

    def setOrientationRy(self, ry):
        self.aAngles[1] = ry

    def setOrientationRz(self, rz):
        self.aAngles[2] = rz

    def updateLocalPose(self):
        rx, ry, rz = self.aAngles

        cx = np.cos(rx)
        sx = np.sin(rx)
        cy = np.cos(ry)
        sy = np.sin(ry)
        cz = np.cos(rz)
        sz = np.sin(rz)

        RotX = np.matrix([[1,  0,   0, 0],
                          [0, cx, -sx, 0],
                          [0, sx,  cx, 0],
                          [0,  0,   0, 1]])

        RotY = np.matrix([[ cy,  0, sy, 0],
                          [  0,  1,  0, 0],
                          [-sy,  0, cy, 0],
                          [  0,  0,  0, 1]])

        RotZ = np.matrix([[cz, -sz, 0, 0],
                          [sz,  cz, 0, 0],
                          [ 0,   0, 1, 0],
                          [ 0,   0, 0, 1]])

        self.mLocalRotation = RotZ*RotY*RotX
        self.mLocalTransformation = self.mLocalTranslation*self.mLocalRotation

    def updateGlobalPose(self, mTransformation):
        self.mGlobalTransformation = mTransformation.copy()
        self.mPoseVertex = self.mGlobalTransformation * self.mRestPoseVertex

    def getDrawLinesInFrontViewSpace(self, imOrgX, imOrgY, imSizeX, imSizeY):
        # X -> mirror(X)
        # Y -> Z
        
        allLines = []
        for i in range(len(self.aDrawEdges)):
            iP1 = self.aDrawEdges[i][0]
            iP2 = self.aDrawEdges[i][1]

            P1 = ((imSizeX-self.mPoseVertex[0, iP1]) + imOrgX, self.mPoseVertex[2, iP1] + imOrgY)
            P2 = ((imSizeX-self.mPoseVertex[0, iP2]) + imOrgX, self.mPoseVertex[2, iP2] + imOrgY)
            
            aLine = (P1, P2)
            # print(aLine)
            allLines.append(aLine)


        return allLines

    
    def getDrawLinesInXYPlane(self):

        allLines = []
        for i in range(len(self.aDrawEdges)):
            iP1 = self.aDrawEdges[i][0]
            iP2 = self.aDrawEdges[i][1]
            #                      X                         Y                         Z
            P1 = (self.mPoseVertex[0, iP1], self.mPoseVertex[1, iP1], self.mPoseVertex[2, iP1])
            P2 = (self.mPoseVertex[0, iP2], self.mPoseVertex[1, iP2], self.mPoseVertex[2, iP2])
            aLine = (P1, P2)
            allLines.append(aLine)

        return allLines

    def getDrawLinesInYZPlane(self):

        # X -> Y
        # Y -> Z
        # Z -> X

        allLines = []
        for i in range(len(self.aDrawEdges)):
            iP1 = self.aDrawEdges[i][0]
            iP2 = self.aDrawEdges[i][1]
            #                      Y                         Z                         X
            P1 = (self.mPoseVertex[1, iP1], self.mPoseVertex[2, iP1], self.mPoseVertex[0, iP1])
            P2 = (self.mPoseVertex[1, iP2], self.mPoseVertex[2, iP2], self.mPoseVertex[0, iP2])
            aLine = (P1, P2)
            allLines.append(aLine)

        return allLines

    def getDrawLinesInXZPlane(self):

        # X -> X
        # Y -> Z
        # Z -> Y

        allLines = []
        for i in range(len(self.aDrawEdges)):
            iP1 = self.aDrawEdges[i][0]
            iP2 = self.aDrawEdges[i][1]
            #                      X                         Z                         Y
            P1 = (self.mPoseVertex[0, iP1], self.mPoseVertex[2, iP1], self.mPoseVertex[1, iP1])
            P2 = (self.mPoseVertex[0, iP2], self.mPoseVertex[2, iP2], self.mPoseVertex[1, iP2])
            aLine = (P1, P2)
            allLines.append(aLine)

        return allLines

    def getDrawColor(self):
        return self.tColor

    def getLocalTransformation(self):
        return self.mLocalTransformation

    def getGlobalTransformation(self):
        return self.mGlobalTransformation



class Skeleton():
    def __init__(self):
        self.lBones = []
        self.nbBones = 0

    def addSerialBones(self, aPoints, tNames, tColors):
        self.lBones = []
        self.nbBones = 0
        
        nbPoints = aPoints.shape[1]

        # Add bones
        for i in range(1, nbPoints-1):
            dp0 = aPoints[:, i] - aPoints[:, i-1]
            dp1 = aPoints[:, i+1] - aPoints[:, i]

            aBone = Bone(tNames[i], dp0, dp1, tColors[i])
            self.lBones.append(aBone)
            self.nbBones += 1

        # Update global transform
        glbT = np.matrix(np.eye(4))
        for iBone in range(self.nbBones):
            localT = self.lBones[iBone].getLocalTransformation()
            glbT = glbT*localT
            self.lBones[iBone].updateGlobalPose(glbT)

    def updateSkeleton(self, id):
        # update the local pose of the bone
        self.lBones[id].updateLocalPose()

        # then update the kinematic chain (global pose)
        if id == 0:
            glbT = np.matrix(np.eye(4))
        else:
            glbT = self.lBones[id-1].getGlobalTransformation()

        for iBone in range(id, self.nbBones):
            localT = self.lBones[iBone].getLocalTransformation()
            glbT = glbT*localT
            self.lBones[iBone].updateGlobalPose(glbT)

    def getNbBones(self):
        return len(self.lBones)

    def getBone(self, id):
        return self.lBones[id]

    # def setBoneOrientation(self, id, rx, ry, rz):
    #     self.lBones[id].setOrientation(rx, ry, rz)
    #     self.updateSkeleton(id)

    def setBoneOrientationRx(self, id, rx):
        self.lBones[id].setOrientationRx(rx)
        self.updateSkeleton(id)

    def setBoneOrientationRy(self, id, ry):
        self.lBones[id].setOrientationRy(ry)
        self.updateSkeleton(id)

    def setBoneOrientationRz(self, id, rz):
        self.lBones[id].setOrientationRz(rz)
        self.updateSkeleton(id)


