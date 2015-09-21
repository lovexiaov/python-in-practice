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
import threading
import rpyc
import sys
import MeterMT

PORT = 11003

Manager = MeterMT.Manager()


class MeterService(rpyc.Service):

    def on_connect(self):
        pass


    def on_disconnect(self):
        pass


    exposed_login = Manager.login
    exposed_get_status = Manager.get_status
    exposed_get_job = Manager.get_job


    def exposed_submit_reading(self, sessionId, meter, when, reading,
            reason=""):
        when = datetime.datetime.strptime(str(when)[:19],
                "%Y-%m-%d %H:%M:%S")
        Manager.submit_reading(sessionId, meter, when, reading, reason)


if __name__ == "__main__":
    import rpyc.utils.server
    print("Meter server startup at {}".format(
            datetime.datetime.now().isoformat()[:19]))
    server = rpyc.utils.server.ThreadedServer(MeterService, port=PORT)
    thread = threading.Thread(target=server.start)
    thread.start()
    try:
        if len(sys.argv) > 1: # Notify if called by a GUI client
            with open(sys.argv[1], "wb") as file:
                file.write(b"\n")
        thread.join()
    except KeyboardInterrupt:
        pass
    server.close()
    print("\rMeter server shutdown at {}".format(
            datetime.datetime.now().isoformat()[:19]))
    MeterMT.Manager._dump()
