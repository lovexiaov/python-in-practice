#!/usr/bin/env python3
# cython: language_level=3
# Copyright © 2012 Qtrac Ltd. All rights reserved.
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

import os
import Hyphenate

# Locate your hyph*.dic files
path = "/usr/share/hyph_dic"
usHyphDic = os.path.join(path, "hyph_en_US.dic")
deHyphDic = os.path.join(path, "hyph_de_DE.dic")

# Create wrappers so you don't have to keep specifying the dictionary
hyphenate = lambda word: Hyphenate.hyphenate(word, usHyphDic)
hyphenate_de = lambda word: Hyphenate.hyphenate(word, deHyphDic)

# Use your wrappers
print(hyphenate("extraordinary"))       # prints: ex-traor-di-nary
print(hyphenate_de("außergewöhnlich"))  # prints: außerge-wöhn-lich
"""

import atexit
cimport chyphenate
cimport cpython.pycapsule as pycapsule
#from libc.stdio cimport printf # Helpful for debugging pointers


class Error(Exception): pass


_hdictForFilename = {}


def hyphenate(str word, str filename, str hyphen="-"):
    """Pass a word to hyphenate and a hyphenation file to use, e.g.,
    hyph_en_US.dic (including its full path), and optionally the
    hyphenation character to use.

    Each hyphenation dictionary file is only loaded the first time it is
    needed; after that it is reused.
    """
    cdef chyphenate.HyphenDict *hdict = _get_hdict(filename)
    cdef bytes bword = word.encode("utf-8")
    cdef int word_size = len(bword)
    cdef bytes hyphens = b"\x00" * (word_size + 5)
    cdef bytes hyphenated_word = b"\x00" * (word_size * 2)
    cdef char **rep = NULL
    cdef int *pos = NULL
    cdef int *cut = NULL
    cdef int failed = chyphenate.hnj_hyphen_hyphenate2(hdict, bword,
            word_size, hyphens, hyphenated_word, &rep, &pos, &cut)
    if failed:
        raise Error("hyphenation failed for '{}'".format(word))
    end = hyphenated_word.find(b"\x00")
    return hyphenated_word[:end].decode("utf-8").replace("=", hyphen)


cdef chyphenate.HyphenDict *_get_hdict(
        str filename) except <chyphenate.HyphenDict*>NULL:
    cdef bytes bfilename = filename.encode("utf-8")
    cdef chyphenate.HyphenDict *hdict = NULL
    if bfilename not in _hdictForFilename:
        hdict = chyphenate.hnj_hyphen_load(bfilename)
        #printf("%p\n", hdict)
        if hdict == NULL:
            raise Error("failed to load '{}'".format(filename))
        _hdictForFilename[bfilename] = pycapsule.PyCapsule_New(
                <void*>hdict, NULL, NULL)
        # Setting a destructor didn't work
    capsule = _hdictForFilename.get(bfilename)
    if not pycapsule.PyCapsule_IsValid(capsule, NULL):
        raise Error("failed to load '{}'".format(filename))
    return <chyphenate.HyphenDict*>pycapsule.PyCapsule_GetPointer(capsule,
            NULL)


def _cleanup():
    cdef chyphenate.HyphenDict *hdict = NULL
    for capsule in _hdictForFilename.values():
        if pycapsule.PyCapsule_IsValid(capsule, NULL):
            hdict = (<chyphenate.HyphenDict*>
                    pycapsule.PyCapsule_GetPointer(capsule, NULL))
            if hdict != NULL:
                chyphenate.hnj_hyphen_free(hdict)


atexit.register(_cleanup)
