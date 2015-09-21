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
import TkUtil.Tooltip

DOCKLEFT = "DockLeft"
DOCKRIGHT = "DockRight"
HIDE = "Hide"
UNDOCK = "Undock"
PAD = TkUtil.PAD


class Window(tk.Frame): # Cannot use a ttk.Frame!

    def __init__(self, master, dockManager, **kwargs):
        super().__init__(master, **kwargs)
        self.dockManager = dockManager
        self.__create_variables()
        self.__create_images()
        self.__create_widgets()
        self.__create_layout()


    def __create_variables(self):
        self.visible = tk.BooleanVar()
        self.visible.set(True)
        self.visible.trace("w", self.show_or_hide)
        self.title = "Dock"
        self.underline = 0
        self.images = {}
        self.area = None
        self.create_variables()


    def create_variables(self):
        "Override to provide additional variables"
        pass


    def __create_images(self):
        imagePath = os.path.join(os.path.dirname(
                os.path.realpath(__file__)), "images")
        for name in (DOCKLEFT, DOCKRIGHT, UNDOCK, HIDE):
            filename = os.path.join(imagePath, name + "_16x16.gif")
            if os.path.exists(filename):
                self.images[name] = tk.PhotoImage(file=filename)
        self.create_images(imagePath)


    def create_images(self, path):
        "Override to provide additional images"
        pass


    def __create_widgets(self):
        self.dockFrame = ttk.Frame(self, relief=tk.RAISED, padding=PAD)
        self.dockLeftButton = ttk.Button(self.dockFrame,
                image=self.images[DOCKLEFT], style="Toolbutton",
                command=self.dock_left)
        TkUtil.Tooltip.Tooltip(self.dockLeftButton, text="Dock Left")
        self.dockRightButton = ttk.Button(self.dockFrame,
                image=self.images[DOCKRIGHT], style="Toolbutton",
                command=self.dock_right)
        TkUtil.Tooltip.Tooltip(self.dockRightButton, text="Dock Right")
        self.dockLabel = ttk.Label(self.dockFrame, text=self.title,
                anchor=tk.CENTER)
        TkUtil.Tooltip.Tooltip(self.dockLabel, text="Drag and drop to "
                "dock elsewhere or to undock")
        self.undockButton = ttk.Button(self.dockFrame,
                image=self.images[UNDOCK], style="Toolbutton",
                command=self.undock)
        TkUtil.Tooltip.Tooltip(self.undockButton, text="Undock")
        self.hideButton = ttk.Button(self.dockFrame,
                image=self.images[HIDE], style="Toolbutton",
                command=lambda *args: self.visible.set(False))
        TkUtil.Tooltip.Tooltip(self.hideButton, text="Hide")
        self.create_widgets()


    def create_widgets(self):
        "Override to provide additional widgets"
        pass


    def __create_layout(self):
        pad = dict(padx=PAD, pady=PAD)
        padW = dict(sticky=tk.W, **pad)
        padWE = dict(sticky=(tk.W, tk.E), **pad)
        self.dockLeftButton.grid(row=0, column=0, sticky=tk.W)
        self.dockRightButton.grid(row=0, column=1, sticky=tk.W)
        ttk.Separator(self.dockFrame).grid(row=0, column=2)
        self.dockLabel.grid(row=0, column=3, sticky=(tk.W, tk.E))
        ttk.Separator(self.dockFrame).grid(row=0, column=4)
        self.undockButton.grid(row=0, column=5, sticky=tk.E)
        self.hideButton.grid(row=0, column=6, sticky=tk.E)
        self.dockFrame.grid(row=0, column=0, columnspan=99, **padWE)
        self.dockFrame.grid_columnconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.create_layout()


    def create_layout(self):
        """Override to layout additional widgets; they should be gridded
        from row 1 and may have up to 99 columns"""
        pass


    def dock_left(self):
        self.area = self.dockManager.left
        self.dockManager.dock(self, self.dockManager.left)
        self.dockFrame.grid()
        self.dockLeftButton.state((TkUtil.DISABLED,))
        self.dockRightButton.state((TkUtil.NOT_DISABLED,))


    def dock_right(self):
        self.area = self.dockManager.right
        self.dockManager.dock(self, self.dockManager.right)
        self.dockFrame.grid()
        self.dockLeftButton.state((TkUtil.NOT_DISABLED,))
        self.dockRightButton.state((TkUtil.DISABLED,))


    def on_close(self):
        if self.area is None or self.area == self.dockManager.right:
            self.dock_right()
        else:
            self.dock_left()


    def undock(self, x=None, y=None):
        self.dockManager.undock(self, x, y)
        self.dockFrame.grid_remove()


    def show_or_hide(self, *args):
        if bool(self.visible.get()):
            self.on_close()
        else:
            self.dockManager.hide(self)


if __name__ == "__main__":
    import sys
    if sys.stdout.isatty():
        application = tk.Tk()
        application.title("Dock")
        dock = Window(application, None)
        dock.pack(fill=tk.BOTH, expand=True)
        dock.bind("<Escape>", lambda *args: application.quit())
        application.bind("<Escape>", lambda *args: application.quit())
        application.mainloop()
    else:
        print("Loaded OK")
