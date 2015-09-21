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

import Command


def main():
    html = []
    grid = UndoableGrid(8, 3)   # (1) Empty
    html.append(grid.as_html("(1) Empty"))
    redLeft = grid.create_cell_command(2, 1, "red")
    redRight = grid.create_cell_command(5, 0, "red")
    redLeft()                   # (2) Do Red Cells
    redRight.do()               # OR: redRight()
    html.append(grid.as_html("(2) Do Red Cells"))
    greenLeft = grid.create_cell_command(2, 1, "lightgreen")
    greenLeft()                 # (3) Do Green Cell
    html.append(grid.as_html("(3) Do Green Cell"))
    rectangleLeft = grid.create_rectangle_macro(1, 1, 2, 2, "lightblue")
    rectangleRight = grid.create_rectangle_macro(5, 0, 6, 1, "lightblue")
    rectangleLeft()             # (4) Do Blue Squares
    rectangleRight.do()         # OR: rectangleRight()
    html.append(grid.as_html("(4) Do Blue Squares"))
    rectangleLeft.undo()        # (5) Undo Left Blue Square
    html.append(grid.as_html("(5) Undo Left Blue Square"))
    greenLeft.undo()            # (6) Undo Left Green Cell
    html.append(grid.as_html("(6) Undo Left Green Cell"))
    rectangleRight.undo()       # (7) Undo Right Blue Square
    html.append(grid.as_html("(7) Undo Right Blue Square"))
    redLeft.undo()              # (8) Undo Red Cells
    redRight.undo()
    html.append(grid.as_html("(8) Undo Red Cells"))
    print('<table border="0"><tr><td>{}</td></tr></table>'.format(
        "</td><td>".join(html)))


class Grid:

    def __init__(self, width, height):
        self.__cells = [["white" for _ in range(height)]
                        for _ in range(width)]


    def cell(self, x, y, color=None):
        if color is None:
            return self.__cells[x][y]
        self.__cells[x][y] = color


    @property
    def rows(self):
        return len(self.__cells[0])


    @property
    def columns(self):
        return len(self.__cells)


    def as_html(self, description=None):
        table = ['<table border="1" style="font-family: fixed">']
        if description is not None:
            table.append('<tr><td colspan="{}">{}</td></tr>'.format(
                self.columns, description))
        for y in range(self.rows):
            table.append("<tr>")
            for x in range(self.columns):
                color = self.__cells[x][y]
                name = color if not color.startswith("light") else color[5:]
                char = (name[0].upper() if color != "white" else
                        '<font color="white">X</font>')
                table.append('<td style="background-color: {}">{}</td>'
                        .format(color if color != "red" else "pink", char))
            table.append("</tr>")
        table.append("</table>")
        return "\n".join(table)


class UndoableGrid(Grid):

    def create_cell_command(self, x, y, color):
        def undo():
            self.cell(x, y, undo.color)
        def do():
            undo.color = self.cell(x, y) # Subtle!
            self.cell(x, y, color)
        return Command.Command(do, undo, "Cell")


    def create_rectangle_macro(self, x0, y0, x1, y1, color):
        macro = Command.Macro("Rectangle")
        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                macro.add(self.create_cell_command(x, y, color))
        return macro


if __name__ == "__main__":
    main()
