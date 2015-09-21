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
import tkinter as tk
import tkinter.ttk as ttk
Spinbox = ttk.Spinbox if hasattr(ttk, "Spinbox") else tk.Spinbox
if __name__ == "__main__": # For stand-alone testing with parallel TkUtil
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
        "..")))
import Board
import TkUtil
import TkUtil.Dialog
from Globals import *


class Window(TkUtil.Dialog.Dialog):

    def __init__(self, master, board):
        self.board = board
        super().__init__(master, "Preferences \u2014 {}".format(APPNAME),
                TkUtil.Dialog.OK_BUTTON|TkUtil.Dialog.CANCEL_BUTTON)
            

    def body(self, master):
        self.create_variables()
        self.create_widgets(master)
        self.create_layout()
        self.create_bindings()
        return self.frame, self.columnsSpinbox


    def create_variables(self):
        self.columns = tk.StringVar()
        self.columns.set(self.board.columns)
        self.rows = tk.StringVar()
        self.rows.set(self.board.rows)
        self.maxColors = tk.StringVar()
        self.maxColors.set(self.board.maxColors)


    def create_widgets(self, master):
        self.frame = ttk.Frame(master)
        self.columnsLabel = TkUtil.Label(self.frame, text="Columns",
                underline=2)
        self.columnsSpinbox = Spinbox(self.frame,
                textvariable=self.columns, from_=Board.MIN_COLUMNS,
                to=Board.MAX_COLUMNS, width=3, justify=tk.RIGHT,
                validate="all")
        self.columnsSpinbox.config(validatecommand=(
            self.columnsSpinbox.register(self.validate_int),
                "columnsSpinbox", "%P"))
        self.rowsLabel = TkUtil.Label(self.frame, text="Rows",
                underline=0)
        self.rowsSpinbox = Spinbox(self.frame, textvariable=self.rows,
                from_=Board.MIN_ROWS, to=Board.MAX_ROWS, width=3,
                justify=tk.RIGHT, validate="all")
        self.rowsSpinbox.config(validatecommand=(
            self.rowsSpinbox.register(self.validate_int),
                "rowsSpinbox", "%P"))
        self.maxColorsLabel = TkUtil.Label(self.frame, text="Max. Colors",
                underline=0)
        self.maxColorsSpinbox = Spinbox(self.frame,
                textvariable=self.maxColors, from_=Board.MIN_MAX_COLORS,
                to=Board.MAX_MAX_COLORS, width=3, justify=tk.RIGHT,
                validate="all")
        self.maxColorsSpinbox.config(validatecommand=(
            self.maxColorsSpinbox.register(self.validate_int),
                "maxColorsSpinbox", "%P"))


    def create_layout(self):
        padW = dict(sticky=tk.W, padx=PAD, pady=PAD)
        padWE = dict(sticky=(tk.W, tk.E), padx=PAD, pady=PAD)
        self.columnsLabel.grid(row=0, column=0, **padW)
        self.columnsSpinbox.grid(row=0, column=1, **padWE)
        self.rowsLabel.grid(row=1, column=0, **padW)
        self.rowsSpinbox.grid(row=1, column=1, **padWE)
        self.maxColorsLabel.grid(row=2, column=0, **padW)
        self.maxColorsSpinbox.grid(row=2, column=1, **padWE)


    def validate_int(self, spinboxName, number):
        return TkUtil.validate_spinbox_int(getattr(self, spinboxName),
                number)


    def create_bindings(self):
        if not TkUtil.mac():
            self.bind("<Alt-l>", lambda *args: self.columnsSpinbox.focus())
            self.bind("<Alt-r>", lambda *args: self.rowsSpinbox.focus())
            self.bind("<Alt-m>",
                    lambda *args: self.maxColorsSpinbox.focus())


    def apply(self):
        columns = int(self.columns.get())
        rows = int(self.rows.get())
        maxColors = int(self.maxColors.get())
        newGame = (columns != self.board.columns or
                   rows != self.board.rows or
                   maxColors != self.board.maxColors)
        if newGame:
            self.board.columns = columns
            self.board.rows = rows
            self.board.maxColors = maxColors
            self.board.new_game()


if __name__ == "__main__":
    if sys.stdout.isatty():
        def close(event):
            application.quit()
        application = tk.Tk()
        scoreText = tk.StringVar()
        board = Board.Board(application, print, scoreText)
        window = Window(application, board)
        application.bind("<Escape>", close)
        board.bind("<Escape>", close)
        application.mainloop()
        print(board.columns, board.rows, board.maxColors)
    else:
        print("Loaded OK")
