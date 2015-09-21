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
import TkUtil.Dialog
from Globals import *


class Window(TkUtil.Dialog.Dialog):

    def __init__(self, master, score, won, newHighScore):
        self.score = score
        self.won = won
        self.newHighScore = newHighScore
        title = "Winner!" if won else "Game Over"
        super().__init__(master, "{} — {}".format(title, APPNAME),
                TkUtil.Dialog.OK_BUTTON)
            

    def initialize(self):
        if self.master is not None:
            self.geometry("+{}+{}".format(self.master.winfo_rootx() + 50,
                self.master.winfo_rooty()))
        self.acceptButton.focus()


    def body(self, master):
        frame = ttk.Frame(master)
        if self.won:
            message = "You won with a score of {:,}!"
            if self.newHighScore:
                message += "\nThat's a new high score!"
        else:
            message = "Game over with a score of {:,}."
        label = ttk.Label(frame, text=message.format(self.score),
                justify=tk.CENTER)
        label.pack(fill=tk.BOTH, padx="7m", pady="4m")
        frame.pack(fill=tk.BOTH)
        return frame


if __name__ == "__main__":
    if sys.stdout.isatty():
        import random
        def close(event):
            window.destroy()
            application.quit()
        application = tk.Tk()
        window = Window(application, random.randint(400, 1600),
                random.choice((True, False)), random.choice((True, False)))
        application.bind("<Escape>", close)
        application.mainloop()
    else:
        print("Loaded OK")
