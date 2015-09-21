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
import multiprocessing
import os
import sys
import Image
import Qtrac


Result = collections.namedtuple("Result", "todo copied scaled name")


def main():
    size, smooth, source, target, concurrency = handle_commandline()
    Qtrac.report("starting...")
    canceled = False
    try:
        scale(size, smooth, source, target, concurrency)
    except KeyboardInterrupt:
        Qtrac.report("canceling...")
        canceled = True
    summarize(concurrency, canceled)


def handle_commandline():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--concurrency", type=int,
            default=multiprocessing.cpu_count(),
            help="specify the concurrency (for debugging and "
                "timing) [default: %(default)d]")
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
    return args.size, args.smooth, source, target, args.concurrency


def scale(size, smooth, source, target, concurrency):
    pipeline = create_pipeline(size, smooth, concurrency)
    for i, (sourceImage, targetImage) in enumerate(
            get_jobs(source, target)):
        pipeline.send((sourceImage, targetImage, i % concurrency))


def create_pipeline(size, smooth, concurrency):
    pipeline = None
    sink = results()
    for who in range(concurrency):
        pipeline = scaler(pipeline, sink, size, smooth, who)
    return pipeline


def get_jobs(source, target):
    for name in os.listdir(source):
        yield os.path.join(source, name), os.path.join(target, name)


@Qtrac.coroutine
def scaler(receiver, sink, size, smooth, me):
    while True:
        sourceImage, targetImage, who = (yield)
        if who == me:
            try:
                result = scale_one(size, smooth, sourceImage, targetImage)
                sink.send(result)
            except Image.Error as err:
                Qtrac.report(str(err), True)
        elif receiver is not None:
            receiver.send((sourceImage, targetImage, who))


@Qtrac.coroutine
def results():
    while True:
        result = (yield)
        results.todo += result.todo
        results.copied += result.copied
        results.scaled += result.scaled
        Qtrac.report("{} {}".format("copied" if result.copied else "scaled",
                os.path.basename(result.name)))
results.todo = results.copied = results.scaled = 0


def scale_one(size, smooth, sourceImage, targetImage):
    oldImage = Image.from_file(sourceImage)
    if oldImage.width <= size and oldImage.height <= size:
        oldImage.save(targetImage)
        return Result(1, 1, 0, targetImage)
    else:
        if smooth:
            scale = min(size / oldImage.width, size / oldImage.height)
            newImage = oldImage.scale(scale)
        else:
            stride = int(math.ceil(max(oldImage.width / size,
                                       oldImage.height / size)))
            newImage = oldImage.subsample(stride)
        newImage.save(targetImage)
        return Result(1, 0, 1, targetImage)


def summarize(concurrency, canceled):
    message = "copied {} scaled {} ".format(results.copied, results.scaled)
    difference = results.todo - (results.copied + results.scaled)
    if difference:
        message += "skipped {} ".format(difference)
    message += "using {} coroutines".format(concurrency)
    if canceled:
        message += " [canceled]"
    Qtrac.report(message)
    print()


if __name__ == "__main__":
    main()
