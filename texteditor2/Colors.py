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
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.colorchooser as colorchooser
Spinbox = ttk.Spinbox if hasattr(ttk, "Spinbox") else tk.Spinbox
if __name__ == "__main__": # For stand-alone testing with parallel TkUtil
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
        "..")))
import TkUtil
import TkUtil.Dock
from Globals import *


FOREGROUND, BACKGROUND = ("FOREGROUND", "BACKGROUND")


class Dock(TkUtil.Dock.Window):

    def create_variables(self):
        self.title = "Colors"
        self.__swatches = {}
        self.__foreground = "#000"
        self.__background = "#FFF"


    def create_widgets(self):
        swatch = TkUtil.swatch(self.foreground, outline="#FFF")
        self.__swatches[self.foreground] = swatch
        self.foregroundButton = ttk.Button(self, text="Foreground ",
                image=swatch, compound=tk.RIGHT,
                command=lambda: self.__set_color(FOREGROUND))
        swatch = self.__get_swatch(self.background)
        self.backgroundButton = ttk.Button(self, text="Background ",
                image=swatch, compound=tk.RIGHT,
                command=lambda: self.__set_color(BACKGROUND))


    def create_layout(self):
        padWE = dict(sticky=(tk.W, tk.E), padx=PAD, pady=PAD)
        self.foregroundButton.grid(row=1, column=0, **padWE)
        self.backgroundButton.grid(row=2, column=0, **padWE)


    @property
    def foreground(self):
        return self.__foreground


    @foreground.setter
    def foreground(self, color):
        self.__set_color(FOREGROUND, color)


    @property
    def background(self):
        return self.__background


    @background.setter
    def background(self, color):
        self.__set_color(BACKGROUND, color)


    def __set_color(self, which, color=None):
        if color is None:
            title = "Choose the {} color".format("background"
                    if which == BACKGROUND else "foreground")
            _, color = colorchooser.askcolor(parent=self, title=title,
                    initialcolor=self.background if which == BACKGROUND
                    else self.foreground)
        if color is not None:
            if which == BACKGROUND:
                self.__background = color
                swatch = self.__get_swatch(color)
                self.backgroundButton.config(image=swatch)
                self.event_generate("<<BackgroundChange>>")
            else:
                self.__foreground = color
                swatch = self.__get_swatch(color)
                self.foregroundButton.config(image=swatch)
                self.event_generate("<<ForegroundChange>>")


    def __get_swatch(self, color):
        swatch = self.__swatches.get(color)
        if swatch is None:
            swatch = TkUtil.swatch(color)
            self.__swatches[color] = swatch
        return swatch


    def __set_foreground_style(self, *args):
        self.event_generate("<<ForegroundStyleChange>>")


    def __set_foreground_width(self, *args):
        self.event_generate("<<ForegroundWidthChange>>")


if __name__ == "__main__":
    if sys.stdout.isatty():
        def on_foreground_change(dock):
            print("foreground", dock.foreground)
        def on_background_change(dock):
            print("background", dock.background)

        application = tk.Tk()
        application.title("Colors")
        dock = Dock(application, None)
        dock.pack(fill=tk.BOTH, expand=True)
        # Since tkinter doesn't support the event.data field we must access
        # the data ourselves
        dock.bind("<<ForegroundChange>>",
                lambda *args: on_foreground_change(dock))
        dock.bind("<<BackgroundChange>>",
                lambda *args: on_background_change(dock))

        dock.bind("<Escape>", lambda *args: application.quit())
        application.bind("<Escape>", lambda *args: application.quit())
        application.mainloop()
    else:
        print("Loaded OK")
