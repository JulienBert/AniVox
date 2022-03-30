

# Get x, y position to center an image within frame draw
def getCenteredImage(imageWidth, imageHeight, frameWidth, frameHeight):
    ratio = imageWidth / imageHeight
    if ratio > 1:
        newWidth = frameWidth
        newHeight = frameWidth / ratio
        paddingH = (frameHeight-newHeight) / 2.0
        paddingW = 0
        
    elif ratio < 1:
        newWidth = frameHeight * ratio
        newHeight = frameHeight
        paddingH = 0
        paddingW = (frameWidth-newWidth) / 2.0
        
    else:
        newWidth = frameWidth
        newHeight = frameHeight
        paddingH = 0
        paddingW = 0

    posMin = (paddingW+1, paddingH+1)
    posMax = (paddingW+newWidth-1, paddingH+newHeight-1)

    scaleWidth = newWidth / imageWidth
    scaleHeight = newHeight / imageHeight

    return posMin, posMax, scaleWidth, scaleHeight