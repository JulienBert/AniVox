import SimpleITK as sitk
import numpy as np

def __exportProjPNG(image, axis):
    aRes = sitk.GetArrayViewFromImage(image)
    aRes = aRes.astype('float32')
    aProj = np.amax(aRes, axis=axis)
    aProj = 255.0 * aProj / aProj.max()
    aProj = aProj.astype('uint8')
    imOut = sitk.GetImageFromArray(aProj)
    sitk.WriteImage(imOut, 'debug.png')

def __binImage(image):
    proc = sitk.BinaryThresholdImageFilter()
    proc.SetLowerThreshold(1.0)
    return proc.Execute(image)

def __sobelImage(image):
    proc = sitk.SobelEdgeDetectionImageFilter()
    return proc.Execute(image)

def __floatImage(image):
    proc = sitk.CastImageFilter()
    proc.SetOutputPixelType(sitk.sitkFloat32)
    return proc.Execute(image)

# Get front and left image of the assembled phantom at rest pose
def getPhantomImageAtRestPose(bodyFilename, bodyPartFilenames):
    
    # Read the main volume
    lImageBodyPart = []
    lImageBodyPart.append(sitk.ReadImage(bodyFilename, imageIO='MetaImageIO'))

    # Read the others body part
    for name in bodyPartFilenames:
        lImageBodyPart.append(sitk.ReadImage(name, imageIO='MetaImageIO'))

    # Assembled the phantom
    for i in range(1, len(lImageBodyPart)):
        Offset = lImageBodyPart[i].GetOrigin()
        lImageBodyPart[0][Offset[0], Offset[1], Offset[2]] = lImageBodyPart[i][:, :, :]
        

    # # image processing
    # for i in range(len(lImageBodyPart)):
        
    #     lImageBodyPart[i] = __binImage(lImageBodyPart[i])

    #     lImageBodyPart[i] = __floatImage(lImageBodyPart[i])
    #     lImageBodyPart[i] = __sobelImage(lImageBodyPart[i])

    # __exportProjPNG(lImageBodyPart[0], axis=1)