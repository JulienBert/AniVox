import SimpleITK as sitk
import numpy as np
from numba import jit
import sys

@jit(nopython=True)
def __core_PoseTransform(nx, ny, nz, aOrg, aGblT, aBody, aImageBodyPart):
    # for each voxel
    for iz in range(0, nz):
        for iy in range(0, ny):
            for ix in range(0, nx):

                # express index voxel in bone org
                px = ix-aOrg[0]
                py = iy-aOrg[1]
                pz = iz-aOrg[2]
                pw = 1

                # apply global transformation
                qx = aGblT[0, 0]*px + aGblT[0, 1]*py + aGblT[0, 2]*pz + aGblT[0, 3]*pw
                qy = aGblT[1, 0]*px + aGblT[1, 1]*py + aGblT[1, 2]*pz + aGblT[1, 3]*pw
                qz = aGblT[2, 0]*px + aGblT[2, 1]*py + aGblT[2, 2]*pz + aGblT[2, 3]*pw

                qx = int(qx)
                qy = int(qy)
                qz = int(qz)

                aBody[qz, qy, qx] = aImageBodyPart[iz, iy, ix]

    return aBody

def __exportProjPNG(image, axis):
    aRes = sitk.GetArrayViewFromImage(image)
    aRes = aRes.astype('float32')
    aProj = np.amax(aRes, axis=axis)
    aProj = 255.0 * aProj / aProj.max()
    aProj = aProj.astype('uint8')
    imOut = sitk.GetImageFromArray(aProj)
    sitk.WriteImage(imOut, 'debug.png')

def __exportPNG(image):
    aRes = sitk.GetArrayViewFromImage(image)
    aRes = aRes.astype('float32')
    aProj = 255.0 * aRes / aRes.max()
    aProj = aProj.astype('uint8')
    imOut = sitk.GetImageFromArray(aProj)
    sitk.WriteImage(imOut, 'debug.png')

def __binImage(image, low, up):
    proc = sitk.BinaryThresholdImageFilter()
    proc.SetLowerThreshold(low)
    proc.SetUpperThreshold(up)
    return proc.Execute(image)

def __sobelImage(image):
    proc = sitk.SobelEdgeDetectionImageFilter()
    return proc.Execute(image)

def __floatImage(image):
    proc = sitk.CastImageFilter()
    proc.SetOutputPixelType(sitk.sitkFloat32)
    return proc.Execute(image)

def __mipImage(image, axis):
    proc = sitk.MaximumProjectionImageFilter()
    proc.SetProjectionDimension(axis)
    return proc.Execute(image)

def __meipImage(image, axis):
    proc = sitk.MeanProjectionImageFilter()
    proc.SetProjectionDimension(axis)
    return proc.Execute(image)

def __log10Image(image):
    proc = sitk.Log10ImageFilter()
    return proc.Execute(image)

def __orImage(image1, image2):
    proc = sitk.OrImageFilter()
    return proc.Execute(image1, image2)

def __addImage(image1, image2):
    proc = sitk.AddImageFilter()
    return proc.Execute(image1, image2)

def __convertImage2rgbd(image):
    size = image.GetSize()
    rgbd = np.zeros(4*size[0]*size[1])
    ind = 0
    # image = __normalizeImage(image)
    for y in range(size[1]):
        for x in range(size[0]):
            val = image[x, y]
            rgbd[ind]   = val  # r
            rgbd[ind+1] = val  # g
            rgbd[ind+2] = val  # b
            rgbd[ind+3] = val  # d   if 0 make transparency

            ind +=4

    return rgbd

def __normalizeImage(image):
    proc = sitk.MinimumMaximumImageFilter()
    proc.Execute(image)
    vmax = proc.GetMaximum()
    vmin = proc.GetMinimum()

    return (image-vmin) / (vmax-vmin)

def __printStatImage(image):
    proc = sitk.StatisticsImageFilter()
    proc.Execute(image)
    vmax = proc.GetMaximum()
    vmin = proc.GetMinimum()
    vmean = proc.GetMean()
    vvar = proc.GetVariance()
    print("vmin", vmin, "vmax", vmax, "vmean", vmean, "var", vvar)

def __threshImage(image, up, low, out):
    proc = sitk.ThresholdImageFilter()
    proc.SetUpper(up)
    proc.SetLower(low)
    proc.SetOutsideValue(out)
    proc.tre
    return proc.Execute(image)

def __flipImage(image, axis=0):
    proc = sitk.FlipImageFilter()
    vecAxis = [False, False, False]
    vecAxis[axis] = True
    proc.SetFlipAxes(vecAxis)
    return proc.Execute(image)

def __getProj2DImage(ImageBody):
    # Processing to get 2D image
    bone1 = __binImage(ImageBody, low=6, up=6)
    bone2 = __binImage(ImageBody, low=9, up=9)
    bone3 = __binImage(ImageBody, low=15, up=15)
    skin = __binImage(ImageBody, low=1, up=40)
    
    bone1 = __orImage(bone1, bone2)
    bone1 = __orImage(bone1, bone3)

    skin = __floatImage(skin)
    bone1 = __floatImage(bone1) * 4  # for highlight bones
    body = __addImage(skin, bone1)
    
    frontImage = __meipImage(body, axis=1)
    frontImage = frontImage[:, 0, :]
    frontImage = __flipImage(frontImage, axis=0)

    sideImage = __meipImage(body, axis=0)
    sideImage = sideImage[0, :, :]
    
    return __convertImage2rgbd(frontImage), frontImage.GetSize(), __convertImage2rgbd(sideImage), sideImage.GetSize()


def getImagesFromFilenames(Filenames):
    listImages = []
    for name in Filenames:
        listImages.append(sitk.ReadImage(name, imageIO='MetaImageIO'))
    return listImages

# Define the bone origin within the image of each body part
def updateImageOrgWithBonesOrg(lImageBodyPart, bonesControlPoints):

    for i in range(1, len(lImageBodyPart)):
        imOrg = lImageBodyPart[i].GetOrigin()

        newXOrg = bonesControlPoints[0, i] - imOrg[0]
        newYOrg = bonesControlPoints[1, i] - imOrg[1]
        newZOrg = bonesControlPoints[2, i] - imOrg[2]

        newOrg = (newXOrg, newYOrg, newZOrg)

        lImageBodyPart[i].SetOrigin(newOrg)

# Get front and left image of the assembled phantom at a given pose
def getPhantomImageAtPose(rightArm, lImageBodyPart):
    # force a copy
    body = sitk.Image(lImageBodyPart[0].GetSize(), lImageBodyPart[0].GetPixelIDValue())
    body[:, :, :] = lImageBodyPart[0][:, :, :]
    aBody = sitk.GetArrayFromImage(body)

    # __printStatImage(body)

    # Then assembled each piece in the main image (body)
    for i in range(1, len(lImageBodyPart)):
        # Get image info
        Org = lImageBodyPart[i].GetOrigin()
        Size = lImageBodyPart[i].GetSize()

        # Get bone and global transformation
        Bone = rightArm.getBone(i-1)
        gblT = Bone.getGlobalTransformation()
        aOrg = np.array(Org)
        aGblT = gblT.A
        aImageBodyPart = sitk.GetArrayFromImage(lImageBodyPart[i])
        
        aBody = __core_PoseTransform(Size[0], Size[1], Size[2], aOrg, aGblT, aBody, aImageBodyPart)
        
    body = sitk.GetImageFromArray(aBody)
    return __getProj2DImage(body)

# Get front and left image of the assembled phantom at rest pose
def getPhantomImageAtRestPose(lImageBodyPart):

    # Then assembled each piece in the main image (body)
    for i in range(1, len(lImageBodyPart)):
        Offset = lImageBodyPart[i].GetOrigin()
        Size = lImageBodyPart[i].GetSize()
        Offset = list(map(int, Offset))
        Size = list(map(int, Size))

        lImageBodyPart[0][Offset[0]:Offset[0]+Size[0],
                          Offset[1]:Offset[1]+Size[1], 
                          Offset[2]:Offset[2]+Size[2]] = lImageBodyPart[i][:, :, :]

    return __getProj2DImage(lImageBodyPart)