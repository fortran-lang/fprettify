"""
Dynamically create tests based on examples in examples/before.
"""

from __future__ import print_function
import sys
import os
import unittest
import hashlib
import logging

import fprettify
from fprettify.fparse_utils import fprettifyParseException, fprettifyInternalException

try:
    # Use the old Python 2's StringIO if available since
    # the converter does not yield unicode strings (yet)
    from StringIO import StringIO
except ImportError:
    from io import StringIO

BEFORE_DIR = r'fortran_tests/before/'
AFTER_DIR = r'fortran_tests/after/'
RESULT_DIR = r'fortran_tests/test_results/'
RESULT_FILE = os.path.join(RESULT_DIR, 'expected_results')

# recognize fortran files by extension
FORTRAN_EXTENSIONS = [".f", ".for", ".ftn", ".f90", ".f95", ".f03", ".fpp"]
FORTRAN_EXTENSIONS += [_.upper() for _ in FORTRAN_EXTENSIONS]

fprettify.set_fprettify_logger(logging.ERROR)


class FPrettifyTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.n_success = 0
        cls.n_parsefail = 0
        cls.n_internalfail = 0
        cls.n_unexpectedfail = 0
        print("-" * 70)
        print("recognized Fortran files")
        print(", ".join(FORTRAN_EXTENSIONS))
        print("-" * 70)
        print("Testing with Fortran files in " + BEFORE_DIR)
        print("Writing formatted Fortran files to " + AFTER_DIR)
        print("Storing expected results in " + RESULT_FILE)
        print("-" * 70)
        print(
            "NOTE: internal error or parse error can happen if file is not 'modern' Fortran")
        print("-" * 70)
        sys.stdout.flush()

    @classmethod
    def tearDownClass(cls):
        format = "{:<20}{:<6}"
        print("-" * 70)
        print(format.format("successful:", cls.n_success))
        print(format.format("parse errors: ", cls.n_parsefail))
        print(format.format("internal errors: ", cls.n_internalfail))
        print(format.format("unexpected errors: ", cls.n_unexpectedfail))
        print("-" * 70)
        sys.stdout.flush()


def addtestmethod(testcase, fpath, ffile):
    def testmethod(testcase):

        dirpath_before = os.path.join(BEFORE_DIR, fpath)
        dirpath_after = os.path.join(AFTER_DIR, fpath)
        if not os.path.exists(dirpath_after):
            os.makedirs(dirpath_after)

        example_before = os.path.join(dirpath_before, ffile)
        example_after = os.path.join(dirpath_after, ffile)

        sep_str = ' : '

        with open(example_before, 'r') as infile:

            outstring = StringIO()

            logger = logging.getLogger('fprettify-logger')
            try:
                fprettify.reformat_ffile(infile, outstring)
                m = hashlib.sha256()
                m.update(outstring.getvalue().encode('utf-8'))
                test_info = "checksum"
                test_line = example_before.replace(
                    BEFORE_DIR, "") + sep_str + m.hexdigest()
                test_content = test_line.strip().split(sep_str)
                with open(example_after, 'w') as outfile:
                    outfile.write(outstring.getvalue())
                FPrettifyTestCase.n_success += 1
            except fprettifyParseException as e:
                logger_d = {'ffilename': e.filename, 'fline': e.line_nr}
                test_info = "parse error"
                logger.exception(test_info, extra=logger_d)
                test_line = example_before.replace(
                    BEFORE_DIR, "") + sep_str + test_info
                test_content = test_line.strip().split(sep_str)
                FPrettifyTestCase.n_parsefail += 1
            except fprettifyInternalException as e:
                logger_d = {'ffilename': e.filename, 'fline': e.line_nr}
                test_info = "internal error"
                logger.exception(test_info, extra=logger_d)
                test_line = example_before.replace(
                    BEFORE_DIR, "") + sep_str + test_info
                test_content = test_line.strip().split(sep_str)
                FPrettifyTestCase.n_internalfail += 1
            except:
                FPrettifyTestCase.n_unexpectedfail += 1
                raise

        with open(RESULT_FILE, 'r') as fpr_hash:
            found = False
            for line in fpr_hash:
                line_content = line.strip().split(sep_str)
                if line_content[0] == test_content[0]:
                    found = True
                    print(test_info, end=" ")
                    sys.stdout.flush()
                    testcase.assertEqual(line_content[1], test_content[1])
                    break

        if not found:
            print(test_info + " new", end=" ")
            sys.stdout.flush()
            with open(RESULT_FILE, 'a') as fpr_hash:
                fpr_hash.write(test_line + '\n')

    # not sure why this even works, using "test something" (with a space) as function name...
    # however it gives optimal test output
    testmethod.__name__ = "test " + os.path.join(fpath, ffile)
    setattr(testcase, testmethod.__name__, testmethod)

if not os.path.exists(BEFORE_DIR):
    os.makedirs(BEFORE_DIR)
if not os.path.exists(AFTER_DIR):
    os.makedirs(AFTER_DIR)
if not os.path.exists(RESULT_DIR):
    os.makedirs(RESULT_DIR)
if not os.path.exists(RESULT_FILE):
    open(RESULT_FILE, 'w').close()

for dirpath, dirnames, filenames in os.walk(BEFORE_DIR):
    for example in [f for f in filenames if any([f.endswith(_) for _ in FORTRAN_EXTENSIONS])]:
        addtestmethod(FPrettifyTestCase, dirpath.replace(
            BEFORE_DIR, ""), example)
