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
import Preferences
import TkUtil
from Globals import *


class Window(ttk.Frame):

    def __init__(self, master):
        super().__init__(master, padding=PAD)
        self.create_variables()
        self.create_images()
        self.create_ui()


    def create_variables(self):
        self.images = {}
        self.statusText = tk.StringVar()
        self.scoreText = tk.StringVar()
        self.helpDialog = None


    def create_images(self):
        imagePath = os.path.join(os.path.dirname(
                os.path.realpath(__file__)), "images")
        for name in (NEW, CLOSE, PREFERENCES, HELP, ABOUT):
            self.images[name] = tk.PhotoImage(
                    file=os.path.join(imagePath, name + "_16x16.gif"))


    def create_ui(self):
        self.create_board()
        self.create_menubar()
        self.create_statusbar()
        self.create_bindings()
        self.master.resizable(False, False)


    def create_menubar(self):
        self.menubar = tk.Menu(self.master)
        self.master.config(menu=self.menubar)
        self.create_file_menu()
        self.create_help_menu()


    def create_file_menu(self):
        modifier = TkUtil.menu_modifier()
        fileMenu = tk.Menu(self.menubar, name="apple")
        fileMenu.add_command(label=NEW, underline=0,
                command=self.board.new_game, compound=tk.LEFT,
                image=self.images[NEW], accelerator=modifier + "+N")
        if TkUtil.mac():
            self.master.createcommand("exit", self.close)
            self.master.createcommand("::tk::mac::ShowPreferences",
                    self.preferences)
        else:
            fileMenu.add_separator()
            fileMenu.add_command(label=PREFERENCES + ELLIPSIS, underline=0,
                    command=self.preferences,
                    image=self.images[PREFERENCES], compound=tk.LEFT)
            fileMenu.add_separator()
            fileMenu.add_command(label="Quit", underline=0,
                    command=self.close, compound=tk.LEFT,
                    image=self.images[CLOSE],
                    accelerator=modifier + "+Q")
        self.menubar.add_cascade(label="File", underline=0,
                menu=fileMenu)


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
        self.board = Board.Board(self.master, self.set_status_text,
                self.scoreText)
        self.board.update_score()
        self.board.pack(fill=tk.BOTH, expand=True)


    def create_statusbar(self):
        statusBar = ttk.Frame(self.master)
        statusLabel = ttk.Label(statusBar, textvariable=self.statusText)
        statusLabel.grid(column=0, row=0, sticky=(tk.W, tk.E))
        scoreLabel = ttk.Label(statusBar, textvariable=self.scoreText,
                relief=tk.SUNKEN)
        scoreLabel.grid(column=1, row=0)
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
        self.quit()


    def preferences(self):
        Preferences.Window(self, self.board)
        self.master.focus()


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
        window = Window(application)
        application.protocol("WM_DELETE_WINDOW", window.close)
        application.mainloop()
    else:
        print("Loaded OK")
