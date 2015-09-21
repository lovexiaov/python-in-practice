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
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
    "..")))
import tkinter as tk
import Main
import TkUtil
import TkUtil.Settings
from Globals import *


def main():
    application = tk.Tk()
    application.withdraw()
    application.title(APPNAME)
    TkUtil.Settings.DOMAIN = "Qtrac"
    TkUtil.Settings.APPNAME = APPNAME
    settings = TkUtil.Settings.load()
    blink = settings.get_bool(GENERAL, BLINK, True)
    application.option_add("*tearOff", False) # Avoid ugly tear menu line
    application.option_add("*insertOffTime", 300 if blink else 0, 100)
    TkUtil.set_application_icons(application, os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "images"))
    filename = sys.argv[1] if len(sys.argv) > 1 else None
    window = Main.Window(application, filename)
    application.protocol("WM_DELETE_WINDOW", window.close)
    application.deiconify()
    application.mainloop()


main()
