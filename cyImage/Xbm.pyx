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
import mmap
import os
import warnings
cimport numpy
from cyImage.Globals import *


_DTYPE = numpy.uint32 # See: http://docs.cython.org/src/tutorial/numpy.html
ctypedef numpy.uint32_t _DTYPE_t

DEF _DEFINE = b"#define"
DEF _BITS = b"bits[]"
DEF _WIDTH = b"width"
DEF _HEIGHT = b"height"
DEF _X_HOT = b"x_hot"
DEF _Y_HOT = b"y_hot"


def load(image, filename):
    with open(filename, "rb") as file:
        xbm = mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ)
        i = xbm.find(_DEFINE)
        j = xbm.find(_BITS)
        if i == -1 or j == -1:
            raise Error("failed to parse '{}'".format(filename))
        _parse_defines(image, xbm[i:j])
        image.pixels = create_array(image.width, image.height,
                ColorForName["white"])
        _parse_bits(image.pixels, image.width, filename,
                xbm[j + len(_BITS):])


cdef void _parse_defines(image, defines):
    parts = defines.split()
    for define, name, value in zip(parts[0::3], parts[1::3], parts[2::3]):
        if define == _DEFINE:
            if name.endswith(_WIDTH):
                image.width = int(value)
            elif name.endswith(_HEIGHT):
                image.height = int(value)
            else:
                for candidate in (_X_HOT, _Y_HOT):
                    if name.endswith(candidate):
                        image.meta[candidate.decode("ascii")] = int(value)
    if image.width is None or image.height is None:
        raise Error("missing dimension in '{}'".format(
            image.filename))


cdef void _parse_bits(_DTYPE_t[:] pixels, int width, str filename,
        bytes bits):
    # Algorithm based on the one used by libclaw
    cdef int i = bits.find(b"{")
    cdef int j = bits.find(b"};", i)
    if i == -1 or j == -1:
        raise Error("missing bits in '{}'".format(filename))
    black = ColorForName["black"]
    cdef int x = 0
    cdef int index = 0
    for value in _values_for_bits(bits[i + 1:j].rstrip()):
        i = 0
        while i != 8 and x != width:
            if value & 1:
                pixels[index] = black
            i += 1
            index += 1
            x += 1
            value >>= 1
        if x == width:
            x = 0


def _values_for_bits(bytes bits):
    cdef int i = 0
    cdef int j
    while i < len(bits):
        j = bits.find(b",", i)
        if j == -1:
            j = len(bits)
        value = bits[i:j].strip()
        if value.startswith((b"0x", b"0X")):
            yield int(value[2:], 16)
        else:
            yield int(value)
        i = j + 1


def save(image, filename):
    with open(filename, "w+t", encoding="ascii") as file:
        _write_header(image, file, sanitized_name(filename))
        _write_pixels(image.pixels, image.width, image.height, file)


cdef void _write_header(image, file, name):
    file.write("#define {}_width {}\n".format(name, image.width))
    file.write("#define {}_height {}\n".format(name, image.height))
    x = image.meta.get("x_hot")
    y = image.meta.get("y_hot")
    if x is not None and y is not None:
        file.write("#define {}_x_hot {}\n".format(name, x))
        file.write("#define {}_y_hot {}\n".format(name, y))
    file.write("static unsigned char {}_bits[] = {{\n  ".format(name))


cdef void _write_pixels(_DTYPE_t[:] pixels, int width, int height, file):
    # Algorithm based on the one used by libclaw
    cdef _DTYPE_t white = ColorForName["white"]
    cdef _DTYPE_t transparent = ColorForName["transparent"]
    cdef int MAX_PER_LINE = 12
    cdef count = 0
    cdef index = 0
    cdef int y, x, offset, value, bits
    for y in range(height):
        offset = y * width
        x = 0
        while x != width:
            value = bits = 0
            while x != width and bits != 8:
                value >>= 1
                if pixels[offset + x] not in (white, transparent):
                    value |= 0x80
                bits += 1
                x += 1
                index += 1
            value >>= 8 - bits
            count += 1
            file.write("0x{:02X}".format(value))
            if index != len(pixels):
                if count == MAX_PER_LINE:
                    file.write(",\n  ")
                    count = 0
                else:
                    file.write(", ")
    # remove spurious trailing comma
    BACK = 3
    offset = file.tell() - BACK
    file.seek(offset, io.SEEK_SET)
    chunk = file.read(BACK)
    i = chunk.find(",")
    if i > -1:
        file.seek(file.tell() - (BACK - i), io.SEEK_SET)
    file.write("};\n")
    file.truncate()
