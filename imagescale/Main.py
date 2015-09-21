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
import multiprocessing
import sys
import threading
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog as filedialog
import tkinter.messagebox as messagebox
Spinbox = ttk.Spinbox if hasattr(ttk, "Spinbox") else tk.Spinbox
if __name__ == "__main__": # For stand-alone testing with parallel TkUtil
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
        "..")))
import About
import TkUtil
import TkUtil.Settings
import ImageScale
from Globals import *


ReportLock = threading.Lock()


class Window(ttk.Frame):

    def __init__(self, master):
        super().__init__(master, padding=PAD)
        self.create_variables()
        self.create_ui()
        self.sourceEntry.focus()


    def create_variables(self):
        settings = TkUtil.Settings.Data
        self.sourceText = tk.StringVar()
        self.targetText = tk.StringVar()
        self.statusText = tk.StringVar()
        self.statusText.set("Choose or enter folders, then click Scale...")
        self.dimensionText = tk.StringVar()
        self.restore = settings.get_bool(GENERAL, RESTORE, True)
        self.total = self.copied = self.scaled = 0
        self.worker = None
        self.state = multiprocessing.Manager().Value("i", IDLE)


    def create_ui(self):
        self.create_widgets()
        self.layout_widgets()
        self.create_bindings()
        settings = TkUtil.Settings.Data
        if self.restore:
            position = settings.get_str(GENERAL, POSITION)
            if position is not None:
                self.master.geometry(position)
        self.master.resizable(False, False)


    def create_widgets(self):
        self.sourceLabel = ttk.Label(self, text="Source Folder:",
                underline=-1 if TkUtil.mac() else 1)
        self.sourceEntry = ttk.Entry(self, width=30,
                textvariable=self.sourceText)
        self.sourceButton = TkUtil.Button(self, text="Source...",
                underline=0, command=lambda *args:
                    self.choose_folder(SOURCE))
        self.helpButton = TkUtil.Button(self, text="Help", underline=0,
                command=self.help)
        self.targetLabel = ttk.Label(self, text="Target Folder:",
                underline=-1 if TkUtil.mac() else 1)
        self.targetEntry = ttk.Entry(self, width=30,
                textvariable=self.targetText)
        self.targetButton = TkUtil.Button(self, text="Target...",
                underline=0, command=lambda *args:
                    self.choose_folder(TARGET))
        self.aboutButton = TkUtil.Button(self, text="About", underline=1,
                command=self.about)
        self.statusLabel = ttk.Label(self, textvariable=self.statusText)
        self.scaleButton = TkUtil.Button(self, text="Scale",
                underline=1, command=self.scale_or_cancel,
                default=tk.ACTIVE, state=tk.DISABLED)
        self.quitButton = TkUtil.Button(self, text="Quit", underline=0,
                command=self.close)
        self.dimensionLabel = ttk.Label(self, text="Max. Dimension:",
                underline=-1 if TkUtil.mac() else 6)
        self.dimensionCombobox = ttk.Combobox(self,
                textvariable=self.dimensionText, state="readonly",
                values=("50", "100", "150", "200", "250", "300", "350",
                        "400", "450", "500"))
        TkUtil.set_combobox_item(self.dimensionCombobox, "400")


    def layout_widgets(self):
        pad = dict(padx=PAD, pady=PAD)
        padWE = dict(sticky=(tk.W, tk.E), **pad)
        self.sourceLabel.grid(row=0, column=0, sticky=tk.W, **pad)
        self.sourceEntry.grid(row=0, column=1, columnspan=3, **padWE)
        self.sourceButton.grid(row=0, column=4, **pad)
        self.targetLabel.grid(row=1, column=0, sticky=tk.W, **pad)
        self.targetEntry.grid(row=1, column=1, columnspan=3, **padWE)
        self.targetButton.grid(row=1, column=4, **pad)
        self.dimensionLabel.grid(row=2, column=0, sticky=tk.W, **pad)
        self.dimensionCombobox.grid(row=2, column=1, **padWE)
        self.helpButton.grid(row=2, column=3, **pad)
        self.scaleButton.grid(row=2, column=4, **pad)
        self.aboutButton.grid(row=3, column=3, **pad)
        self.quitButton.grid(row=3, column=4, **pad)
        self.statusLabel.grid(row=3, column=0, columnspan=3, **padWE)
        self.grid()


    def create_bindings(self):
        if not TkUtil.mac():
            self.master.bind("<Alt-a>", lambda *args:
                    self.targetEntry.focus())
            self.master.bind("<Alt-b>", self.about)
            self.master.bind("<Alt-c>", self.scale_or_cancel)
            self.master.bind("<Alt-h>", self.help)
            self.master.bind("<Alt-i>", lambda *args:
                    self.dimensionCombobox.focus())
            self.master.bind("<Alt-o>", lambda *args:
                    self.sourceEntry.focus())
            self.master.bind("<Alt-q>", self.close)
            self.master.bind("<Alt-s>", lambda *args: self.choose_folder(
                    SOURCE))
            self.master.bind("<Alt-t>", lambda *args: self.choose_folder(
                    TARGET))
            self.master.bind("<F1>", self.help)
        self.sourceEntry.bind("<KeyRelease>", self.update_ui)
        self.targetEntry.bind("<KeyRelease>", self.update_ui)
        self.master.bind("<Return>", self.scale_or_cancel)


    def close(self, event=None):
        settings = TkUtil.Settings.Data
        settings.put(GENERAL, RESTORE, self.restore)
        if self.restore:
            geometry = TkUtil.geometry_for_str(self.master.geometry())
            position = TkUtil.str_for_geometry(x=geometry.x, y= geometry.y)
            settings.put(GENERAL, POSITION, position)
        TkUtil.Settings.save()
        if self.worker is not None and self.worker.is_alive():
            self.state.value = TERMINATING
            self.update_ui()
            self.worker.join() # Wait for worker to finish
        self.quit()


    def help(self, event=None):
        paras = [
"""Reads all the images in the source directory and produces smoothly
scaled copies in the target directory."""]
        messagebox.showinfo("Help — {}".format(APPNAME),
                "\n\n".join([para.replace("\n", " ") for para in paras]),
                parent=self)


    def about(self, event=None):
        About.Window(self)


    def update_ui(self, *args):
        guiState = self.state.value
        if guiState == WORKING:
            text = "Cancel"
            underline = 0 if not TkUtil.mac() else -1
            state = "!" + tk.DISABLED
        elif guiState in {CANCELED, TERMINATING}:
            text = "Canceling..."
            underline = -1
            state = tk.DISABLED
        elif guiState == IDLE:
            text = "Scale"
            underline = 1 if not TkUtil.mac() else -1
            state = ("!" + tk.DISABLED if self.sourceText.get() and
                     self.targetText.get() else tk.DISABLED)
        self.scaleButton.state((state,))
        self.scaleButton.config(text=text, underline=underline)
        state = tk.DISABLED if guiState != IDLE else "!" + tk.DISABLED
        for widget in (self.sourceEntry, self.sourceButton,
                self.targetEntry, self.targetButton):
            widget.state((state,))
        self.master.update() # Make sure the GUI refreshes


    def choose_folder(self, which):
        if which == SOURCE:
            name, mustexist, variable = "Source", True, self.sourceText
        else:
            name, mustexist, variable = "Target", False, self.targetText
        path = filedialog.askdirectory(parent=self,
                title="Choose {} Folder — {}".format(name, APPNAME),
                mustexist=mustexist)
        if path:
            variable.set(os.path.normpath(os.path.realpath(path)))
            self.update_ui()


    def scale_or_cancel(self, event=None):
        if self.scaleButton.instate((tk.DISABLED,)):
            return
        if self.scaleButton.cget("text") == "Cancel":
            self.state.value = CANCELED
            self.update_ui()
        else:
            self.state.value = WORKING
            self.update_ui()
            self.scale()


    def scale(self):
        self.total = self.copied = self.scaled = 0
        self.configure(cursor="watch")
        self.statusText.set("Scaling...")
        self.master.update() # Make sure the GUI refreshes
        target = self.targetText.get()
        if not os.path.exists(target):
            os.makedirs(target)
        self.worker = threading.Thread(target=ImageScale.scale, args=(
                int(self.dimensionText.get()), self.sourceText.get(),
                target, self.report_progress, self.state,
                self.when_finished))
        self.worker.daemon = True
        self.worker.start() # returns immediately


    def report_progress(self, future):
        if self.state.value in {CANCELED, TERMINATING}:
            return
        with ReportLock:    # Serializes calls to Window.report_progress()
            self.total += 1 # and accesses to self.total, etc.
            if future.exception() is None:
                result = future.result()
                self.copied += result.copied
                self.scaled += result.scaled
                name = os.path.basename(result.name)
                self.statusText.set("{} {}".format(
                        "Copied" if result.copied else "Scaled", name))
                self.master.update() # Make sure the GUI refreshes


    # Must only be called by the single worker thread when it has finished
    def when_finished(self):
        self.state.value = IDLE
        self.configure(cursor="arrow")
        self.update_ui()
        result = "Copied {} Scaled {}".format(self.copied, self.scaled)
        difference = self.total - (self.copied + self.scaled)
        if difference: # This will kick in if the user canceled
            result += " Skipped {}".format(difference)
        self.statusText.set(result)
        self.master.update() # Make sure the GUI refreshes


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
