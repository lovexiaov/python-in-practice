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
import Shapes
import TkUtil
import TkUtil.Dialog
from Globals import *


class Window(TkUtil.Dialog.Dialog):

    def __init__(self, master, options):
        self.options = options
        board = self.options.board
        self.columns = tk.StringVar()
        self.columns.set(board.columns)
        self.rows = tk.StringVar()
        self.rows.set(board.rows)
        self.maxColors = tk.StringVar()
        self.maxColors.set(board.maxColors)
        self.delay = tk.StringVar()
        self.delay.set(board.delay)
        self.restore = tk.BooleanVar()
        self.restore.set(self.options.restore)
        self.showToolbar = tk.BooleanVar()
        self.showToolbar.set(self.options.showToolbar)
        super().__init__(master, "Preferences — {}".format(APPNAME),
                TkUtil.Dialog.OK_BUTTON|TkUtil.Dialog.CANCEL_BUTTON)
            

    def body(self, master):
        self.notebook = ttk.Notebook(master)
        self.notebook.enable_traversal()
        self.generalFrame = ttk.Frame(self.notebook)
        self.create_general_widgets(self.generalFrame)
        self.layout_general_widgets(self.generalFrame)
        self.advancedFrame = ttk.Frame(self.notebook)
        self.create_advanced_widgets(self.advancedFrame)
        self.layout_advanced_widgets(self.advancedFrame)
        self.notebook.add(self.generalFrame, text=GENERAL,
                underline=-1 if TkUtil.mac() else 0, padding=PAD)
        self.notebook.add(self.advancedFrame, text=ADVANCED,
                underline=-1 if TkUtil.mac() else 0, padding=PAD)
        self.notebook.pack(fill=tk.BOTH)
        self.create_bindings()
        return self.notebook


    def create_general_widgets(self, master):
        self.shapeLabel = TkUtil.Label(master, text="Shape", underline=0)
        self.shapeCombobox = ttk.Combobox(master,
                textvariable=self.options.shapeName, state="readonly",
                values=sorted(Shapes.ShapeForName.keys()))
        self.columnsLabel = TkUtil.Label(master, text="Columns",
                underline=2)
        self.columnsSpinbox = Spinbox(master, textvariable=self.columns,
                from_=Board.MIN_COLUMNS, to=Board.MAX_COLUMNS, width=3,
                justify=tk.RIGHT, validate="all")
        self.columnsSpinbox.config(validatecommand=(
            self.columnsSpinbox.register(self.validate_int),
                "columnsSpinbox", "%P"))

        self.rowsLabel = TkUtil.Label(master, text="Rows", underline=0)
        self.rowsSpinbox = Spinbox(master, textvariable=self.rows,
                from_=Board.MIN_ROWS, to=Board.MAX_ROWS, width=3,
                justify=tk.RIGHT, validate="all")
        self.rowsSpinbox.config(validatecommand=(
            self.rowsSpinbox.register(self.validate_int),
                "rowsSpinbox", "%P"))

        self.maxColorsLabel = TkUtil.Label(master, text="Max. Colors",
                underline=0)
        self.maxColorsSpinbox = Spinbox(master,
                textvariable=self.maxColors, from_=Board.MIN_MAX_COLORS,
                to=Board.MAX_MAX_COLORS, width=3, justify=tk.RIGHT,
                validate="all")
        self.maxColorsSpinbox.config(validatecommand=(
            self.maxColorsSpinbox.register(self.validate_int),
                "maxColorsSpinbox", "%P"))


    def layout_general_widgets(self, master):
        pad = dict(padx=PAD, pady=PAD)
        self.shapeLabel.grid(row=0, column=0, sticky=tk.W, **pad)
        self.shapeCombobox.grid(row=0, column=1, sticky=tk.W, columnspan=4,
                **pad)
        ttk.Separator(master).grid(row=1, column=0, columnspan=99,
                sticky=(tk.W, tk.E))
        self.columnsLabel.grid(row=2, column=0, sticky=tk.W, **pad)
        self.columnsSpinbox.grid(row=2, column=1, sticky=tk.W, **pad)
        self.rowsLabel.grid(row=2, column=3, sticky=tk.E, **pad)
        self.rowsSpinbox.grid(row=2, column=4, sticky=tk.E, **pad)
        self.maxColorsLabel.grid(row=3, column=0, sticky=tk.W, **pad)
        self.maxColorsSpinbox.grid(row=3, column=1, sticky=tk.W, **pad)


    def validate_int(self, spinboxName, number):
        return TkUtil.validate_spinbox_int(getattr(self, spinboxName),
                number)


    def create_advanced_widgets(self, master):
        self.delayLabel = TkUtil.Label(master, text="Delay (ms)",
                underline=0)
        self.delaySpinbox = Spinbox(master, textvariable=self.delay,
                from_=Board.MIN_DELAY, to=Board.MAX_DELAY, increment=25,
                width=4, justify=tk.RIGHT, validate="all")
        self.delaySpinbox.config(validatecommand=(
            self.delaySpinbox.register(self.validate_int),
                "delaySpinbox", "%P"))

        self.zoomLabel = TkUtil.Label(master, text="Zoom (%)", underline=0)
        self.zoomSpinbox = Spinbox(master,
                textvariable=self.options.zoom, from_=Board.MIN_ZOOM,
                to=Board.MAX_ZOOM, increment=Board.ZOOM_INC, width=4,
                justify=tk.RIGHT, validate="all")
        self.zoomSpinbox.config(validatecommand=(
            self.zoomSpinbox.register(self.validate_int),
                "zoomSpinbox", "%P"))

        self.showToolbarCheckbutton = TkUtil.Checkbutton(master,
                text="Show Toolbar", underline=5,
                variable=self.showToolbar)

        self.restoreCheckbutton = TkUtil.Checkbutton(master,
                text="Restore Position", underline=0,
                variable=self.restore)


    def layout_advanced_widgets(self, master):
        pad = dict(padx=PAD, pady=PAD)
        options = dict(sticky=tk.W, **pad)
        self.delayLabel.grid(row=0, column=0, **options)
        self.delaySpinbox.grid(row=0, column=1, **options)
        self.zoomLabel.grid(row=1, column=0, **options)
        self.zoomSpinbox.grid(row=1, column=1, **options)
        self.showToolbarCheckbutton.grid(row=2, column=0,
                sticky=(tk.W, tk.E), columnspan=2, **pad)
        self.restoreCheckbutton.grid(row=3, column=0, sticky=(tk.W, tk.E),
                columnspan=2, **pad)


    def create_bindings(self):
        if not TkUtil.mac():
            for letter in "dlmrstz":
                self.bind("<Alt-{}>".format(letter), self.handle_shortcut)
            # Don't need these thanks to Notebook.enable_traversal()
            #self.bind("<Alt-a>", 
            #        lambda event: self.notebook.select(self.advancedFrame))
            #self.bind("<Alt-g>", 
            #        lambda event: self.notebook.select(self.generalFrame))


    def handle_shortcut(self, event):
        key = event.keysym
        tabName = self.notebook.tab(self.notebook.select(), "text")
        methodForTabAndKey = {
                (GENERAL, "l"): self.columnsSpinbox.focus,
                (GENERAL, "m"): self.maxColorsSpinbox.focus,
                (GENERAL, "r"): self.rowsSpinbox.focus,
                (GENERAL, "s"): self.shapeCombobox.focus,
                (ADVANCED, "d"): self.delaySpinbox.focus,
                (ADVANCED, "r"): self.restoreCheckbutton.invoke,
                (ADVANCED, "t"): self.showToolbarCheckbutton.invoke,
                (ADVANCED, "z"): self.zoomSpinbox.focus}
        method = methodForTabAndKey.get((tabName, key))
        if method is not None:
            method()


    def apply(self):
        columns = int(self.columns.get())
        rows = int(self.rows.get())
        maxColors = int(self.maxColors.get())
        board = self.options.board
        newGame = (columns != board.columns or rows != board.rows or
                   maxColors != board.maxColors)
        board.delay = int(self.delay.get())
        self.options.showToolbar = bool(self.showToolbar.get())
        self.options.restore = bool(self.restore.get())
        self.options.ok = True
        if newGame:
            board.columns = columns
            board.rows = rows
            board.maxColors = maxColors
            board.new_game()


if __name__ == "__main__":
    if sys.stdout.isatty():
        import Options
        def close(event):
            window.destroy()
            board.destroy()
            application.quit()
        application = tk.Tk()
        shapeName = tk.StringVar()
        shapeName.set("Square")
        zoom = tk.StringVar()
        zoom.set(100)
        scoreText = tk.StringVar()
        board = Board.Board(application, zoom, shapeName, print, scoreText)
        options = Options.Options(False, True, False, shapeName, zoom,
                board)
        window = Window(application, options)
        if window.ok:
            print(options)
        application.bind("<Escape>", close)
        application.mainloop()
    else:
        print("Loaded OK")
