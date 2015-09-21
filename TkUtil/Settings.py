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

import configparser
import os
import sys


Data = None # This is set after load() has been called
# DOMAIN and APPNAME must be populated before calling any functions
DOMAIN = None 
APPNAME = None
_SUFFIX = ".ini"


class ConfigParser(configparser.ConfigParser):


    def get_str(self, section, option, default=None):
        if self.has_option(section, option):
            return self.get(section, option)
        return default


    def get_int(self, section, option, default=None):
        if self.has_option(section, option):
            return self.getint(section, option)
        return default


    def get_float(self, section, option, default=None):
        if self.has_option(section, option):
            return self.getfloat(section, option)
        return default


    def get_bool(self, section, option, default=None):
        if self.has_option(section, option):
            return self.getboolean(section, option)
        return default


    def put(self, section, option, value):
        if not self.has_section(section):
            self.add_section(section)
        self.set(section, option, str(value))


def load():
    global Data
    Data = ConfigParser()
    filename = _load_filename()
    if filename is not None:
        Data.read(filename)
    return Data


def save():
    with open(_save_filename(), "w") as file:
        Data.write(file)


def _load_filename():
    assert APPNAME
    filename = APPNAME + _SUFFIX
    paths = _path_list()
    for path in paths:
        file = os.path.join(path, filename)
        if os.path.exists(file):
            return file
    # return None # No settings file exists


def _save_filename():
    assert APPNAME
    filename = APPNAME + _SUFFIX
    paths = _path_list()
    for path in paths:
        if os.path.exists(path):
            return os.path.join(path, filename)
        else:
            try:
                os.makedirs(path)
                return os.path.join(path, filename)
            except os.error:
                pass
    raise OSError("no valid path to save settings to")


def _path_list():
    assert DOMAIN
    paths = []
    home = os.path.expanduser("~")
    if sys.platform.startswith("win"):
        path = os.path.expandvars("%APPDATA%")
        if "%" not in path:
            paths.append(path)
        path = os.path.expandvars("%COMMON_APPDATA%")
        if "%" not in path:
            paths.append(path)
        paths.append(r"\Users\Default\AppData\Local")
        paths.append(home)
    else:
        paths.append(home + "/.")
        path = os.path.join(home, ".config")
        paths.append(path)
        path = os.path.join(path, DOMAIN)
        paths.append(path)
        paths.reverse()
    return paths


if __name__ == "__main__":
    DOMAIN = "Qtrac"
    APPNAME = "MyApp"
    print(_path_list())
    print(_save_filename())
    print(_load_filename())
