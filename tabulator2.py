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

import sys
if sys.version_info[:2] < (3, 2):
    from xml.sax.saxutils import escape
else:
    from html import escape


WINNERS = ("Nikolai Andrianov", "Matt Biondi", "Bjørn Dæhlie",
        "Birgit Fischer", "Sawao Kato", "Larisa Latynina", "Carl Lewis",
        "Michael Phelps", "Mark Spitz", "Jenny Thompson")


def main():
    htmlLayout = Layout(HtmlTabulator)
    for rows in range(2, 6):
        print(htmlLayout.tabulate(rows, WINNERS))
    textLayout = Layout(TextTabulator)
    for rows in range(2, 6):
        print(textLayout.tabulate(rows, WINNERS))


class Layout:

    def __init__(self, tabulator):
        self.tabulator = tabulator


    def tabulate(self, rows, items):
        return self.tabulator.tabulate(rows, items)


class HtmlTabulator:

    @staticmethod
    def tabulate(rows, items):
        columns, remainder = divmod(len(items), rows)
        if remainder:
            columns += 1
        column = 0
        table = ['<table border="1">\n']
        for item in items:
            if column == 0:
                table.append("<tr>")
            table.append("<td>{}</td>".format(escape(str(item))))
            column += 1
            if column == columns:
                table.append("</tr>\n")
            column %= columns
        if table[-1][-1] != "\n":
            table.append("</tr>\n")
        table.append("</table>\n")
        return "".join(table)


class TextTabulator:

    @staticmethod
    def tabulate(rows, items):
        columns, remainder = divmod(len(items), rows)
        if remainder:
            columns += 1
            remainder = (rows * columns) - len(items)
            if remainder == columns:
                remainder = 0
        column = columnWidth = 0
        for item in items:
            columnWidth = max(columnWidth, len(item))
        columnDivider = ("-" * (columnWidth + 2)) + "+"
        divider = "+" + (columnDivider * columns) + "\n"
        table = [divider]
        for item in items + (("",) * remainder):
            if column == 0:
                table.append("|")
            table.append(" {:<{}} |".format(item, columnWidth))
            column += 1
            if column == columns:
                table.append("\n")
            column %= columns
        table.append(divider)
        return "".join(table)


if __name__ == "__main__":
    main()
