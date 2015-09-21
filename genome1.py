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
import sys

TRANSFORM, SUMMARIZE = ("TRANSFORM", "SUMMARIZE")

Code = collections.namedtuple("Code", "name code kind")


def main():
    genome = 3 * GENOME
    for code in CODE:
        context = dict(genome=genome, target="G[AC]{2}TT", replace="TCGA")
        execute(code, context)


def execute(code, context):
    try:
        exec(code.code, globals(), context)
        result = context.get("result")
        error = context.get("error")
        handle_result(code, result, error)
    except Exception as err:
        print("'{}' raised an exception: {}\n".format(code.name, err))


def handle_result(code, result, error):
    if error is not None:
        print("'{}' error: {}".format(code.name, error))
    elif result is None:
        print("'{}' produced no result".format(code.name))
    elif code.kind == TRANSFORM:
        genome = result
        try:
            print("'{}' produced a genome of length {}".format(code.name,
                    len(genome)))
        except TypeError as err:
            print("'{}' error: expected a sequence result: {}".format(
                    code.name, err))
    elif code.kind == SUMMARIZE:
        print("'{}' produced a result of {}".format(code.name, result))
    print()


CODE = (
    Code("Count",
"""
import re
matches = re.findall(target, genome)
if matches:
    result = len(matches)
else:
    error = "'{}' not found".format(target)
""", SUMMARIZE)
,
    Code("Replace",
"""
import re
result, count = re.subn(target, replace, genome)
if not count:
    error = "no '{}' replacements made".format(target)
""", TRANSFORM)
,
    Code("Exception Test",
"""
result = 0
for i in range(len(genome)):
    if genome[i] = "A":
        result += 1
""", SUMMARIZE)
,
    Code("Error Test",
"""
import re
matches = re.findall(target * 5, genome)
if matches:
    result = len(matches)
else:
    error = "'{}' not found".format(target)
""", TRANSFORM)
,
    Code("No Result Test",
"""
# No result
""", TRANSFORM)
,
    Code("Wrong Kind Test",
"""
result = len(genome)
""", TRANSFORM)
,
    Code("Termination Test",
"""
import sys
result = "terminating"
sys.exit()
""", SUMMARIZE)
,
    Code("Length",
"""
result = len(genome)
""", SUMMARIZE)
)


GENOME = """TGTTAGTCGCTCCTCGGTCTAAGACATCAAAGTCGGTCTGCGCGGCTGCTCCCTTAGCGCTG
CATAAGAGCGGGGCAGAGAGAGATAGGCGTTTTGACCGTGGCGAGCAAGGCGCGTCATAGTGTCGCCGTGACTG
ATCCTACTGGGTTCTTGCTACTGCCCGGGTCGCAATCCAAAATCTCCACGCGCTGCCACCCCGAAGAAGATATA
TGTCACTGAATTGTATTGGTAACATAGTCGAATTGGGTTCAGGTAAGTTAGTCGTTTAGCCGCTGCGACAGTGG
TGGAAGGGCGAATAGTGTAAAATTTCGCCTGTTAGTGAACATTATCAGGCTGCCATCGTTGATCGCCCCTCTTA
AACTCAGTCTTAAATGAGTTCCCGCCTAAGGTCATTCGTGCCTTGATGATTGATAGCTCGATTGGTCCCTTATG
AAACCGGACCAGAAATGTACCCGCTGAACCGGTGTCATAAGTGTCGCCGTCCCTACGATCGACACTTCCTGAGC
ACGAACGATTTGCGACGCTGTAATGCCACGAGGACTGCATTGAAGATTTTTTGTCCTAGGTGTATGTGCTTCTC
AGGAAGATGCACTACGCACTCCCCTTATCACGGGTGTGACCATCAGGTAGCGTAGGAAGATTAAGACCGCGTAA
CTATCCCTTTCCGTCGCACTCCGACGTCTCAGCACATGTGCGGGGGCCCCTAATTGAGAAACAGTCCATGGTTG
TCCGTAAGTTTCGGAAATCAACTTCACTGCTAGATGGTTGGACGCCAAGGCTCAATAGGTTGGACTCTAAGAAG
""".replace("\n", "")


if __name__ == "__main__":
    main()
