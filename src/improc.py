import SimpleITK as sitk
from matplotlib.pyplot import bone
import numpy as np

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
    proc = sitk.MinimumMaximumImageFilter()
    proc.Execute(image)
    vmax = proc.GetMaximum()
    vmin = proc.GetMinimum()
    print("vmin", vmin, "vmax", vmax)

def __threshImage(image, up, low, out):
    proc = sitk.ThresholdImageFilter()
    proc.SetUpper(up)
    proc.SetLower(low)
    proc.SetOutsideValue(out)
    proc.tre
    return proc.Execute(image)


# Get front and left image of the assembled phantom at rest pose
def getPhantomImageAtRestPose(bodyFilename, bodyPartFilenames):
    
    # Read the main volume
    lImageBodyPart = []
    lImageBodyPart.append(sitk.ReadImage(bodyFilename, imageIO='MetaImageIO'))

    # Read the others body part
    for name in bodyPartFilenames:
        lImageBodyPart.append(sitk.ReadImage(name, imageIO='MetaImageIO'))

    # Proc the image to get contour

    lImageFront = []
    lImageSide = []
    for i in range(len(lImageBodyPart)):
        lImageBodyPart[i] = __binImage(lImageBodyPart[i])
        lImageBodyPart[i] = __floatImage(lImageBodyPart[i])

        frontImage = __mipImage(lImageBodyPart[i], axis=1)
        frontImage = __sobelImage(frontImage)
        frontImage = frontImage[:, 0, :]
        lImageFront.append(frontImage)

        sideImage = __mipImage(lImageBodyPart[i], axis=0)
        sideImage = __sobelImage(sideImage)
        sideImage = sideImage[0, :, :]
        lImageSide.append(sideImage)

    # Then assembled each piece in the main image (body)
    for i in range(1, len(lImageBodyPart)):
        Offset = lImageBodyPart[i].GetOrigin()
        Size = lImageBodyPart[i].GetSize()
        Offset = list(map(int, Offset))
        Size = list(map(int, Size))

        # front view (XZ)
        lImageFront[0][Offset[0]:Offset[0]+Size[0], 
                       Offset[2]:Offset[2]+Size[2]] += lImageFront[i][:, :]
        # side view (YZ)
        lImageSide[0][Offset[1]:Offset[1]+Size[1],
                      Offset[2]:Offset[2]+Size[2]] += lImageSide[i][:, :]

    lImageFront[0] = __threshImage(lImageFront[0], up=1, out=1)
    lImageSide[0] = __threshImage(lImageSide[0], up=1, out=1)

    return __convertImage2rgbd(lImageFront[0]), lImageFront[0].GetSize(), __convertImage2rgbd(lImageSide[0]), lImageSide[0].GetSize()

# Get front and left image of the assembled phantom at rest pose
def _getPhantomImageAtRestPose(bodyFilename, bodyPartFilenames):
    
    # Read the main volume
    lImageBodyPart = []
    lImageBodyPart.append(sitk.ReadImage(bodyFilename, imageIO='MetaImageIO'))

    # Read the others body part
    for name in bodyPartFilenames:
        lImageBodyPart.append(sitk.ReadImage(name, imageIO='MetaImageIO'))

    # Then assembled each piece in the main image (body)
    for i in range(1, len(lImageBodyPart)):
        Offset = lImageBodyPart[i].GetOrigin()
        Size = lImageBodyPart[i].GetSize()
        Offset = list(map(int, Offset))
        Size = list(map(int, Size))

        lImageBodyPart[0][Offset[0]:Offset[0]+Size[0],
                          Offset[1]:Offset[1]+Size[1], 
                          Offset[2]:Offset[2]+Size[2]] = lImageBodyPart[i][:, :, :]

    # Processing to get 2D image
    bone1 = __binImage(lImageBodyPart[0], low=6, up=6)
    bone2 = __binImage(lImageBodyPart[0], low=9, up=9)
    bone3 = __binImage(lImageBodyPart[0], low=15, up=15)
    skin = __binImage(lImageBodyPart[0], low=1, up=40)
    
    bone1 = __orImage(bone1, bone2)
    bone1 = __orImage(bone1, bone3)

    skin = __floatImage(skin)
    bone1 = __floatImage(bone1) * 2  # for highlight bones
    body = __addImage(skin, bone1)
    
    frontImage = __meipImage(body, axis=1)
    frontImage = frontImage[:, 0, :]

    sideImage = __meipImage(body, axis=0)
    sideImage = sideImage[0, :, :]
    
    return __convertImage2rgbd(frontImage), frontImage.GetSize(), __convertImage2rgbd(sideImage), sideImage.GetSize()