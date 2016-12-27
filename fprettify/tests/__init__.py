"""
Dynamically create tests based on examples in examples/before.
"""

from __future__ import print_function
import sys
import os
import unittest
import hashlib
import logging
import io
import re

import fprettify
from fprettify.fparse_utils import FprettifyParseException, FprettifyInternalException

try:
    # Use the old Python 2's StringIO if available since
    # the converter does not yield unicode strings (yet)
    from StringIO import StringIO
except ImportError:
    from io import StringIO

BEFORE_DIR = r'fortran_tests/before/'
AFTER_DIR = r'fortran_tests/after/'
RESULT_DIR = r'fortran_tests/test_results/'
RESULT_FILE = os.path.join(RESULT_DIR, u'expected_results')

# recognize fortran files by extension
FORTRAN_EXTENSIONS = [u".f", u".for", u".ftn",
                      u".f90", u".f95", u".f03", u".fpp"]
FORTRAN_EXTENSIONS += [_.upper() for _ in FORTRAN_EXTENSIONS]

fprettify.set_fprettify_logger(logging.ERROR)


class FPrettifyTestCase(unittest.TestCase):
    """
    test class to be recognized by unittest.
    """

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
        print(u"-" * 70)
        print(u"recognized Fortran files")
        print(u", ".join(FORTRAN_EXTENSIONS))
        print(u"-" * 70)
        print(u"Testing with Fortran files in " + BEFORE_DIR)
        print(u"Writing formatted Fortran files to " + AFTER_DIR)
        print(u"Storing expected results in " + RESULT_FILE)
        print(u"-" * 70)
        print(
            u"NOTE: internal error or parse error can happen if file is not 'modern' Fortran")
        print(u"-" * 70)
        sys.stdout.flush()

    @classmethod
    def tearDownClass(cls):
        """
        tearDownClass to be recognized by unittest.
        """

        format = u"{:<20}{:<6}"
        print(u"-" * 70)
        print(format.format(u"successful:", cls.n_success))
        print(format.format(u"parse errors: ", cls.n_parsefail))
        print(format.format(u"internal errors: ", cls.n_internalfail))
        print(format.format(u"unexpected errors: ", cls.n_unexpectedfail))
        print(u"-" * 70)
        sys.stdout.flush()


def addtestmethod(testcase, fpath, ffile):
    """ add a test method for each example. """

    def testmethod(testcase):
        """ this is the test method invoked for each example. """

        dirpath_before = os.path.join(BEFORE_DIR, fpath)
        dirpath_after = os.path.join(AFTER_DIR, fpath)
        if not os.path.exists(dirpath_after):
            os.makedirs(dirpath_after)

        example_before = os.path.join(dirpath_before, ffile)
        example_after = os.path.join(dirpath_after, ffile)

        def test_result(path, info):
            return [path.replace(BEFORE_DIR, u""), info]

        with io.open(example_before, 'r', encoding='utf-8') as infile:

            outstring = StringIO()

            try:
                fprettify.reformat_ffile(infile, outstring)
                m = hashlib.sha256()
                m.update(outstring.getvalue().encode('utf-8'))

                test_info = u"checksum"
                test_content = test_result(example_before, m.hexdigest())

                with io.open(example_after, 'w', encoding='utf-8') as outfile:
                    outfile.write(outstring.getvalue())
                FPrettifyTestCase.n_success += 1
            except FprettifyParseException as e:
                test_info = u"parse error"
                fprettify.log_exception(e, test_info)
                test_content = test_result(example_before, test_info)
                FPrettifyTestCase.n_parsefail += 1
            except FprettifyInternalException as e:
                test_info = u"internal error"
                fprettify.log_exception(e, test_info)
                test_content = test_result(example_before, test_info)
                FPrettifyTestCase.n_internalfail += 1
            except:
                FPrettifyTestCase.n_unexpectedfail += 1
                raise

        if os.path.isfile(example_after):
            with io.open(example_before, 'r', encoding='utf-8') as infile:
                before_nosp=re.sub(r'\n{3,}',r'\n\n', infile.read().lower().replace(' ', '').replace('\t',''))

            with io.open(example_after, 'r', encoding='utf-8') as outfile:
                after_nosp=outfile.read().lower().replace(' ', '')

            testcase.assertMultiLineEqual(before_nosp, after_nosp)

        sep_str = u' : '
        with io.open(RESULT_FILE, 'r', encoding='utf-8') as fpr_hash:
            found = False
            for line in fpr_hash:
                line_content = line.strip().split(sep_str)
                if line_content[0] == test_content[0]:
                    found = True
                    print(test_info, end=u" ")
                    sys.stdout.flush()
                    testcase.assertEqual(line_content[1], test_content[1])
                    break

        if not found:
            print(test_info + u" new", end=u" ")
            sys.stdout.flush()
            with io.open(RESULT_FILE, 'a', encoding='utf-8') as fpr_hash:
                fpr_hash.write(sep_str.join(test_content) + u'\n')

    # not sure why this even works, using "test something" (with a space) as function name...
    # however it gives optimal test output
    testmethod.__name__ = str("test " + os.path.join(fpath, ffile))
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
    for example in [f for f in filenames if any( f.endswith(_) for _ in FORTRAN_EXTENSIONS)]:
        addtestmethod(FPrettifyTestCase, dirpath.replace(
            BEFORE_DIR, u""), example)
