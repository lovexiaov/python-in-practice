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

ABOUT = "About"
APPNAME = "ImageScale"
GENERAL = "General"
PAD = "0.75m"
POSITION = "position"
RESTORE = "Restore"
SOURCE, TARGET = ("SOURCE", "TARGET")
VERSION = "1.0.0"
WORKING, CANCELED, TERMINATING, IDLE = ("WORKING", "CANCELED",
        "TERMINATING", "IDLE")

class Canceled(Exception): pass
