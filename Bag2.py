#!/usr/bin/env python3
# Copyright © 2012-13 Qtrac Ltd. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. It is provided for educational
# purposes and is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.


class Bag:

    def __init__(self, items=None):
        """
        >>> bag = Bag(list("ABCDEB"))
        >>> bag.count("A"), bag.count("B"), bag.count("Z")
        (1, 2, 0)
        """
        self.__bag = {}
        if items is not None:
            for item in items:
                self.add(item)


    def clear(self):
        """
        >>> bag = Bag(list("ABCDEB"))
        >>> bag.count("A"), bag.count("B"), bag.count("Z")
        (1, 2, 0)
        >>> len(bag) # "Z" was added but count of 0 doesn't count in len
        6
        >>> bag.clear()
        >>> len(bag)
        0
        """
        self.__bag.clear()


    def add(self, item):
        """
        >>> bag = Bag(list("ABCDEB"))
        >>> bag.add("B")
        >>> bag.add("X")
        >>> bag.count("A"), bag.count("B"), bag.count("Z")
        (1, 3, 0)
        """
        self.__bag[item] = self.__bag.get(item, 0) + 1


    def __delitem__(self, item):
        """
        >>> bag = Bag(list("ABCDEB"))
        >>> print(len(bag))
        6
        >>> del bag["B"]
        >>> del bag["Z"]
        Traceback (most recent call last):
            ...
        KeyError: 'Z'
        >>> bag.count("A"), bag.count("B"), bag.count("Z")
        (1, 1, 0)
        >>> del bag["B"]
        >>> bag.count("A"), bag.count("B"), bag.count("Z")
        (1, 0, 0)
        >>> del bag["C"], bag["D"], bag["E"]
        >>> print(len(bag))
        1
        >>> del bag["A"]
        >>> print(len(bag))
        0
        >>> del bag["A"]
        Traceback (most recent call last):
            ...
        KeyError: 'A'
        """
        if self.__bag.get(item) is not None:
            self.__bag[item] -= 1
            if self.__bag[item] <= 0:
                del self.__bag[item]
        else:
            raise KeyError(str(item))


    def count(self, item):
        """
        >>> bag = Bag(list("ABCDEB"))
        >>> bag.count("B"), bag.count("X")
        (2, 0)
        """
        return self.__bag.get(item, 0)


    def __len__(self):
        """
        >>> bag = Bag(list("ABCDEB"))
        >>> len(bag)
        6
        >>> bag.add("B")
        >>> len(bag)
        7
        >>> bag.add("X")
        >>> len(bag)
        8
        >>> bag.add("B")
        >>> len(bag)
        9
        >>> del bag["Z"]
        Traceback (most recent call last):
            ...
        KeyError: 'Z'
        >>> len(bag)
        9
        >>> del bag["A"]
        >>> len(bag)
        8
        >>> for _ in range(4): del bag["B"]
        >>> len(bag)
        4
        >>> bag.clear()
        >>> len(bag)
        0
        """
        return sum(count for count in self.__bag.values())


    def __iter__(self):
        """
        >>> bag = Bag(list("DABCDEBCCDD"))
        >>> for key in sorted(bag.items()): print(key, end=" ")
        A B B C C C D D D D E 
        >>> for key in sorted(bag): print(key, end=" ")
        A B B C C C D D D D E 
        >>> for _ in range(4): del bag["D"]
        >>> for key in sorted(bag.items()): print(key, end=" ")
        A B B C C C E 
        >>> for key in sorted(bag): print(key, end=" ")
        A B B C C C E 
        >>> del bag["A"]
        >>> for key in sorted(bag.items()): print(key, end=" ")
        B B C C C E 
        >>> for key in sorted(bag): print(key, end=" ")
        B B C C C E 
        """
        for item, count in self.__bag.items():
            for _ in range(count):
                yield item


    items = __iter__


    def __contains__(self, item):
        """
        >>> bag = Bag(list("DABCDEBCCDD"))
        >>> "D" in bag
        True
        >>> del bag["D"]
        >>> "D" in bag
        True
        >>> del bag["D"]
        >>> "D" in bag
        True
        >>> del bag["D"]
        >>> "D" in bag
        True
        >>> del bag["D"]
        >>> "D" in bag
        False
        >>> "X" in bag
        False
        """
        return item in self.__bag


if __name__ == "__main__":
    import doctest
    doctest.testmod()
