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
import re
import tkinter as tk
import tkinter.ttk as ttk
if __name__ == "__main__": # For stand-alone testing with parallel TkUtil
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
        "..")))
import TkUtil
from Globals import *


class Window(tk.Toplevel):

    def __init__(self, master, editor):
        super().__init__(master)
        self.withdraw()
        self.editor = editor
        self.editor.tag_config(FIND_TAG, background="yellow")
        self.editor.tag_config(REPLACE_TAG, background="#C1FFC1")
        self.create_ui()
        self.resizable(False, False)
        self.deiconify()
        if self.winfo_viewable():
            self.transient(master)
        self.wait_visibility()


    def create_ui(self):
        self.create_variables()
        self.create_widgets()
        self.create_layout()
        self.create_bindings()
        self.unextend()
        self.findEntry.focus()


    def create_variables(self):
        self.caseSensitive = tk.IntVar()
        self.caseSensitive.set(0)
        self.wholeWords = tk.IntVar()
        self.wholeWords.set(0)
        self.extensionWidgets = ()
        if not TkUtil.x11():
            self.images = {}
            imagePath = os.path.join(os.path.dirname(
                    os.path.realpath(__file__)), "images")
            for name in (EXTEND, UNEXTEND):
                filename = os.path.join(imagePath, name + "_16x16.gif")
                if os.path.exists(filename):
                    self.images[name] = tk.PhotoImage(file=filename)


    def create_widgets(self):
        self.findLabel = TkUtil.Label(self, text="Find:", underline=1)
        self.findEntry = ttk.Entry(self, width=25)
        self.replaceLabel = TkUtil.Label(self, text="Replace:",
                underline=1)
        self.replaceEntry = ttk.Entry(self, width=25)
        self.caseSensitiveCheckbutton = TkUtil.Checkbutton(self,
                text="Case Sensitive", underline=5,
                variable=self.caseSensitive)
        self.wholeWordsCheckbutton = TkUtil.Checkbutton(self,
                text="Whole Words", underline=0,
                variable=self.wholeWords)
        self.findButton = TkUtil.Button(self, text="Find", underline=0,
                command=self.find, default=tk.ACTIVE, state=tk.DISABLED)
        self.replaceButton = TkUtil.Button(self, text="Replace",
                underline=0, command=self.replace, state=tk.DISABLED)
        self.closeButton = TkUtil.Button(self, text="Close", underline=0,
                command=self.close)
        if TkUtil.x11():
            self.extendButton = TkUtil.ToggleButton(self, text="Extend",
                    underline=1, command=self.toggle_extend)
        else:
            self.extendButton = ttk.Button(self, text="Extend",
                    underline=1, command=self.toggle_extend,
                    image=self.images[UNEXTEND], compound=tk.LEFT)
        self.extensionWidgets = (self.replaceLabel, self.replaceEntry,
                self.replaceButton)


    def create_layout(self):
        pad = dict(padx=PAD, pady=PAD)
        padWE = dict(sticky=(tk.W, tk.E), **pad)
        self.findLabel.grid(row=0, column=0, sticky=tk.W, **pad)
        self.findEntry.grid(row=0, column=1, **padWE)
        self.replaceLabel.grid(row=1, column=0, sticky=tk.W, **pad)
        self.replaceEntry.grid(row=1, column=1, **padWE)
        self.caseSensitiveCheckbutton.grid(row=2, column=0, columnspan=2,
                **padWE)
        self.wholeWordsCheckbutton.grid(row=3, column=0, columnspan=2,
                **padWE)
        self.findButton.grid(row=0, column=2, **padWE)
        self.replaceButton.grid(row=1, column=2, **padWE)
        self.closeButton.grid(row=2, column=2, **padWE)
        self.extendButton.grid(row=3, column=2, **padWE)
        self.grid_columnconfigure(1, weight=1)
        self.minsize(180, 90)
        self.maxsize(600, 150)
        self.geometry("+{}+{}".format(self.master.winfo_rootx() + 200,
                self.master.winfo_rooty() - 30))


    def create_bindings(self):
        self.protocol("WM_DELETE_WINDOW", self.close)
        if not TkUtil.mac():
            self.bind("<Alt-c>", self.close)
            self.bind("<Alt-e>", lambda *args: self.replaceEntry.focus())
            self.bind("<Alt-f>", self.find)
            self.bind("<Alt-i>", lambda *args: self.findEntry.focus())
            self.bind("<Alt-r>", self.replace)
            self.bind("<Alt-s>",
                    lambda *args: self.caseSensitiveCheckbutton.invoke())
            self.bind("<Alt-w>",
                    lambda *args: self.wholeWordsCheckbutton.invoke())
            self.bind("<Alt-x>", lambda *args: self.extendButton.invoke())
        self.bind("<Return>", self.find)
        self.bind("<Escape>", self.close)
        self.findEntry.bind("<KeyRelease>", self.update_ui)
        self.replaceEntry.bind("<KeyRelease>", self.update_ui)


    def update_ui(self, event=None):
        state = "!" + tk.DISABLED if self.findEntry.get() else tk.DISABLED
        self.findButton.state((state,))
        self.replaceButton.state((state,))
        # We allow the replace button to be enabled even if there's no
        # replacement text since the user might want to replace
        # something with nothing.


    def find(self, event=None):
        text = self.findEntry.get()
        assert text
        length = len(text)
        caseInsensitive = not self.caseSensitive.get()
        wholeWords = self.wholeWords.get()
        if wholeWords:
            text = r"\m{}\M".format(re.escape(text)) # Tcl regex syntax
        self.editor.tag_remove(FIND_TAG, "1.0", tk.END)
        insert = self.editor.index(tk.INSERT)
        start = self.editor.search(text, insert, nocase=caseInsensitive,
                regexp=wholeWords)
        if start and start == insert:
            start = self.editor.search(text, "{} +{} char".format(
                    insert, length), nocase=caseInsensitive,
                    regexp=wholeWords)
        if start:
            self.editor.mark_set(tk.INSERT, start)
            self.editor.see(start)
            end = "{} +{} char".format(start, length)
            self.editor.tag_add(FIND_TAG, start, end)
            return start, end
        return None, None


    def replace(self, event=None):
        start, end = self.find()
        if start is not None and end is not None:
            self.editor.tag_remove(FIND_TAG, start, end)
            self.editor.edit_separator()
            self.editor.delete(start, end)
            self.editor.insert(start, self.replaceEntry.get(), REPLACE_TAG)
            self.editor.edit_separator()
            # tkinter.Text for Tk 8.5.11 doesn't support replace()


    def close(self, event=None):
        self.editor.tag_remove(FIND_TAG, "1.0", tk.END)
        self.editor.tag_remove(REPLACE_TAG, "1.0", tk.END)
        self.withdraw()


    def toggle_extend(self, event=None):
        if self.extendButton.instate((TkUtil.NOT_SELECTED,)):
            self.extend()
        else:
            self.unextend()


    def extend(self):
        self.extendButton.state((TkUtil.SELECTED,))
        self.extendButton.config(text="Unextend",
                underline=3 if not TkUtil.mac() else -1)
        if not TkUtil.x11():
            self.extendButton.config(image=self.images[UNEXTEND])
        self.title("Find and Replace \u2014 {}".format(APPNAME))
        for widget in self.extensionWidgets:
            widget.grid()


    def unextend(self):
        self.extendButton.state((TkUtil.NOT_SELECTED,))
        self.extendButton.config(text="Extend",
                underline=1 if not TkUtil.mac() else -1)
        if not TkUtil.x11():
            self.extendButton.config(image=self.images[EXTEND])
        self.title("Find \u2014 {}".format(APPNAME))
        for widget in self.extensionWidgets:
            widget.grid_remove()


if __name__ == "__main__":
    if sys.stdout.isatty():
        application = tk.Tk()
        window = tk.Text(application)
        window.insert(tk.END, """This is some text and here is some
more. And this is yet more and more and MORE. And moreover there's
overmore to come some more.""")
        window.pack()
        find = Window(application, window)
        application.bind("<Control-q>", lambda *args: application.quit())
        window.bind("<Control-q>", lambda *args: application.quit())
        application.geometry("+0+200")
        application.mainloop()
    else:
        print("Loaded OK")
