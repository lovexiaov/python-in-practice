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
# This module is based on Fredrik Lundh's code:
# http://effbot.org/zone/tkinter-autoscrollbar.htm

import tkinter.ttk as ttk


class Scrollbar(ttk.Scrollbar):

    def set(self, first, last):
        if float(first) <= 0.0 and float(last) >= 1.0:
            self.grid_remove()
        else:
            self.grid()
        super().set(first, last)


    def pack(self, *args, **kwargs):
        raise NotImplementedError()


    def place(self, *args, **kwargs):
        raise NotImplementedError()


if __name__ == "__main__":
    import sys
    if not sys.stdout.isatty():
        print("Loaded OK")
