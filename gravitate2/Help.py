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

import os
import re
import tkinter as tk
import tkinter.ttk as ttk
if __name__ == "__main__": # For stand-alone testing with parallel TkUtil
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
        "..")))
import TkUtil
from Globals import *


_TEXT = """\
The aim of the game is to remove all the tiles from the board.

When a tile is clicked, that tile, and any vertically or
horizontally adjoining tiles of the same color, are removed.
(If there are no adjoining tiles the click has no effect.)

The more tiles removed in one go, the more points you score!

Keyboard users can navigate using the arrow keys and
delete by pressing the spacebar."""


class Window(tk.Toplevel):

    def __init__(self, master):
        super().__init__(master)
        self.withdraw()
        self.title("Help \u2014 {}".format(APPNAME))
        self.create_ui()
        self.reposition()
        self.resizable(False, False)
        self.deiconify()
        if self.winfo_viewable():
            self.transient(master)
        self.wait_visibility()


    def create_ui(self):
        self.helpLabel = ttk.Label(self, text=_TEXT, background="white",
                justify=tk.CENTER)
        self.closeButton = TkUtil.Button(self, text="Close", underline=0)
        self.helpLabel.pack(anchor=tk.N, expand=True, fill=tk.BOTH,
                padx=PAD, pady=PAD, ipadx="2m", ipady="2m")
        self.closeButton.pack(anchor=tk.S)
        self.protocol("WM_DELETE_WINDOW", self.close)
        if not TkUtil.mac():
            self.bind("<Alt-c>", self.close)
        self.bind("<Escape>", self.close)
        self.bind("<Expose>", self.reposition)


    def reposition(self, event=None):
        if self.master is not None:
            self.geometry("+{}+{}".format(self.master.winfo_rootx() + 50,
                self.master.winfo_rooty() + 50))


    def close(self, event=None):
        self.withdraw()


if __name__ == "__main__":
    if sys.stdout.isatty():
        application = tk.Tk()
        window = Window(application)
        application.bind("<Control-q>", lambda *args: application.quit())
        window.bind("<Control-q>", lambda *args: application.quit())
        application.mainloop()
    else:
        print("Loaded OK")
