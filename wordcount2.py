#!/usr/bin/env python3
# Copyright © 2012-13 Qtrac Ltd. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. It is provided for educational
# purposes and is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.

import abc
import html.parser
import os
import re
import sys


def main():
    if len(sys.argv) == 1 or sys.argv[1] in {"-h", "--help"}:
        print("usage: {} <files>".format(os.path.basename(sys.argv[0])))
        sys.exit(1)
    count_words_in_files(sys.argv[1:])


def count_words_in_files(files):
    total = 0
    for filename in files:
        count = count_words(filename)
        if count is not None:
            total += count
            print("{:9,} words in {}".format(count, filename))
    print("total: {:,} words".format(total))


def count_words(filename):
    for wordCounter in (PlainTextWordCounter, HtmlWordCounter):
        if wordCounter.can_count(filename):
            return wordCounter.count(filename)


class AbstractWordCounter(
        metaclass=abc.ABCMeta):

    @staticmethod
    @abc.abstractmethod
    def can_count(filename):
        pass


    @staticmethod
    @abc.abstractmethod
    def count(filename):
        pass


class PlainTextWordCounter(AbstractWordCounter):

    @staticmethod
    def can_count(filename):
        return filename.lower().endswith(".txt")


    @staticmethod
    def count(filename):
        if not PlainTextWordCounter.can_count(filename):
            return 0
        regex = re.compile(r"\w+")
        total = 0
        with open(filename, encoding="utf-8") as file:
            for line in file:
                for _ in regex.finditer(line):
                    total += 1
        return total


class HtmlWordCounter(AbstractWordCounter):

    class __HtmlParser(html.parser.HTMLParser):

        def __init__(self):
            super().__init__()
            self.regex = re.compile(r"\w+")
            self.inText = True
            self.text = []
            self.count = 0


        def handle_starttag(self, tag, attrs):
            if tag in {"script", "style"}:
                self.inText = False


        def handle_endtag(self, tag):
            if tag in {"script", "style"}:
                self.inText = True
            else:
                for _ in self.regex.finditer(" ".join(self.text)):
                    self.count += 1
                self.text = []


        def handle_data(self, text):
            if self.inText:
                text = text.rstrip()
                if text:
                    self.text.append(text)


    @staticmethod
    def can_count(filename):
        return filename.lower().endswith((".htm", ".html"))


    @staticmethod
    def count(filename):
        if not HtmlWordCounter.can_count(filename):
            return 0
        parser = HtmlWordCounter.__HtmlParser()
        with open(filename, encoding="utf-8") as file:
            parser.feed(file.read())
        return parser.count


if __name__ == "__main__":
    main()
