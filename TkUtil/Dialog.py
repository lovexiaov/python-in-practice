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
# Inspired by the Python standard library's dialogs.

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
    "..")))
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as tkfont
Spinbox = ttk.Spinbox if hasattr(ttk, "Spinbox") else tk.Spinbox
import TkUtil

OK_BUTTON =     0b0001
CANCEL_BUTTON = 0b0010
YES_BUTTON =    0b0100
NO_BUTTON =     0b1000

PAD = TkUtil.PAD

class Dialog(tk.Toplevel): # See MeterLogin.py for a simple example subclass

    def __init__(self, master=None, title=None, buttons=OK_BUTTON,
            default=OK_BUTTON):
        master = master or tk._default_root
        super().__init__(master)
        self.withdraw() # hide until ready to show
        if title is not None:
            self.title(title)
        self.buttons = buttons
        self.default = default
        self.acceptButton = None
        self.__create_ui()
        self.__position()
        self.ok = None
        self.deiconify() # show
        if self.grid() is None: # A saner minsize than 1x1
            self.minsize(80, 40)
        else:
            self.minsize(10, 5)
        if self.winfo_viewable():
            self.transient(master)
        self.initialize()
        self.initialFocusWidget.focus() # give focus to first widget
        self.wait_visibility()
        self.grab_set()
        self.wait_window(self)


    def __create_ui(self):
        widget = self.body(self)
        if isinstance(widget, (tuple, list)):
            body, focusWidget = widget
        else:
            body = focusWidget = widget
        self.initialFocusWidget = focusWidget
        buttons = self.button_box(self)
        body.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.W, tk.E))
        buttons.grid(row=1, column=0)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)


    def __position(self):
        self.protocol("WM_DELETE_WINDOW", self.__cancel)
        if self.master is not None:
            self.geometry("+{}+{}".format(self.master.winfo_rootx() + 50,
                self.master.winfo_rooty() + 50))


    def __ok(self, event=None):
        if not self.validate():
            self.initialFocusWidget.focus()
            return
        self.withdraw()
        self.update_idletasks()
        try:
            self.ok = True
            self.apply()
        finally:
            self.__cancel()


    def __cancel(self, event=None):
        if self.ok is None:
            self.ok = False
        self.initialFocusWidget = None
        if self.master is not None:
            self.master.focus()
        self.destroy()


    def initialize(self):
        """Override to execute anything that needs to be done after all
        the widgets have been created"""
        pass


    def add_button(self, master, text, underline, command, default=False,
            shortcut=None):
        button = TkUtil.Button(master, text=text, underline=underline,
                command=command)
        if default:
            button.config(default=tk.ACTIVE)
        button.pack(side=tk.LEFT, padx=PAD, pady=PAD)
        if shortcut is not None and int(button.cget("underline")) != -1:
            self.bind(shortcut, command)
        return button


    def button_box(self, master):
        """Override to create the dialog's buttons; you must return the
        containing widget"""
        frame = ttk.Frame(master)
        if self.buttons & OK_BUTTON:
            self.acceptButton = self.add_button(frame, "OK", 0, self.__ok,
                    self.default == OK_BUTTON, "<Alt-o>")
        if self.buttons & CANCEL_BUTTON:
            self.add_button(frame, "Cancel", 0, self.__cancel,
                    self.default == CANCEL_BUTTON, "<Alt-c>")
        if self.buttons & YES_BUTTON:
            self.acceptButton = self.add_button(frame, "Yes", 0, self.__ok,
                    self.default == YES_BUTTON, "<Alt-y>")
        if self.buttons & NO_BUTTON:
            self.add_button(frame, "No", 0, self.__cancel,
                    self.default == NO_BUTTON, "<Alt-n>")
        self.bind("<Return>", self.__ok, "+")
        self.bind("<Escape>", self.__cancel, "+")
        return frame


    def body(self, master):
        """Override to create the dialog's body; you must return the
        containing widget and the focus widget, or just the containing
        widget"""
        label = ttk.Label(master, text="[Override Dialog.body()]")
        return label


    def validate(self):
        "Override to implement whole dialog validation"
        return True


    def apply(self):
        "Override to implement OK action"
        pass


class Result:

    def __init__(self, value=None):
        self.value = value
        self.ok = False


    def __str__(self):
        return "'{}' {}".format(self.value, self.ok)


class _StrDialog(Dialog):

    def __init__(self, master, title, prompt, result):
        """result must be a Result object; value will contain the str
        result; ok will contain True if the user clicked OK or False if
        they clicked Cancel."""
        self.prompt = prompt
        self.value = tk.StringVar()
        self.value.set(result.value)
        self.result = result
        super().__init__(master, title, OK_BUTTON|CANCEL_BUTTON)


    def body(self, master):
        frame = ttk.Frame(master)
        label = ttk.Label(frame, text=self.prompt)
        label.pack(side=tk.LEFT, fill=tk.X, padx=PAD, pady=PAD)
        entry = ttk.Entry(frame, textvariable=self.value)
        entry.pack(side=tk.LEFT, padx=PAD, pady=PAD)
        return frame, entry


    def apply(self):
        self.result.value = self.value.get()
        self.result.ok = True


class _NumberDialogBase(Dialog): # Abstract base class

    def __init__(self, master, title, prompt, result, minimum=None,
            maximum=None, format=None):
        """result must be a Result object; value will contain the int
        or float result; ok will contain True if the user clicked OK or
        False if they clicked Cancel."""
        self.prompt = prompt
        self.minimum = minimum
        self.maximum = maximum
        self.format = format
        self.value = tk.StringVar()
        self.value.set(result.value)
        self.result = result
        super().__init__(master, title, OK_BUTTON|CANCEL_BUTTON)


class _IntDialog(_NumberDialogBase):

    def body(self, master):
        frame = ttk.Frame(master)
        label = ttk.Label(frame, text=self.prompt)
        label.pack(side=tk.LEFT, fill=tk.X, padx=PAD, pady=PAD)
        self.spinbox = Spinbox(frame, from_=self.minimum, to=self.maximum,
                textvariable=self.value, validate="all")
        self.spinbox.config(validatecommand=(
            self.spinbox.register(self.validate), "%P"))
        self.spinbox.pack(side=tk.LEFT, padx=PAD, pady=PAD)
        return frame, self.spinbox


    def validate(self, number=None):
        return TkUtil.validate_spinbox_int(self.spinbox, number)


    def apply(self):
        self.result.value = int(self.value.get())
        self.result.ok = True


class _FloatDialog(_NumberDialogBase):

    def body(self, master):
        frame = ttk.Frame(master)
        label = ttk.Label(frame, text=self.prompt)
        label.pack(side=tk.LEFT, fill=tk.X, padx=PAD, pady=PAD)
        self.spinbox = Spinbox(frame, from_=self.minimum, to=self.maximum,
                textvariable=self.value, validate="all",
                format=self.format)
        self.spinbox.config(validatecommand=(
            self.spinbox.register(self.validate), "%P"))
        self.spinbox.pack(side=tk.LEFT, padx=PAD, pady=PAD)
        return frame, self.spinbox


    def validate(self, number=None):
        return TkUtil.validate_spinbox_float(self.spinbox, number)


    def apply(self):
        self.result.value = float(self.value.get())
        self.result.ok = True


def get_str(master, title, prompt, initial=""):
    """Returns None if the user cancelled or a string"""
    result = Result(initial)
    _StrDialog(master, title, prompt, result)
    return result.value if result.ok else None


def get_int(master, title, prompt, initial=0, minimum=None,
        maximum=None):
    """Returns None if the user cancelled or an int in the given range"""
    assert minimum is not None and maximum is not None
    result = Result(initial)
    _IntDialog(master, title, prompt, result, minimum, maximum)
    return result.value if result.ok else None


def get_float(master, title, prompt, initial=0.0, minimum=None,
        maximum=None, format="%0.2f"):
    """Returns None if the user cancelled or a float in the given range"""
    assert minimum is not None and maximum is not None
    result = Result(initial)
    _FloatDialog(master, title, prompt, result, minimum, maximum, format)
    return result.value if result.ok else None


if __name__ == "__main__":
    if sys.stdout.isatty():
        application = tk.Tk()
        Dialog(application, "Dialog")
        x = get_str(application, "Get Str", "Name", "test")
        print("str", x)
        x = get_int(application, "Get Int", "Percent")#, 5, 0, 100)
        print("int", x)
        x = get_float(application, "Get Float", "Angle", 90, 0, 90)
        print("float", x)
        application.bind("<Escape>", lambda *args: application.quit())
        application.mainloop()
    else:
        print("Loaded OK")
