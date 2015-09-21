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


class Options:

    def __init__(self, restoreWindow, restoreFont, restoreSession, blink):
        self.restoreWindow = restoreWindow
        self.restoreFont = restoreFont
        self.restoreSession = restoreSession
        self.blink = blink


    def __str__(self):
        return ("restoreWindow={} restoreFont={} restoreSession={} "
                "blink={}".format(self.restoreWindow, self.restoreFont,
                self.restoreSession, self.blink))
