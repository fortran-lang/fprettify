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
RESULT_FILE = os.path.join(RESULT_DIR, u'expected_results')

# recognize fortran files by extension
FORTRAN_EXTENSIONS = [u".f", u".for", u".ftn",
                      u".f90", u".f95", u".f03", u".fpp"]
FORTRAN_EXTENSIONS += [_.upper() for _ in FORTRAN_EXTENSIONS]

fprettify.set_fprettify_logger(logging.ERROR)


class FPrettifyTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
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
        format = u"{:<20}{:<6}"
        print(u"-" * 70)
        print(format.format(u"successful:", cls.n_success))
        print(format.format(u"parse errors: ", cls.n_parsefail))
        print(format.format(u"internal errors: ", cls.n_internalfail))
        print(format.format(u"unexpected errors: ", cls.n_unexpectedfail))
        print(u"-" * 70)
        sys.stdout.flush()


def addtestmethod(testcase, fpath, ffile):
    def testmethod(testcase):

        dirpath_before = os.path.join(BEFORE_DIR, fpath)
        dirpath_after = os.path.join(AFTER_DIR, fpath)
        if not os.path.exists(dirpath_after):
            os.makedirs(dirpath_after)

        example_before = os.path.join(dirpath_before, ffile)
        example_after = os.path.join(dirpath_after, ffile)

        sep_str = u' : '

        with io.open(example_before, 'r', encoding='utf-8') as infile:

            outstring = StringIO()

            logger = logging.getLogger('fprettify-logger')
            try:
                fprettify.reformat_ffile(infile, outstring)
                m = hashlib.sha256()
                m.update(outstring.getvalue().encode('utf-8'))
                test_info = u"checksum"
                test_line = example_before.replace(
                    BEFORE_DIR, u"") + sep_str + m.hexdigest()
                test_content = test_line.strip().split(sep_str)
                with io.open(example_after, 'w', encoding='utf-8') as outfile:
                    outfile.write(outstring.getvalue())
                FPrettifyTestCase.n_success += 1
            except fprettifyParseException as e:
                logger_d = {u'ffilename': e.filename, u'fline': e.line_nr}
                test_info = u"parse error"
                logger.exception(test_info, extra=logger_d)
                test_line = example_before.replace(
                    BEFORE_DIR, u"") + sep_str + test_info
                test_content = test_line.strip().split(sep_str)
                FPrettifyTestCase.n_parsefail += 1
            except fprettifyInternalException as e:
                logger_d = {u'ffilename': e.filename, u'fline': e.line_nr}
                test_info = u"internal error"
                logger.exception(test_info, extra=logger_d)
                test_line = example_before.replace(
                    BEFORE_DIR, u"") + sep_str + test_info
                test_content = test_line.strip().split(sep_str)
                FPrettifyTestCase.n_internalfail += 1
            except:
                FPrettifyTestCase.n_unexpectedfail += 1
                raise

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
                fpr_hash.write(test_line + u'\n')

    # not sure why this even works, using "test something" (with a space) as function name...
    # however it gives optimal test output
    testmethod.__name__ = str("test " + os.path.join(fpath, ffile))
    setattr(testcase, testmethod.__name__, testmethod)

if not os.path.exists(BEFORE_DIR):
    os.makedirs(BEFORE_DIR)
if not os.path.exists(AFTER_DIR):
    os.makedirs(AFTER_DIR)
if not os.path.exists(RESULT_DIR):
    os.makedirs(RESULT_DIR)
if not os.path.exists(RESULT_FILE):
    io.open(RESULT_FILE, 'w', encoding='utf-8').close()

for dirpath, dirnames, filenames in os.walk(BEFORE_DIR):
    for example in [f for f in filenames if any([f.endswith(_) for _ in FORTRAN_EXTENSIONS])]:
        addtestmethod(FPrettifyTestCase, dirpath.replace(
            BEFORE_DIR, u""), example)
