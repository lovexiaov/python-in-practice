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
# This module is a simplification and adaptation of the code provided by
# Michael Lange at http://tkinter.unpy.net/wiki/ToolTip

if __name__ == "__main__": # For stand-alone testing with parallel TkUtil
    import os
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
        "..")))
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as tkfont
import TkUtil


class Tooltip:

    def __init__(self, master, text, delay=1200, showTime=10000,
            background="lightyellow"):
        self.master = master
        self.text = text
        self.delay = delay
        self.showTime = showTime
        self.background = background
        self.timerId = None
        self.tip = None
        self.master.bind("<Enter>", self.enter, "+")
        self.master.bind("<Leave>", self.leave, "+")

    
    def enter(self, event=None):
        if self.timerId is None and self.tip is None:
            self.timerId = self.master.after(self.delay, self.show)
        

    def leave(self, event=None):
        if self.timerId is not None:
            id = self.timerId
            self.timerId = None
            self.master.after_cancel(id)
        self.hide()


    def hide(self):
        if self.tip is not None:
            tip = self.tip
            self.tip = None
            tip.destroy()


    def show(self):
        self.leave()
        self.tip = tk.Toplevel(self.master)
        self.tip.withdraw() # Don't show until we have the geometry
        self.tip.wm_overrideredirect(True) # No window decorations etc.
        if TkUtil.mac():
            self.tip.tk.call("::tk::unsupported::MacWindowStyle",
                    "style", self.tip._w, "help", "none")
        label = ttk.Label(self.tip, text=self.text, padding=1,
                background=self.background, wraplength=480,
                relief=None if TkUtil.mac() else tk.GROOVE,
                font=tkfont.nametofont("TkTooltipFont"))
        label.pack()
        x, y = self.position()
        self.tip.wm_geometry("+{}+{}".format(x, y))
        self.tip.deiconify()
        if self.master.winfo_viewable():
            self.tip.transient(self.master)
        self.tip.update_idletasks()
        self.timerId = self.master.after(self.showTime, self.hide)

    
    def position(self):
        tipx = self.tip.winfo_reqwidth()
        tipy = self.tip.winfo_reqheight()
        width = self.tip.winfo_screenwidth()
        height = self.tip.winfo_screenheight()
        y = self.master.winfo_rooty() + self.master.winfo_height()
        if y + tipy > height:
            y = self.master.winfo_rooty() - tipy
        x = self.tip.winfo_pointerx()
        if x < 0:
            x = 0
        elif x + tipx > width:
            x = width - tipx
        return x, y


if __name__ == "__main__":
    if sys.stdout.isatty():
        application = tk.Tk()
        application.title("Tooltip")
        box = tk.Listbox(application)
        box.insert("end", "This is a listbox")
        box.pack(side="top")
        Tooltip(box, text="This is a tooltip with all the options left at "
            " their default values, so this is what you get if you just "
            " give a tooltip text")
        button = tk.Button(application, text="Quit",
                command=application.quit)
        button.pack(side="bottom")
        Tooltip(button, text="Click to Terminate")
        application.mainloop()
    else:
        print("Loaded OK")
