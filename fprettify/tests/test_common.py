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
import os, sys, io
import inspect
import hashlib
from datetime import datetime
import unittest
import fprettify

def joinpath(path1, path2):
    return os.path.normpath(os.path.join(path1, path2))

#ToDo: replace with __FILE__
_MYPATH = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))

_TIMESTAMP = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

# main directory for running tests
TEST_MAIN_DIR = joinpath(_MYPATH, r'../../fortran_tests')

# directory for external Fortran code
TEST_EXT_DIR = joinpath(TEST_MAIN_DIR, r'test_code')

# directory containing Fortran examples
EXAMPLE_DIR = joinpath(_MYPATH, r'../../examples/in')

# backup directory
BACKUP_DIR = joinpath(TEST_MAIN_DIR, r'test_code_in_' + _TIMESTAMP)

# where to store summarized results
RESULT_DIR = joinpath(TEST_MAIN_DIR, r'test_results')

# expected hash-sums
RESULT_FILE = joinpath(RESULT_DIR, r'expected_results')

# test failures
FAILED_FILE = joinpath(RESULT_DIR, r'failed_results')

# path to fprettify 
RUNSCRIPT = joinpath(_MYPATH, r"../../fprettify.py")


class FprettifyTestCase(unittest.TestCase):
    """
    test class to be recognized by unittest.
    """

    def shortDescription(self):
        """don't print doc string of testmethod"""
        return None

    def setUp(self):
        """
        setUp to be recognized by unittest.
        We have large files to compare, raise the limit
        """
        self.maxDiff = None

    @classmethod
    def setUpClass(cls):
        """
        setUpClass to be recognized by unittest.
        """

        cls.n_success = 0
        cls.n_parsefail = 0
        cls.n_internalfail = 0
        cls.n_unexpectedfail = 0

        FprettifyTestCase.eprint("-" * 70)
        FprettifyTestCase.eprint("recognized Fortran files")
        FprettifyTestCase.eprint(", ".join(fprettify.FORTRAN_EXTENSIONS))
        FprettifyTestCase.eprint("-" * 70)
        FprettifyTestCase.eprint("Applying fprettify to Fortran files in " + TEST_EXT_DIR)
        FprettifyTestCase.eprint("Writing backup of original files to " + BACKUP_DIR)
        FprettifyTestCase.eprint("Storing expected results in " + RESULT_FILE)
        FprettifyTestCase.eprint("Storing failed results in " + FAILED_FILE)
        FprettifyTestCase.eprint("-" * 70)

    @classmethod
    def tearDownClass(cls):
        """
        tearDownClass to be recognized by unittest. Used for test summary
        output.
        """
        if cls.n_parsefail + cls.n_internalfail > 0:
            format = "{:<20}{:<6}"
            FprettifyTestCase.eprint('\n' + "=" * 70)
            FprettifyTestCase.eprint("IGNORED errors: invalid or old Fortran")
            FprettifyTestCase.eprint("-" * 70)
            FprettifyTestCase.eprint(format.format("parse errors: ", cls.n_parsefail))
            FprettifyTestCase.eprint(format.format("internal errors: ", cls.n_internalfail))

    @staticmethod
    def write_result(filename, content, sep_str):  # pragma: no cover
        with io.open(filename, 'a', encoding='utf-8') as outfile:
            outfile.write(sep_str.join(content) + '\n')

    @staticmethod
    def eprint(*args, **kwargs):
        """
        Print to stderr - to print output compatible with default unittest output.
        """
    
        print(*args, file=sys.stderr, flush=True, **kwargs)

