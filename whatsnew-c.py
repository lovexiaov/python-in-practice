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
import multiprocessing
import os
import sys
import tempfile
import webbrowser
import Feed
import Qtrac


def main():
    limit, concurrency = handle_commandline()
    Qtrac.report("starting...")
    datafile = os.path.join(os.path.dirname(__file__), "whatsnew.dat")
    filename = os.path.join(tempfile.gettempdir(), "whatsnew.html") 
    canceled = False
    with open(filename, "wt", encoding="utf-8") as file:
        write_header(file)
        pipeline = create_pipeline(limit, concurrency, file)
        try:
            for i, feed in enumerate(Feed.iter(datafile)):
                pipeline.send((feed, i % concurrency))
        except KeyboardInterrupt:
            Qtrac.report("canceling...")
            canceled = True
        write_footer(file, results.ok, results.todo, canceled,
                concurrency)
    if not canceled:
        webbrowser.open(filename)


def handle_commandline():
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--limit", type=int, default=0,
            help="the maximum items per feed [default: unlimited]")
    parser.add_argument("-c", "--concurrency", type=int,
            default=multiprocessing.cpu_count() * 4,
            help="specify the concurrency (for debugging and "
                "timing) [default: %(default)d]")
    args = parser.parse_args()
    return args.limit, args.concurrency


def write_header(file):
    file.write("<!doctype html>\n")
    file.write("<html><head><title>What's New</title></head>\n")
    file.write("<body><h1>What's New</h1>\n")


def write_footer(file, ok, todo, canceled, concurrency):
    file.write("</body></html>\n")
    Qtrac.report("read {}/{} feeds using {} coroutines{}".format(ok, todo,
            concurrency, " [canceled]" if canceled else ""))
    print()


def create_pipeline(limit, concurrency, file):
    pipeline = None
    sink = results(file)
    for who in range(concurrency):
        pipeline = reader(pipeline, sink, limit, who)
    return pipeline


@Qtrac.coroutine
def reader(receiver, sink, limit, me):
    while True:
        feed, who = (yield)
        if who == me:
            ok, result = Feed.read(feed, limit)
            if not ok:
                Qtrac.report(result, True)
                result = None
            else:
                Qtrac.report("read {} at {}".format(feed.title, feed.url))
            sink.send(result)
        elif receiver is not None:
            receiver.send((feed, who))


@Qtrac.coroutine
def results(file):
    while True:
        result = (yield)
        results.todo += 1
        if result is not None:
            results.ok += 1
            for item in result:
                file.write(item)
results.todo = results.ok = 0


if __name__ == "__main__":
    main()
