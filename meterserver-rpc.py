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
import os
import sys
import xmlrpc.server
if sys.version_info[:2] > (3, 1):
    import warnings
    warnings.simplefilter("ignore", ResourceWarning) # For stdlib socket.py
import Meter


HOST = "localhost"
PORT = 11002
PATH = "/meter"


class RequestHandler(xmlrpc.server.SimpleXMLRPCRequestHandler):
    rpc_paths = (PATH,)


def main():
    host, port, notify = handle_commandline()
    manager, server = setup(host, port)
    print("Meter server startup at  {} on {}:{}{}".format(
            datetime.datetime.now().isoformat()[:19], host, port, PATH))
    try:
        if notify:
            with open(notify, "wb") as file:
                file.write(b"\n")
        server.serve_forever()
    except KeyboardInterrupt:
        print("\rMeter server shutdown at {}".format(
                datetime.datetime.now().isoformat()[:19]))
        manager._dump()


def handle_commandline():
    parser = argparse.ArgumentParser(conflict_handler="resolve")
    parser.add_argument("-h", "--host", default=HOST,
            help="hostname [default %(default)s]")
    parser.add_argument("-p", "--port", default=PORT, type=int,
            help="port number [default %(default)d]")
    parser.add_argument("--notify", help="specify a notification file") 
    args = parser.parse_args()
    return args.host, args.port, args.notify


def setup(host, port):
    manager = Meter.Manager()
    server = xmlrpc.server.SimpleXMLRPCServer((host, port),
            requestHandler=RequestHandler, logRequests=False)
    server.register_introspection_functions()
    for method in (manager.login, manager.get_job, manager.submit_reading,
            manager.get_status):
        server.register_function(method)
    return manager, server


if __name__ == "__main__":
    main()
