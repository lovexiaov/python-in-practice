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
import tempfile
try:
    import cyImage as Image
except ImportError:
    import Image


YELLOW, CYAN, BLUE, RED, BLACK = (Image.color_for_name(color)
    for color in ("yellow", "cyan", "blue", "red", "black"))


def main():
    filename = os.path.join(tempfile.gettempdir(), "image.xpm")
    image = Image.Image(300, 60)
    draw_and_save_image(image, filename)

    filename = os.path.join(tempfile.gettempdir(), "proxy.xpm")
    image = ImageProxy(Image.Image, 300, 60)
    draw_and_save_image(image, filename)


def draw_and_save_image(image, filename):
    image.rectangle(0, 0, 299, 59, fill=YELLOW)
    image.ellipse(0, 0, 299, 59, fill=CYAN)
    image.ellipse(60, 20, 120, 40, BLUE, RED)
    image.ellipse(180, 20, 240, 40, BLUE, RED)
    image.rectangle(180, 32, 240, 40, fill=CYAN)
    assert image.size == (300, 60) # force the image to be created
    assert image.width == 300 and image.height == 60
    image.line(181, 32, 239, 32, BLUE)
    image.line(140, 50, 160, 50, BLACK)
    image.save(filename)
    print("saved", filename)


class ImageProxy:

    def __init__(self, ImageClass, width=None, height=None, filename=None):
        assert (width is not None and height is not None) or \
                filename is not None
        self.Image = ImageClass
        self.__image = None
        self.commands = []
        if filename is not None:
            self.load(filename)
        else:
            self.commands = [(self.Image, width, height)]


    @property
    def image(self):
        if self.__image is None:
            command = self.commands.pop(0)
            function, *args = command
            self.__image = function(*args)
            for command in self.commands:
                function, *args = command
                function(self.image, *args)
        return self.__image


    def load(self, filename):
        self.__image = None
        self.commands = [(self.Image, None, None, filename)]


    def save(self, filename=None):
        self.image.save(filename)


    def set_pixel(self, x, y, color):
        if self.image is None:
            self.commands.append((self.Image.set_pixel, x, y, color))
        else:
            self.image.set_pixel(x, y, color)


    def line(self, x0, y0, x1, y1, color):
        if self.image is None:
            self.commands.append((self.Image.line, x0, y0, x1, y1, color))
        else:
            self.image.line(x0, y0, x1, y1, color)


    def rectangle(self, x0, y0, x1, y1, outline=None, fill=None):
        if self.image is None:
            self.commands.append((self.Image.rectangle, x0, y0, x1, y1,
                    outline, fill))
        else:
            self.image.rectangle(x0, y0, x1, y1, outline, fill)


    def ellipse(self, x0, y0, x1, y1, outline=None, fill=None):
        if self.image is None:
            self.commands.append((self.Image.ellipse, x0, y0, x1, y1,
                    outline, fill))
        else:
            self.image.ellipse(x0, y0, x1, y1, outline, fill)


    def pixel(self, x, y):
        return self.image.pixel(x, y)


    def subsample(self, stride):
        return self.image.subsample(stride)


    def scale(self, ratio):
        return self.image.scale(ratio)


    @property
    def size(self):
        return self.image.size


    @property
    def width(self):
        return self.image.width


    @property
    def height(self):
        return self.image.height


if __name__ == "__main__":
    main()
