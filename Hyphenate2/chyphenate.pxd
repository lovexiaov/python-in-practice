# Copyright © 2012 Qtrac Ltd. All rights reserved.
# This program or module is free software: you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version. It is provided for
# educational purposes and is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.


cdef extern from "hyphen.h":
    ctypedef struct HyphenDict:
        pass

    HyphenDict *hnj_hyphen_load(char *filename)
    void hnj_hyphen_free(HyphenDict *hdict)
    int hnj_hyphen_hyphenate2(HyphenDict *hdict, char *word,
            int word_size, char *hyphens, char *hyphenated_word,
            char ***rep, int **pos, int **cut)
