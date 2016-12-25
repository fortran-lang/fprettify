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

BEFORE_DIR = r'examples/before/'
AFTER_DIR = r'examples/after/'
HASHDIR = r'examples/test_checksums/'
HASHFILE = os.path.join(HASHDIR, 'sha256_hash')
FORTRAN_EXTENSIONS = [".f90", ".F", ".f"]

class FPrettifyTestCase(unittest.TestCase):
    def setUp(self):
        fprettify.set_fprettify_logger(logging.INFO)

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

            with open(example_after, 'w') as outfile:
                fprettify.reformat_ffile(infile, outfile)

            m = hashlib.sha256()
            with open(example_after, 'r') as outfile:
                m.update(outfile.read().encode('utf-8'))
            test_line = example_before.replace(BEFORE_DIR,"") + sep_str + m.hexdigest()
            test_content = test_line.strip().split(sep_str)

        with open(HASHFILE, 'r') as fpr_hash:
            found = False
            for line in fpr_hash:
                line_content = line.strip().split(sep_str)
                if line_content[0] == test_content[0]:
                    found = True
                    print("checksum", end=" ")
                    sys.stdout.flush()
                    testcase.assertEqual(line_content[1], test_content[1])
                    break

        if not found:
            print("new", end=" ")
            sys.stdout.flush()
            with open(HASHFILE, 'a') as fpr_hash:
                fpr_hash.write(test_line+'\n')

    testmethod.__name__ = "test_" + ffile
    setattr(testcase, testmethod.__name__, testmethod)


if not os.path.exists(BEFORE_DIR):
    os.makedirs(BEFORE_DIR)
if not os.path.exists(AFTER_DIR):
    os.makedirs(AFTER_DIR)
if not os.path.exists(HASHDIR):
    os.makedirs(HASHDIR)
if not os.path.exists(HASHFILE):
    open(HASHFILE, 'w').close()

for dirpath, dirnames, filenames in os.walk(BEFORE_DIR):
    for example in [f for f in filenames if any([f.endswith(_) for _ in FORTRAN_EXTENSIONS])]:
        addtestmethod(FPrettifyTestCase, dirpath.replace(BEFORE_DIR,""), example)

if __name__ == '__main__':
    unittest.main(argv=sys.argv)
