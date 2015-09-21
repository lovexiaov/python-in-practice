#!/usr/bin/env python3
# cython: language_level=3
# Copyright © 2012 Qtrac Ltd. All rights reserved.
# This program or module is free software: you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version. It is provided for
# educational purposes and is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.

# Throughout, pixels and newPixels are really of type
# numpy.ndarray[_DTYPE_t] but using a memory view is almost 4x faster

from libc.math cimport round
import numpy
cimport numpy
cimport cython


# See: http://docs.cython.org/src/tutorial/numpy.html
_DTYPE = numpy.uint32
ctypedef numpy.uint32_t _DTYPE_t

cdef struct Argb:
    int alpha
    int red
    int green
    int blue

DEF MAX_COMPONENT = 0xFF


@cython.boundscheck(False)
def scale(_DTYPE_t[:] pixels, int width, int height, double ratio):
    """returns a smoothly scaled copy of this image

    ratio is how much to scale by, e.g., 0.75 means reduce width and
    height to ¾ their original size, 0.5 to half (making the image ¼
    of the original size), and so on.
    """
    assert 0 < ratio < 1
    cdef int rows = <int>round(height * ratio)
    cdef int columns = <int>round(width * ratio)
    cdef _DTYPE_t[:] newPixels = numpy.zeros(rows * columns, dtype=_DTYPE)
    cdef double yStep = height / rows
    cdef double xStep = width / columns
    cdef int index = 0
    cdef int row, column, y0, y1, x0, x1
    for row in range(rows):
        y0 = <int>round(row * yStep)
        y1 = <int>round(y0 + yStep)
        for column in range(columns):
            x0 = <int>round(column * xStep)
            x1 = <int>round(x0 + xStep)
            newPixels[index] = _mean(pixels, width, height, x0, y0, x1, y1)
            index += 1
    return columns, newPixels


@cython.cdivision(True)
@cython.boundscheck(False)
cdef _DTYPE_t _mean(_DTYPE_t[:] pixels, int width, int height, int x0,
        int y0, int x1, int y1):
    cdef int alphaTotal = 0
    cdef int redTotal = 0
    cdef int greenTotal = 0
    cdef int blueTotal = 0
    cdef int count = 0
    cdef int y, x, offset
    cdef Argb argb
    for y in range(y0, y1):
        if y >= height:
            break
        offset = y * width
        for x in range(x0, x1):
            if x >= width:
                break
            argb = _argb_for_color(pixels[offset + x])
            alphaTotal += argb.alpha
            redTotal += argb.red
            greenTotal += argb.green
            blueTotal += argb.blue
            count += 1
    cdef int a = <int>round(alphaTotal / count)
    cdef int r = <int>round(redTotal / count)
    cdef int g = <int>round(greenTotal / count)
    cdef int b = <int>round(blueTotal / count)
    return _color_for_argb(a, r, g, b)


cdef inline Argb _argb_for_color(_DTYPE_t color):
    """returns an ARGB quadruple for a color specified as a numpy.uint32"""
    return Argb((color >> 24) & MAX_COMPONENT,
            (color >> 16) & MAX_COMPONENT, (color >> 8) & MAX_COMPONENT,
            (color & MAX_COMPONENT))


cdef inline _DTYPE_t _color_for_argb(int a, int r, int g, int b):
    """returns a numpy.uint32 representing the given ARGB values"""
    return (((a & MAX_COMPONENT) << 24) | ((r & MAX_COMPONENT) << 16) |
            ((g & MAX_COMPONENT) << 8) | (b & MAX_COMPONENT))
