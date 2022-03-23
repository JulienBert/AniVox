import dearpygui.dearpygui as dpg
import numpy as np
import tools, rigging

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

        ## Load images
        pathImagePhanFront = '../data/mash_cont_front.png'
        pathImagePhanSide = '../data/mash_cont_side.png'

        width, height, channels, data = dpg.load_image(pathImagePhanFront)
        self.imagePhanFrontPosMin, self.imagePhanFrontPosMax = tools.getCenteredImage(width, height, self.frameWidth, self.frameHeight)
        with dpg.texture_registry():
            dpg.add_static_texture(width, height, data, tag='image_phan_front')

        width, height, channels, data = dpg.load_image(pathImagePhanSide)
        self.imagePhanSidePosMin, self.imagePhanSidePosMax = tools.getCenteredImage(width, height, self.frameWidth, self.frameHeight)
        with dpg.texture_registry():
            dpg.add_static_texture(width, height, data, tag='image_phan_side')

        # # Test
        # with dpg.handler_registry():
        #     dpg.add_mouse_click_handler(callback=self.toto)


        

    # def toto(self, sender, app_data):
    #     x, y = dpg.get_mouse_pos(local=False)
    #     px, py = dpg.get_item_rect_min('leftView')
    #     print(x-px, y-py)
    #     # print(x, y)
    #     # print(px, py)
    #     #print(dpg.get_mouse_pos(local=False))
    #     #print(dpg.get_item_rect_max('leftView'))

    #     self.buildArms()

    def buildArms(self):
        limRot = (360, 360, 360)

        bonesControlPoints = np.array([[0, 180, 165, 140, 135],
                                       [0, 215, 360, 490, 580],
                                       [0,   0,   0,   0,   0]])
        bonesNames = ('org', 'rightArm', 'rightForearm', 'rightHand')
        bonesColors = (self.PBlue, self.PGreen, self.PYellow, self.PGold)

        rightArm = rigging.Skeleton()
        rightArm.addSerialBones(bonesControlPoints, bonesNames, bonesColors)
        return rightArm

    def drawSkeleton(self, skel):
        
        try:
            dpg.delete_item('bonesLayer')
        except:
            # The first time this layer doesn't exist, pass
            pass
        
        with dpg.draw_layer(parent='leftView', tag='bonesLayer'):

            nBones = skel.getNbBones()
            for i in range(nBones):
                aBone = skel.getBone(i)

                allLines = aBone.getDrawLines()
                for aLine in allLines:
                    dpg.draw_line(aLine[0], aLine[1], color=aBone.getDrawColor(), thickness=2)

    # Callback RIGHT ARM
    def callBackSliderRotXArmRight(self, sender, app_data):
        self.rightArm.setBoneOrientationRx(0, np.pi*app_data/180.0)
        self.drawSkeleton(self.rightArm)

    # def callBackSliderRotYArmRight(self, sender, app_data):
    #     self.rightArm.setBoneOrientationRy(0, np.pi*app_data/180.0)
    #     self.drawSkeleton(self.rightArm)

    def callBackSliderRotZArmRight(self, sender, app_data):
        self.rightArm.setBoneOrientationRz(0, np.pi*app_data/180.0)
        self.drawSkeleton(self.rightArm)

    def callBackSliderRotXForearmRight(self, sender, app_data):
        self.rightArm.setBoneOrientationRx(1, np.pi*app_data/180.0)
        self.drawSkeleton(self.rightArm)

    def callBackSliderRotZForearmRight(self, sender, app_data):
        self.rightArm.setBoneOrientationRz(1, np.pi*app_data/180.0)
        self.drawSkeleton(self.rightArm)

    def callBackSliderRotXHandRight(self, sender, app_data):
        self.rightArm.setBoneOrientationRx(2, np.pi*app_data/180.0)
        self.drawSkeleton(self.rightArm)

    def callBackSliderRotZHandRight(self, sender, app_data):
        self.rightArm.setBoneOrientationRz(2, np.pi*app_data/180.0)
        self.drawSkeleton(self.rightArm)

    def callBackResetRightArm(self, sender, app_data):
        dpg.configure_item('sliderRotXArmRight', default_value=0)
        dpg.configure_item('sliderRotZArmRight', default_value=0)
        dpg.configure_item('sliderRotXForearmRight', default_value=0)
        dpg.configure_item('sliderRotZForearmRight', default_value=0)
        dpg.configure_item('sliderRotXHandRight', default_value=0)
        dpg.configure_item('sliderRotZHandRight', default_value=0)

        for i in range(self.rightArm.nbBones):
            self.rightArm.setBoneOrientationRx(i, 0.0)
            self.rightArm.setBoneOrientationRz(i, 0.0)

        self.drawSkeleton(self.rightArm)

    # Start Main app
    def start(self):

        # Main window
        with dpg.window(label="Main Window", width=self.mainWinWidth, height=self.mainWinHeight, pos=(0, 0), no_background=True,
                                no_move=True, no_resize=True, no_collapse=True, no_close=True, no_title_bar=True):
            
            with dpg.group(horizontal=True):
                with dpg.group(horizontal=False, width=self.frameWidth):

                    dpg.add_text('RIGHT Arm', color=self.PGreen)
                    dpg.add_slider_int(label='Rot X', default_value=0, min_value=-90, max_value=90,
                                       callback=self.callBackSliderRotXArmRight, tag='sliderRotXArmRight')
                    # dpg.add_slider_int(label='Rot Y', default_value=0, min_value=-90, max_value=90,
                    #                    callback=self.callBackSliderRotYArmRight, tag='sliderRotYArmRight')
                    dpg.add_slider_int(label='Rot Z', default_value=0, min_value=-90, max_value=90,
                                       callback=self.callBackSliderRotZArmRight, tag='sliderRotZArmRight')
                    dpg.add_text('RIGHT Forearm', color=self.PYellow)
                    dpg.add_slider_int(label='Rot X', default_value=0, min_value=-90, max_value=90,
                                       callback=self.callBackSliderRotXForearmRight, tag='sliderRotXForearmRight')
                    dpg.add_slider_int(label='Rot Z', default_value=0, min_value=-90, max_value=90,
                                       callback=self.callBackSliderRotZForearmRight, tag='sliderRotZForearmRight')
                    dpg.add_text('RIGHT Hand', color=self.PGold)
                    dpg.add_slider_int(label='Rot X', default_value=0, min_value=-90, max_value=90,
                                       callback=self.callBackSliderRotXHandRight, tag='sliderRotXHandRight')
                    dpg.add_slider_int(label='Rot Z', default_value=0, min_value=-90, max_value=90,
                                       callback=self.callBackSliderRotZHandRight, tag='sliderRotZHandRight')

                    dpg.add_button(label='RESET', small=True, callback=self.callBackResetRightArm)
                    

                with dpg.drawlist(tag='leftView', width=self.frameWidth, height=self.frameHeight):
                    dpg.draw_image('image_phan_front', 
                                    pmin=self.imagePhanFrontPosMin, 
                                    pmax=self.imagePhanFrontPosMax,
                                    uv_min=(0, 0),
                                    uv_max=(1, 1))
                    dpg.draw_polygon(points=[(0, 0), (self.frameWidth, 0), (self.frameWidth, self.frameHeight), 
                                     (0, self.frameHeight), (0, 0)], color=(255, 255, 255, 255))
                
                with dpg.drawlist(tag='rightView', width=self.frameWidth, height=self.frameHeight):
                    dpg.draw_image('image_phan_side', 
                                    pmin=self.imagePhanSidePosMin, 
                                    pmax=self.imagePhanSidePosMax,
                                    uv_min=(0, 0),
                                    uv_max=(1, 1))         
                    dpg.draw_polygon(points=[(0, 0), (self.frameWidth, 0), (self.frameWidth, self.frameHeight), 
                                     (0, self.frameHeight), (0, 0)], color=(255, 255, 255, 255))

        
        # draw
        self.rightArm = self.buildArms()
        self.drawSkeleton(self.rightArm)

        dpg.start_dearpygui()

        



if __name__ == '__main__':
    App = MainApp()
    App.start()