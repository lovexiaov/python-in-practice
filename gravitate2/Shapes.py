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


class _Shape: # Abstract base class

    def __init__(self, name, underline):
        self.name = name
        self.underline = underline


    @abc.abstractmethod
    def create(self, canvas, length, x0, y0, x1, y1, color, outline):
        canvas.create_rectangle(x0, y0, x1, y1, fill=outline, width=0)


    def three_colors(self, canvas, color):
        r, g, b = canvas.winfo_rgb(color)
        color = "#{:04X}{:04X}{:04X}".format(r, g, b)
        dark = "#{:04X}{:04X}{:04X}".format(max(0, int(r * 0.5)),
                max(0, int(g * 0.5)), max(0, int(b * 0.5)))
        light = "#{:04X}{:04X}{:04X}".format(min(0xFFFF, int(r * 1.5)),
                min(0xFFFF, int(g * 1.5)), min(0xFFFF, int(b * 1.5)))
        return light, color, dark


    def gradient(self, canvas, color, steps):
        r, g, b = canvas.winfo_rgb(color)
        step = 1.0 / steps
        offset = 0.67
        for x in range(steps):
            if offset <= 1:
                yield "#{:04X}{:04X}{:04X}".format(max(0, int(r * offset)),
                        max(0, int(g * offset)), max(0, int(b * offset)))
            else:
                yield "#{:04X}{:04X}{:04X}".format(
                        min(0xFFFF, int(r * offset)),
                        min(0xFFFF, int(g * offset)),
                        min(0xFFFF, int(b * offset)))
            offset += step


class _Circle(_Shape):

    def __init__(self):
        super().__init__("Circle", 0)


    def create(self, canvas, length, x0, y0, x1, y1, color, outline):
        if color is None:
            super().create(canvas, length, x0, y0, x1, y1, color, outline)
        else:
            steps = min((x1 - x0) // 1, (y1 - y0) // 1) // 2
            for color in self.gradient(canvas, color, steps):
                canvas.create_oval(x0, y0, x1, y1, fill=color, width=0)
                x0 += 1
                y0 += 1
                x1 -= 1
                y1 -= 1


class _Hexagon(_Shape):

    def __init__(self):
        super().__init__("Hexagon", 0)


    def create(self, canvas, length, x0, y0, x1, y1, color, outline):
        if color is None:
            super().create(canvas, length, x0, y0, x1, y1, color, outline)
        else:
            steps = min((x1 - x0) // 1, (y1 - y0) // 1) // 2
            for color in self.gradient(canvas, color, steps):
                length = x1 - x0
                half = length // 2
                fifth = length // 5
                four_fifths = fifth * 4
                canvas.create_polygon(
                        x0,        y0 + fifth, 
                        x0 + half, y0,
                        x1,        y0 + fifth,
                        x1,        y0 + four_fifths,
                        x0 + half, y1,
                        x0,        y0 + four_fifths,
                        fill=color, width=0)
                x0 += 1
                y0 += 1
                x1 -= 1
                y1 -= 1


class _Octagon(_Shape):

    def __init__(self):
        super().__init__("Octagon", 0)


    def create(self, canvas, length, x0, y0, x1, y1, color, outline):
        if color is None:
            super().create(canvas, length, x0, y0, x1, y1, color, outline)
        else:
            steps = min((x1 - x0) // 1, (y1 - y0) // 1) // 2
            for color in self.gradient(canvas, color, steps):
                quarter = (x1 - x0) // 4
                three_quarters = quarter * 3
                canvas.create_polygon(
                        x0,                  y0 + quarter,
                        x0 + quarter,        y0,
                        x0 + three_quarters, y0,
                        x1,                  y0 + quarter,
                        x1,                  y0 + three_quarters,
                        x0 + three_quarters, y1,
                        x0 + quarter,        y1,
                        x0,                  y0 + three_quarters,
                        fill=color, width=0)
                x0 += 1
                y0 += 1
                x1 -= 1
                y1 -= 1


class _Spiral(_Shape):

    def __init__(self):
        super().__init__("Spiral", 0)


    def create(self, canvas, length, x0, y0, x1, y1, color, outline):
        if color is None:
            super().create(canvas, length, x0, y0, x1, y1, color, outline)
        else:
            STEPS = 6
            colors = list(self.gradient(canvas, color, STEPS + 1))
            canvas.create_rectangle(x0, y0, x1, y1, fill=colors.pop(0),
                    width=0)
            coords = (x0,      y0,
                      x1,      y0,
                      x1,      y1,
                      x0 +  3, y1,
                      x0 +  3, y0 +  3,
                      x1 -  3, y0 +  3,
                      x1 -  3, y1 -  3,
                      x0 +  6, y1 -  3,
                      x0 +  6, y0 +  6,
                      x1 -  6, y0 +  6,
                      x1 -  6, y1 -  6,
                      x0 +  9, y1 -  6,
                      x0 +  9, y0 +  9,
                      x1 -  9, y0 +  9,
                      x1 -  9, y1 -  9,
                      x0 + 12, y1 -  9,
                      x0 + 12, y0 + 12,
                      x1 - 12, y0 + 12,
                      x1 - 12, y1 - 12,
                      x0 + 15, y1 - 12,
                      x0 + 15, y0 + 15,
                      x1 - 15, y0 + 15,
                      x1 - 15, y1 - 15,
                      x0 + 18, y1 - 15,
                      x0 + 18, y0 + 18,
                      x1 - 18, y0 + 18
                     )
            CHUNK = len(coords) // STEPS
            for i in range(STEPS):
                start = i * CHUNK
                end = start + CHUNK + 2
                canvas.create_line(*coords[start:end], smooth=False,
                        fill=colors[i], width=2)


class _Square(_Shape):

    def __init__(self):
        super().__init__("Square", 3)


    def create(self, canvas, length, x0, y0, x1, y1, color, outline):
        if color is None:
            super().create(canvas, length, x0, y0, x1, y1, color, outline)
        else:
            light, color, dark = self.three_colors(canvas, color)
            offset = 4
            # ________
            # |\__t__/|
            # |l| m |r|
            # |/-----\|
            # ----b----
            #
            canvas.create_polygon( # t
                    x0,          y0,
                    x0 + offset, y0 + offset,
                    x1 - offset, y0 + offset,
                    x1,          y0,
                    fill=light, outline=light)
            canvas.create_polygon( # l
                    x0,          y0,
                    x0,          y1,
                    x0 + offset, y1 - offset,
                    x0 + offset, y0 + offset,
                    fill=light, outline=light)
            canvas.create_polygon( # r
                    x1 - offset, y0 + offset,
                    x1,          y0,
                    x1,          y1,
                    x1 - offset, y1 - offset,
                    fill=dark, outline=dark)
            canvas.create_polygon( # b
                    x0,          y1,
                    x0 + offset, y1 - offset,
                    x1 - offset, y1 - offset,
                    x1,          y1,
                    fill=dark, outline=dark)
            canvas.create_rectangle( # m
                    x0 + offset, y0 + offset,
                    x1 - offset, y1 - offset,
                    fill=color, outline=color)


Shapes = [_Square(), _Circle(), _Hexagon(), _Octagon(), _Spiral()]
ShapeForName = {}
for shape in Shapes:
    ShapeForName[shape.name] = shape


if __name__ == "__main__":
    import sys
    if not sys.stdout.isatty():
        print("Loaded OK")
