#!/usr/bin/env python3
# Copyright © 2012 Qtrac Ltd. All rights reserved.
# This program or module is free software: you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version. It is provided for
# educational purposes and is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.

"""
A framework for image processing.

Images are stored in instances of the Image class. The data is stored as
ARGB colors in a numpy.array() with dtype uint32.

Rather than creating Images directly, use one of the construction
functions, create(), from_file(), or from_data().

For sophisticated image processing install numpy _and_ scipy and use
the scipy image processing functions.
"""

import sys
from libc.math cimport round
from libc.stdlib cimport abs
import numpy
cimport numpy
cimport cython
import cyImage.cyImage.Xbm as Xbm
import cyImage.cyImage.Xpm as Xpm
import cyImage.cyImage._Scale as Scale
from cyImage.Globals import *


_DTYPE = numpy.uint32 # See: http://docs.cython.org/src/tutorial/numpy.html
ctypedef numpy.uint32_t _DTYPE_t


class Image:

    def __init__(self, width=None, height=None, filename=None,
            background=None, pixels=None):
        """Create Images using one of the convenience construction
        functions: from_file(), create(), and from_data()
        
        Although .width and .height are public they should not be
        changed except in load() methods."""
        assert (width is not None and (height is not None or
                pixels is not None) or (filename is not None))
        if filename is not None: # From file
            self.load(filename)
        elif pixels is not None: # From data
            self.width = width
            self.height = len(pixels) // width
            self.filename = filename
            self.meta = {}
            self.pixels = pixels
        else: # Empty
            self.width = width
            self.height = height
            self.filename = filename
            self.meta = {}
            self.pixels = create_array(width, height, background)


    @classmethod
    def from_file(Class, filename):
        return Class(filename=filename)


    @classmethod
    def create(Class, width, height, background=None):
        return Class(width=width, height=height, background=background)


    @classmethod
    def from_data(Class, width, pixels):
        return Class(width=width, pixels=pixels)


    def load(self, filename):
        """loads the image from the file called filename; the format is
        determined by the file suffix"""
        suffix = os.path.splitext(filename)[1].lower()
        load = _loadForSuffix.get(suffix)
        if load is not None:
            self.width = self.height = None
            self.meta = {}
            load(self, filename)
            self.filename = filename
        else:
            raise Error("cannot load files of {} format".format(suffix))


    def save(self, filename=None):
        """saves the image to a file called filename; the format is
        determined by the file suffix"""
        filename = filename if filename is not None else self.filename
        if not filename:
            raise Error("can't save without a filename")
        suffix = os.path.splitext(filename)[1].lower()
        save = _saveForSuffix.get(suffix)
        if save is not None:
            save(self, filename)
            self.filename = filename
        else:
            raise Error("cannot save files of {} format".format(suffix))


    def pixel(self, int x, int y):
        """returns the color at the given pixel as an ARGB int; x and y
        must be in range"""
        return self.pixels[(y * self.width) + x]


    def set_pixel(self, int x, int y, _DTYPE_t color):
        """sets the given pixel to the given color; x and y must be in
        range; color must be an ARGB int"""
        self.pixels[(y * self.width) + x] = color


    # Bresenham's mid-point line scanning algorithm from 
    # http://en.wikipedia.org/wiki/Bresenham%27s_line_algorithm 
    def line(self, int x0, int y0, int x1, int y1, _DTYPE_t color):
        """draws the line in the given color; the coordinates must be in
        range; the color must be an ARGB int"""
        cdef int dx = abs(x1 - x0)
        cdef int dy = abs(y1 - y0)
        cdef int xInc = 1 if x0 < x1 else -1
        cdef int yInc = 1 if y0 < y1 else -1
        cdef int err = dx - dy
        cdef int err2
        while True:
            self.set_pixel(x0, y0, color)
            if x0 == x1 and y0 == y1:
                break
            err2 = 2 * err
            if err2 > -dy:
                err -= dy
                x0 += xInc
            if err2 < dx:
                err += dx
                y0 += yInc


    def rectangle(self, int x0, int y0, int x1, int y1, outline=None,
            fill=None):
        """draws a rectangle outline if outline is not None and fill is
        None, or a filled rectangle if outline is None and fill is not
        None, or an outlined and filled rectangle if both are not None;
        the coordinates must be in range; the outline and fill colors
        must be ARGB ints"""
        assert outline is not None or fill is not None
        if fill is not None:
            if y0 > y1:
                y0, y1 = y1, y0
            if outline is not None: # no point drawing over the outline
                x0 += 1
                x1 -= 1
                y0 += 1
                y1 -= 1
            for y in range(y0, y1 + 1):
                self.line(x0, y, x1, y, fill)
        if outline is not None:
            self.line(x0, y0, x1, y0, outline)
            self.line(x1, y0, x1, y1, outline)
            self.line(x1, y1, x0, y1, outline)
            self.line(x0, y1, x0, y0, outline)


    def ellipse(self, int x0, int y0, int x1, int y1, outline=None,
            fill=None):
        """draws an ellipse outline if outline is not None and fill is
        None, or a filledn ellipse if outline is None and fill is not
        None, or an outlined and filledn ellipse if both are not None;
        the coordinates must be in range; the outline and fill colors
        must be ARGB ints"""
        assert outline is not None or fill is not None
        if x0 > x1:
            x0, x1 = x1, x0
        if y0 > y1:
            y0, y1 = y1, y0
        cdef int width = x1 - x0
        cdef int height = y1 - y0
        cdef int halfWidth, halfHeight, midX, midY
        cdef double dx, dy, a, b, a2, b2, p
        if fill is not None:
            # Algorithm based on
            # http://stackoverflow.com/questions/10322341/
            # simple-algorithm-for-drawing-filled-ellipse-in-c-c
            halfWidth = width // 2
            halfHeight = height // 2
            midX = x0 + halfWidth
            midY = y0 + halfHeight
            for y in range(-halfHeight, halfHeight + 1):
                for x in range(-halfWidth, halfWidth + 1):
                    dx =  x / halfWidth
                    dy =  y / halfHeight
                    if ((dx * dx) + (dy * dy)) <= 1:
                        self.set_pixel(<int>round(midX + x),
                                       <int>round(midY + y), fill)
        if outline is not None:
            # Midpoint ellipse algorithm from "Computer Graphics
            # Principles and Practice".
            if x1 > x0:
                midX = ((x1 - x0) // 2) + x0
            else:
                midX = ((x0 - x1) // 2) + x1
            if y1 > y0:
                midY = ((y1 - y0) // 2) + y0
            else:
                midY = ((y0 - y1) // 2) + y1

            def ellipse_point(dx, dy):
                # dx is always an int; dy is always a float
                self.set_pixel(midX + dx, <int>round(midY + dy), outline)
                self.set_pixel(midX - dx, <int>round(midY - dy), outline)
                self.set_pixel(midX + dx, <int>round(midY - dy), outline)
                self.set_pixel(midX - dx, <int>round(midY + dy), outline)

            a = abs(x1 - x0) / 2
            b = abs(y1 - y0) / 2
            a2 = a ** 2
            b2 = b ** 2
            dx = 0
            dy = b
            p = b2 - (a2 * b) + (a2 / 4)
            ellipse_point(dx, dy)
            while (a2 * (dy - 0.5)) > (b2 * (dx + 1)):
                if p < 0:
                    p += b2 * ((2 * dx) + 3)
                    dx += 1
                else:
                    p += (b2 * ((2 * dx) + 3)) + (a2 * ((-2 * dy) + 2))
                    dx += 1
                    dy -= 1
                ellipse_point(dx, dy)
            p = ((b2 * ((dx + 0.5) ** 2)) + (a2 * ((dy - 1) ** 2)) -
                 (a2 * b2))
            while dy > 0:
                if p < 0:
                    p += (b2 * ((2 * dx) + 2)) + (a2 * ((-2 * dy) + 3))
                    dx += 1
                    dy -= 1
                else:
                    p += a2 * ((-2 * dy) + 3)
                    dy -= 1
                ellipse_point(dx, dy)


    def subsample(self, int stride):
        """returns a subsampled copy of this image.
        
        stride should be at least 2 but not too big; a stride of 2
        produces an image ½ the width and height (¼ the original size),
        a stride of 3 produces an image ⅓ the width and height, and so on.

        Subsampling produces good results for photographs: but poor
        results for text for which scale() is best.
        """
        assert (2 <= stride <= min(self.width // 2, self.height // 2) and
                isinstance(stride, int))
        cdef _DTYPE_t[:] pixels = create_array(self.width // stride,
                self.height // stride)
        cdef int offset
        cdef int index = 0
        cdef int height = self.height - (self.height % stride)
        cdef int width = self.width - (self.width % stride)
        for y in range(0, height, stride):
            offset = y * self.width
            for x in range(0, width, stride):
                if index == len(pixels):
                    break
                pixels[index] = self.pixels[offset + x]
                index += 1
        return self.from_data(self.width // stride, pixels)


    def scale(self, double ratio):
        """returns a smoothly scaled copy of this image

        ratio is how much to scale by, e.g., 0.75 means reduce width and
        height to ¾ their original size, 0.5 to half (making the image ¼
        of the original size), and so on.

        Scaling produces good results even for text.
        """
        assert 0 < ratio < 1
        cdef int columns
        cdef _DTYPE_t[:] pixels
        columns, pixels = Scale.scale(self.pixels, self.width, self.height,
                ratio)
        return self.from_data(columns, pixels)


    def __str__(self):
        width = self.width or 0
        height = self.height or 0
        s = "{}x{}".format(width, height)
        if self.filename:
            s += " " + self.filename
        return s


    @property
    def size(self):
        """Convenience method to return the image's size"""
        return self.width, self.height


    def _dump(self, file=sys.stdout, alpha=True):
        assert (self.width * self.height) == len(self.pixels)
        for y in range(self.height):
            for x in range(self.width):
                color = self.pixel(x, y)
                if alpha:
                    file.write("{:08X} ".format(color))
                else:
                    file.write("{:06X} ".format(color & CLEAR_ALPHA))
            file.write("\n")
        file.write("\n")


_loadForSuffix = {".xbm": Xbm.load, ".xpm": Xpm.load,}
_saveForSuffix = {".xbm": Xbm.save, ".xpm": Xpm.save,}
