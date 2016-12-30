"""
Dynamically create tests based on examples in examples/before.
"""
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from builtins import *

import sys
import os
import unittest
import hashlib
import logging
import io
import re
import difflib

# allow for unicode for stdin / stdout
try:
    # python 3
    sys.stderr = io.TextIOWrapper(
        sys.stderr.detach(), encoding='UTF-8', line_buffering=True)
except AttributeError:
    # python 2
    import codecs
    utf8_writer = codecs.getwriter('utf-8')
    sys.stderr = utf8_writer(sys.stderr)

import fprettify
from fprettify.fparse_utils import FprettifyParseException, FprettifyInternalException

BEFORE_DIR = r'fortran_tests/before/'
AFTER_DIR = r'fortran_tests/after/'
RESULT_DIR = r'fortran_tests/test_results/'
RESULT_FILE = os.path.join(RESULT_DIR, 'expected_results')

# recognize fortran files by extension
FORTRAN_EXTENSIONS = [".f", ".for", ".ftn",
                      ".f90", ".f95", ".f03", ".fpp"]
FORTRAN_EXTENSIONS += [_.upper() for _ in FORTRAN_EXTENSIONS]

fprettify.set_fprettify_logger(logging.ERROR)

def eprint(*args, **kwargs):
    """
    Print to stderr - to print output compatible with default unittest output.
    """

    print(*args, file=sys.stderr, **kwargs)
    sys.stderr.flush() # python 2 print does not have flush argument

class FPrettifyTestCase(unittest.TestCase):
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
        self.longMessage = False

    @classmethod
    def setUpClass(cls):
        """
        setUpClass to be recognized by unittest.
        """

        cls.n_success = 0
        cls.n_parsefail = 0
        cls.n_internalfail = 0
        cls.n_unexpectedfail = 0

        eprint("-" * 70)
        eprint("recognized Fortran files")
        eprint(", ".join(FORTRAN_EXTENSIONS))
        eprint("-" * 70)
        eprint("Testing with Fortran files in " + BEFORE_DIR)
        eprint("Writing formatted Fortran files to " + AFTER_DIR)
        eprint("Storing expected results in " + RESULT_FILE)
        eprint("-" * 70)

    @classmethod
    def tearDownClass(cls):
        """
        tearDownClass to be recognized by unittest. Used for test summary
        output.
        """
        format = "{:<20}{:<6}"
        eprint('\n'+"=" * 70)
        eprint("IGNORED errors: invalid or old Fortran")
        eprint("-" * 70)
        eprint(format.format("parse errors: ", cls.n_parsefail))
        eprint(format.format("internal errors: ", cls.n_internalfail))

def addtestmethod(testcase, fpath, ffile):
    """add a test method for each example."""

    def testmethod(testcase):
        """this is the test method invoked for each example."""

        dirpath_before = os.path.join(BEFORE_DIR, fpath)
        dirpath_after = os.path.join(AFTER_DIR, fpath)
        if not os.path.exists(dirpath_after):
            os.makedirs(dirpath_after)

        example_before = os.path.join(dirpath_before, ffile)
        example_after = os.path.join(dirpath_after, ffile)

        def test_result(path, info):
            return [path.replace(BEFORE_DIR, ""), info]

        with io.open(example_before, 'r', encoding='utf-8') as infile:

            outstring = io.StringIO()

            try:
                fprettify.reformat_ffile(infile, outstring)
                m = hashlib.sha256()
                m.update(outstring.getvalue().encode('utf-8'))

                test_info = "checksum"
                test_content = test_result(example_before, m.hexdigest())

                with io.open(example_after, 'w', encoding='utf-8') as outfile:
                    outfile.write(outstring.getvalue())
                FPrettifyTestCase.n_success += 1
            except FprettifyParseException as e:
                test_info = "parse error"
                fprettify.log_exception(e, test_info)
                test_content = test_result(example_before, test_info)
                FPrettifyTestCase.n_parsefail += 1
            except FprettifyInternalException as e:
                test_info = "internal error"
                fprettify.log_exception(e, test_info)
                test_content = test_result(example_before, test_info)
                FPrettifyTestCase.n_internalfail += 1
            except:
                FPrettifyTestCase.n_unexpectedfail += 1
                raise

        after_exists = os.path.isfile(example_after)
        if after_exists:
            with io.open(example_before, 'r', encoding='utf-8') as infile:
                before_content = infile.read()
                before_nosp = re.sub(r'\n{3,}', r'\n\n', before_content.lower().replace(' ', '').replace('\t', ''))

            with io.open(example_after, 'r', encoding='utf-8') as outfile:
                after_content = outfile.read()
                after_nosp = after_content.lower().replace(' ', '')

            testcase.assertMultiLineEqual(before_nosp, after_nosp)

        sep_str = ' : '
        with io.open(RESULT_FILE, 'r', encoding='utf-8') as fpr_hash:
            found = False
            for line in fpr_hash:
                line_content = line.strip().split(sep_str)
                if line_content[0] == test_content[0]:
                    found = True
                    eprint(test_info, end=" ")
                    msg=''
                    if test_info == "checksum" and after_exists:
                        d = difflib.Differ()
                        result = list(d.compare(before_content.splitlines(True), after_content.splitlines(True)))
                        msg = '\n'+''.join(result)

                    testcase.assertEqual(line_content[1], test_content[1], msg)
                    break

        if not found:
            eprint(test_info + " new", end=" ")
            with io.open(RESULT_FILE, 'a', encoding='utf-8') as fpr_hash:
                fpr_hash.write(sep_str.join(test_content) + '\n')

    # not sure why this even works, using "test something" (with a space) as function name...
    # however it gives optimal test output
    try:
        testmethod.__name__ = ("test " + os.path.join(fpath, ffile))
    except TypeError:
        # need to encode in python 2 since we are using unicode strings
        testmethod.__name__ = (
            "test " + os.path.join(fpath, ffile)).encode('utf-8')

    setattr(testcase, testmethod.__name__, testmethod)

# make sure all directories exist
if not os.path.exists(BEFORE_DIR):
    os.makedirs(BEFORE_DIR)
if not os.path.exists(AFTER_DIR):
    os.makedirs(AFTER_DIR)
if not os.path.exists(RESULT_DIR):
    os.makedirs(RESULT_DIR)
if not os.path.exists(RESULT_FILE):
    io.open(RESULT_FILE, 'w', encoding='utf-8').close()

# this prepares FPrettifyTestCase class when module is loaded by unittest
for dirpath, dirnames, filenames in os.walk(BEFORE_DIR):
    for example in [f for f in filenames if any(f.endswith(_) for _ in FORTRAN_EXTENSIONS)]:
        addtestmethod(FPrettifyTestCase, dirpath.replace(
            BEFORE_DIR, ""), example)
