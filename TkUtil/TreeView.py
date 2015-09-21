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


class TreeView(ttk.Frame):
    """A scrollable tk.TreeView widget

    Note that the kwargs are given to the tk.TreeView not the outer
    ttk.Frame. (You can always configure the frame afterwards.)

    To access methods use treeView.xscrollbar, treeView.yscrollbar, or
    treeView.treeview.
    """

    def __init__(self, master=None, **kwargs):
        super().__init__(master)
        self.frame = self
        self.treeview = ttk.Treeview(self, **kwargs)
        self.xscrollbar = TkUtil.Scrollbar.Scrollbar(self,
                command=self.treeview.xview, orient=tk.HORIZONTAL)
        self.yscrollbar = TkUtil.Scrollbar.Scrollbar(self,
                command=self.treeview.yview, orient=tk.VERTICAL)
        self.treeview.configure(yscrollcommand=self.yscrollbar.set,
                xscrollcommand=self.xscrollbar.set)
        self.xscrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        self.yscrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.treeview.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.W, tk.E))
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)


if __name__ == "__main__":
    if sys.stdout.isatty():
        application = tk.Tk()
        application.title("TreeView")
        treeView = TreeView(application)
        for i, x in enumerate(("One", "Two", "Three", "Four", "Five",
                "Six", "Seven", "Eight", "Nine", "Ten")):
            treeView.treeview.insert("", tk.END, str(i), text=x)
            treeView.treeview.insert(str(i), tk.END, text="child of {}"
                    .format(x))
        treeView.pack(fill=tk.BOTH, expand=True)
        application.mainloop()
    else:
        print("Loaded OK")
