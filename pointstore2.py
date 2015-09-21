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

import atexit
import os
import shelve
import sys
import tempfile
import time
import Qtrac


def main():
    regression = False
    size = int(1e6)
    if len(sys.argv) > 1 and sys.argv[1] == "-P":
        regression = True
        size = 20
    Qtrac.remove_if_exists(os.path.join(tempfile.gettempdir(), "point.db"))
    start = time.clock()
    points = []
    for i in range(size):
        points.append(Point(i, i ** 2, i // 2))
    end = time.clock() - start
    assert points[size - 1].x == size - 1
    print(len(points))
    if not regression: # wait until we can see how much memory is used
        print("took {} secs to create {:,} points".format(end, size))
        input("press Enter to finish")


class Point:

    __slots__ = ()
    __dbm = shelve.open(os.path.join(tempfile.gettempdir(), "point.db"))

    def __init__(self, x=0, y=0, z=0, color=None):
        self.x = x
        self.y = y
        self.z = z
        self.color = color


    def __key(self, name):
        return  "{:X}:{}".format(id(self), name)


    def __getattr__(self, name):
        return Point.__dbm[self.__key(name)]


    def __setattr__(self, name, value):
        Point.__dbm[self.__key(name)] = value


    def __repr__(self):
        return "Point({0.x!r}, {0.y!r}, {0.z!r}, {0.color!r})".format(self)


    atexit.register(__dbm.close)


if __name__ == "__main__":
    main()
