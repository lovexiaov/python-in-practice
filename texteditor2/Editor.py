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
if __name__ == "__main__": # For stand-alone testing with parallel TkUtil
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
        "..")))
import TkUtil.TextEdit
from Globals import *


def report(text=None):
    print(text)


class Editor(TkUtil.TextEdit.TextEdit):

    def __init__(self, master, set_status_text=report, **kwargs):
        super().__init__(master, **kwargs)
        self.set_status_text = set_status_text
        self.filename = None
        for justify in (tk.LEFT, tk.CENTER, tk.RIGHT):
            self.text.tag_configure(justify, justify=justify)


    def is_empty(self):
        end = self.text.index(tk.END)
        if end == "2.0":
            return len(self.text.get("1.0", end).strip()) == 0
        return False


    def align(self, alignment):
        for justify in {tk.LEFT, tk.CENTER, tk.RIGHT} - {alignment}:
            self.text.tag_remove(justify, "1.0", tk.END)
        self.text.tag_add(alignment, "1.0", tk.END)


    def edit_redo(self): # Needed because Redo is always enabled.
        try:
            self.text.edit_redo()
        except tk._tkinter.TclError as err:
            if str(err) != "nothing to redo":
                self.set_status_text("Can't redo: {}".format(err))


    def new(self):
        self.delete("1.0", tk.END)
        self.edit_modified(False)
        self.edit_reset()
        self.filename = None
        self.master.title(APPNAME)
        self.set_status_text("")


    def load(self, filename):
        self.delete("1.0", tk.END)
        try:
            with open(filename, "r", encoding="utf-8") as file:
                self.insert("1.0", file.read())
        except EnvironmentError as err:
            self.set_status_text("Failed to load {}".format(filename))
            return False
        self.mark_set(tk.INSERT, "1.0")
        self.edit_modified(False)
        self.edit_reset()
        self.master.title("{} \u2014 {}".format(os.path.basename(filename),
                APPNAME))
        self.filename = filename
        self.set_status_text("Loaded {}".format(filename))
        return True


    def save(self, filename=None):
        if filename is not None:
            self.filename = filename
        self.master.title("{} \u2014 {}".format(os.path.basename(
                self.filename), APPNAME))
        try:
            with open(self.filename, "w", encoding="utf-8") as file:
                file.write(self.get("1.0", tk.END))
        except EnvironmentError as err:
            self.set_status_text("Failed to save {}".format(self.filename))
            return False
        self.edit_modified(False)
        self.set_status_text("Saved {}".format(self.filename))
        return True


if __name__ == "__main__":
    if sys.stdout.isatty():
        application = tk.Tk()
        application.title("Editor")
        editor = Editor(application)
        editor.pack(fill=tk.BOTH, expand=True)
        editor.insert("end", "This is a test of the Editor.")
        editor.text.focus()
        application.mainloop()
    else:
        print("Loaded OK")
