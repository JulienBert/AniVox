import dearpygui.dearpygui as dpg
import numpy as np
import tools, rigging, improc

class MainApp():
    def __init__(self):
        ## Screen setup
        try:
            from screeninfo import get_monitors
            self.mainWinWidth = get_monitors()[0].width
            self.mainWinHeight = get_monitors()[0].height
        except:
            print('/!\\ Could not find screeninfo module; run pip install screeninfo')
            self.mainWinWidth = 3840
            self.mainWinHeight = 2160    

        self.mainWinWidth /= 2
        self.mainWinHeight /= 2
        self.mainWinWidth = int(self.mainWinWidth)
        self.mainWinHeight = int(self.mainWinHeight)

        self.frameWidth = (0.90*self.mainWinWidth) // 3
        self.frameHeight = 0.95*self.mainWinHeight

        ## Colors palette
        self.PBlue = (27, 231, 255, 255)
        self.PGreen = (110, 235, 131, 255)
        self.PYellow = (228, 255, 26, 255)
        self.PGold = (232, 170, 20, 255)
        self.PRed = (255, 87, 20, 255)
        self.PGround = (39, 44, 53, 255)
        self.PWhite = (255, 255, 255, 255)

        ## init UI
        dpg.create_context()
        dpg.create_viewport(title='AniVox', clear_color=self.PGround, width=self.mainWinWidth, height=self.mainWinHeight)
        dpg.set_global_font_scale(2)

        dpg.setup_dearpygui()
        dpg.show_viewport()

        ## Everything is express in 3D image phantom space

        ## Build the right arm
        bonesControlPointsR = np.array([[0, 156, 166, 179],    # x
                                        [0, 54,  53,  52],     # y
                                        [0, 118, 197, 268]])   # z
        bonesNamesR = ('org', 'rightArm', 'rightForearm')
        bonesColorsR = (self.PWhite, self.PGreen, self.PYellow)

        self.rightArm = rigging.Skeleton()
        self.rightArm.addSerialBones(bonesControlPointsR, bonesNamesR, bonesColorsR)

        ## Build the left arm
        bonesControlPointsL = np.array([[0, 35, 26, 12],       # x
                                        [0, 54, 54, 52],       # y
                                        [0, 118, 197, 268]])   # z

        bonesNamesL = ('org', 'leftArm', 'leftForearm')
        bonesColorsL = (self.PWhite, self.PBlue, self.PRed)

        self.leftArm = rigging.Skeleton()
        self.leftArm.addSerialBones(bonesControlPointsL, bonesNamesL, bonesColorsL)

        ## Load the corresponding 3D image of the arm
        bodyPartFilenames = ['../data/mash_body.mhd', '../data/mash_right_arm.mhd', '../data/mash_right_forearm.mhd',
                             '../data/mash_left_arm.mhd', '../data/mash_left_forearm.mhd']
        self.lImageBodyPart = improc.getImagesFromFilenames(bodyPartFilenames)

        improc.updateImageOrgWithBonesOrg(self.lImageBodyPart, bonesControlPointsL, bonesControlPointsR)

        ## Prepare for viewing image

        # Volume size
        self.bodySize = self.lImageBodyPart[0].GetSize()
        self.phanSize = (400, 400, 600)

        self.imagePhanFrontWidth, self.imagePhanFrontHeight = self.phanSize[0], self.phanSize[2]
        self.imagePhanSideWidth, self.imagePhanSideHeight = self.phanSize[1], self.phanSize[2]

        frontPMin, frontPMax, frontScaleW, frontScaleH = tools.getCenteredImage(self.imagePhanFrontWidth, self.imagePhanFrontHeight, self.frameWidth, self.frameHeight)
        self.imagePhanFrontPosMin = frontPMin
        self.imagePhanFrontPosMax = frontPMax
        self.imagePhanFrontScaleWidth = frontScaleW
        self.imagePhanFrontScaleHeight = frontScaleH
        # print(f'Front image: offset {frontPMin} scaling {frontScaleW:.3f} {frontScaleH:.3f}')
        
        sidePMin, sidePMax, sideScaleW, sideScaleH = tools.getCenteredImage(self.imagePhanSideWidth, self.imagePhanSideHeight, self.frameWidth, self.frameHeight)
        self.imagePhanSidePosMin = sidePMin
        self.imagePhanSidePosMax = sidePMax
        self.imagePhanSideScaleWidth = sideScaleW
        self.imagePhanSideScaleHeight = sideScaleH

        ## Then get 2D projection image into texture for displaying
        dataFront, sizeFront, dataSide, sizeSide = improc.getPhantomImageAtPose(self.rightArm, self.leftArm, self.lImageBodyPart, self.phanSize)

        with dpg.texture_registry():
            dpg.add_dynamic_texture(self.imagePhanFrontWidth, self.imagePhanFrontHeight, dataFront, tag='image_phan_front')

        with dpg.texture_registry():
            dpg.add_dynamic_texture(self.imagePhanSideWidth, self.imagePhanSideHeight, dataSide, tag='image_phan_side')
 
    #     # Test
    #     with dpg.handler_registry():
    #         dpg.add_mouse_click_handler(callback=self.toto)
        

    # def toto(self, sender, app_data):
    #     x, y = dpg.get_mouse_pos(local=False)
    #     px, py = dpg.get_item_rect_min('leftView')
    #     print(x-px, y-py)
    #     # print(x, y)
    #     # print(px, py)
    #     #print(dpg.get_mouse_pos(local=False))
    #     #print(dpg.get_item_rect_max('leftView'))

    # #     self.buildArms()

    def drawSkeleton(self, lSkel):
        
        try:
            dpg.delete_item('bonesLayerLeftView')
        except:
            # The first time this layer doesn't exist, pass
            pass
        
        with dpg.draw_layer(parent='leftView', tag='bonesLayerLeftView'):

            for skel in lSkel:
                nBones = skel.getNbBones()
                for i in range(nBones):
                    aBone = skel.getBone(i)

                    allLines = aBone.getDrawLinesInFrontViewSpace(self.imagePhanFrontPosMin[0], 
                                                                self.imagePhanFrontPosMin[1], 
                                                                self.imagePhanFrontWidth, 
                                                                self.imagePhanFrontHeight,
                                                                self.imagePhanFrontScaleWidth,
                                                                self.imagePhanFrontScaleHeight,
                                                                self.bodySize[0],
                                                                self.bodySize[2])
                    
                    for aLine in allLines:
                        dpg.draw_line(aLine[0], aLine[1], color=aBone.getDrawColor(), thickness=2)

        try:
            dpg.delete_item('bonesLayerRightView')
        except:
            # The first time this layer doesn't exist, pass
            pass
        
        with dpg.draw_layer(parent='rightView', tag='bonesLayerRightView'):

            for skel in lSkel:
                nBones = skel.getNbBones()
                for i in range(nBones):
                    aBone = skel.getBone(i)

                    allLines = aBone.getDrawLinesInSideViewSpace(self.imagePhanSidePosMin[0], 
                                                                self.imagePhanSidePosMin[1], 
                                                                self.imagePhanSideWidth, 
                                                                self.imagePhanSideHeight,
                                                                self.imagePhanSideScaleWidth,
                                                                self.imagePhanSideScaleHeight,
                                                                self.bodySize[1],
                                                                self.bodySize[2])

                    for aLine in allLines:
                        dpg.draw_line(aLine[0], aLine[1], color=aBone.getDrawColor(), thickness=2)

    # Callback RIGHT ARM
    def callBackSliderRotXArmRight(self, sender, app_data):
        self.rightArm.setBoneOrientationRx(0, np.pi*app_data/180.0)
        self.drawSkeleton([self.leftArm, self.rightArm])

    def callBackSliderRotYArmRight(self, sender, app_data):
        self.rightArm.setBoneOrientationRy(0, np.pi*app_data/180.0)
        self.drawSkeleton([self.leftArm, self.rightArm])

    def callBackSliderRotZArmRight(self, sender, app_data):
        self.rightArm.setBoneOrientationRz(0, np.pi*app_data/180.0)
        self.drawSkeleton([self.leftArm, self.rightArm])

    def callBackSliderRotXForearmRight(self, sender, app_data):
        self.rightArm.setBoneOrientationRx(1, np.pi*app_data/180.0)
        self.drawSkeleton([self.leftArm, self.rightArm])

    def callBackResetRightArm(self, sender, app_data):
        dpg.configure_item('sliderRotXArmRight', default_value=0)
        dpg.configure_item('sliderRotYArmRight', default_value=0)
        dpg.configure_item('sliderRotZArmRight', default_value=0)
        dpg.configure_item('sliderRotXForearmRight', default_value=0)

        for i in range(self.rightArm.nbBones):
            self.rightArm.setBoneOrientationRx(i, 0.0)
            self.rightArm.setBoneOrientationRy(i, 0.0)
            self.rightArm.setBoneOrientationRz(i, 0.0)

        self.drawSkeleton([self.leftArm, self.rightArm])

    # Callback LEFT ARM
    def callBackSliderRotXArmLeft(self, sender, app_data):
        self.leftArm.setBoneOrientationRx(0, np.pi*app_data/180.0)
        self.drawSkeleton([self.leftArm, self.rightArm])

    def callBackSliderRotYArmLeft(self, sender, app_data):
        self.leftArm.setBoneOrientationRy(0, np.pi*app_data/180.0)
        self.drawSkeleton([self.leftArm, self.rightArm])

    def callBackSliderRotZArmLeft(self, sender, app_data):
        self.leftArm.setBoneOrientationRz(0, np.pi*app_data/180.0)
        self.drawSkeleton([self.leftArm, self.rightArm])

    def callBackSliderRotXForearmLeft(self, sender, app_data):
        self.leftArm.setBoneOrientationRx(1, np.pi*app_data/180.0)
        self.drawSkeleton([self.leftArm, self.rightArm])

    def callBackResetLeftArm(self, sender, app_data):
        dpg.configure_item('sliderRotXArmLeft', default_value=0)
        dpg.configure_item('sliderRotYArmLeft', default_value=0)
        dpg.configure_item('sliderRotZArmLeft', default_value=0)
        dpg.configure_item('sliderRotXForearmLeft', default_value=0)

        for i in range(self.rightArm.nbBones):
            self.leftArm.setBoneOrientationRx(i, 0.0)
            self.leftArm.setBoneOrientationRy(i, 0.0)
            self.leftArm.setBoneOrientationRz(i, 0.0)

        self.drawSkeleton([self.leftArm, self.rightArm])

    def callBackShowRightBones(self, sender, app_data):
        flag = dpg.get_value(sender)
        dpg.configure_item('bonesLayerLeftView', show=flag)
        dpg.configure_item('bonesLayerRightView', show=flag)

    def callBackUpdateSkin(self):
        ## get 2D projection image into texture for displaying
        dataFront, sizeFront, dataSide, sizeSide = improc.getPhantomImageAtPose(self.rightArm, self.leftArm, self.lImageBodyPart, self.phanSize)
        dpg.set_value('image_phan_front', dataFront)
        dpg.set_value('image_phan_side', dataSide)

    # Start Main app
    def start(self):

        # Main window
        with dpg.window(label="Main Window", width=self.mainWinWidth, height=self.mainWinHeight, pos=(0, 0), no_background=True,
                                no_move=True, no_resize=True, no_collapse=True, no_close=True, no_title_bar=True):
            
            with dpg.group(horizontal=True):
                with dpg.group(horizontal=False, width=self.frameWidth):

                    # Right arm
                    dpg.add_text('RIGHT Arm', color=self.PGreen)
                    dpg.add_slider_int(label='Rot X', default_value=0, min_value=-30, max_value=180,
                                       callback=self.callBackSliderRotXArmRight, tag='sliderRotXArmRight')
                    dpg.add_slider_int(label='Rot Y', default_value=0, min_value=-8, max_value=120,
                                       callback=self.callBackSliderRotYArmRight, tag='sliderRotYArmRight')
                    dpg.add_slider_int(label='Rot Z', default_value=0, min_value=-90, max_value=90,
                                       callback=self.callBackSliderRotZArmRight, tag='sliderRotZArmRight')
                    dpg.add_text('RIGHT Forearm', color=self.PYellow)
                    dpg.add_slider_int(label='Rot X', default_value=0, min_value=0, max_value=150,
                                       callback=self.callBackSliderRotXForearmRight, tag='sliderRotXForearmRight')
                    dpg.add_button(label='RESET RIGHT ARM', small=True, callback=self.callBackResetRightArm)
                    dpg.add_spacer(height=40)

                    # Left arm
                    dpg.add_text('LEFT Arm', color=self.PBlue)
                    dpg.add_slider_int(label='Rot X', default_value=0, min_value=-30, max_value=180,
                                       callback=self.callBackSliderRotXArmLeft, tag='sliderRotXArmLeft')
                    dpg.add_slider_int(label='Rot Y', default_value=0, min_value=8, max_value=-120,
                                       callback=self.callBackSliderRotYArmLeft, tag='sliderRotYArmLeft')
                    dpg.add_slider_int(label='Rot Z', default_value=0, min_value=-90, max_value=90,
                                       callback=self.callBackSliderRotZArmLeft, tag='sliderRotZArmLeft')
                    dpg.add_text('LEFT Forearm', color=self.PRed)
                    dpg.add_slider_int(label='Rot X', default_value=0, min_value=0, max_value=150,
                                       callback=self.callBackSliderRotXForearmLeft, tag='sliderRotXForearmLeft')
                    dpg.add_button(label='RESET LEFT ARM', small=True, callback=self.callBackResetLeftArm)
                    
                    dpg.add_spacer(height=40)
                    dpg.add_checkbox(label="Show bones", default_value=True, callback=self.callBackShowRightBones, tag='checkShowRightBones')
                    dpg.add_spacer(height=40)
                    dpg.add_button(label='UPDATE SKIN', small=True, callback=self.callBackUpdateSkin)

                with dpg.drawlist(tag='leftView', width=self.frameWidth, height=self.frameHeight):
                    dpg.draw_image('image_phan_front', 
                                    pmin=self.imagePhanFrontPosMin, 
                                    pmax=self.imagePhanFrontPosMax,
                                    uv_min=(0, 0),
                                    uv_max=(1, 1))
                    dpg.draw_polygon(points=[(0, 0), (self.frameWidth, 0), (self.frameWidth, self.frameHeight), 
                                     (0, self.frameHeight), (0, 0)], color=(255, 255, 255, 255))

                    dpg.draw_polygon(points=[(self.imagePhanFrontPosMin[0], self.imagePhanFrontPosMin[1]),
                                             (self.imagePhanFrontPosMax[0], self.imagePhanFrontPosMin[1]),
                                             (self.imagePhanFrontPosMax[0], self.imagePhanFrontPosMax[1]),
                                             (self.imagePhanFrontPosMin[0], self.imagePhanFrontPosMax[1]),
                                             (self.imagePhanFrontPosMin[0], self.imagePhanFrontPosMin[1])], 
                                             color=self.PGold)
                
                with dpg.drawlist(tag='rightView', width=self.frameWidth, height=self.frameHeight):
                    dpg.draw_image('image_phan_side', 
                                    pmin=self.imagePhanSidePosMin, 
                                    pmax=self.imagePhanSidePosMax,
                                    uv_min=(0, 0),
                                    uv_max=(1, 1))         
                    dpg.draw_polygon(points=[(0, 0), (self.frameWidth, 0), (self.frameWidth, self.frameHeight), 
                                     (0, self.frameHeight), (0, 0)], color=(255, 255, 255, 255))

                    dpg.draw_polygon(points=[(self.imagePhanSidePosMin[0], self.imagePhanSidePosMin[1]),
                                             (self.imagePhanSidePosMax[0], self.imagePhanSidePosMin[1]),
                                             (self.imagePhanSidePosMax[0], self.imagePhanSidePosMax[1]),
                                             (self.imagePhanSidePosMin[0], self.imagePhanSidePosMax[1]),
                                             (self.imagePhanSidePosMin[0], self.imagePhanSidePosMin[1])], 
                                             color=self.PGold)

        
        # draw
        
        self.drawSkeleton([self.leftArm, self.rightArm])

        dpg.start_dearpygui()

        



if __name__ == '__main__':
    App = MainApp()
    App.start()