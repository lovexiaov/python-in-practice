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

"""
    import Image
Use the above rather than importing this module explicitly. This works
because Image imports any modules it finds (to allow for new image
processing modules to be added post-facto).

This Image plugin module can read and write .png files if PyPNG is
installed. See http://pypi.python.org/pypi/pypng
"""

import os
import sys
import warnings
import Image
# These are due to issues with the png module
if sys.version_info[:2] >= (3, 2):
    warnings.simplefilter("ignore", ResourceWarning)
warnings.simplefilter("ignore", DeprecationWarning)

try:
    import png
except ImportError:
    png = None


def can_load(filename):
    """Returns 100 if this module can do a lossless load, 0 if it can't
    load the file, and something inbetween if it can do a lossy load."""
    return (80 if png is not None and
            os.path.splitext(filename)[1].lower() == ".png" else 0)


def can_save(filename):
    """Returns 100 if this module can do a lossless save, 0 if it can't
    save the file, and something inbetween if it can do a lossy save."""
    return can_load(filename)


if png is not None:
    def load(image, filename):
        """load a PNG file"""
        reader = png.Reader(filename=filename)
        image.width, image.height, pixels, _ = reader.asRGBA8()
        image.pixels = Image.create_array(image.width, image.height)
        index = 0
        for row in pixels:
            for r, g, b, α in zip(row[::4], row[1::4], row[2::4], row[3::4]):
                image.pixels[index] = Image.color_for_argb(α, r, g, b)
                index += 1


    def save(image, filename):
        """save a PNG file"""
        with open(filename, "wb") as file:
            writer = png.Writer(width=image.width, height=image.height,
                    alpha=True)
            writer.write_array(file, list(_rgba_for_pixels(image.pixels)))


    def _rgba_for_pixels(pixels):
        for color in pixels:
            α, r, g, b = Image.argb_for_color(color)
            for component in (r, g, b, α):
                yield component
