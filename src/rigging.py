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
        #                o p1
        #          pr   /
        #           +  /  
        #           | /
        #           |/
        #  pm +-----p-----+ pp
        #          /|
        #         o |
        #        p0 +    
        #           pq
        
        d = 10 # width and height of the diamond head
        
        self.aAngles = np.zeros(3)
        self.tColor = tColor

        self.sBoneName = name

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

        ## Compute bone vertices

        # get vector p1p0
        p1p0 = p1-p0
        p1p0 = p1p0 / np.linalg.norm(p1p0) 

        # get p
        p = p0 + d*p1p0
        # expres p0 in regard to p
        p0p = p0 - p

        # rot around y-axis
        pm = np.array([p0p[2], p0p[1], -p0p[0]])
        pp = np.array([-p0p[2], p0p[1], p0p[0]])

        # rot around x-axis
        pq = np.array([p0p[0], -p0p[2], p0p[1]])
        pr = np.array([p0p[0], p0p[2], -p0p[1]])

        # rotate all points of pi/4 around the z-axis in order 
        # than the bone face is aligned with x-axis (facing the front view) 
        hs2 = np.sqrt(2.0) / 2.0
        pm2 = np.array([pm[0]*hs2-pm[1]*hs2, pm[0]*hs2+pm[1]*hs2, pm[2]])
        pp2 = np.array([pp[0]*hs2-pp[1]*hs2, pp[0]*hs2+pp[1]*hs2, pp[2]])
        pq2 = np.array([pq[0]*hs2-pq[1]*hs2, pq[0]*hs2+pq[1]*hs2, pq[2]])
        pr2 = np.array([pr[0]*hs2-pr[1]*hs2, pr[0]*hs2+pr[1]*hs2, pr[2]])

        # put back in gbl frame
        pm2 = p + pm2
        pp2 = p + pp2
        pq2 = p + pq2
        pr2 = p + pr2

        #                                  0      1      2       3       4       5      
        self.mRestPoseVertex = np.matrix([[p0[0], p1[0], pp2[0], pm2[0], pq2[0], pr2[0]],
                                          [p0[1], p1[1], pp2[1], pm2[1], pq2[1], pr2[1]],  
                                          [p0[2], p1[2], pp2[2], pm2[2], pq2[2], pr2[2]],
                                          [    1,     1,     1,       1,      1,      1]], 'float32')

        self.aDrawEdges = np.array([[0, 2], [0, 3], [0, 4], [0, 5],
                                    [1, 2], [1, 3], [1, 4], [1, 5],
                                    [2, 4], [4, 3], [3, 5], [5, 2]], 'int16')

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

    def getDrawLinesInFrontViewSpace(self, imOrgX, imOrgY, imSizeX, imSizeY, imScaleX, imScaleY, 
                                     bodySizeX, bodySizeY):
        # X -> mirror(X)
        # Y -> Z
        
        # offset between the final image and the vox body phantom
        offsetX = (imSizeX-bodySizeX) // 2
        offsetY = (imSizeY-bodySizeY) // 2
        # print(imSizeX, imSizeY)
        # print(bodySizeX, bodySizeY)
        # print(offsetX, offsetY)

        allLines = []
        for i in range(len(self.aDrawEdges)):
            iP1 = self.aDrawEdges[i][0]
            iP2 = self.aDrawEdges[i][1]

            P1 = (bodySizeX-self.mPoseVertex[0, iP1],
                  self.mPoseVertex[2, iP1])
            P2 = (bodySizeX-self.mPoseVertex[0, iP2],
                  self.mPoseVertex[2, iP2])
            
            P1 = (P1[0]+offsetX, P1[1]+offsetY)
            P2 = (P2[0]+offsetX, P2[1]+offsetY)

            P1 = (imScaleX*P1[0], imScaleY*P1[1])
            P2 = (imScaleX*P2[0], imScaleY*P2[1])

            P1 = (P1[0]+imOrgX, P1[1]+imOrgY)
            P2 = (P2[0]+imOrgX, P2[1]+imOrgY)
            
            aLine = (P1, P2)
            allLines.append(aLine)

        return allLines

    def getDrawLinesInSideViewSpace(self, imOrgX, imOrgY, imSizeX, imSizeY, imScaleX, imScaleY,
                                    bodySizeX, bodySizeY):
        # X -> Y
        # Y -> Z

        offsetX = (imSizeX-bodySizeX) // 2
        offsetY = (imSizeY-bodySizeY) // 2
        
        allLines = []
        for i in range(len(self.aDrawEdges)):
            iP1 = self.aDrawEdges[i][0]
            iP2 = self.aDrawEdges[i][1]

            P1 = (self.mPoseVertex[1, iP1],
                  self.mPoseVertex[2, iP1])
            P2 = (self.mPoseVertex[1, iP2],
                  self.mPoseVertex[2, iP2])

            P1 = (P1[0]+offsetX, P1[1]+offsetY)
            P2 = (P2[0]+offsetX, P2[1]+offsetY)
            
            P1 = (imScaleX*P1[0], imScaleY*P1[1])
            P2 = (imScaleX*P2[0], imScaleY*P2[1])

            P1 = (P1[0]+imOrgX, P1[1]+imOrgY)
            P2 = (P2[0]+imOrgX, P2[1]+imOrgY)
            
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


