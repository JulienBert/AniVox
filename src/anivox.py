# -*- coding: utf-8 -*-
from __future__ import absolute_import

import pyglet
from pyglet import gl
import imgui
from imgui.integrations.pyglet import create_renderer

from gui import MenuGUI
from rigging import Skeleton

# class Model:

#     def get_tex(self,file):
#         tex = pyglet.image.load(file).get_texture()
#         gl.glTexParameterf(gl.GL_TEXTURE_2D,gl.GL_TEXTURE_MIN_FILTER,gl.GL_NEAREST)
#         gl.glTexParameterf(gl.GL_TEXTURE_2D,gl.GL_TEXTURE_MAG_FILTER,gl.GL_NEAREST)
#         return pyglet.graphics.TextureGroup(tex)

#     def __init__(self):

#         self.top = self.get_tex('grass_top.png')
#         self.side = self.get_tex('grass_side.png')
#         self.bottom = self.get_tex('dirt.png')

#         self.batch = pyglet.graphics.Batch()

#         tex_coords = ('t2f',(0,0, 1,0, 1,1, 0,1, ))

#         x,y,z = 0,0,-1
#         X,Y,Z = x+1,y+1,z+1

#         self.batch.add(4,gl.GL_QUADS,self.side,('v3f',(x,y,z, x,y,Z, x,Y,Z, x,Y,z, )),tex_coords)
#         self.batch.add(4,gl.GL_QUADS,self.side,('v3f',(X,y,Z, X,y,z, X,Y,z, X,Y,Z, )),tex_coords)
#         self.batch.add(4,gl.GL_QUADS,self.bottom,('v3f',(x,y,z, X,y,z, X,y,Z, x,y,Z, )),tex_coords)
#         self.batch.add(4,gl.GL_QUADS,self.top,('v3f',(x,Y,Z, X,Y,Z, X,Y,z, x,Y,z, )),tex_coords)
#         self.batch.add(4,gl.GL_QUADS,self.side,('v3f',(X,y,z, x,y,z, x,Y,z, X,Y,z, )),tex_coords)
#         self.batch.add(4,gl.GL_QUADS,self.side,('v3f',(x,y,Z, X,y,Z, X,Y,Z, x,Y,Z, )),tex_coords)


#     def draw(self):
#         self.batch.draw()

class MyApp(pyglet.window.Window):
    
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

        # Get window size
        self.width, self.height = self.get_size()
        
        # Create imgui context
        imgui.create_context()
        self.impl = create_renderer(self)

        # Get gui instance
        self.guiMenu = MenuGUI()

        # Skeleton instance
        self.skeleton = Skeleton()

        # Init OpenGL
        self.openGLInit()

        self.ViewRot = 0

    def openGLInit(self):
        gl.glClearColor(0.0, 0.0, 0.0, 0.0)
        gl.glClearDepth(1.0) 
        gl.glDepthFunc(gl.GL_LESS)
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glShadeModel(gl.GL_SMOOTH)
        
        
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.gluPerspective(70, float(self.width)/float(self.height), 0.05, 1000)
        gl.glMatrixMode(gl.GL_MODELVIEW)

    def openGLViewInit(self):
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.gluPerspective(70, self.width/self.height, 0.05, 1000);
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()

        # gl.glEnable(gl.GL_LIGHTING)
        # gl.glLightfv(gl.GL_LIGHT0, gl.GL_AMBIENT, (gl.GLfloat*4)(1,1,1,1))
        # gl.glLightfv(gl.GL_LIGHT0, gl.GL_DIFFUSE, (gl.GLfloat*4)(1,1,1,1))
        # gl.glEnable(gl.GL_LIGHT0)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if buttons == 1:
            self.ViewRot += dx

    def on_draw(self):
        self.clear()
        self.openGLViewInit()
        
        # gl.glPushMatrix()
        gl.glTranslatef(0, 0, -500)
        gl.glRotatef(0, 1.0, 0.0, 0.0)
        gl.glRotatef(self.ViewRot, 0.0, 1.0, 0.0)
        gl.glRotatef(0, 0.0, 0.0, 1.0)
        
        

        self.skeleton.draw()
        # self.model.draw()
        # gl.glPopMatrix()

        # UI
        imgui.new_frame()

        self.guiMenu.Build()
        imgui.render()
        self.impl.render(imgui.get_draw_data())
        
        imgui.end_frame()

    def run(self):
        pyglet.app.run()


if __name__ == "__main__":
    app = MyApp(width=1280, height=720, caption='Test', resizable=False)
    app.run()