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


class Dock(TkUtil.Dock.Window):

    def create_variables(self):
        self.title = "Display"
        self.__wordWrap = tk.StringVar()
        self.__wordWrap.set("Word")
        self.__wordWrap.trace("w", self.__set_word_wrap)
        self.__blockCursor = tk.IntVar()
        self.__blockCursor.set(False)
        self.__blockCursor.trace("w", self.__set_block_cursor)
        self.__lineSpacing = tk.StringVar()
        self.__lineSpacing.set(0)
        self.__lineSpacing.trace("w", self.__set_line_spacing)


    def create_widgets(self):
        self.wordWrapLabel = ttk.Label(self, text="Wrap:")
        self.wordWrapCombobox = ttk.Combobox(self, state="readonly",
                values=["None", "Character", "Word"],
                textvariable=self.__wordWrap, width=10)
        self.blockCursorCheckbutton = ttk.Checkbutton(self,
                text="Block Cursor", variable=self.__blockCursor)
        self.lineSpacingLabel = ttk.Label(self, text="Line Spacing:")
        self.lineSpacingSpinbox = tk.Spinbox(self, from_=0, to=32,
                width=3, validate="all", justify=tk.RIGHT,
                textvariable=self.__lineSpacing)
        self.lineSpacingSpinbox.config(validatecommand=(
                self.lineSpacingSpinbox.register(self.__validate_int),
                    "lineSpacingSpinbox", "%P"))


    def create_layout(self):
        pad = dict(padx=PAD, pady=PAD)
        padW = dict(sticky=tk.W, **pad)
        padWE = dict(sticky=(tk.W, tk.E), **pad)
        self.wordWrapLabel.grid(row=1, column=0, **padW)
        self.wordWrapCombobox.grid(row=1, column=1, columnspan=2, **padWE)
        self.blockCursorCheckbutton.grid(row=2, column=0, columnspan=3,
                **padWE)
        self.lineSpacingLabel.grid(row=3, column=0, columnspan=2, **padW)
        self.lineSpacingSpinbox.grid(row=3, column=2, stick=tk.E, **pad)


    def __set_word_wrap(self, *args):
        self.event_generate("<<WordWrapChanged>>")


    def __set_block_cursor(self, *args):
        self.event_generate("<<BlockCursorChanged>>")


    def __set_line_spacing(self, *args):
        self.event_generate("<<LineSpacingChanged>>")


    def __validate_int(self, spinbox, number):
        spinbox = getattr(self, spinbox)
        return TkUtil.validate_spinbox_int(spinbox, number)


    @property
    def word_wrap(self):
        wrap = self.__wordWrap.get().lower()
        if wrap == "character":
            wrap = "char"
        return wrap


    @word_wrap.setter
    def word_wrap(self, value):
        if value.lower() == "char":
            value = "character"
        self.__wordWrap.set(value.title())


    @property
    def block_cursor(self):
        return bool(self.__blockCursor.get())


    @block_cursor.setter
    def block_cursor(self, value):
        self.__blockCursor.set(value)


    @property
    def line_spacing(self):
        return int(self.__lineSpacing.get())


    @line_spacing.setter
    def line_spacing(self, value):
        self.__lineSpacing.set(value)


if __name__ == "__main__":
    if sys.stdout.isatty():
        application = tk.Tk()
        application.title("Display")
        dock = Dock(application, None)
        dock.pack(fill=tk.BOTH, expand=True)
        dock.bind("<Escape>", lambda *args: application.quit())
        application.bind("<Escape>", lambda *args: application.quit())
        application.mainloop()
    else:
        print("Loaded OK")
