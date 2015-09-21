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

# Build with: python3 setup.py build_ext --inplace

import distutils.core
import distutils.extension
import Cython.Distutils


distutils.core.setup(name="Hyphenate2",
        cmdclass={"build_ext": Cython.Distutils.build_ext},
        ext_modules=[distutils.extension.Extension("Hyphenate",
                ["Hyphenate.pyx"], libraries=["hyphen"])])
