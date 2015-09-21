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
import re
import socket
import sys
import urllib.request
if sys.version_info[:2] < (3, 2):
    from xml.sax.saxutils import escape
else:
    import warnings
    warnings.simplefilter("ignore", ResourceWarning) # For stdlib socket.py
    warnings.simplefilter("ignore", DeprecationWarning) # For etree
    from html import escape
try:
    import feedparser
except ImportError:
    feedparser = None
    print("using a simple built-in RSS parser: see "
          "http://pypi.python.org/pypi/feedparser/ "
          "for a full-featured RSS and Atom parser")
try:
    import lxml.etree as etree
except ImportError:
    import xml.parsers.expat # for ExpatError
    import xml.etree.ElementTree as etree


Feed = collections.namedtuple("Feed", "title url")


def iter(filename):
    name = None
    with open(filename, "rt", encoding="utf-8") as file:
        for line in file:
            line = line.rstrip()
            if not line or line.startswith("#"):
                continue
            if name is None:
                name = line
            else:
                yield Feed(name, line)
                name = None


def read(feed, limit, timeout=10):
    try:
        with urllib.request.urlopen(feed.url, None, timeout) as file:
            data = file.read()
        body = _parse(data, limit)
        if body:
            body = ["<h2>{}</h2>\n".format(escape(feed.title))] + body
            return True, body
        return True, None
    except (ValueError, urllib.error.HTTPError, urllib.error.URLError,
            etree.ParseError, socket.timeout) as err:
        return False, "Error: {}: {}".format(feed.url, err)


if feedparser is not None:
    def _parse(data, limit):
        output = []
        feed = feedparser.parse(data) # Atom + RSS
        for entry in feed["entries"]:
            title = entry.get("title")
            link = entry.get("link")
            if title:
                if link:
                    output.append('<li><a href="{}">{}</a></li>'.format(
                            link, escape(title)))
                else:
                    output.append('<li>{}</li>'.format(escape(title)))
            if limit and len(output) == limit:
                break
        if output:
            return ["<ul>"] + output + ["</ul>"]
else:
    def _parse(data, limit):
        tree = etree.fromstring(data)
        output = []
        # RSS
        prefix = ""
        tag = "*/item"
        if tree.find(tag) is None:
            prefix = "{http://purl.org/rss/1.0/}"
            tag = prefix + "item"
        for element in tree.findall(tag):
            title = element.find(prefix + "title")
            link = element.find(prefix + "link")
            if link is None:
                link = element.find("guid")
            _maybe_append(output, title, link)
            if limit and len(output) == limit:
                break
        if output:
            return ["<ul>"] + output + ["</ul>"]


def _maybe_append(output, title, link):
    if title is not None and title.text:
        if link is not None and link.text:
            output.append('<li><a href="{}">{}</a></li>'.format(link.text,
                    escape(title.text)))
        else:
            output.append('<li>{}</li>'.format(escape(title.text)))
