#!/usr/bin/env python3
# Copyright © 2012-13 Qtrac Ltd. All rights reserved.
# This program or module is free software: you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version. It is provided for
# educational purposes and is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.

import os
import pyglet
from pyglet.gl import *


SIZE = 400
ANGLE_INCREMENT = 5


def main():
    caption = "Cylinder (pyglet)"
    width = height = SIZE
    resizable = True
    try:
        config = Config(sample_buffers=1, samples=4, depth_size=16,
                double_buffer=True)
        window = Window(width, height, caption=caption, config=config,
                resizable=resizable)
    except pyglet.window.NoSuchConfigException:
        window = Window(width, height, caption=caption,
                resizable=resizable)
    path = os.path.realpath(os.path.dirname(__file__))
    icon16 = pyglet.image.load(os.path.join(path, "cylinder_16x16.png"))
    icon32 = pyglet.image.load(os.path.join(path, "cylinder_32x32.png"))
    window.set_icon(icon16, icon32)
    pyglet.app.run()


def vector(*args):
    return (GLfloat * len(args))(*args)


class Window(pyglet.window.Window):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_minimum_size(200, 200)
        self.xAngle = 0
        self.yAngle = 0
        self._initialize_gl()
        self._z_axis_list = pyglet.graphics.vertex_list(2,
                ("v3i", (0, 0, -1000, 0, 0, 1000)),
                ("c3B", (255, 0, 255) * 2)) # one color per vertex


    def _initialize_gl(self):
        glClearColor(195/255, 248/255, 248/255, 1)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_POINT_SMOOTH)
        glHint(GL_POINT_SMOOTH_HINT, GL_NICEST)
        glEnable(GL_LINE_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        glEnable(GL_COLOR_MATERIAL) # 1
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glLightfv(GL_LIGHT0, GL_POSITION, vector(0.5, 0.5, 1, 0))
        glLightfv(GL_LIGHT0, GL_SPECULAR, vector(0.5, 0.5, 1, 1))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, vector(1, 1, 1, 1))
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 50)
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, vector(1, 1, 1, 1))
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE) # 2
        # 1 & 2 mean that we can use glColor*() to color materials


    def on_draw(self):
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glTranslatef(0, 0, -600)
        glRotatef(self.xAngle, 1, 0, 0)
        glRotatef(self.yAngle, 0, 1, 0)
        self._draw_axes()
        self._draw_cylinder()
        glPopMatrix()


    def _draw_axes(self):
        glBegin(GL_LINES)                 # x-axis (traditional-style)
        glColor3f(1, 0, 0)
        glVertex3f(-1000, 0, 0)
        glVertex3f(1000, 0, 0)
        glEnd()
        pyglet.graphics.draw(2, GL_LINES, # y-axis (pyglet-style "live")
                ("v3i", (0, -1000, 0, 0, 1000, 0)),
                ("c3B", (0, 0, 255) * 2))
        self._z_axis_list.draw(GL_LINES)  # z-axis (efficient pyglet-style)


    def _draw_cylinder(self):
        glPushMatrix()
        try:
            glTranslatef(0, 0, -200)
            cylinder = gluNewQuadric()
            gluQuadricNormals(cylinder, GLU_SMOOTH)
            glColor3ub(48, 200, 48)
            gluCylinder(cylinder, 25, 25, 400, 24, 24)
        finally:
            gluDeleteQuadric(cylinder)
        glPopMatrix()


    def on_resize(self, width, height):
        width = width if width else 1
        height = height if height else 1
        aspectRatio = width / height
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(35.0, aspectRatio, 1.0, 1000.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

# Escape is predefined to close the window so no on_key_press() needed
    def on_text_motion(self, motion): # Rotate about the x or y axis
        if motion == pyglet.window.key.MOTION_UP:
            self.xAngle -= ANGLE_INCREMENT
        elif motion == pyglet.window.key.MOTION_DOWN:
            self.xAngle += ANGLE_INCREMENT
        elif motion == pyglet.window.key.MOTION_LEFT:
            self.yAngle -= ANGLE_INCREMENT
        elif motion == pyglet.window.key.MOTION_RIGHT:
            self.yAngle += ANGLE_INCREMENT


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--regression":
        print("Loaded OK")
    else:
        main()
