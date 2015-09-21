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
from Qtrac import coroutine


def main():
    print("Handler Chain #1")
    pipeline = key_handler(mouse_handler(timer_handler()))
    while True:
        event = Event.next()
        if event.kind == Event.TERMINATE:
            break
        pipeline.send(event)

    print("\nHandler Chain #2 (debugging)")
    pipeline = debug_handler(pipeline)
    while True:
        event = Event.next()
        if event.kind == Event.TERMINATE:
            break
        pipeline.send(event)


@coroutine
def debug_handler(successor, file=sys.stdout):
    while True:
        event = (yield)
        file.write("*DEBUG*: {}\n".format(event))
        successor.send(event)


@coroutine
def mouse_handler(successor=None):
    while True:
        event = (yield)
        if event.kind == Event.MOUSE:
            print("Click:   {}".format(event))
        elif successor is not None:
            successor.send(event)


@coroutine
def key_handler(successor=None):
    while True:
        event = (yield)
        if event.kind == Event.KEYPRESS:
            print("Press:   {}".format(event))
        elif successor is not None:
            successor.send(event)


@coroutine
def timer_handler(successor=None):
    while True:
        event = (yield)
        if event.kind == Event.TIMER:
            print("Timeout: {}".format(event))
        elif successor is not None:
            successor.send(event)


if __name__ == "__main__":
    main()
