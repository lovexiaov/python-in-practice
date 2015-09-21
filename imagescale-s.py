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
import collections
import math
import os
import sys
import Image
import Qtrac

Result = collections.namedtuple("Result", "copied scaled")
Summary = collections.namedtuple("Summary", "todo copied scaled canceled")


def main():
    size, smooth, source, target = handle_commandline()
    Qtrac.report("starting...")
    summary = scale(size, smooth, source, target)
    summarize(summary)


def handle_commandline():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--size", default=400, type=int,
            help="make a scaled image that fits the given dimension "
                "[default: %(default)d]")
    parser.add_argument("-S", "--smooth", action="store_true",
            help="use smooth scaling (slow but good for text)")
    parser.add_argument("source",
            help="the directory containing the original .xpm images")
    parser.add_argument("target",
            help="the directory for the scaled .xpm images")
    args = parser.parse_args()
    source = os.path.abspath(args.source)
    target = os.path.abspath(args.target)
    if source == target:
        args.error("source and target must be different")
    if not os.path.exists(args.target):
        os.makedirs(target)
    return args.size, args.smooth, source, target


def scale(size, smooth, source, target):
    canceled = False
    todo = copied = scaled = 0
    for sourceImage, targetImage in get_jobs(source, target):
        try:
            todo += 1
            result = scale_one(size, smooth, sourceImage, targetImage)
            copied += result.copied
            scaled += result.scaled
            Qtrac.report("{} {}".format("copied" if result.copied
                    else "scaled", os.path.basename(targetImage)))
        except Image.Error as err:
            Qtrac.report(str(err), True)
        except KeyboardInterrupt:
            Qtrac.report("canceling...")
            canceled = True
            break
    return Summary(todo, copied, scaled, canceled)


def get_jobs(source, target):
    for name in os.listdir(source):
        yield os.path.join(source, name), os.path.join(target, name)


def scale_one(size, smooth, sourceImage, targetImage):
    oldImage = Image.from_file(sourceImage)
    if oldImage.width <= size and oldImage.height <= size:
        oldImage.save(targetImage)
        return Result(1, 0)
    else:
        if smooth:
            scale = min(size / oldImage.width, size / oldImage.height)
            newImage = oldImage.scale(scale)
        else:
            stride = int(math.ceil(max(oldImage.width / size,
                                       oldImage.height / size)))
            newImage = oldImage.subsample(stride)
        newImage.save(targetImage)
        return Result(0, 1)


def summarize(summary):
    message = "copied {} scaled {} ".format(summary.copied, summary.scaled)
    difference = summary.todo - (summary.copied + summary.scaled)
    if difference:
        message += "skipped {} ".format(difference)
    message += "single-threaded"
    if summary.canceled:
        message += " [canceled]"
    Qtrac.report(message)
    print()


if __name__ == "__main__":
    main()
