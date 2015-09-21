Python in Practice by Mark Summerfield

ISBN: 978-0321905635

Copyright © 2012-13 Qtrac Ltd. 

All the example programs and modules are copyright © Qtrac Ltd. 2012-13.
They are free software: you can redistribute them and/or modify them
under the terms of the GNU General Public License as published by the
Free Software Foundation, either version version 3 of the License, or
(at your option) any later version. They are provided for educational
purposes and are distributed in the hope that they will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
Public Licenses (in file gpl-3.0.txt) for more details.

All the book's examples are designed to be educational, and many are
also designed to be useful. I hope that you find them helpful, and are
perhaps able to use some of them as starting points for your own
projects.

Most of the icons are from Debian (e.g., GNOME, Tango, and Oxygen) and
so are open source licensed. (Visit http://www.debian.org/
http://www.gnome.org/ http://tango.freedesktop.org/ and
http://www.oxygen-icons.org/ for more information.)

Here is the list of programs referred to in the book grouped by chapter.
Dependencies on third-party packages are listed in []s with URLs at the
end. All the examples work with Python 3.3+ and many with 3.2 and 3.1.

Chapter 1: Creational Design Patterns
    Abstract Factory: diagram1.py diagram2.py
    Builder: formbuilder.py
    Factory Method: gameboard1.py gameboard2.py gameboard3.py gameboard4.py
Chapter 2: Structural Design Patterns
    Adaptor: render1.py render2.py
    Bridge: barchart1.py barchart2.py barchart3.py
    Composite: stationery1.py stationery2.py
    Decorator: validate1.py validate2.py mediator1d.py mediator2d.py
    Facade: Unpack.py
    Flyweight: pointstore1.py pointstore2.py
    Proxy: imageproxy1.py imageproxy2.py
    Singleton: Session.py
Chapter 3: Behavioral Design Patterns
    Chain of Responsibility: eventhandler1.py eventhandler2.py
    Command: grid.py Command.py
    Interpreter: genome1.py genome2.py genome3.py
    Iterator: Bag1.py Bag2.py Bag3.py
    Mediator: mediator1.py mediator2.py
    Memento (use pickle or json)
    Observer: observer1.py observer2.py
    State: multiplexer1.py multiplexer2.py
    Strategy: tabulator1.py tabulator2.py tabulator3.py tabulator4.py
    Template Method: wordcount1.py wordcount2.py
    Visitor (use map() or list comprehensions or a for loop)
    Case Study: Image/
Chapter 4: High-Level Concurrency
    imagescale-s.py imagescale-t.py imagescale-q-m.py imagescale-m.py
    imagescale-c.py
    whatsnew.py whatsnew-t.py whatsnew-q.py whatsnew-m.py whatsnew-q-m.py
    whatsnew-c.py Feed.py
	[Recommends feedparser and lxml]
    Case Study: imagescale/ [Recommends Cython; numpy]
Chapter 5: Extending Python [Only tested on Linux; should work
			     cross-platform]
    Hyphenate1.py
    Hyphenate2/ [Requires Cython and libhyphen]
    benchmark_Scale.py Scale/Fast.pyx [Requires Cython; numpy]
    Case Study: cyImage/ benchmark_Image.py imagescale-s.py
	imagescale-cy.py imagescale.py [Requires Cython; numpy]
Chapter 6: High-Level Networking
    Meter.py MeterMT.py
    meterclient-rpc.py meterserver-rpc.py meter-rpc.pyw
    meterclient-rpyc.py meterserver-rpyc.py meter-rpyc.pyw [Requires rpyc]
Chapter 7: Creating GUIs with Tkinter
    hello.pyw
    TkUtil/
    currency/
    gravitate/
    gravitate2/
    texteditor/
    texteditor2/

Chapter 8: Openg GL 3D Graphics
    cylinder1.pyw
    cylinder2.pyw
    gravitate3d.pyw

Many chapters also require:
    Qtrac.py
    Image/
    cyImage/

Third-party packages:
    Modern package managers:
	(1) Grab the file: http://python-distribute.org/distribute_setup.py
	(2) In a console execute:
		$ python distribute_setup.py
		$ easy_install pip
	    Note you may have to give a path on windows, e.g.,
		C:\> c:\python33\python c:\Users\<Username>\Downloads\distribute_setup.py
		C:\> c:\python33\scripts\easy_install pip
	See: http://pythonhosted.org/distribute/

    Cython	http://cython.org
    feedparser  http://pypi.python.org/pypi/feedparser
    lxml	http://lxml.de
    numpy	http://numpy.scipy.org
    pyglet	http://www.pyglet.org
    PyOpenGL	http://pyopengl.sourceforge.net
    pypng 	http://pypi.python.org/pypi/pypng
    regex 	http://pypi.python.org/pypi/regex
    rpyc	http://rpyc.sourceforge.net
