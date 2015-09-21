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

import numpy


MAX_COMPONENT = 0xFF


def scale(pixels, width, height, ratio):
    """returns a smoothly scaled copy of this image

    ratio is how much to scale by, e.g., 0.75 means reduce width and
    height to ¾ their original size, 0.5 to half (making the image ¼
    of the original size), and so on.

    Scaling is slow but produces good results even for text;
    subsample() is faster.
    """
    assert 0 < ratio < 1
    rows = round(height * ratio)
    columns = round(width * ratio)
    newPixels = numpy.zeros(rows * columns, dtype=numpy.uint32)
    yStep = height / rows
    xStep = width / columns
    index = 0
    for row in range(rows):
        y0 = round(row * yStep)
        y1 = round(y0 + yStep)
        for column in range(columns):
            x0 = round(column * xStep)
            x1 = round(x0 + xStep)
            newPixels[index] = _mean(pixels, width, height, x0, y0, x1, y1)
            index += 1
    return columns, newPixels


def _mean(pixels, width, height, x0, y0, x1, y1):
    alphaTotal, redTotal, greenTotal, blueTotal, count = 0, 0, 0, 0, 0
    for y in range(y0, y1):
        if y >= height:
            break
        offset = y * width # Compute this per row rather than per pixel
        for x in range(x0, x1):
            if x >= width:
                break
            a, r, g, b = _argb_for_color(pixels[offset + x])
            alphaTotal += a
            redTotal += r
            greenTotal += g
            blueTotal += b
            count += 1
    a = int(round(alphaTotal / count))
    r = int(round(redTotal / count))
    g = int(round(greenTotal / count))
    b = int(round(blueTotal / count))
    return _color_for_argb(a, r, g, b)


# color is always a numpy.uint32
def _argb_for_color(color):
    color = int(color)
    return ((color >> 24) & MAX_COMPONENT, (color >> 16) & MAX_COMPONENT,
            (color >> 8) & MAX_COMPONENT, (color & MAX_COMPONENT))


# We don't need to check that the values are in range because they come
# from a numpy.uint32
def _color_for_argb(a, r, g, b):
    return (((a & MAX_COMPONENT) << 24) | ((r & MAX_COMPONENT) << 16) |
            ((g & MAX_COMPONENT) << 8) | (b & MAX_COMPONENT))
