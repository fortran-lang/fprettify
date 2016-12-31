#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
import subprocess
import inspect

# allow unicode for stdin / stdout, it's a mess
try:
    # python 3
    sys.stderr = io.TextIOWrapper(
        sys.stderr.detach(), encoding='UTF-8', line_buffering=True)

except AttributeError:
    # python 2
    import codecs
    utf8_writer = codecs.getwriter('UTF-8')
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


class AlienInvasion(Exception):
    """Should not happen"""
    pass


def eprint(*args, **kwargs):
    """
    Print to stderr - to print output compatible with default unittest output.
    """

    print(*args, file=sys.stderr, **kwargs)
    sys.stderr.flush()  # python 2 print does not have flush argument


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

        mypath = os.path.dirname(os.path.abspath(
            inspect.getfile(inspect.currentframe())))
        cls.runscript = os.path.join(mypath, "../fprettify_run.py")

    @classmethod
    def tearDownClass(cls):
        """
        tearDownClass to be recognized by unittest. Used for test summary
        output.
        """
        if cls.n_parsefail + cls.n_internalfail < 0:
            format = "{:<20}{:<6}"
            eprint('\n' + "=" * 70)
            eprint("IGNORED errors: invalid or old Fortran")
            eprint("-" * 70)
            eprint(format.format("parse errors: ", cls.n_parsefail))
            eprint(format.format("internal errors: ", cls.n_internalfail))

    def test_whitespace(self):
        """simple test for whitespace formatting options -w in [0, 1, 2]"""
        instring = "(/-a-b-(a+b-c)/(-c)*d**e,f[1]%v/)"
        outstring_exp = ["(/-a-b-(a+b-c)/(-c)*d**e,f[1]%v/)",
                         "(/-a-b-(a+b-c)/(-c)*d**e, f[1]%v/)",
                         "(/-a - b - (a + b - c)/(-c)*d**e, f[1]%v/)"]

        outstring = []
        for w in range(0, 3):
            p1 = subprocess.Popen([self.runscript, '-w', str(w)],
                                  stdout=subprocess.PIPE, stdin=subprocess.PIPE)
            outstring.append(p1.communicate(
                instring.encode('UTF-8'))[0].decode('UTF-8'))

        for istr, outstr in enumerate(outstring):
            self.assertEqual(outstring_exp[istr], outstr.strip())

    def test_indent(self):
        """simple test for indent options -i in [0, 3, 4]"""

        indents = [0, 3, 4]

        instring = "iF(teSt)ThEn\nCaLl subr(a,b,&\nc,(/d,&\ne,f/))\nEnD iF"
        outstring_exp = [
            "iF (teSt) ThEn\n" +
            " " * ind + "CaLl subr(a, b, &\n" +
            " " * (10 + ind) + "c, (/d, &\n" +
            " " * (15 + ind) + "e, f/))\nEnD iF"
            for ind in indents
        ]

        outstring = []
        for ind in indents:
            p1 = subprocess.Popen([self.runscript, '-i', str(ind)],
                                  stdout=subprocess.PIPE, stdin=subprocess.PIPE)
            outstring.append(p1.communicate(
                instring.encode('UTF-8'))[0].decode('UTF-8'))

        for istr, outstr in enumerate(outstring):
            self.assertEqual(outstring_exp[istr], outstr.strip())

    def test_io(self):
        """simple test for io (file inplace, stdin & stdout)"""

        # io and unicode
        outstring = []
        instring = "CALL  alien_invasion( 👽 )"
        outstring_exp = "CALL alien_invasion(👽)"

        alien_file = "alien_invasion.f90"
        if os.path.isfile(alien_file):
            raise AlienInvasion("remove file alien_invasion.f90")

        try:
            with io.open(alien_file, 'w', encoding='utf-8') as infile:
                infile.write(instring)

            # testing stdin --> stdout
            p1 = subprocess.Popen(self.runscript,
                                  stdout=subprocess.PIPE, stdin=subprocess.PIPE)
            outstring.append(p1.communicate(
                instring.encode('UTF-8'))[0].decode('UTF-8'))

            # testing file --> stdout
            p1 = subprocess.Popen([self.runscript, alien_file, '--stdout'],
                                  stdout=subprocess.PIPE)
            outstring.append(p1.communicate(
                instring.encode('UTF-8')[0])[0].decode('UTF-8'))

            # testing file --> file (inplace)
            p1 = subprocess.Popen([self.runscript, alien_file])
            p1.wait()

            with io.open(alien_file, 'r', encoding='utf-8') as infile:
                outstring.append(infile.read())

            for outstr in outstring:
                self.assertEqual(outstring_exp, outstr.strip())
        except:
            if os.path.isfile(alien_file):
                os.remove(alien_file)
            raise
        else:
            os.remove(alien_file)


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
                before_nosp = re.sub(
                    r'\n{3,}', r'\n\n', before_content.lower().replace(' ', '').replace('\t', ''))

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
                    msg = ''
                    if test_info == "checksum" and after_exists:
                        result = list(difflib.unified_diff(before_content.splitlines(
                            True), after_content.splitlines(True), fromfile=test_content[0], tofile=line_content[0]))
                        msg = '\n' + ''.join(result)

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
