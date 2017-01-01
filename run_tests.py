#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

    if args.reset:
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
