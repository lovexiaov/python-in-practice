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

This Image plugin module can read and write .xpm files.

This module can load and save most XPM files. However, it ignores
extensions and monochrome and symbolic color keys (so if an XPM file
with these is loaded they are discarded and won't appear if the file is
then saved). Also, the image name is discarded in favor of a sanitized
version of the filename.

Its meta data may optionally include x_hot and y_hot ints to indicate
the image's hotspot.
"""

import io
import itertools
import os
import warnings
import Image


_XPM = "/* XPM */"
(_WANT_XPM, _WANT_NAME, _WANT_VALUES, _WANT_COLOR, _WANT_PIXELS,
 _DONE) = ("WANT_XPM", "WANT_NAME", "WANT_VALUES", "WANT_COLOR",
        "WANT_PIXELS", "DONE")
_CODES = "".join((chr(x) for x in range(32, 127) if chr(x) not in '\\"'))


def can_load(filename):
    """Returns 100 if this module can do a lossless load, 0 if it can't
    load the file, and something inbetween if it can do a lossy load."""
    return 80 if os.path.splitext(filename)[1].lower() == ".xpm" else 0


def can_save(filename):
    """Returns 100 if this module can do a lossless save, 0 if it can't
    save the file, and something inbetween if it can do a lossy save."""
    return can_load(filename)


def load(image, filename):
    """load an XPM file"""
    colors = cpp = count = None
    state = _WANT_XPM
    palette = {}
    index = 0
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
                image.pixels = Image.create_array(image.width,
                        image.height)


def _parse_xpm(lino, line):
    if line != _XPM:
        raise Image.Error("invalid XPM file line {}: missing '{}'"
                .format(lino, _XPM))
    return _WANT_NAME


def _parse_name(lino, line):
    line = line.replace(" ", "")
    if line.startswith("static") and line.endswith("[]={"):
        return _WANT_VALUES
    raise Image.Error("invalid XPM file line {}: missing image name"
            .format(lino))


def _parse_values(lino, line, image):
    line = _sanitize_quoted_line(lino, line)
    parts = line.split()
    if len(parts) not in {4, 5, 6, 7}:
        raise Image.Error("invalid XPM file line {}: invalid values"
                .format(lino))
    if parts[-1] == "XPMEXT":
        parts = parts[:-1]
        warnings.warn("ignoring extensions in XPM file")
    parts = [int(x) for x in parts]
    image.width, image.height, colors, cpp = parts[:4]
    count = colors
    if len(parts) == 6:
        image.meta["x_hot"] = parts[4]
        image.meta["y_hot"] = parts[5]
    return colors, cpp, count, _WANT_COLOR


def _parse_color(lino, line, palette, cpp, count):
    line = _sanitize_quoted_line(lino, line)
    key = line[:cpp]
    parts = line[cpp + 1:].split()
    if len(parts) % 2 != 0:
        raise Image.Error("invalid XPM file line {}: invalid color".format(
                lino))
    pairs = sorted(zip(parts[::2], parts[1::2]))
    name = pairs[0][1].strip()
    palette[key] = (Image.ColorForName["transparent"]
            if name.lower() == "none" else Image.color_for_name(name))
    count -= 1
    if count == 0:
        return count, _WANT_PIXELS
    return count, _WANT_COLOR


def _parse_pixels(lino, line, pixels, palette, cpp, count, index):
    line = _sanitize_quoted_line(lino, line)
    for i in range(0, len(line), cpp):
        color = palette[line[i:i + cpp]]
        pixels[index] = color
        index += 1
    count -= 1
    if count == 0:
        return count, _DONE, index
    return count, _WANT_PIXELS, index


def _sanitize_quoted_line(lino, line):
    line = line.rstrip(",};")
    if not (line.startswith('"') and line.endswith('"')):
        raise Image.Error("invalid line {}: \"{}\"".format(lino, line))
    return line[1:-1]


def save(image, filename):
    """save an XPM file"""
    name = Image.sanitized_name(filename)
    palette, cpp = _palette_and_cpp(image.pixels)
    with open(filename, "w+t", encoding="ascii") as file:
        _write_header(image, file, name, cpp, len(palette))
        _write_palette(file, palette)
        _write_pixels(image, file, palette)


def _palette_and_cpp(pixels):
    colors = set()
    transparent = Image.ColorForName["transparent"]
    for color in pixels:
        if color == transparent:
            name = "None" # special-case transparent
        else: # strip off alpha
            name = "#{:06X}".format(color & Image.CLEAR_ALPHA)
        colors.add((color, name))
    cpp = 1
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


def _write_header(image, file, name, cpp, colors):
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


def _write_pixels(image, file, palette):
    for y in range(image.height):
        file.write('"')
        for x in range(image.width):
            code = palette[image.pixel(x, y)][0]
            file.write(code)
        file.write('",\n')
    file.seek(file.tell() - 2, io.SEEK_SET) # Get rid of spurious ,\n
    file.write("};\n")
