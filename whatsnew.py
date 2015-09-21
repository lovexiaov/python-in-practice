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
import os
import sys
import tempfile
import webbrowser
import Feed
import Qtrac


def main():
    limit = handle_commandline()
    filename = os.path.join(tempfile.gettempdir(), "whatsnew.html") 
    canceled = False
    todo = done = 0
    with open(filename, "wt", encoding="utf-8") as file:
        file.write("<!doctype html>\n")
        file.write("<html><head><title>What's New</title></head>\n")
        file.write("<body><h1>What's New</h1>\n")
        todo, done, canceled = write_body(file, limit)
        file.write("</body></html>\n")
    Qtrac.report("read {}/{} feeds{}".format(done, todo, " [canceled]" if
            canceled else ""))
    print()
    if not canceled:
        webbrowser.open(filename)


def handle_commandline():
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--limit", type=int, default=0,
            help="the maximum items per feed [default: unlimited]")
    args = parser.parse_args()
    return args.limit


def write_body(file, limit):
    canceled = False
    todo = done = 0
    filename = os.path.join(os.path.dirname(__file__), "whatsnew.dat")
    for feed in Feed.iter(filename):
        todo += 1
        try:
            ok, result = Feed.read(feed, limit)
            if not ok:
                Qtrac.report(result, True)
            elif result is not None:
                Qtrac.report("read {} at {}".format(feed.title, feed.url))
                for item in result:
                    file.write(item)
                done += 1
        except KeyboardInterrupt:
            Qtrac.report("canceling...")
            canceled = True
            break
    return todo, done, canceled


if __name__ == "__main__":
    main()
