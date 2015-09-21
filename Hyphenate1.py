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

"""
Typical usage:

>>> import os
>>> import Hyphenate1 as Hyphenate
>>> 
>>> # Locate your hyph*.dic files
>>> path = "/usr/share/hyph_dic"
>>> if not os.path.exists(path): path = os.path.dirname(__file__)
>>> usHyphDic = os.path.join(path, "hyph_en_US.dic")
>>> deHyphDic = os.path.join(path, "hyph_de_DE.dic")
>>> 
>>> # Create wrappers so you don't have to keep specifying the dictionary
>>> hyphenate = lambda word: Hyphenate.hyphenate(word, usHyphDic)
>>> hyphenate_de = lambda word: Hyphenate.hyphenate(word, deHyphDic)
>>> 
>>> # Use your wrappers
>>> print(hyphenate("extraordinary"))
ex-traor-di-nary
>>> print(hyphenate_de("außergewöhnlich"))
außerge-wöhn-lich
"""

import atexit
import ctypes
import ctypes.util


class Error(Exception): pass


_libraryName = ctypes.util.find_library("hyphen")
if _libraryName is None:
    _libraryName = ctypes.util.find_library("hyphen.uno")
if _libraryName is None:
    raise Error("cannot find hyphenation library")

# API taken from hyphen.h
_LibHyphen = ctypes.CDLL(_libraryName)


_load = _LibHyphen.hnj_hyphen_load
_load.argtypes = [ctypes.c_char_p]  # const char *filename
_load.restype = ctypes.c_void_p     # HyphenDict *

_int_p = ctypes.POINTER(ctypes.c_int)
_char_p_p = ctypes.POINTER(ctypes.c_char_p)

# The ctypes.c_void_p passed to _hyphenate and _unload is really of type
# struct HyphenDict*
_hyphenate = _LibHyphen.hnj_hyphen_hyphenate2
_hyphenate.argtypes = [
        ctypes.c_void_p,    # HyphenDict *hdict
        ctypes.c_char_p,    # const char *word
        ctypes.c_int,       # int word_size
        ctypes.c_char_p,    # char *hyphens [not needed]
        ctypes.c_char_p,    # char *hyphenated_word
        _char_p_p,          # char ***rep   [not needed]
        _int_p,             # int **pos     [not needed]
        _int_p]             # int **cut     [not needed]
_hyphenate.restype = ctypes.c_int # int

_unload = _LibHyphen.hnj_hyphen_free
_unload.argtypes = [ctypes.c_void_p]  # HyphenDict *hdict
_unload.restype = None

_hdictForFilename = {}


def hyphenate(word, filename, hyphen="-"):
    """Pass a word to hyphenate and a hyphenation file to use, e.g.,
    hyph_en_US.dic (including its full path), and optionally the
    hyphenation character to use.

    Each hyphenation dictionary file is only loaded the first time it is
    needed; after that it is reused.
    """
    originalWord = word
    hdict = _get_hdict(filename)
    word = word.encode("utf-8")
    word_size = ctypes.c_int(len(word))
    word = ctypes.create_string_buffer(word)
    hyphens = ctypes.create_string_buffer(len(word) + 5)
    hyphenated_word = ctypes.create_string_buffer(len(word) * 2)
    rep = _char_p_p(ctypes.c_char_p(None))
    pos = _int_p(ctypes.c_int(0))
    cut = _int_p(ctypes.c_int(0))
    if _hyphenate(hdict, word, word_size, hyphens, hyphenated_word, rep,
            pos, cut):
        raise Error("hyphenation failed for '{}'".format(originalWord))
    return hyphenated_word.value.decode("utf-8").replace("=", hyphen)


def _get_hdict(filename):
    if filename not in _hdictForFilename:
        hdict = _load(ctypes.create_string_buffer(
                filename.encode("utf-8")))
        if hdict is None:
            raise Error("failed to load '{}'".format(filename))
        _hdictForFilename[filename] = hdict
    hdict = _hdictForFilename.get(filename)
    if hdict is None:
        raise Error("failed to load '{}'".format(filename))
    return hdict


def _cleanup():
    for hyphens in _hdictForFilename.values():
        _unload(hyphens)


atexit.register(_cleanup)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
