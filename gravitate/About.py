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
import tkinter as tk
import tkinter.font as tkfont
if __name__ == "__main__": # For stand-alone testing with parallel TkUtil
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
        "..")))
import TkUtil
import TkUtil.About
from Globals import *


class Window(TkUtil.About.Window):

    def __init__(self, master):
        super().__init__(master, APPNAME, height=20)
            

    def create_tags(self):
        super().create_tags() # for url tag
        # Don't modify predefined fonts!
        baseFont = tkfont.nametofont("TkDefaultFont")
        size = baseFont.cget("size") # -ve is pixels +ve is points
        bodyFont = tkfont.Font(family=baseFont.cget("family"), size=size)
        titleFont = tkfont.Font(family=baseFont.cget("family"),
                size=((size - 8) if size < 0 else (size + 3)),
                weight=tkfont.BOLD)

        self.text.config(font=bodyFont)
        self.text.tag_config("title", font=titleFont,
                foreground="navyblue", spacing1=3, spacing3=5)
        self.text.tag_config("versions", foreground="darkgreen")
        self.text.tag_config("above5", spacing1=5)
        self.text.tag_config("above3", spacing1=3)


    def populate_text(self):
        self.text.insert(tk.END, "{}\n".format(APPNAME), ("title",
                "center"))
        self.text.insert(tk.END, "Copyright © 2012-13 Qtrac Ltd. "
                "All rights reserved.\n", ("center",))
        self.text.insert(tk.END, "www.qtrac.eu/pipbook.html\n", ("center",
                "url", "above5"))
        self.add_lines("""
This program or module is free software: you can redistribute it
and/or modify it under the terms of the GNU General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version. It is provided for
educational purposes and is distributed in the hope that it will be
useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.""")
        self.add_lines("""
{} was inspired by tile fall/same game which was originally
written for the Amiga and Psion by Adam Dawes.""".format(APPNAME))
        self.text.insert(tk.END, "\n" + TkUtil.about(self.master, APPNAME,
                VERSION), ("versions", "center", "above3"))


if __name__ == "__main__":
    if sys.stdout.isatty():
        application = tk.Tk()
        Window(application)
        application.mainloop()
    else:
        print("Loaded OK")
