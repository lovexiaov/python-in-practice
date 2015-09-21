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

import datetime
import getpass
import socket
import sys
import warnings
import rpyc
if sys.version_info[:2] > (3, 1):
    warnings.simplefilter("ignore", ResourceWarning) # For stdlib socket.py
if not sys.stdout.isatty(): # For regression testing
    warnings.simplefilter("ignore", getpass.GetPassWarning)
if sys.version_info[:2] < (3, 3):
    ConnectionError = socket.error


HOST = "localhost"
PORT = 11003


def main():
    username, password = login()
    if username is not None:
        try:
            service = rpyc.connect(HOST, PORT)
            manager = service.root
            sessionId, name = manager.login(username, password)
            print("Welcome, {}, to Meter RPYC".format(name))
            interact(manager, sessionId)
        except ConnectionError as err:
            print("Error: Is the meter server running? {}".format(err))


def login():
    loginName = getpass.getuser()
    username = input("Username [{}]: ".format(loginName))
    if not username:
        username = loginName
    password = getpass.getpass() 
    if not password:
        return None, None
    return username, password


def interact(manager, sessionId):
    accepted = True
    while True:
        if accepted:
            meter = manager.get_job(sessionId)
            if not meter:
                print("All jobs done")
                break
        accepted, reading, reason = get_reading(meter)
        if not accepted:
            continue
        if (not reading or reading == -1) and not reason:
            break
        accepted = submit(manager, sessionId, meter, reading, reason)


def get_reading(meter):
    reading = input("Reading for meter {}: ".format(meter))
    if reading:
        try:
            return True, int(reading), ""
        except ValueError:
            print("Invalid reading")
            return False, 0, ""
    else:
        return True, -1, input("Reason for meter {}: ".format(meter))


def submit(manager, sessionId, meter, reading, reason):
    try:
        now = datetime.datetime.now()
        manager.submit_reading(sessionId, meter, now, reading, reason)
        count, total = manager.get_status(sessionId)
        print("Accepted: you have read {} out of {} readings".format(
                count, total))
        return True
    except (EOFError, rpyc.core.vinegar.GenericException) as err:
        print("Error: {}".format(err))
        return False


if __name__ == "__main__":
    main()
