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
import random
import sys
try:
    import ssl
except ImportError:
    ssl = None


_private = {}
_sessionIDkey = 0


def id():
    return _private[_sessionIDkey]


def reset(size=11):
    if ssl is not None and sys.version_info[:2] >= (3, 3):
        sessionId = ssl.RAND_bytes(size)
    else:
        try:
            sessionId = os.urandom(size)
        except NotImplementedError:
            sessionId = ""
            while len(sessionId) < size:
                sessionId += str(random.random())[2:] # Skip leading "0."
            sessionId = sessionId[:size].encode("utf-8")
    _private[_sessionIDkey] = sessionId
    return sessionId


reset()


if __name__ == "__main__":
    sessionId = id()
    print(len(sessionId), type(sessionId))
    print(sessionId)
