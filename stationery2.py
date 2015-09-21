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

import itertools
import sys


def main():
    pencil = Item.create("Pencil", 0.40)
    ruler = Item.create("Ruler", 1.60)
    eraser = make_item("Eraser", 0.20)
    pencilSet = Item.compose("Pencil Set", pencil, ruler, eraser)
    box = Item.create("Box", 1.00)
    boxedPencilSet = make_composite("Boxed Pencil Set", box, pencilSet)
    boxedPencilSet.add(pencil)
    for item in (pencil, ruler, eraser, pencilSet, boxedPencilSet):
        item.print()
    assert not pencil.composite
    pencil.add(eraser, box)
    assert pencil.composite
    pencil.print()
    pencil.remove(eraser)
    assert pencil.composite
    pencil.remove(box)
    assert not pencil.composite
    pencil.print()


class Item:

    def __init__(self, name, *items, price=0.00):
        self.name = name
        self.price = price
        self.children = []
        if items:
            self.add(*items)


    @classmethod
    def create(Class, name, price):
        return Class(name, price=price)


    @classmethod
    def compose(Class, name, *items):
        return Class(name, *items)

    
    @property
    def composite(self):
        return bool(self.children)


    def add(self, first, *items):
        self.children.extend(itertools.chain((first,), items))


    def remove(self, item):
        self.children.remove(item)


    def __iter__(self):
        return iter(self.children)


    @property
    def price(self):
        return (sum(item.price for item in self) if self.children else
                self.__price)


    @price.setter
    def price(self, price):
        self.__price = price


    def print(self, indent="", file=sys.stdout):
        print("{}${:.2f} {}".format(indent, self.price, self.name),
                file=file)
        for child in self:
            child.print(indent + "      ")


def make_item(name, price):
    return Item(name, price=price)


def make_composite(name, *items):
    return Item(name, *items)


if __name__ == "__main__":
    main()
