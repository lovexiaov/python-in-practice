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
import os
import platform
import re
import sys
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as tkfont


SELECTED = "selected"
NOT_SELECTED = "!" + SELECTED
DISABLED = "disabled"
NOT_DISABLED = "!" + DISABLED
TOGGLE_BUTTON_STYLE = "Toggle.TButton"
PAD = "0.75m"


def mac():
    return tk._default_root.tk.call("tk", "windowingsystem") == "aqua"

def windows():
    return tk._default_root.tk.call("tk", "windowingsystem") == "win32"

def x11():
    return tk._default_root.tk.call("tk", "windowingsystem") == "x11"

# Ctrl is nicer than Control for menus
def menu_modifier():
    return "Command" if mac() else "Ctrl"
# Control is necessary for key bindings
def key_modifier():
    return "Command" if mac() else "Control"


_GEOMETRY_RX = re.compile(r"^=?(?:(?P<width>\d+)x(?P<height>\d+))?"
        r"(?P<x>[-+]\d+)(?P<y>[-+]\d+)$")
Geometry = collections.namedtuple("Geometry", "width height x y")


def geometry_for_str(geometry):
    """Returns a Geometry named tuple with int values; or None"""
    match = _GEOMETRY_RX.match(geometry)
    if match is not None:
        width = int(match.group("width"))
        height = int(match.group("height"))
        if not(width == 1 and height == 1):
            x = int(match.group("x"))
            y = int(match.group("y"))
            return Geometry(width, height, x, y)


def str_for_geometry(*, width=None, height=None, x=None, y=None):
    """Returns a geometry string based on one or two pairs of numbers"""
    if width is None:
        return "{:+}{:+}".format(x if x is not None else 0,
                y if y is not None else 0)
    elif x is None:
        return "{}x{}".format(width if width is not None else 1,
                height if height is not None else 1)
    return "{}x{}{:+}{:+}".format(width if width is not None else 1,
            height if height is not None else 1,
            x if x is not None else 0, y if y is not None else 0)


def set_application_icons(application, path):
    """Sets the application/window icon for all top-level windows.
    Assumes that the application has two icons in the given path,
    icon_16x16.gif and icon_32x32.gif. (Does nothing on Mac OS X.)
    """
    icon32 = tk.PhotoImage(file=os.path.join(path, "icon_32x32.gif"))
    icon16 = tk.PhotoImage(file=os.path.join(path, "icon_16x16.gif"))
    application.tk.call("wm", "iconphoto", application, "-default", icon32,
            icon16)


def swatch(fill, size=16, outline="#000"):
    """Returns a square color swatch with the given fill outlined in
    black or the given outline color."""
    innerSize = size - 1
    image = tk.PhotoImage(width=size, height=size)
    image.put(fill, (1, 1, innerSize, innerSize))
    image.put(outline, (0, 0, size, 1))
    image.put(outline, (0, innerSize, size, size))
    image.put(outline, (0, 1, 1, size))
    image.put(outline, (innerSize, 1, size, size))
    return image


def set_combobox_item(combobox, text, fuzzy=False):
    for index, value in enumerate(combobox.cget("values")):
        if (fuzzy and text in value) or (value == text):
            combobox.current(index)
            return
    combobox.current(0 if len(combobox.cget("values")) else -1)


def bind_context_menu(widget, callback):
    if mac():
        widget.bind("<2>", callback, "+")
        widget.bind("<Control-1>", callback, "+")
    else:
        widget.bind("<3>", callback, "+")


def font_families():
    """Returns all the system-specific font families, plus the three
    guaranteed built-in font families"""
    return sorted(set(tkfont.families()) |
            {"Helvetica", "Times", "Courier"})


def canonicalize_font_family(family):
    lfamily = family.lower()
    if lfamily == "sans-serif":
        return "Helvetica"
    if lfamily in {"newspaper", "serif"}:
        return "Times"
    if lfamily == "typewriter":
        return "Courier"
    return family


def layout_in_rows(container, width, height, widgets, force=False):
    """Lays out the widgets in rows in the container with the given width.
    Assumes that container is gridded."""
    WidgetData = collections.namedtuple("WidgetData",
            "widget x y width visible")
    oldData = []
    for widget in widgets:
        visible = bool(widget.visible.get()
                if hasattr(widget, "visible") else True)
        oldData.append(WidgetData(widget, widget.winfo_x(),
                widget.winfo_y(), widget.winfo_width(), visible))
        height = max(height, widget.winfo_height())
    newData = []
    frameHeight = height
    x = y = 0
    for data in oldData:
        if not data.visible:
            # We don't need this for the purpose of calculation; but we
            # do need it to compare oldData with newData to avoid
            # redoing the layout unnecessarily.
            newData.append(data)
            continue
        if x > 0 and x + data.width > width: # Doesn't fit
            x = 0
            y += height
            frameHeight += height
        newData.append(WidgetData(data.widget, x, y, data.width, True))
        x += data.width
    if force or oldData != newData:
        container.config(height=frameHeight, width=width)
        for widget in widgets:
            widget.place_forget() # Harmless for those already forgotten
        visible = False
        for data in newData:
            if data.visible:
                data.widget.place(x=data.x, y=data.y)
                visible = True
        if not visible:
            container.grid_remove()
        else:
            container.grid()
    

def add_toolbar_buttons(toolbar, buttons):
    """Adds the buttons to the toolbar; adds Separators for Nones"""
    for i, button in enumerate(buttons):
        if button is None:
            button = ttk.Separator(toolbar)
        else:
            button.config(takefocus=False)
            if isinstance(button, ttk.Button):
                button.config(style="Toolbutton")
        button.pack(side=tk.LEFT, padx=(0 if i == 0 else 2), pady=2)


def validate_spinbox_float(spinbox, number=None):
    if number is None:
        number = spinbox.get()
    if number == "":
        return True
    try:
        x = float(number)
        if float(spinbox.cget("from")) <= x <= float(spinbox.cget("to")):
            return True
    except ValueError:
        pass
    return False


def validate_spinbox_int(spinbox, number=None):
    if number is None:
        number = spinbox.get()
    if number == "":
        return True
    try:
        x = int(number)
        if int(spinbox.cget("from")) <= x <= int(spinbox.cget("to")):
            return True
    except ValueError:
        pass
    return False


def about(application, appname=None, appversion=None):
    data = []
    if appname is not None:
        data.append("{}{}".format(appname,
            (" " + appversion) if appversion is not None else ""))
    python = platform.python_implementation()
    if python == "CPython":
        python = python[1:]
    data.append("{0} {1.major}.{1.minor}.{1.micro}".format(python,
            sys.version_info))
    data.append("Tk {}".format(application.tk.getvar(
            "tk_patchLevel")))
    system = platform.system()
    if system == "Linux":
        distro, version = platform.dist()[:2]
        if distro:
            system = "{}/{}".format(system, distro)
            if version:
                system += " " + version
    elif system == "Windows":
        version, service_pack = platform.win32_ver()[:2]
        if version:
            system = "{} {}".format(system, version)
            if service_pack:
                system += " (SP {})".format(service_pack)
    elif system == "Mac":
        version, info = platform.mac_ver()
        if version:
            system = "{} {}".format(system, version)
            if info:
                system += "." + info[0]
    return " • ".join(data) + "\n" + system + " • " + platform.machine()


# No shortcuts on Mac OS X
class Button(ttk.Button):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if mac():
            self.config(underline=-1)


class Label(ttk.Label):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if mac():
            self.config(underline=-1)


class Checkbutton(ttk.Checkbutton):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if mac():
            self.config(underline=-1)


class Radiobutton(ttk.Radiobutton):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if mac():
            self.config(underline=-1)


# This works on X11 but not Mac OS X 10.5 or Windows 7
# Could do: ("!disabled", "pressed", "sunken"),
class ToggleButton(Button):

    __prepared = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not ToggleButton.__prepared:
            style = ttk.Style()
            style.configure(TOGGLE_BUTTON_STYLE)
            style.map(TOGGLE_BUTTON_STYLE, relief=[
                ("pressed", "sunken"),
                ("selected", "sunken"),
                ("!selected", "raised")])
            ToggleButton.__prepared = True
        self.config(style=TOGGLE_BUTTON_STYLE)
