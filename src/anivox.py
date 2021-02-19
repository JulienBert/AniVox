# -*- coding: utf-8 -*-
from __future__ import absolute_import

import pyglet
import imgui
from imgui.integrations.pyglet import create_renderer
from pyglet import gl

class Model:

    def get_tex(self,file):
        tex = pyglet.image.load(file).get_texture()
        gl.glTexParameterf(gl.GL_TEXTURE_2D,gl.GL_TEXTURE_MIN_FILTER,gl.GL_NEAREST)
        gl.glTexParameterf(gl.GL_TEXTURE_2D,gl.GL_TEXTURE_MAG_FILTER,gl.GL_NEAREST)
        return pyglet.graphics.TextureGroup(tex)

    def __init__(self):

        self.top = self.get_tex('grass_top.png')
        self.side = self.get_tex('grass_side.png')
        self.bottom = self.get_tex('dirt.png')

        self.batch = pyglet.graphics.Batch()

        tex_coords = ('t2f',(0,0, 1,0, 1,1, 0,1, ))

        x,y,z = 0,0,-1
        X,Y,Z = x+1,y+1,z+1

        self.batch.add(4,gl.GL_QUADS,self.side,('v3f',(x,y,z, x,y,Z, x,Y,Z, x,Y,z, )),tex_coords)
        self.batch.add(4,gl.GL_QUADS,self.side,('v3f',(X,y,Z, X,y,z, X,Y,z, X,Y,Z, )),tex_coords)
        self.batch.add(4,gl.GL_QUADS,self.bottom,('v3f',(x,y,z, X,y,z, X,y,Z, x,y,Z, )),tex_coords)
        self.batch.add(4,gl.GL_QUADS,self.top,('v3f',(x,Y,Z, X,Y,Z, X,Y,z, x,Y,z, )),tex_coords)
        self.batch.add(4,gl.GL_QUADS,self.side,('v3f',(X,y,z, x,y,z, x,Y,z, X,Y,z, )),tex_coords)
        self.batch.add(4,gl.GL_QUADS,self.side,('v3f',(x,y,Z, X,y,Z, X,Y,Z, x,Y,Z, )),tex_coords)


    def draw(self):
        self.batch.draw()

class MyApp(pyglet.window.Window):
    
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

        self.Width, self.Height = self.get_size()
        
        # self.window = pyglet.window.Window(width=1280, height=720, resizable=False)
        self.image = pyglet.resource.image('body.png')

        self.imageWidth = 470//2
        self.imageHeight = 1458//2

        self.image.width = self.imageWidth
        self.image.height = self.imageHeight

        # self.on_draw = self.window.event(self.on_draw)
        # self.on_mouse_motion = self.window.event(self.on_mouse_motion)

        imgui.create_context()
        self.impl = create_renderer(self)

        self.model = Model()

        self.RotX = 0
        self.RotY = 0

        self.OpenGLInit()

    def OpenGLInit(self):
        gl.glClearColor(0.0, 0.0, 0.0, 0.0)
        gl.glClearDepth(1.0) 
        gl.glDepthFunc(gl.GL_LESS)
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glShadeModel(gl.GL_SMOOTH)   
        
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.gluPerspective(70.0, float(self.Width)/float(self.Height), 0.05, 1000.0)
        gl.glMatrixMode(gl.GL_MODELVIEW)

    def OpenGLViewInit(self):
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.gluPerspective(70,self.Width/self.Height,0.05,1000);
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if buttons == 1:
            self.RotX += dy
            self.RotY += dx

    def on_draw(self):
        self.clear()
        self.OpenGLViewInit()
        
        # gl.glPushMatrix()
        pos = (0.5,0.5,5.0)
        gl.glTranslatef(-pos[0],-pos[1],-pos[2],)
        gl.glRotatef(self.RotX,1.0,0.0,0.0)
        gl.glRotatef(self.RotY,0.0,1.0,0.0)
        gl.glRotatef(0,0.0,0.0,1.0)
        
        self.model.draw()
        # gl.glPopMatrix()

        # UI
        imgui.new_frame()
        if imgui.begin_main_menu_bar():
            if imgui.begin_menu("File", True):

                clicked_quit, selected_quit = imgui.menu_item(
                    "Quit", 'Cmd+Q', False, True
                )

                if clicked_quit:
                    exit(1)

                imgui.end_menu()
            imgui.end_main_menu_bar()

        imgui.render()
        self.impl.render(imgui.get_draw_data())
        imgui.end_frame()

    def run(self):
        pyglet.app.run()


if __name__ == "__main__":
    app = MyApp(width=1280, height=720, caption='Test', resizable=False)
    app.run()