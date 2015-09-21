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

import getpass
import tkinter as tk
import tkinter.ttk as ttk
if __name__ == "__main__": # For stand-alone testing with parallel TkUtil
    import os
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
        "..")))
import TkUtil
import TkUtil.Dialog


PAD = "0.75m"


class Result:

    def __init__(self):
        self.username = None
        self.password = None
        self.ok = False


    def __str__(self):
        return "username={} password={} ok={}".format(self.username,
                self.password, self.ok)


class Window(TkUtil.Dialog.Dialog):

    def __init__(self, master, result):
        self.result = result
        super().__init__(master, "Meter — Login",
                TkUtil.Dialog.OK_BUTTON|TkUtil.Dialog.CANCEL_BUTTON)
            

    def initialize(self):
        self.update_ui()


    def body(self, master):
        self.create_widgets(master)
        self.create_layout()
        self.create_bindings()
        return self.frame, self.usernameEntry


    def create_widgets(self, master):
        self.frame = ttk.Frame(master)
        self.usernameLabel = ttk.Label(self.frame, text="Username:",
                underline=-1 if TkUtil.mac() else 0)
        self.usernameEntry = ttk.Entry(self.frame, width=25)
        self.usernameEntry.insert(0, getpass.getuser())
        self.passwordLabel = ttk.Label(self.frame, text="Password:",
                underline=-1 if TkUtil.mac() else 0)
        self.passwordEntry = ttk.Entry(self.frame, width=25, show="•")


    def create_layout(self):
        self.usernameLabel.grid(row=0, column=0, padx=PAD, pady=PAD)
        self.usernameEntry.grid(row=0, column=1, padx=PAD, pady=PAD)
        self.passwordLabel.grid(row=1, column=0, padx=PAD, pady=PAD)
        self.passwordEntry.grid(row=1, column=1, padx=PAD, pady=PAD)


    def validate(self):
        return self.usernameEntry.get() and self.passwordEntry.get()


    def create_bindings(self):
        if not TkUtil.mac():
            self.bind("<Alt-p>", lambda *args: self.passwordEntry.focus())
            self.bind("<Alt-u>", lambda *args: self.usernameEntry.focus())
        self.usernameEntry.bind("<KeyRelease>", self.update_ui)
        self.passwordEntry.bind("<KeyRelease>", self.update_ui)


    def update_ui(self, event=None):
        state = "!" + tk.DISABLED if self.validate() else tk.DISABLED
        self.acceptButton.state((state,))


    def apply(self):
        self.result.username = self.usernameEntry.get()
        self.result.password = self.passwordEntry.get()
        self.result.ok = True


if __name__ == "__main__":
    if sys.stdout.isatty():
        def close(event):
            window.destroy()
            application.quit()
        application = tk.Tk()
        result = Result()
        window = Window(application, result)
        print(result.username, result.password)
        application.bind("<Escape>", close)
        application.mainloop()
    else:
        print("Loaded OK")
