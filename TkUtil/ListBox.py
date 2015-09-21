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
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
    "..")))
import tkinter as tk
import tkinter.ttk as ttk
import TkUtil.Scrollbar


class ListBox(ttk.Frame):
    """A scrollable tk.ListBox widget

    Note that the kwargs are given to the tk.ListBox not the outer
    ttk.Frame. (You can always configure the frame afterwards.)

    In general:
    listBox.method() or listBox.listbox.method() -> listBox.listbox.method()
    listBox.yscrollbar.method() -> listBox.yscrollbar.method()
    listBox.frame.method() -> listBox.method()
    Exceptions: private methods always go to the frame; methods that are
    in the frame (e.g., bind(), cget(), config() etc.), go to the frame,
    so for those use, say, listBox.listbox.config() etc.
    """

    def __init__(self, master=None, **kwargs):
        super().__init__(master)
        self.frame = self
        self.listbox = tk.Listbox(self, **kwargs)
        self.xscrollbar = TkUtil.Scrollbar.Scrollbar(self,
                command=self.listbox.xview, orient=tk.HORIZONTAL)
        self.yscrollbar = TkUtil.Scrollbar.Scrollbar(self,
                command=self.listbox.yview, orient=tk.VERTICAL)
        self.listbox.configure(yscrollcommand=self.yscrollbar.set,
                xscrollcommand=self.xscrollbar.set)
        self.xscrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        self.yscrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.listbox.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.W, tk.E))
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)


    def __getattr__(self, name):
        # This is only used if attribute lookup fails, so, e.g.,
        # listBox.cget() will succeed (on the frame) without coming
        # here, but listBox.index() will fail (there is no
        # ttk.Frame.index method) and will come here.
        return getattr(self.listbox, name)


if __name__ == "__main__":
    if sys.stdout.isatty():
        application = tk.Tk()
        application.title("ListBox")
        listBox = ListBox(application)
        for i, x in enumerate(("One", "Two", "Three", "Four", "Five",
                "Six", "Seven", "Eight", "Nine", "Ten")):
            listBox.insert(i, x)
        listBox.pack(fill=tk.BOTH, expand=True)
        application.mainloop()
    else:
        print("Loaded OK")
