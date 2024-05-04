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


import hashlib
import logging
import io
import re
import os
import difflib
import configparser
import shutil
import shlex
import fprettify
from fprettify.tests.test_common import  TEST_MAIN_DIR, TEST_EXT_DIR, BACKUP_DIR, RESULT_DIR, RESULT_FILE, FAILED_FILE, FprettifyTestCase, joinpath


fprettify.set_fprettify_logger(logging.ERROR)

def generate_suite(suite=None, name=None):
    import git
    config = configparser.ConfigParser()
    config.read(joinpath(TEST_MAIN_DIR, 'testsuites.config'))

    if suite is None and name is None:
        return None

    for key in config.sections():
        code = config[key]
        if code['suite'] == suite or key == name:
            orig = os.getcwd()
            try:
                os.chdir(TEST_EXT_DIR)

                if not os.path.isdir(code['path']):
                    print(f"obtaining {key} ...")
                    exec(code['obtain'])
            finally:
                os.chdir(orig)

            addtestcode(code['path'], code['options'])
    return FprettifyTestCase

def addtestcode(code_path, options):
    print(f"creating test cases from {code_path} ...")
    # dynamically create test cases from fortran files in test directory
    for dirpath, _, filenames in os.walk(joinpath(TEST_EXT_DIR, code_path)):
        for example in [f for f in filenames if any(f.endswith(_) for _ in fprettify.FORTRAN_EXTENSIONS)]:
            rel_dirpath = os.path.relpath(dirpath, start=TEST_EXT_DIR)
            addtestmethod(FprettifyTestCase, rel_dirpath, example, options)

def addtestmethod(testcase, fpath, ffile, options):
    """add a test method for each example."""

    def testmethod(testcase):
        """this is the test method invoked for each example."""

        example_path = joinpath(TEST_EXT_DIR, fpath)
        backup_path = joinpath(BACKUP_DIR, fpath)
        if not os.path.exists(backup_path):
            os.makedirs(backup_path)

        example = joinpath(example_path, ffile)
        example_backup = joinpath(backup_path, ffile)

        def test_result(path, info):
            return [os.path.relpath(path, TEST_EXT_DIR), info]

        with io.open(example, 'r', encoding='utf-8') as infile:
            instring = infile.read()

        # write backup of original file
        with io.open(example_backup, 'w', encoding='utf-8') as outfile:
            outfile.write(instring)

        # apply fprettify
        with io.open(example, 'r', encoding='utf-8') as infile:
            outfile = io.StringIO()

            try:
                parser = fprettify.get_arg_parser()
                args = parser.parse_args(shlex.split(options))
                args = fprettify.process_args(args)

                fprettify.reformat_ffile(infile, outfile, **args)
                outstring = outfile.getvalue()
                m = hashlib.sha256()
                m.update(outstring.encode('utf-8'))

                test_info = "checksum"
                test_content = test_result(example, m.hexdigest())

                FprettifyTestCase.n_success += 1
            except fprettify.FprettifyParseException as e:
                test_info = "parse error"
                fprettify.log_exception(e, test_info, level="warning")
                test_content = test_result(example, test_info)
                FprettifyTestCase.n_parsefail += 1
            except fprettify.FprettifyInternalException as e:
                test_info = "internal error"
                fprettify.log_exception(e, test_info, level="warning")
                test_content = test_result(example, test_info)
                FprettifyTestCase.n_internalfail += 1
            except:  # pragma: no cover
                FprettifyTestCase.n_unexpectedfail += 1
                raise

        # overwrite example
        with io.open(example, 'w', encoding='utf-8') as outfile:
            outfile.write(outstring)

        # check that no changes other than whitespace changes or lower/upper case occured
        before_nosp = re.sub(
            r'\n{3,}', r'\n\n', instring.lower().replace(' ', '').replace('\t', ''))

        after_nosp = outstring.lower().replace(' ', '')

        testcase.assertMultiLineEqual(before_nosp, after_nosp)

        sep_str = ' : '
        with io.open(RESULT_FILE, 'r', encoding='utf-8') as infile:
            found = False
            for line in infile:
                line_content = line.strip().split(sep_str)
                if line_content[0] == test_content[0]:
                    found = True
                    FprettifyTestCase.eprint(test_info, end=" ")
                    msg = '{} (old) != {} (new)'.format(
                        line_content[1], test_content[1])
                    if test_info == "checksum" and outstring.count('\n') < 10000:
                        # difflib can not handle large files
                        result = list(difflib.unified_diff(instring.splitlines(
                            True), outstring.splitlines(True), fromfile=test_content[0], tofile=line_content[0]))
                        msg += '\n' + ''.join(result)
                    try:
                        testcase.assertEqual(
                            line_content[1], test_content[1], msg)
                    except AssertionError:  # pragma: no cover
                        FprettifyTestCase.write_result(
                            FAILED_FILE, test_content, sep_str)
                        raise
                    break

        if not found:  # pragma: no cover
            FprettifyTestCase.eprint(test_info + " new", end=" ")
            FprettifyTestCase.write_result(RESULT_FILE, test_content, sep_str)

    # not sure why this even works, using "test something" (with a space) as function name...
    # however it gives optimal test output
    testmethod.__name__ = ("test " + joinpath(fpath, ffile))

    setattr(testcase, testmethod.__name__, testmethod)

# make sure all directories exist
if not os.path.exists(TEST_EXT_DIR):  # pragma: no cover
    os.makedirs(TEST_EXT_DIR)
if not os.path.exists(BACKUP_DIR):  # pragma: no cover
    os.makedirs(BACKUP_DIR)
if not os.path.exists(RESULT_DIR):  # pragma: no cover
    os.makedirs(RESULT_DIR)
if not os.path.exists(RESULT_FILE):  # pragma: no cover
    io.open(RESULT_FILE, 'w', encoding='utf-8').close()
if os.path.exists(FAILED_FILE):  # pragma: no cover
    # erase failures from previous testers
    io.open(FAILED_FILE, 'w', encoding='utf-8').close()


