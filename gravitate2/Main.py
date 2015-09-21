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
import tkinter.messagebox as messagebox
Spinbox = ttk.Spinbox if hasattr(ttk, "Spinbox") else tk.Spinbox
if __name__ == "__main__": # For stand-alone testing with parallel TkUtil
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
        "..")))
import About
import Board
import Help
import Options
import Preferences
import Shapes
import TkUtil
import TkUtil.Settings
import TkUtil.Tooltip
from Globals import *


class Window(ttk.Frame):

    def __init__(self, master):
        super().__init__(master, padding=PAD)
        self.create_variables()
        self.create_images()
        self.create_ui()


    def create_variables(self):
        self.helpDialog = None
        settings = TkUtil.Settings.Data
        self.toolbar = None
        self.showToolbar = tk.BooleanVar()
        self.showToolbar.set(settings.get_bool(GENERAL, SHOWTOOLBAR, True))
        self.shapeName = tk.StringVar()
        self.shapeName.set(settings.get_str(GENERAL, SHAPENAME,
                Shapes.Shapes[0].name))
        self.images = {}
        self.statusText = tk.StringVar()
        self.scoreText = tk.StringVar()
        self.zoom = tk.StringVar()
        self.zoom.set(settings.get_int(GENERAL, ZOOM, 100))
        self.restore = settings.get_bool(GENERAL, RESTORE, True)


    def create_ui(self):
        self.create_board() # Must come before (hideable) toolbar and menu
        self.create_menubar()
        if self.showToolbar.get():
            self.toggle_toolbar()
        self.create_statusbar()
        self.create_bindings()
        settings = TkUtil.Settings.Data
        if self.restore:
            position = settings.get_str(GENERAL, POSITION)
            if position is not None:
                self.master.geometry(position)
        self.master.resizable(False, False)


    def create_images(self):
        imagePath = os.path.join(os.path.dirname(
                os.path.realpath(__file__)), "images")
        for name in ([NEW, CLOSE, PREFERENCES, SHAPE, HELP, ABOUT] +
                sorted(Shapes.ShapeForName.keys())):
            self.images[name] = tk.PhotoImage(
                    file=os.path.join(imagePath, name + "_16x16.gif"))


    def create_menubar(self):
        self.menubar = tk.Menu(self.master)
        self.master.config(menu=self.menubar)
        self.create_file_menu()
        self.create_edit_menu()
        self.create_help_menu()


    def create_file_menu(self):
        # Ctrl is nicer than Control for menus
        modifier = TkUtil.menu_modifier()
        fileMenu = tk.Menu(self.menubar, name="apple")
        fileMenu.add_command(label=NEW, underline=0,
                command=self.board.new_game, compound=tk.LEFT,
                image=self.images[NEW], accelerator=modifier + "+N")
        if TkUtil.mac():
            self.master.createcommand("exit", self.close)
        else:
            fileMenu.add_separator()
            fileMenu.add_command(label="Quit", underline=0,
                    command=self.close, compound=tk.LEFT,
                    image=self.images[CLOSE],
                    accelerator=modifier + "+Q")
        self.menubar.add_cascade(label="File", underline=0,
                menu=fileMenu)


    def create_edit_menu(self):
        editMenu = tk.Menu(self.menubar)
        shapeMenu = tk.Menu(editMenu)
        editMenu.add_cascade(label=SHAPE, underline=0,
                menu=shapeMenu, image=self.images[SHAPE],
                compound=tk.LEFT)
        for name in sorted(Shapes.ShapeForName.keys()):
            shape = Shapes.ShapeForName[name]
            shapeMenu.add_radiobutton(label=shape.name,
                    underline=shape.underline, value=shape.name,
                    variable=self.shapeName, compound=tk.LEFT,
                    image=self.images[shape.name])
        if TkUtil.mac():
            self.master.createcommand("::tk::mac::ShowPreferences",
                    self.preferences)
        else:
            editMenu.add_command(label=PREFERENCES + ELLIPSIS, underline=0,
                    command=self.preferences,
                    image=self.images[PREFERENCES], compound=tk.LEFT)
        editMenu.add_checkbutton(label="Show Toolbar", underline=5,
                onvalue=True, offvalue=False, variable=self.showToolbar,
                command=self.toggle_toolbar)
        self.menubar.add_cascade(label="Edit", underline=0,
                menu=editMenu)


    def create_help_menu(self):
        helpMenu = tk.Menu(self.menubar, name="help")
        if TkUtil.mac():
            self.master.createcommand("tkAboutDialog", self.about)
            self.master.createcommand("::tk::mac::ShowHelp", self.help)
        else:
            helpMenu.add_command(label=HELP, underline=0,
                    command=self.help, image=self.images[HELP],
                    compound=tk.LEFT, accelerator="F1")
            helpMenu.add_command(label=ABOUT, underline=0,
                    command=self.about, image=self.images[ABOUT],
                    compound=tk.LEFT)
        self.menubar.add_cascade(label=HELP, underline=0,
                menu=helpMenu)


    def create_board(self):
        settings = TkUtil.Settings.Data
        columns = settings.get_int(BOARD, COLUMNS, Board.DEF_COLUMNS)
        rows = settings.get_int(BOARD, ROWS, Board.DEF_ROWS)
        maxColors = settings.get_int(BOARD, MAXCOLORS,
                Board.DEF_MAX_COLORS)
        delay = settings.get_int(BOARD, DELAY, Board.DEF_DELAY)
        self.board = Board.Board(self.master, self.zoom,
                self.shapeName, self.set_status_text, self.scoreText,
                columns, rows, maxColors, delay)
        self.board.highScore = settings.get_int(BOARD, HIGHSCORE, 0)
        self.board.update_score()
        self.board.pack(fill=tk.BOTH, expand=True)


    def create_toolbar(self):
        self.toolbar = ttk.Frame(self.master)
        newButton = ttk.Button(self.toolbar, text=NEW, takefocus=False,
                image=self.images[NEW], command=self.board.new_game)
        TkUtil.Tooltip.Tooltip(newButton, text="New Game")
        zoomLabel = ttk.Label(self.toolbar, text="Zoom:")
        self.zoomSpinbox = Spinbox(self.toolbar,
                textvariable=self.zoom, from_=Board.MIN_ZOOM,
                to=Board.MAX_ZOOM, increment=Board.ZOOM_INC, width=3,
                justify=tk.RIGHT, validate="all")
        self.zoomSpinbox.config(validatecommand=(
                self.zoomSpinbox.register(self.validate_int), "%P"))
        TkUtil.Tooltip.Tooltip(self.zoomSpinbox, text="Zoom level (%)")
        self.shapeCombobox = ttk.Combobox(self.toolbar, width=8,
                textvariable=self.shapeName, state="readonly",
                values=sorted(Shapes.ShapeForName.keys()))
        TkUtil.Tooltip.Tooltip(self.shapeCombobox, text="Tile Shape")
        TkUtil.add_toolbar_buttons(self.toolbar, (newButton, None,
                zoomLabel, self.zoomSpinbox, self.shapeCombobox))
        self.toolbar.pack(side=tk.TOP, fill=tk.X, before=self.board)


    def validate_int(self, number):
        return TkUtil.validate_spinbox_int(self.zoomSpinbox, number)


    def create_statusbar(self):
        statusBar = ttk.Frame(self.master)
        statusLabel = ttk.Label(statusBar, textvariable=self.statusText)
        statusLabel.grid(column=0, row=0, sticky=(tk.W, tk.E))
        scoreLabel = ttk.Label(statusBar, textvariable=self.scoreText,
                relief=tk.SUNKEN)
        scoreLabel.grid(column=1, row=0)
        TkUtil.Tooltip.Tooltip(scoreLabel,
                text="Current score (High score)")
        statusBar.columnconfigure(0, weight=1)
        statusBar.pack(side=tk.BOTTOM, fill=tk.X)
        self.set_status_text("Click a tile or click File→New for a new "
                "game")


    def set_status_text(self, text):
        self.statusText.set(text)
        self.master.after(SHOW_TIME, lambda: self.statusText.set(""))


    def create_bindings(self):
        # Can't use Ctrl for key bindings
        modifier = TkUtil.key_modifier()
        self.master.bind("<{}-n>".format(modifier), self.board.new_game)
        self.master.bind("<{}-q>".format(modifier), self.close)
        self.master.bind("<F1>", self.help)


    def close(self, event=None):
        settings = TkUtil.Settings.Data
        settings.put(BOARD, COLUMNS, self.board.columns)
        settings.put(BOARD, ROWS, self.board.rows)
        settings.put(BOARD, MAXCOLORS, self.board.maxColors)
        settings.put(BOARD, DELAY, self.board.delay)
        settings.put(BOARD, HIGHSCORE, self.board.highScore)
        settings.put(GENERAL, SHAPENAME, self.shapeName.get())
        settings.put(GENERAL, ZOOM, int(self.zoom.get()))
        settings.put(GENERAL, SHOWTOOLBAR, bool(self.showToolbar.get()))
        settings.put(GENERAL, RESTORE, self.restore)
        if self.restore:
            geometry = TkUtil.geometry_for_str(self.master.geometry())
            position = TkUtil.str_for_geometry(x=geometry.x, y= geometry.y)
            settings.put(GENERAL, POSITION, position)
        TkUtil.Settings.save()
        self.quit()


    def toggle_toolbar(self):
        if self.toolbar is None:
            self.create_toolbar()
        else:
            self.toolbar.pack_forget()
            self.toolbar = None


    def preferences(self):
        oldShapeName = self.shapeName.get()
        oldZoom = self.zoom.get()
        showToolbar = bool(self.showToolbar.get())
        options = Options.Options(False, showToolbar, self.restore,
                self.shapeName, self.zoom, self.board)
        Preferences.Window(self, options)
        if options.ok:
            if options.showToolbar != showToolbar:
                self.showToolbar.set(not showToolbar)
                self.toggle_toolbar()
            self.restore = options.restore
        else:
            self.shapeName.set(oldShapeName)
            self.zoom.set(oldZoom)
        self.focus()


    def help(self, event=None):
        if self.helpDialog is None:
            self.helpDialog = Help.Window(self)
        else:
            self.helpDialog.deiconify()


    def about(self):
        About.Window(self)


if __name__ == "__main__":
    if sys.stdout.isatty():
        application = tk.Tk()
        application.title("Window")
        TkUtil.Settings.DOMAIN = "Qtrac"
        TkUtil.Settings.APPNAME = APPNAME
        TkUtil.Settings.load()
        window = Window(application)
        application.protocol("WM_DELETE_WINDOW", window.close)
        application.mainloop()
    else:
        print("Loaded OK")
