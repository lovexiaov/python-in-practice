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

import argparse
import cProfile
import os
import sys
import tempfile
import time
import Image
import Scale
try:
    import cyImage
except ImportError:
    cyImage = None

SHOW_SAVE_TIME = False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-P", "--noprofile", action="store_true",
            help="only use inside a regression.py file")
    parser.add_argument("image", nargs="?", default=os.path.join(
            os.path.dirname(__file__), "regressiondata/photo.xpm"),
            help="image filename [default %(default)s]")
    args = parser.parse_args()
    profile = not args.noprofile

    if SHOW_SAVE_TIME:
        print("Loading", args.image, end="")
    start = time.time()
    image = Image.Image.from_file(args.image)
    end = time.time() - start
    if SHOW_SAVE_TIME:
        print("\rLoaded with Image in {:.3f} sec{}".format(end,
                " " * len(args.image)))

    if cyImage is not None:
        if SHOW_SAVE_TIME:
            print("Loading", args.image, end="")
        start = time.time()
        image1 = cyImage.Image.from_file(args.image)
        end = time.time() - start
        if SHOW_SAVE_TIME:
            print("\rLoaded with cyImage in {:.3f} sec{}".format(end,
                    " " * len(args.image)))

    if profile:
        print("Scaling using Image.scale()...")
        cProfile.runctx("image.scale(0.5)", globals(), locals())
        if cyImage is not None:
            print("Scaling using cyImage.scale()...")
            cProfile.runctx("image1.scale(0.5)", globals(), locals())

    filenames = []
    for name, function in (("Scale.scale_slow", Scale.scale_slow),
            ("Scale.scale_fast", Scale.scale_fast)):
        scale(image, name, profile)
        filenames.append((os.path.splitext(name)[1][1:], function))

    if profile and SHOW_SAVE_TIME:
        print("Saving rescaled images...")
    filename = os.path.join(tempfile.gettempdir(), "scale.xpm")

    start = time.time()
    scaled = image.scale(0.5)
    end = time.time() - start
    if not profile:
        print("Scaled with Image.scale() in {:.3f} sec".format(end))
    if SHOW_SAVE_TIME:
        start = time.time()
        scaled.save(filename)
        end = time.time() - start
        print("Saved {} with Image.save() in {:.3f} sec".format(filename,
                end))

    if cyImage is not None:
        start = time.time()
        scaled1 = image1.scale(0.5)
        end = time.time() - start
        if not profile:
            print("Scaled with cyImage.scale() in {:.3f} sec".format(end))
        if SHOW_SAVE_TIME:
            start = time.time()
            scaled1.save(filename)
            end = time.time() - start
            print("Saved {} with cyImage.save() in {:.3f} sec".format(
                    filename, end))

    for filename, function in filenames:
        save(image, filename, function, profile)


def scale(image, function, profile):
    if profile:
        print("Scaling using {}()...".format(function))
        cProfile.runctx("{}(image.pixels, image.width, "
                "image.height, 0.5)".format(function), globals(), locals())


def save(image, name, function, profile):
    filename = os.path.join(tempfile.gettempdir(), name + ".xpm")
    start = time.time()
    width, pixels = function(image.pixels, image.width, image.height, 0.5)
    end = time.time() - start
    if not profile:
        print("Scaled with {}() in {:.3f} sec".format(name, end))
    if SHOW_SAVE_TIME:
        image = Image.Image.from_data(width, pixels)
        start = time.time()
        image.save(filename)
        end = time.time() - start
        print("Saved {} in {:.3f} sec".format(filename, end))


if __name__ == "__main__":
    main()

