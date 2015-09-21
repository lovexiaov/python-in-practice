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

import sys
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

SIZE = 400
ANGLE_INCREMENT = 5


def main():
    glutInit(sys.argv)
    glutInitWindowSize(SIZE, SIZE)
    window = glutCreateWindow(b"Cylinder (PyOpenGL)")
    glutInitDisplayString(b"double=1 rgb=1 samples=4 depth=16")
    scene = Scene(window)
    glutDisplayFunc(scene.display)
    glutReshapeFunc(scene.reshape)
    glutKeyboardFunc(scene.keyboard)
    glutSpecialFunc(scene.special)
    glutMainLoop()


def vector(*args):
    return (GLfloat * len(args))(*args)


class Scene:

    def __init__(self, window):
        self.window = window
        self.xAngle = 0
        self.yAngle = 0
        self._initialize_gl()


    def _initialize_gl(self):
        glClearColor(195/255, 248/255, 248/255, 1)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_POINT_SMOOTH)
        glHint(GL_POINT_SMOOTH_HINT, GL_NICEST)
        glEnable(GL_LINE_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        glEnable(GL_COLOR_MATERIAL)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glLightfv(GL_LIGHT0, GL_POSITION, vector(0.5, 0.5, 1, 0))
        glLightfv(GL_LIGHT0, GL_SPECULAR, vector(0.5, 0.5, 1, 1))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, vector(1, 1, 1, 1))
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 50)
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, vector(1, 1, 1, 1))
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)


    def display(self):
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
        glBegin(GL_LINES)
        glColor3f(1, 0, 0)      # x-axis
        glVertex3f(-1000, 0, 0)
        glVertex3f(1000, 0, 0)
        glColor3f(0, 0, 1)      # y-axis
        glVertex3f(0, -1000, 0)
        glVertex3f(0, 1000, 0)
        glColor3f(1, 0, 1)      # z-axis
        glVertex3f(0, 0, -1000)
        glVertex3f(0, 0, 1000)
        glEnd()


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


    def reshape(self, width, height):
        width = width if width else 1
        height = height if height else 1
        aspectRatio = width / height
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(35.0, aspectRatio, 1.0, 1000.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()


    def keyboard(self, key, x, y):
        if key == b"\x1B": # Escape
            glutDestroyWindow(self.window)


    def special(self, key, x, y):
        if key == GLUT_KEY_UP:
            self.xAngle -= ANGLE_INCREMENT
        elif key == GLUT_KEY_DOWN:
            self.xAngle += ANGLE_INCREMENT
        elif key == GLUT_KEY_LEFT:
            self.yAngle -= ANGLE_INCREMENT
        elif key == GLUT_KEY_RIGHT:
            self.yAngle += ANGLE_INCREMENT
        glutPostRedisplay()


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--regression":
        print("Loaded OK")
    else:
        main()
