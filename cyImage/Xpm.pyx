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

import io
import itertools
import os
import warnings
cimport numpy
from cyImage.Globals import *

# Reading & writing the files as bytes rather than strs barely makes any
# difference.

_DTYPE = numpy.uint32 # See: http://docs.cython.org/src/tutorial/numpy.html
ctypedef numpy.uint32_t _DTYPE_t

_XPM = "/* XPM */"
(_WANT_XPM, _WANT_NAME, _WANT_VALUES, _WANT_COLOR, _WANT_PIXELS,
 _DONE) = range(6)
_CODES = "".join((chr(x) for x in range(32, 127) if chr(x) not in '\\"'))


def load(image, str filename):
    colors = None
    cdef int cpp = 0
    cdef int count = 0
    cdef int index = 0
    cdef int state = _WANT_XPM
    cdef int lino
    cdef str line
    palette = {}
    with open(filename, "rt", encoding="ascii") as file:
        for lino, line in enumerate(file, start=1):
            line = line.strip()
            if not line or (line.startswith(("/*", "//")) and state !=
                    _WANT_XPM):
                continue
            # if branches are ordered by frequency of occurrence
            if state == _WANT_COLOR:
                count, state = _parse_color(lino, line, palette, cpp,
                        count)
                if state == _WANT_PIXELS:
                    count = image.height
            elif state == _WANT_PIXELS:
                count, state, index = _parse_pixels(lino, line,
                        image.pixels, palette, cpp, count, index)
                if state == _DONE:
                    break
            elif state == _WANT_XPM:
                state = _parse_xpm(lino, line)
            elif state == _WANT_NAME:
                state = _parse_name(lino, line)
            elif state == _WANT_VALUES:
                colors, cpp, count, state = _parse_values(lino, line,
                        image)
                image.pixels = create_array(image.width, image.height)


cdef int _parse_xpm(int lino, str line) except -1:
    if line != _XPM:
        raise Error("invalid XPM file line {}: missing '{}'"
                .format(lino, _XPM))
    return _WANT_NAME


cdef int _parse_name(int lino, str line) except -1:
    line = line.replace(" ", "")
    if line.startswith("static") and line.endswith("[]={"):
        return _WANT_VALUES
    raise Error("invalid XPM file line {}: missing image name"
            .format(lino))


cdef object _parse_values(int lino, str line, image):
    line = _sanitize_quoted_line(lino, line)
    parts = line.split()
    if len(parts) not in {4, 5, 6, 7}:
        raise Error("invalid XPM file line {}: invalid values"
                .format(lino))
    if parts[-1] == "XPMEXT":
        parts = parts[:-1]
        warnings.warn("ignoring extensions in XPM file")
    parts = [int(x) for x in parts]
    cdef int colors, cpp
    image.width, image.height, colors, cpp = parts[:4]
    cdef int count = colors
    if len(parts) == 6:
        image.meta["x_hot"] = parts[4]
        image.meta["y_hot"] = parts[5]
    return colors, cpp, count, _WANT_COLOR


cdef object _parse_color(int lino, str line, palette, int cpp, int count):
    line = _sanitize_quoted_line(lino, line)
    cdef str key = line[:cpp]
    parts = line[cpp + 1:].split()
    if len(parts) % 2 != 0:
        raise Error("invalid XPM file line {}: invalid color".format(
                lino))
    pairs = sorted(zip(parts[::2], parts[1::2]))
    cdef str name = pairs[0][1].strip()
    palette[key] = (ColorForName["transparent"] if name.lower() == "none"
                    else color_for_name(name))
    count -= 1
    if count == 0:
        return count, _WANT_PIXELS
    return count, _WANT_COLOR


cdef object _parse_pixels(int lino, str line, _DTYPE_t[:] pixels,
        dict palette, int cpp, int count, int index):
    line = _sanitize_quoted_line(lino, line)
    for i in range(0, len(line), cpp):
        color = palette[line[i:i + cpp]]
        pixels[index] = color
        index += 1
    count -= 1
    if count == 0:
        return count, _DONE, index
    return count, _WANT_PIXELS, index


cdef object _sanitize_quoted_line(int lino, str line):
    line = line.rstrip(",};")
    if not (line.startswith('"') and line.endswith('"')):
        raise Error("invalid line {}: \"{}\"".format(lino, line))
    return line[1:-1]


def save(image, filename):
    name = sanitized_name(filename)
    palette, cpp = _palette_and_cpp(image.pixels)
    with open(filename, "w+t", encoding="ascii") as file:
        _write_header(image, file, name, cpp, len(palette))
        _write_palette(file, palette)
        _write_pixels(image.pixels, image.width, image.height, file,
                palette)


cdef object _palette_and_cpp(_DTYPE_t[:] pixels):
    colors = set()
    cdef _DTYPE_t transparent = ColorForName["transparent"]
    for color in pixels:
        if color == transparent:
            name = "None" # special-case transparent
        else:
            name = "#{:06X}".format(color & CLEAR_ALPHA) # strip off alpha
        colors.add((color, name))
    cdef int cpp = 1
    while True:
        if len(colors) <= len(_CODES) ** cpp:
            break
        cpp += 1
    # we turn the colors into a list so that we get the same order every
    # time (this doesn't matter for the format but helps with
    # regressions testing)
    colors = sorted(colors, reverse=True)
    palette = {}
    for code in itertools.product(_CODES, repeat=cpp):
        if not colors:
            break
        color, name = colors.pop()
        palette[color] = ("".join(code), name)
    return palette, cpp


cdef void _write_header(image, file, name, cpp, colors):
    file.write("{}\nstatic unsigned char *{}[] = {{\n".format(_XPM, name))
    file.write('"{} {} {} {}'.format(image.width, image.height, colors,
        cpp))
    x = image.meta.get("x_hot")
    y = image.meta.get("y_hot")
    if x is not None and y is not None:
        file.write(" {} {}".format(x, y))
    file.write('",\n')


def _write_palette(file, palette):
    for code, name in sorted(palette.values(),
            key=lambda v: " " if v[1] == "None" else v[1]):
        file.write('"{}\tc {}",\n'.format(code, name)) # \t is nicer in vim


cdef void _write_pixels(_DTYPE_t[:] pixels, int width, int height, file,
        palette):
    cdef int y, x, offset
    for y in range(height):
        file.write('"')
        offset = y * width
        for x in range(width):
            code = palette[pixels[offset + x]][0]
            file.write(code)
        file.write('",\n')
    file.seek(file.tell() - 2, io.SEEK_SET) # Get rid of spurious ,\n
    file.write("};\n")
