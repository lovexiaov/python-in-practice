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

"""
A class that keeps track of dock windows to ensure that they are
shown/hidden as appropriate.

Assumes that areas are gridded (and then immediately removed) and that
dock windows are packed within them.

Dock windows *must* provide an on_close method, _should_ provide a
title property, and _may_ provide a minsize 2-tuple property.
"""

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
    "..")))
import tkinter as tk
import TkUtil


class DockManager:

    def __init__(self, left=None, top=None, bottom=None, right=None):
        self.left = left
        self.top = top
        self.bottom = bottom
        self.right = right
        self.docked = {left: [], top: [], bottom: [], right: []}
        self.xy_for_dock = {} # Use to undock to last undock position


    def dock(self, dock, area):
        if not self.__remove_area(dock): # Wasn't already docked
            self.xy_for_dock[dock] = (dock.winfo_rootx(),
                    dock.winfo_rooty())
        if not len(self.docked[area]):
            area.grid()
        self.docked[area].append(dock)
        dock.pack_forget()
        dock.tk.call("wm", "forget", dock)
        options = {"in": area, "padx": 2, "pady": 2, "fill": tk.X}
        dock.config(relief=tk.GROOVE, borderwidth=2)
        dock.pack(**options)


    def undock(self, dock, x=None, y=None):
        """Warning: On Mac OS X 10.5 undocking works imperfectly.
        Left and right docking work fine though.
        """
        dock.pack_forget()
        dock.config(relief=tk.FLAT, borderwidth=0)
        dock.tk.call("wm", "manage", dock)
        on_close = dock.register(dock.on_close)
        dock.tk.call("wm", "protocol", dock, "WM_DELETE_WINDOW", on_close)
        title = dock.title if hasattr(dock, "title") else "Dock"
        dock.tk.call("wm", "title", dock, title)
        minsize = dock.minsize if hasattr(dock, "minsize") else (60, 30)
        dock.tk.call("wm", "minsize", dock, *minsize)
        dock.tk.call("wm", "resizable", dock, False, False)
        if TkUtil.windows():
            dock.tk.call("wm", "attributes", dock, "-toolwindow", True)
        if x is not None and y is not None:
            self.xy_for_dock[dock] = (x, y)
        x, y = self.xy_for_dock.get(dock, (None, None))
        if x is not None and y is not None:
            dock.tk.call("wm", "geometry", dock, "{:+}{:+}".format(x, y))
        self.__remove_area(dock)


    def hide(self, dock):
        dock.pack_forget()
        dock.tk.call("wm", "forget", dock)
        self.__remove_area(dock)


    def __remove_area(self, dock):
        for area in self.docked:
            if dock in self.docked[area]:
                self.docked[area].remove(dock)
                if not len(self.docked[area]):
                    area.grid_remove()
                return True
        return False


if __name__ == "__main__":
    if not sys.stdout.isatty():
        print("Loaded OK")
