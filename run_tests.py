#!/usr/bin/env python
# -*- coding: utf-8 -*-
###############################################################################
#    This file is part of fprettify.
#    Copyright (C) 2016-2019 Patrick Seewald, CP2K developers group
#
#    fprettify is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    fprettify is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with fprettify. If not, see <http://www.gnu.org/licenses/>.
###############################################################################

import unittest
from fprettify.tests import FPrettifyTestCase, FAILED_FILE, RESULT_FILE
import fileinput
import io
import os
import sys
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Run tests', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-r", "--reset", action='store_true', default=False,
                        help="Reset test results to new results of failed tests")

    args = parser.parse_args()

    suite = unittest.TestLoader().loadTestsFromTestCase(FPrettifyTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)

    if args.reset and os.path.isfile(FAILED_FILE):
        sep_str = ' : '
        with io.open(FAILED_FILE, 'r', encoding='utf-8') as infile:
            for failed_line in infile:
                failed_content = failed_line.strip().split(sep_str)
                for result_line in fileinput.input(RESULT_FILE, inplace=True):
                    result_content = result_line.strip().split(sep_str)
                    if result_content[0] == failed_content[0]:
                        sys.stdout.write(failed_line)
                    else:
                        sys.stdout.write(result_line)

        os.remove(FAILED_FILE)
