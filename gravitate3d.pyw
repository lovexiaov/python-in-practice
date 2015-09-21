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

import collections
import heapq
import itertools
import math
import os
import random
import pyglet
from pyglet.gl import *


SIZE = 475
BOARD_SIZE = 4 # Must be > 1.
ANGLE_INCREMENT = 5
RADIUS_FACTOR = 10
DELAY = 0.5 # seconds
COLORS = [
        (255,   0,   0), # red
        (  0, 255,   0), # green
        (  0, 255, 255), # blue
        (  0, 255, 255), # cyan
        (255,   0, 255), # magenta
        (255, 255,   0), # yellow
        (160, 160, 164), # gray
        (165,  42,  42), # brown
        ]
MIN_COLORS = 4
MAX_COLORS = min(len(COLORS), MIN_COLORS)
SELECTING_ENUMS = (GL_ALPHA_TEST, GL_DEPTH_TEST, GL_DITHER,
        GL_LIGHT0, GL_LIGHTING, GL_MULTISAMPLE, GL_TEXTURE_1D,
        GL_TEXTURE_2D, GL_TEXTURE_3D)
# Can't enable/disable GL_BLEND because it interacts badly with pyglet
# text labels


def main():
    caption = "Gravitate 3D"
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
    icon16 = pyglet.image.load(os.path.join(path, "gravitate_16x16.png"))
    icon32 = pyglet.image.load(os.path.join(path, "gravitate_32x32.png"))
    window.set_icon(icon16, icon32)
    pyglet.app.run()


def vector(*args):
    return (GLfloat * len(args))(*args)


class SceneObject:

    __SelectColor = 0

    def __init__(self, color):
        self.color = color
        SceneObject.__SelectColor += 1
        self.selectColor = SceneObject.__SelectColor


    @property
    def selectColor(self):
        return self.__selectColor


    @selectColor.setter
    def selectColor(self, value):
        if value is None or isinstance(value, tuple):
            self.__selectColor = value
        else:
            parts = []
            for _ in range(3):
                value, y = divmod(value, 256)
                parts.append(y)
            self.__selectColor = tuple(parts)


    def __str__(self):
        return "{}:{}".format(self.color, self.selectColor)


class Selecting:

    def __init__(self, selecting):
        self.selecting = selecting


    def __enter__(self):
        if self.selecting:
            for enum in SELECTING_ENUMS:
                glDisable(enum)
            glShadeModel(GL_FLAT)


    def __exit__(self, exc_type, exc_value, traceback):
        if self.selecting:
            for enum in SELECTING_ENUMS:
                glEnable(enum)
            glShadeModel(GL_SMOOTH)


class Window(pyglet.window.Window):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_minimum_size(200, 200)
        self.xAngle = 10
        self.yAngle = -15
        self.minColors = MIN_COLORS
        self.maxColors = MAX_COLORS
        self.delay = DELAY
        self.board_size = BOARD_SIZE
        self._initialize_gl()
        self.label = pyglet.text.Label("", bold=True, font_size=11,
                anchor_x="center")
        self._new_game()


    def _initialize_gl(self):
        glClearColor(0.9, 0.9, 0.9, 1) # lightgray
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_MULTISAMPLE)
        glEnable(GL_CULL_FACE)
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


    def _new_game(self):
        self.score = 0
        self.gameOver = False
        self.selected = None
        self.selecting = False
        self.label.text = ("Click to Select • Click again to Delete • "
                "Arrows to Rotate")
        random.shuffle(COLORS)
        colors = COLORS[:self.maxColors]
        self.board = []
        for x in range(self.board_size):
            self.board.append([])
            for y in range(self.board_size):
                self.board[x].append([])
                for z in range(self.board_size):
                    color = random.choice(colors)
                    self.board[x][y].append(SceneObject(color))


    def on_draw(self):
        diameter = min(self.width, self.height) / (self.board_size * 1.5)
        radius = diameter / 2
        offset = radius - ((diameter * self.board_size) / 2)
        radius = max(RADIUS_FACTOR, radius - RADIUS_FACTOR)
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glRotatef(self.xAngle, 1, 0, 0)
        glRotatef(self.yAngle, 0, 1, 0)
        with Selecting(self.selecting):
            self._draw_spheres(offset, radius, diameter)
        glPopMatrix()
        if self.label.text:
            self.label.y = (-self.height // 2) + 10
            self.label.draw()


    def _draw_spheres(self, offset, radius, diameter):
        try:
            sphere = gluNewQuadric()
            gluQuadricNormals(sphere, GLU_SMOOTH)
            for x, y, z in itertools.product(range(self.board_size),
                    repeat=3):
                sceneObject = self.board[x][y][z]
                if self.selecting:
                    color = sceneObject.selectColor
                else:
                    color = sceneObject.color
                if color is not None:
                    self._draw_sphere(sphere, x, y, z, offset, radius,
                            diameter, color)
        finally:
            gluDeleteQuadric(sphere)


    def _draw_sphere(self, sphere, x, y, z, offset, radius, diameter,
            color):
        if self.selected == (x, y, z):
            radius += RADIUS_FACTOR
        glPushMatrix()
        x = offset + (x * diameter)
        y = offset + (y * diameter)
        z = offset + (z * diameter)
        glTranslatef(x, y, z)
        glColor3ub(*color)
        gluSphere(sphere, radius, 24, 24)
        glPopMatrix()


    def on_resize(self, width, height):
        size = min(self.width, self.height) / 2
        height = height if height else 1
        width = width if width else 1
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        if width <= height:
            glOrtho(-size, size, -size * height / width,
                    size * height / width, -size, size)
        else:
            glOrtho(-size * width / height, size * width / height,
                    -size, size, -size, size)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()


    def on_key_press(self, symbol, modifiers):
        if (symbol == pyglet.window.key.ESCAPE or
            ((modifiers & pyglet.window.key.MOD_CTRL or
              modifiers & pyglet.window.key.MOD_COMMAND) and
              symbol == pyglet.window.key.Q)):
            pyglet.app.exit()
        elif ((modifiers & pyglet.window.key.MOD_CTRL or
               modifiers & pyglet.window.key.MOD_COMMAND) and
              symbol == pyglet.window.key.N):
            self._new_game()
        elif (symbol in {pyglet.window.key.DELETE, pyglet.window.key.SPACE,
                        pyglet.window.key.BACKSPACE} and
              self.selected is not None):
            self._delete()


    def _delete(self):
        x, y, z = self.selected
        self.selected = None
        color = self.board[x][y][z].color
        if not self._is_legal(x, y, z, color):
            return
        self._delete_adjoining(x, y, z, color)
        self.label.text = "{:,}".format(self.score)
        pyglet.clock.schedule_once(self._close_up, self.delay)


    def _is_legal(self, x, y, z, color):
        """A legal click is on a colored sphere that is adjacent to
        another sphere of the same color."""
        if z > 0 and self.board[x][y][z - 1].color == color:
            return True
        if (z + 1 < self.board_size and
            self.board[x][y][z + 1].color == color):
            return True
        if y > 0 and self.board[x][y - 1][z].color == color:
            return True
        if (y + 1 < self.board_size and
            self.board[x][y + 1][z].color == color):
            return True
        if x > 0 and self.board[x - 1][y][z].color == color:
            return True
        if (x + 1 < self.board_size and
            self.board[x + 1][y][z].color == color):
            return True
        return False


    def _delete_adjoining(self, x, y, z, color):
        adjoining = set()
        self._populate_adjoining(x, y, z, color, adjoining)
        self.score += len(adjoining) ** (self.maxColors - 2)
        for x, y, z in adjoining:
            sceneObject = self.board[x][y][z]
            sceneObject.color = sceneObject.selectColor = None


    def _populate_adjoining(self, x, y, z, color, adjoining):
        if not ((0 <= x < self.board_size) and
                (0 <= y < self.board_size) and
                (0 <= z < self.board_size)):
            return # Fallen off an edge
        if ((x, y, z) in adjoining or
            self.board[x][y][z].color != color):
            return # Color doesn't match or already done
        adjoining.add((x, y, z))
        self._populate_adjoining(x - 1, y, z, color, adjoining)
        self._populate_adjoining(x + 1, y, z, color, adjoining)
        self._populate_adjoining(x, y - 1, z, color, adjoining)
        self._populate_adjoining(x, y + 1, z, color, adjoining)
        self._populate_adjoining(x, y, z - 1, color, adjoining)
        self._populate_adjoining(x, y, z + 1, color, adjoining)


    def _close_up(self, seconds):
        self._move()
        self._check_game_over()


    def _move(self):
        moved = True
        while moved:
            moved = False
            for x, y, z in itertools.product(range(self.board_size),
                    repeat=3):
                if self.board[x][y][z].color is not None:
                    if self._move_if_possible(x, y, z):
                        moved = True
                        break


    def _move_if_possible(self, x, y, z):
        empty_neighbours = self._empty_neighbours(x, y, z)
        if empty_neighbours:
            move, nx, ny, nz = self._nearest_to_middle(x, y, z,
                    empty_neighbours)
            if move:
                new = self.board[nx][ny][nz]
                old = self.board[x][y][z]
                new.color = old.color
                new.selectColor = old.selectColor
                old.color = old.selectColor = None
                return True
        return False


    def _empty_neighbours(self, x, y, z):
        neighbours = set()
        for nx, ny, nz in ((x - 1, y, z), (x + 1, y, z), (x, y - 1, z),
                (x, y + 1, z), (x, y, z - 1), (x, y, z + 1)):
            if (0 <= nx < self.board_size and
                0 <= ny < self.board_size and
                0 <= nz < self.board_size and
                self.board[nx][ny][nz].color is None):
                neighbours.add((nx, ny, nz))
        return neighbours


    def _nearest_to_middle(self, x, y, z, empty_neighbours):
        mid = self.board_size // 2
        Δold = math.sqrt(((x - mid) ** 2) + ((y - mid) ** 2) +
                ((z - mid) ** 2))
        heap = []
        for nx, ny, nz in empty_neighbours:
            if self._is_square(nx, ny, nz):
                Δnew = math.sqrt(((nx - mid) ** 2) + ((ny - mid) ** 2) +
                        ((nz - mid) ** 2))
                heapq.heappush(heap, (Δnew, nx, ny, nz))
        Δnew, nx, ny, nz = heap[0]
        return (True, nx, ny, nz) if Δold > Δnew else (False, x, y, z)


    def _is_square(self, x, y, z):
        if z > 0 and self.board[x][y][z - 1].color is not None:
            return True
        if (z + 1 < self.board_size and
            self.board[x][y][z + 1].color is not None):
            return True
        if y > 0 and self.board[x][y - 1][z].color is not None:
            return True
        if (y + 1 < self.board_size and
            self.board[x][y + 1][z].color is not None):
            return True
        if x > 0 and self.board[x - 1][y][z].color is not None:
            return True
        if (x + 1 < self.board_size and
            self.board[x + 1][y][z].color is not None):
            return True
        return False


    def _check_game_over(self):
        text = "{} \u2014 Click for New Game • Esc to Quit"
        userWon, canMove = self._check_tiles()
        if userWon:
            self.label.text = text.format("You Won! \u2014 {:,}".format(
                    self.score))
            self.gameOver = True
        elif not canMove:
            self.label.text = text.format("Game Over")
            self.gameOver = True


    def _check_tiles(self):
        countForColor = collections.defaultdict(int)
        userWon = True 
        canMove = False
        for x, y, z in itertools.product(range(self.board_size),
                repeat=3):
                color = self.board[x][y][z].color
                if color is not None:
                    countForColor[color] += 1
                    userWon = False
                    if self._is_legal(x, y, z, color): # We _can_ move
                        canMove = True
        if 1 in countForColor.values():
            canMove = False
        return userWon, canMove


    def on_text_motion(self, motion): # Rotate about the x or y axis
        if motion == pyglet.window.key.MOTION_UP:
            self.xAngle -= ANGLE_INCREMENT
        elif motion == pyglet.window.key.MOTION_DOWN:
            self.xAngle += ANGLE_INCREMENT
        elif motion == pyglet.window.key.MOTION_LEFT:
            self.yAngle -= ANGLE_INCREMENT
        elif motion == pyglet.window.key.MOTION_RIGHT:
            self.yAngle += ANGLE_INCREMENT


    def on_mouse_press(self, x, y, button, modifiers):
        if self.gameOver:
            self._new_game()
            return
        self.selecting = True
        self.on_draw()
        self.selecting = False
        selectColor = (GLubyte * 3)()
        glReadPixels(x, y, 1, 1, GL_RGB, GL_UNSIGNED_BYTE, selectColor)
        selectColor = tuple([component for component in selectColor])
        self._clicked(selectColor)
        # for systems whose coords have y top-left do:
        #   viewport = (GLint * 4)()
        #   glGetIntegerv(GL_VIEWPORT, viewport)
        # and in the glReadPixels() call, replace y with
        #   viewport[3] - y


    def _clicked(self, selectColor):
        for x, y, z in itertools.product(range(self.board_size), repeat=3):
            if selectColor == self.board[x][y][z].selectColor:
                if (x, y, z) == self.selected:
                    self._delete() # Second click deletes
                else:
                    self.selected = (x, y, z)
                return


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--regression":
        print("Loaded OK")
    else:
        main()
