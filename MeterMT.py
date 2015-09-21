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

import collections
import hashlib
import random
import sys
import threading

random.seed(917) # Predictable random numbers for regression testing

Reading = collections.namedtuple("Reading", "when reading reason username")


class Error(Exception): pass


class ThreadSafeDict:

    def __init__(self, *args, **kwargs):
        self._dict = dict(*args, **kwargs)
        self._lock = threading.Lock()


    def copy(self):
        with self._lock:
            return self.__class__(**self._dict)


    def get(self, key, default=None):
        with self._lock:
            return self._dict.get(key, default)


    def __len__(self):
        with self._lock:
            return len(self._dict)


    def __getitem__(self, key):
        with self._lock:
            return self._dict[key]


    def __setitem__(self, key, value):
        with self._lock:
            self._dict[key] = value


    def __delitem__(self, key):
        with self._lock:
            del self._dict[key]


    def __contains__(self, key):
        with self._lock:
            return key in self._dict


class _MeterDict(ThreadSafeDict):

    def insert_if_missing(self, key, value=None):
        with self._lock:
            if key not in self._dict:
                self._dict[key] = value
                return True
        return False


    def status(self, username):
        count = total = 0
        with self._lock:
            for reading in self._dict.values():
                if reading is not None:
                    total += 1
                    if reading.username == username:
                        count += 1
        return count, total


class Manager:

    SessionId = 0
    SessionIdLock = threading.Lock()
    UsernameForSessionId = ThreadSafeDict()
    ReadingForMeter = _MeterDict()


    def login(self, username, password):
        name = name_for_credentials(username, password)
        if name is None:
            raise Error("Invalid username or password")
        with Manager.SessionIdLock:
            Manager.SessionId += 1
            sessionId = Manager.SessionId
        Manager.UsernameForSessionId[sessionId] = username
        return sessionId, name


    def get_status(self, sessionId):
        username = self._username_for_sessionid(sessionId)
        return Manager.ReadingForMeter.status(username)


    def get_job(self, sessionId):
        self._username_for_sessionid(sessionId)
        while True: # Create fake meter
            kind = random.choice("GE")
            meter = "{}{}".format(kind, random.randint(40000,
                    99999 if kind == "G" else 999999))
            if Manager.ReadingForMeter.insert_if_missing(meter):
                return meter


    def _username_for_sessionid(self, sessionId):
        try:
            return Manager.UsernameForSessionId[sessionId]
        except KeyError:
            raise Error("Invalid session ID")


    def submit_reading(self, sessionId, meter, when, reading,
            reason=""):
        if (not isinstance(reading, int) or reading < 0) and not reason:
            raise Error("Invalid reading")
        if meter not in Manager.ReadingForMeter:
            raise Error("Invalid meter ID")
        username = self._username_for_sessionid(sessionId)
        reading = Reading(when, reading, reason, username)
        Manager.ReadingForMeter[meter] = reading


    @staticmethod
    def _dump(file=sys.stdout):
        ReadingForMeter = Manager.ReadingForMeter.copy()
        for meter, reading in sorted(ReadingForMeter.items()):
            if reading is not None:
                print("{}={}@{}[{}]{}".format(meter, reading.reading,
                        reading.when.isoformat()[:16], reading.reason,
                        reading.username), file=file)


_User = collections.namedtuple("User", "username sha256")

def name_for_credentials(username, password):
    sha = hashlib.sha256()
    sha.update(password.encode("utf-8"))
    user = _User(username, sha.hexdigest())
    return _Users.get(user)

# No locks for read-only data. Returns None for invalid username or password

# Passwords are stored as SHA256 hex digests, e.g.,
#   sha = hashlib.sha256()
#   sha.update(b"pear")         # "pear" is the password
#   digest = sha.hexdigest()    # digest is what's stored as the sha256
_Users = {
    _User("adam",   # Password: adam
    "f7f376a1fcd0d0e11a10ed1b6577c99784d3a6bbe669b1d13fae43eb64634f6e"):
    "Adam Best",
    _User("carol",  # Password: carol
    "4c26d9074c27d89ede59270c0ac14b71e071b15239519f75474b2f3ba63481f5"):
    "Carol Dent",
    _User("eric",   # Password: eric
    "6f9edcd3408cbda14a837e6a44fc5b7f64ccc9a2477c1498fcb13c777ffb9605"):
    "Eric Fawn",
    _User("gwenda", # Password: gwenda
    "b0d0c7e0a2c7251768699b85e2ac9cdee23521ac6b1645fafec35eb93ca8870a"):
    "Gwenda Harris"
    }


if __name__ == "__main__":
    print("Loaded OK")
