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
import Event


def main():
    print("Handler Chain #1")
    handler1 = TimerHandler(KeyHandler(MouseHandler(NullHandler())))
    # Could pass None or nothing instead of the NullHandler
    while True:
        event = Event.next()
        if event.kind == Event.TERMINATE:
            break
        handler1.handle(event)

    print("\nHandler Chain #2 (debugging)")
    handler2 = DebugHandler(handler1)
    while True:
        event = Event.next()
        if event.kind == Event.TERMINATE:
            break
        handler2.handle(event)


class NullHandler:

    def __init__(self, successor=None):
        self.__successor = successor


    def handle(self, event):
        if self.__successor is not None:
            self.__successor.handle(event)


class DebugHandler(NullHandler):

    def __init__(self, successor=None, file=sys.stdout):
        super().__init__(successor)
        self.__file = file


    def handle(self, event):
        self.__file.write("*DEBUG*: {}\n".format(event))
        super().handle(event)


class MouseHandler(NullHandler):

    def handle(self, event):
        if event.kind == Event.MOUSE:
            print("Click:   {}".format(event))
        else:
            super().handle(event)


class KeyHandler(NullHandler):

    def handle(self, event):
        if event.kind == Event.KEYPRESS:
            print("Press:   {}".format(event))
        else:
            super().handle(event)


class TimerHandler(NullHandler):

    def handle(self, event):
        if event.kind == Event.TIMER:
            print("Timeout: {}".format(event))
        else:
            super().handle(event)


if __name__ == "__main__":
    main()
