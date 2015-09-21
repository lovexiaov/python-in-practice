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

import abc
import collections
import sys
import textwrap
if sys.version_info[:2] < (3, 2):
    from xml.sax.saxutils import escape
else:
    from html import escape

# Thanks to Nick Coghlan for these!
if sys.version_info[:2] >= (3, 3):
    class Renderer(metaclass=abc.ABCMeta):

        @classmethod
        def __subclasshook__(Class, Subclass):
            if Class is Renderer:
                attributes = collections.ChainMap(*(Superclass.__dict__
                        for Superclass in Subclass.__mro__))
                methods = ("header", "paragraph", "footer")
                if all(method in attributes for method in methods):
                    return True
            return NotImplemented
else:
    class Renderer(metaclass=abc.ABCMeta):

        @classmethod
        def __subclasshook__(Class, Subclass):
            if Class is Renderer:
                needed = {"header", "paragraph", "footer"}
                for Superclass in Subclass.__mro__:
                    for meth in needed.copy():
                        if meth in Superclass.__dict__:
                            needed.discard(meth)
                    if not needed:
                        return True
            return NotImplemented


MESSAGE = """This is a very short {} paragraph that demonstrates
the simple {} class."""

def main():
    paragraph1 = MESSAGE.format("plain-text", "TextRenderer")
    paragraph2 = """This is another short paragraph just so that we can
see two paragraphs in action."""
    title = "Plain Text"
    textPage = Page(title, TextRenderer(22))
    textPage.add_paragraph(paragraph1)
    textPage.add_paragraph(paragraph2)
    textPage.render()

    print()

    paragraph1 = MESSAGE.format("HTML", "HtmlRenderer")
    title = "HTML"
    file = sys.stdout
    htmlPage = Page(title, HtmlRenderer(HtmlWriter(file)))
    htmlPage.add_paragraph(paragraph1)
    htmlPage.add_paragraph(paragraph2)
    htmlPage.render()

    try:
        page = Page(title, HtmlWriter())
        page.render()
        print("ERROR! rendering with an invalid renderer")
    except TypeError as err:
        print(err)


class Page:

    def __init__(self, title, renderer):
        if not isinstance(renderer, Renderer):
            raise TypeError("Expected object of type Renderer, got {}".
                    format(type(renderer).__name__))
        self.title = title
        self.renderer = renderer
        self.paragraphs = []


    def add_paragraph(self, paragraph):
        self.paragraphs.append(paragraph)


    def render(self):
        self.renderer.header(self.title)
        for paragraph in self.paragraphs:
            self.renderer.paragraph(paragraph)
        self.renderer.footer()


class TextRenderer:

    def __init__(self, width=80, file=sys.stdout):
        self.width = width
        self.file = file
        self.previous = False


    def header(self, title):
        self.file.write("{0:^{2}}\n{1:^{2}}\n".format(title,
                "=" * len(title), self.width))


    def paragraph(self, text):
        if self.previous:
            self.file.write("\n")
        self.file.write(textwrap.fill(text, self.width))
        self.file.write("\n")
        self.previous = True


    def footer(self):
        pass


class HtmlWriter:

    def __init__(self, file=sys.stdout):
        self.file = file


    def header(self):
        self.file.write("<!doctype html>\n<html>\n")


    def title(self, title):
        self.file.write("<head><title>{}</title></head>\n".format(
                escape(title)))

    def start_body(self):
        self.file.write("<body>\n")


    def body(self, text):
        self.file.write("<p>{}</p>\n".format(escape(text)))


    def end_body(self):
        self.file.write("</body>\n")


    def footer(self):
        self.file.write("</html>\n")


class HtmlRenderer:

    def __init__(self, htmlWriter):
        self.htmlWriter = htmlWriter


    def header(self, title):
        self.htmlWriter.header()
        self.htmlWriter.title(title)
        self.htmlWriter.start_body()


    def paragraph(self, text):
        self.htmlWriter.body(text)


    def footer(self):
        self.htmlWriter.end_body()
        self.htmlWriter.footer()


if __name__ == "__main__":
    main()
