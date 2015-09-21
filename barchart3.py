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

import abc
import os
import re
import tempfile
import Qtrac
try:
    import cyImage as Image
except ImportError:
    import Image


def main():
    pairs = (("Mon", 16), ("Tue", 17), ("Wed", 19), ("Thu", 22),
            ("Fri", 24), ("Sat", 21), ("Sun", 19))
    textBarCharter = BarCharter(TextBarRenderer())
    textBarCharter.render("Forecast 6/8", pairs)
    imageBarCharter = BarCharter(ImageBarRenderer())
    imageBarCharter.render("Forecast 6/8", pairs)


class BarRenderer(Qtrac.Requirer):
    required_methods = {"initialize", "draw_caption", "draw_bar",
            "finalize"}


class BarCharter:

    def __init__(self, renderer):
        if not isinstance(renderer, BarRenderer):
            raise TypeError("Expected object of type BarRenderer, got {}".
                    format(type(renderer).__name__))
        self.__renderer = renderer


    def render(self, caption, pairs):
        maximum = max(value for _, value in pairs)
        self.__renderer.initialize(len(pairs), maximum)
        self.__renderer.draw_caption(caption)
        for name, value in pairs:
            self.__renderer.draw_bar(name, value)
        self.__renderer.finalize()


class TextBarRenderer:

    def __init__(self, scaleFactor=40):
        self.scaleFactor = scaleFactor


    def initialize(self, bars, maximum):
        assert bars > 0 and maximum > 0
        self.scale = self.scaleFactor / maximum


    def draw_caption(self, caption):
        print("{0:^{2}}\n{1:^{2}}".format(caption, "=" * len(caption),
                self.scaleFactor))


    def draw_bar(self, name, value):
        print("{} {}".format("*" * int(value * self.scale), name))


    def finalize(self):
        pass


class ImageBarRenderer:

    COLORS = [Image.color_for_name(name) for name in ("red", "green",
              "blue", "yellow", "magenta", "cyan")]


    def __init__(self, stepHeight=10, barWidth=30, barGap=2):
        self.stepHeight = stepHeight
        self.barWidth = barWidth
        self.barGap = barGap


    def initialize(self, bars, maximum):
        assert bars > 0 and maximum > 0
        self.index = 0
        color = Image.color_for_name("white")
        self.image = Image.Image(bars * (self.barWidth + self.barGap),
                maximum * self.stepHeight, background=color)


    def draw_caption(self, caption):
        self.filename = os.path.join(tempfile.gettempdir(),
                re.sub(r"\W+", "_", caption) + ".xpm")


    def draw_bar(self, name, value):
        color = ImageBarRenderer.COLORS[self.index %
                len(ImageBarRenderer.COLORS)]
        width, height = self.image.size
        x0 = self.index * (self.barWidth + self.barGap)
        x1 = x0 + self.barWidth
        y0 = height - (value * self.stepHeight)
        y1 = height - 1
        self.image.rectangle(x0, y0, x1, y1, fill=color)
        self.index += 1


    def finalize(self):
        self.image.save(self.filename)
        print("wrote", self.filename)


if __name__ == "__main__":
    main()
