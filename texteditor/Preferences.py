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

import tkinter as tk
import tkinter.ttk as ttk
if __name__ == "__main__": # For stand-alone testing with parallel TkUtil
    import os
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
        "..")))
import TkUtil
import TkUtil.Dialog
import TkUtil.Tooltip
from Globals import *


class Window(TkUtil.Dialog.Dialog):

    def __init__(self, master, options):
        self.options = options
        super().__init__(master, "Preferences \u2014 {}".format(APPNAME),
                TkUtil.Dialog.OK_BUTTON|TkUtil.Dialog.CANCEL_BUTTON)
            

    def body(self, master):
        self.create_variables()
        self.create_widgets(master)
        self.create_layout()
        self.create_bindings()
        return self.frame, self.restoreWindowCheckbutton


    def create_variables(self):
        self.restoreWindow = tk.BooleanVar()
        self.restoreWindow.set(self.options.restoreWindow)
        self.restoreFont = tk.BooleanVar()
        self.restoreFont.set(self.options.restoreFont)
        self.restoreSession = tk.BooleanVar()
        self.restoreSession.set(self.options.restoreSession)
        self.blink = tk.BooleanVar()
        self.blink.set(self.options.blink)


    def create_widgets(self, master):
        self.frame = ttk.Frame(master)
        self.restoreFrame = ttk.Labelframe(self.frame, text="Restore")
        self.restoreWindowCheckbutton = TkUtil.Checkbutton(
                self.restoreFrame, text="Window Position and Size",
                underline=0, variable=self.restoreWindow)
        TkUtil.Tooltip.Tooltip(self.restoreWindowCheckbutton,
                "Restore Toolbars and Window Position and Size at Startup")
        self.restoreFontCheckbutton = TkUtil.Checkbutton(self.restoreFrame,
                text="Font Settings", underline=0,
                variable=self.restoreFont)
        TkUtil.Tooltip.Tooltip(self.restoreFontCheckbutton,
                "Restore the Last Used Font Settings at Startup")
        self.restoreSessionCheckbutton = TkUtil.Checkbutton(
                self.restoreFrame, text="Session", underline=0,
                variable=self.restoreSession)
        TkUtil.Tooltip.Tooltip(self.restoreSessionCheckbutton,
                "Open the Last Edited File at Startup")
        self.otherFrame = ttk.Labelframe(self.frame, text="Other")
        self.blinkCheckbutton = TkUtil.Checkbutton(self.otherFrame,
                text="Blinking Cursor", underline=0, variable=self.blink)
        TkUtil.Tooltip.Tooltip(self.blinkCheckbutton,
                "Switch Cursor Blink On or Off")


    def create_layout(self):
        options = dict(fill=tk.X, expand=True, padx=PAD, pady=PAD)
        for widget in (self.restoreWindowCheckbutton,
                self.restoreFontCheckbutton,
                self.restoreSessionCheckbutton, self.blinkCheckbutton,
                self.restoreFrame, self.otherFrame):
            widget.pack(**options)


    def create_bindings(self):
        if not TkUtil.mac():
            self.bind("<Alt-b>",
                    lambda *args: self.blinkCheckbutton.invoke())
            self.bind("<Alt-f>",
                    lambda *args: self.restoreFontCheckbutton.invoke())
            self.bind("<Alt-s>",
                    lambda *args: self.restoreSessionCheckbutton.invoke())
            self.bind("<Alt-w>",
                    lambda *args: self.restoreWindowCheckbutton.invoke())


    def apply(self):
        self.options.restoreWindow = bool(self.restoreWindow.get())
        self.options.restoreFont = bool(self.restoreFont.get())
        self.options.restoreSession = bool(self.restoreSession.get())
        self.options.blink = bool(self.blink.get())


if __name__ == "__main__":
    if sys.stdout.isatty():
        import Options
        def close(event):
            window.destroy()
            application.quit()
        application = tk.Tk()
        application.bind("<Escape>", close)
        options = Options.Options(False, False, False, False)
        window = Window(application, options)
        application.mainloop()
        print(options)
    else:
        print("Loaded OK")
