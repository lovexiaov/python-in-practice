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

import random
import string

random.seed(917) # Don't want random for regression tests

MOUSE, KEYPRESS, TIMER, TERMINATE = ("MOUSE", "KEYPRESS", "TIMER",
        "TERMINATE")


def next():
    kinds = ([MOUSE] * 7) + ([KEYPRESS] * 11) + ([TIMER] * 5) + [TERMINATE]
    kind = random.choice(kinds)
    if kind == MOUSE:
        return Event(kind, button=random.randint(1, 3),
                x=random.randint(0, 640), y=random.randint(0, 480))
    elif kind == KEYPRESS:
        return Event(kind, ctrl=random.randint(1, 7) == 1,
                shift=random.randint(1, 5) == 1,
                key=random.choice(string.ascii_lowercase))
    return Event(kind) # TIMER or TERMINATE


class Event:

    TimerId = 0

    def __init__(self, kind, **kwargs):
        assert kind in {MOUSE, KEYPRESS, TIMER, TERMINATE}
        self.kind = kind
        self.kwargs = kwargs
        if self.kind == TIMER:
            self.kwargs["id"] = Event.TimerId
            Event.TimerId += 1


    def __str__(self):
        if self.kind == MOUSE:
            return "Button {} ({}, {})".format(
                    self.kwargs.get("button", 1), self.kwargs.get("x", -1),
                    self.kwargs.get("y", -1))
        elif self.kind == KEYPRESS:
            return "Key {}{}{}".format(
                    "Ctrl+" if self.kwargs.get("ctrl", False) else "",
                    "Shift+" if self.kwargs.get("shift", False) else "",
                    self.kwargs.get("key", ""))
        elif self.kind == TIMER:
            return "Timer {}".format(self.kwargs.get("id", -1))
        elif self.kind == TERMINATE:
            return "Terminate"
