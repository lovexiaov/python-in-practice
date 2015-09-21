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
#
# This module is a simplification and adaptation of the standard
# library's ScrolledText module.

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
    "..")))
import tkinter as tk
import tkinter.ttk as ttk
import TkUtil.Scrollbar


class TextEdit(ttk.Frame):
    """A scrollable tk.Text widget

    Note that the kwargs are given to the tk.Text not the outer
    ttk.Frame. (You can always configure the frame afterwards.)

    In general:
    textEdit.method() or textEdit.text.method() -> textEdit.text.method()
    textEdit.yscrollbar.method() -> textEdit.yscrollbar.method()
    textEdit.frame.method() -> textEdit.method()
    Exceptions: private methods always go to the frame; methods that are
    in the frame (e.g., bind(), cget(), config() etc.), go to the frame,
    so for those use, say, textEdit.text.config() etc.
    """

    def __init__(self, master=None, **kwargs):
        super().__init__(master)
        self.frame = self
        self.text = tk.Text(self, **kwargs)
        self.xscrollbar = TkUtil.Scrollbar.Scrollbar(self,
                command=self.text.xview, orient=tk.HORIZONTAL)
        self.yscrollbar = TkUtil.Scrollbar.Scrollbar(self,
                command=self.text.yview, orient=tk.VERTICAL)
        self.text.configure(yscrollcommand=self.yscrollbar.set,
                xscrollcommand=self.xscrollbar.set)
        self.xscrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        self.yscrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.text.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.W, tk.E))
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)


    def __getattr__(self, name):
        # This is only used if attribute lookup fails, so, e.g.,
        # textEdit.cget() will succeed (on the frame) without coming
        # here, but textEdit.index() will fail (there is no
        # ttk.Frame.index method) and will come here.
        return getattr(self.text, name)


if __name__ == "__main__":
    if sys.stdout.isatty():
        application = tk.Tk()
        application.title("TextEdit")
        textEdit = TextEdit(application, wrap=tk.NONE)
        textEdit.pack(fill=tk.BOTH, expand=True)
        def check():
            textEdit.frame.config(borderwidth=2)
            print("frame", textEdit.frame.cget("borderwidth"))
            print("yscrollbar", textEdit.yscrollbar.fraction(5, 5))
            textEdit.insert("end",
                "This is a test of the method delegation.\n" * 20)
            print("text", textEdit.text.index(tk.INSERT))
            print("text", textEdit.index(tk.INSERT))
        textEdit.text.focus()
        application.after(50, check)
        application.mainloop()
    else:
        print("Loaded OK")
