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

import collections
import concurrent.futures
import multiprocessing
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
        ".."))) # For access to parallel Image
try:
    import cyImage as Image
except ImportError:
    import Image
from Globals import *


Result = collections.namedtuple("Result", "name copied scaled")


def scale(size, source, target, report_progress, state, when_finished):
    futures = set()
    with concurrent.futures.ProcessPoolExecutor(
            max_workers=multiprocessing.cpu_count()) as executor:
        for sourceImage, targetImage in get_jobs(source, target):
            future = executor.submit(scale_one, size, sourceImage,
                    targetImage, state)
            future.add_done_callback(report_progress)
            futures.add(future)
            if state.value in {CANCELED, TERMINATING}:
                for future in futures:
                    future.cancel()
                executor.shutdown()
                break
        concurrent.futures.wait(futures) # Keep working until finished
    if state.value != TERMINATING:
        when_finished()


def get_jobs(source, target):
    for name in os.listdir(source):
        yield os.path.join(source, name), os.path.join(target, name)


def scale_one(size, sourceImage, targetImage, state):
    if state.value in {CANCELED, TERMINATING}:
        raise Canceled()
    oldImage = Image.Image.from_file(sourceImage)
    if state.value in {CANCELED, TERMINATING}:
        raise Canceled()
    if oldImage.width <= size and oldImage.height <= size:
        oldImage.save(targetImage)
        return Result(targetImage, 1, 0)
    else:
        scale = min(size / oldImage.width, size / oldImage.height)
        newImage = oldImage.scale(scale)
        if state.value in {CANCELED, TERMINATING}:
            raise Canceled()
        newImage.save(targetImage)
        return Result(targetImage, 0, 1)


if __name__ == "__main__":
    print("Loaded OK")
