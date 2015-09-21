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

import argparse
import datetime
import getpass
import socket
import sys
import xmlrpc.client
import warnings
if sys.version_info[:2] > (3, 1):
    warnings.simplefilter("ignore", ResourceWarning) # For stdlib socket.py
if not sys.stdout.isatty(): # For regression testing
    warnings.simplefilter("ignore", getpass.GetPassWarning)
if sys.version_info[:2] < (3, 3):
    ConnectionError = socket.error


HOST = "localhost"
PORT = 11002
PATH = "/meter"


def main():
    host, port = handle_commandline()
    username, password = login()
    if username is not None:
        try:
            manager = xmlrpc.client.ServerProxy("http://{}:{}{}".format(
                    host, port, PATH))
            sessionId, name = manager.login(username, password)
            print("Welcome, {}, to Meter RPC".format(name))
            interact(manager, sessionId)
        except xmlrpc.client.Fault as err:
            print(err)
        except ConnectionError as err:
            print("Error: Is the meter server running? {}".format(err))


def handle_commandline():
    parser = argparse.ArgumentParser(conflict_handler="resolve")
    parser.add_argument("-h", "--host", default=HOST,
            help="hostname [default %(default)s]")
    parser.add_argument("-p", "--port", default=PORT, type=int,
            help="port number [default %(default)d]")
    args = parser.parse_args()
    return args.host, args.port


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
    except (xmlrpc.client.Fault, ConnectionError) as err:
        print(err)
        return False


if __name__ == "__main__":
    main()
